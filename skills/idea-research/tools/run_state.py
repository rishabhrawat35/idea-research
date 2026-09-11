#!/usr/bin/env python3
"""run_state.py, the stage ledger for one idea-research run.

A ten stage pipeline that depends on somebody remembering every stage is a
pipeline that loses a stage quietly. This script turns the checklist into data,
so a script can say which stage has no output on disk.

    python3 tools/run_state.py init  runs/<slug>/ --mode new-thing
    python3 tools/run_state.py done  runs/<slug>/ <stage-id> [--note "one line"]
    python3 tools/run_state.py check runs/<slug>/ [--strict] [--json]

It writes runs/<slug>/_state.json for scripts and runs/<slug>/_state.md for
people. Standard library only, Python 3.8 compatible.

Exit codes: 0 clean, 1 anything the caller must fix.
"""

import argparse
import datetime
import json
import os
import sys

SCHEMA = 1

# The pipeline, in order. `outputs` are paths relative to the run directory.
# Every stage names at least one output, so a stage that never ran is visible on
# disk rather than only in its own record. A stage whose `outputs` list is empty
# would be proved by its record in _state.json alone, which is how the lint gate
# used to pass on trust.
STAGES = [
    {"id": "brief",     "label": "brief",              "outputs": ["00_brief.md"]},
    {"id": "scout",     "label": "scout",              "outputs": ["01_scout.md"]},
    {"id": "research",  "label": "research lanes",      "outputs": ["_findings.md", "lanes/"]},
    # Four later prompts read claims_brief.md rather than the full ledger, so a
    # run that never wrote the brief must fail here instead of failing later.
    {"id": "ledger",    "label": "claim ledger",       "outputs": ["claims_summary.md",
                                                                   "claims_brief.md",
                                                                   "contradictions.md",
                                                                   "verify_queue.md"]},
    {"id": "pair",      "label": "for and against",    "outputs": ["04a_case_for.md",
                                                                   "04b_case_against.md"]},
    {"id": "reconcile", "label": "reconcile",          "outputs": ["05_reconcile.md"]},
    {"id": "checkback", "label": "checkback",          "outputs": ["05c_checkback.md"],
     "optional": True},
    # write comes before design, because SKILL.md writes the answer at stage 6 and
    # designs the page at stage 7. The order is read by check's "First gap" line, so
    # an inverted list sends an orchestrator to the design agent with no ANSWER.md.
    {"id": "write",     "label": "write answer",       "outputs": ["ANSWER.md"]},
    {"id": "design",    "label": "design and structure", "outputs": ["theme.json",
                                                                   "layout.md"]},
    {"id": "lint",      "label": "lint gate",          "outputs": ["lint.json"]},
    # The UX peer now runs beside the editor rather than inside the design
    # stage, so 07_ux.md is proof that the edit stage ran both judges.
    {"id": "edit",      "label": "edit pass",          "outputs": ["06_edit.md",
                                                                   "07_ux.md"]},
    {"id": "render",    "label": "render",             "outputs": ["report.html",
                                                                   "ANSWER_clean.md"]},
]

STAGE_IDS = [s["id"] for s in STAGES]
BY_ID = dict((s["id"], s) for s in STAGES)

MODES = ["full", "teardown", "money-first", "new-thing", "proxy", "quick"]

# quick mode skips the adversarial pair, the reconciler, the checkback, the
# design stage and the edit pass. It keeps render, so a quick run still hands
# over a page, built on the default theme. Every other mode runs the whole
# pipeline.
QUICK_STAGES = ["brief", "scout", "research", "ledger", "write", "lint", "render"]


def stages_for_mode(mode):
    if mode == "quick":
        return [s for s in STAGE_IDS if s in QUICK_STAGES]
    return list(STAGE_IDS)


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat()


def state_paths(run_dir):
    return (os.path.join(run_dir, "_state.json"),
            os.path.join(run_dir, "_state.md"))


def die(msg, code=1):
    sys.stderr.write("run_state: " + msg + "\n")
    return code


def is_optional(stage_id):
    return bool(BY_ID[stage_id].get("optional"))


# ---------------------------------------------------------------- load / save

def load_state(run_dir):
    """Return (state, error_message). state is None when it could not be read."""
    js, _ = state_paths(run_dir)
    if os.path.isfile(run_dir):
        return None, ("%s is a file, not a run directory. This command takes "
                      "runs/<slug>/, the directory that holds the file."
                      % run_dir)
    if not os.path.isdir(run_dir):
        return None, ("no such run directory: %s" % run_dir)
    if not os.path.exists(js):
        return None, ("no _state.json in %s\n"
                      "            this run was never initialised. Run:\n"
                      "              python3 tools/run_state.py init %s --mode full"
                      % (run_dir, run_dir))
    try:
        with open(js, "r") as fh:
            state = json.load(fh)
    except ValueError as exc:
        return None, ("_state.json is not valid JSON (%s). Re-run init to rebuild it."
                      % exc)
    except (IOError, OSError) as exc:
        return None, ("cannot read _state.json (%s)" % exc)
    if not isinstance(state, dict) or "mode" not in state:
        return None, "_state.json is not a run state file. Re-run init to rebuild it."
    if state.get("mode") not in MODES:
        return None, ("_state.json names an unknown mode %r. Valid modes: %s"
                      % (state.get("mode"), ", ".join(MODES)))
    stages = state.get("stages")
    if not isinstance(stages, dict):
        state["stages"] = {}
    return state, None


def save_state(run_dir, state):
    js, md = state_paths(run_dir)
    state["updated"] = now_iso()
    # stage_order is a copy of the pipeline, so it is rewritten on every save. Written
    # once at init, a run started before the write and design stages were put back in
    # pipeline order would have carried the old order for the rest of its life.
    state["stage_order"] = STAGE_IDS
    with open(js, "w") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    with open(md, "w") as fh:
        fh.write(render_markdown(run_dir, state))


# ------------------------------------------------------------------ inspection

def inspect(run_dir, state):
    """Build one row per stage: what is required, what is on disk, what was recorded."""
    mode = state["mode"]
    required = stages_for_mode(mode)
    recorded = state.get("stages", {})
    rows = []
    for index, stage in enumerate(STAGES, start=1):
        sid = stage["id"]
        rec = recorded.get(sid) or {}
        outputs = list(stage["outputs"])
        missing = [o for o in outputs
                   if not os.path.exists(os.path.join(run_dir, o))]
        in_mode = sid in required
        optional = is_optional(sid)
        row = {
            "order": index,
            "id": sid,
            "label": stage["label"],
            "outputs": outputs,
            "missing": missing,
            "present": (not missing) if outputs else None,
            "in_mode": in_mode,
            "optional": optional,
            "recorded": bool(rec),
            "note": (rec.get("note") or "").strip(),
            "at": rec.get("at", ""),
        }
        row["status"] = status_of(row)
        row["gap"] = gap_reason(row)
        rows.append(row)
    return rows


def status_of(row):
    if not row["in_mode"]:
        return "not in this mode"
    if not row["outputs"]:
        return "recorded" if row["recorded"] else "NOT RECORDED"
    if row["missing"]:
        shown = row["missing"][:2]
        tail = ", ..." if len(row["missing"]) > 2 else ""
        if row["optional"]:
            return "optional, absent"
        return "MISSING " + ", ".join(shown) + tail
    return "present"


def gap_reason(row):
    """The one sentence a person needs, or empty when this stage is fine."""
    if not row["in_mode"] or row["optional"]:
        return ""
    if not row["outputs"]:
        if not row["recorded"]:
            return ("stage %s (%s) writes no file of its own and was never "
                    "recorded. Run it, then: run_state.py done <run> %s"
                    % (row["id"], row["label"], row["id"]))
        return ""
    if row["missing"]:
        return ("stage %s (%s) has no %s in the run directory"
                % (row["id"], row["label"], ", ".join(row["missing"])))
    return ""


def outputs_cell(row):
    if not row["outputs"]:
        return "(no file, record only)"
    return ", ".join(row["outputs"])


def note_cell(row):
    if not row["in_mode"]:
        return "-"
    if row["note"]:
        return row["note"]
    if row["recorded"]:
        return "(recorded, no note)"
    if row["outputs"] and not row["missing"]:
        return "(output on disk, never recorded)"
    return "-"


# --------------------------------------------------------------- text renderer

def table(rows, headers):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = []
    fmt = lambda cells: "  " + "  ".join(
        cells[i].ljust(widths[i]) for i in range(len(cells))).rstrip()
    lines.append(fmt(headers))
    lines.append(fmt(["-" * w for w in widths]))
    for row in rows:
        lines.append(fmt(row))
    return lines


def render_check(run_dir, state, rows, strict):
    mode = state["mode"]
    required = [r for r in rows if r["in_mode"] and not r["optional"]]
    gaps = [r for r in rows if r["gap"]]
    out = []
    out.append("run   : %s" % os.path.abspath(run_dir))
    out.append("mode  : %s" % mode)
    out.append("stages: %d required, %d optional, %d not in this mode"
               % (len(required),
                  len([r for r in rows if r["in_mode"] and r["optional"]]),
                  len([r for r in rows if not r["in_mode"]])))
    out.append("state : initialised %s, last change %s"
               % (state.get("created", "?"), state.get("updated", "?")))
    out.append("")
    body = [[str(r["order"]), r["id"], outputs_cell(r), r["status"], note_cell(r)]
            for r in rows]
    out.extend(table(body, ["#", "stage", "required output", "status", "note"]))
    out.append("")
    clean = len([r for r in required if not r["gap"]])
    if not gaps:
        out.append("OK. %d of %d required stages have their output." % (clean, len(required)))
    else:
        out.append("%d of %d required stages complete. %d gap%s."
                   % (clean, len(required), len(gaps), "" if len(gaps) == 1 else "s"))
        out.append("First gap: " + gaps[0]["gap"] + ".")
        if not strict:
            out.append("Not strict, so this exits 0. Add --strict to make it a gate.")
    return "\n".join(out) + "\n"


def render_markdown(run_dir, state):
    rows = inspect(run_dir, state)
    gaps = [r for r in rows if r["gap"]]
    out = []
    out.append("# Run state")
    out.append("")
    out.append("Written by `tools/run_state.py`. Read it when a run goes wrong,")
    out.append("and change the run rather than this file.")
    out.append("")
    out.append("- run: `%s`" % os.path.abspath(run_dir))
    out.append("- mode: **%s**" % state["mode"])
    out.append("- initialised: %s" % state.get("created", "?"))
    out.append("- last change: %s" % state.get("updated", "?"))
    if gaps:
        out.append("- open gaps: %d. First: %s." % (len(gaps), gaps[0]["gap"]))
    else:
        out.append("- open gaps: none")
    out.append("")
    out.append("| # | stage | required output | status | recorded | note |")
    out.append("| - | ----- | --------------- | ------ | -------- | ---- |")
    for r in rows:
        out.append("| %d | %s | %s | %s | %s | %s |"
                   % (r["order"], r["id"], outputs_cell(r), r["status"],
                      r["at"] or "-", note_cell(r) if r["note"] else "-"))
    out.append("")
    out.append("Modes: %s. A quick run needs only: %s."
               % (", ".join(MODES), ", ".join(QUICK_STAGES)))
    out.append("checkback is optional in every mode and never fails a check.")
    out.append("")
    return "\n".join(out)


# ------------------------------------------------------------------ subcommands

def cmd_init(args):
    run_dir = args.run
    if os.path.isfile(run_dir):
        return die("%s is a file, not a run directory. init takes runs/<slug>/, "
                   "the directory that holds the run." % run_dir)
    if not os.path.isdir(run_dir):
        try:
            os.makedirs(run_dir)
        except OSError as exc:
            return die("cannot create run directory %s (%s)" % (run_dir, exc))
    js, md = state_paths(run_dir)
    kept = {}
    old = None
    if os.path.exists(js):
        old, err = load_state(run_dir)
        if old is None:
            sys.stderr.write("run_state: existing _state.json unusable (%s). "
                             "Rebuilding it.\n" % err.splitlines()[0])
        elif args.reset:
            pass
        else:
            kept = old.get("stages", {})
    state = {
        "schema": SCHEMA,
        "mode": args.mode,
        "run": os.path.abspath(run_dir),
        "created": (old or {}).get("created") or now_iso(),
        "stages": kept,
        "stage_order": STAGE_IDS,
    }
    save_state(run_dir, state)
    verb = "re-initialised" if old is not None else "initialised"
    print("%s %s in mode %s" % (verb, os.path.abspath(run_dir), args.mode))
    if kept:
        print("kept %d recorded stage%s: %s"
              % (len(kept), "" if len(kept) == 1 else "s",
                 ", ".join(sorted(kept))))
    elif old is not None:
        print("no recorded stages carried over")
    req = stages_for_mode(args.mode)
    print("required stages: %s" % ", ".join(
        s for s in req if not is_optional(s)))
    opt = [s for s in req if is_optional(s)]
    print("optional: %s" % (", ".join(opt) if opt else
                            "none in this mode (checkback is skipped)"))
    print("wrote %s and %s" % (os.path.basename(js), os.path.basename(md)))
    return 0


def cmd_done(args):
    state, err = load_state(args.run)
    if state is None:
        return die(err)
    sid = args.stage
    if sid not in BY_ID:
        return die("unknown stage id %r\n            valid ids: %s"
                   % (sid, " ".join(STAGE_IDS)))
    note = (args.note or "").strip()
    if "\n" in note:
        note = note.splitlines()[0].strip()
    entry = {"at": now_iso()}
    if note:
        entry["note"] = note
    was = state["stages"].get(sid)
    state["stages"][sid] = entry
    save_state(args.run, state)

    print("recorded %s at %s" % (sid, entry["at"]))
    if was:
        print("note: this stage was already recorded at %s. Overwritten."
              % was.get("at", "?"))
    if note:
        print("note: %s" % note)
    stage = BY_ID[sid]
    if sid not in stages_for_mode(state["mode"]):
        print("warning: %s is not required in mode %s. Recorded anyway."
              % (sid, state["mode"]))
    missing = [o for o in stage["outputs"]
               if not os.path.exists(os.path.join(args.run, o))]
    if missing:
        print("warning: recorded, but %s is not in the run directory yet. "
              "check will still call this a gap." % ", ".join(missing))
    return 0


def cmd_check(args):
    state, err = load_state(args.run)
    if state is None:
        if args.json:
            print(json.dumps({"ok": False, "error": " ".join(err.split())},
                             indent=2))
        else:
            sys.stderr.write("run_state: " + err + "\n")
        return 1
    rows = inspect(args.run, state)
    gaps = [r for r in rows if r["gap"]]
    if args.json:
        payload = {
            "schema": SCHEMA,
            "run": os.path.abspath(args.run),
            "mode": state["mode"],
            "created": state.get("created", ""),
            "updated": state.get("updated", ""),
            "ok": not gaps,
            "gap_count": len(gaps),
            "first_gap": gaps[0]["gap"] if gaps else "",
            "stages": rows,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        sys.stdout.write(render_check(args.run, state, rows, args.strict))
    if gaps and args.strict:
        if not args.json:
            sys.stderr.write("run_state: " + gaps[0]["gap"] + "\n")
        return 1
    return 0


# ------------------------------------------------------------------------ main

def build_parser():
    epilog = ("stage ids in order: " + " ".join(STAGE_IDS)
              + "\nmodes: " + ", ".join(MODES)
              + "\nquick mode requires only: " + ", ".join(QUICK_STAGES)
              + "\ncheckback is optional in every mode and never fails a check.")
    p = argparse.ArgumentParser(
        prog="run_state.py",
        description="Record and verify which pipeline stages a run has actually done.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subs = p.add_subparsers(dest="cmd")

    i = subs.add_parser("init", help="create _state.json and _state.md for a run")
    i.add_argument("run", help="the run directory, runs/<slug>/")
    i.add_argument("--mode", required=True, choices=MODES)
    i.add_argument("--reset", action="store_true",
                   help="drop stages already recorded instead of keeping them")
    i.set_defaults(func=cmd_init)

    d = subs.add_parser("done", help="record that one stage finished")
    d.add_argument("run", help="the run directory, runs/<slug>/")
    d.add_argument("stage", help="one of: " + " ".join(STAGE_IDS))
    d.add_argument("--note", default="", help="one line a person will read later")
    d.set_defaults(func=cmd_done)

    c = subs.add_parser("check", help="print one row per stage and find the first gap")
    c.add_argument("run", help="the run directory, runs/<slug>/")
    c.add_argument("--strict", action="store_true",
                   help="exit 1 naming the first gap only")
    c.add_argument("--json", action="store_true", help="machine readable output")
    c.set_defaults(func=cmd_check)
    return p


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1
    args.run = args.run.rstrip(os.sep) or os.sep
    try:
        return args.func(args)
    except (IOError, OSError) as exc:
        return die("file system error: %s" % exc)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
