"""Score downloaded runs. Every number comes from the run files.

    kaggle b t download <slug> -o results -f
    python3 tasks/summarize.py [results]
"""
import collections
import json
import pathlib
import sys

ROWS_PER_TASK = 68
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results")
WRONG_FILTER = {"quoted-wrong-filter", "quoted-no-filter", "correct-wrong-filter"}


def row_results(run_dir: pathlib.Path) -> tuple[list[dict], int]:
    """Per-row dicts returned by the *-row task, and the number of errored rows.

    Task versions with `%choose` keep one run file and write the completed rows
    to rows-<label>.json; older versions keep one run file per row.
    """
    for f in run_dir.glob("rows-*.json"):
        rows = json.loads(f.read_text())
        return rows, ROWS_PER_TASK - len(rows)
    rows, errored = [], 0
    for f in sorted(run_dir.glob("*-row-run_param_id_*.run.json")):
        d = json.loads(f.read_text())
        if d.get("state") != "BENCHMARK_TASK_RUN_STATE_COMPLETED" or not d.get("results"):
            errored += 1
            continue
        rows.append(d["results"][0]["dictResult"])
    return rows, errored


def table(rows: list[dict], key: str) -> str:
    groups: dict = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = int(r[key]) if isinstance(r[key], float) else r[key]
        g = groups[k]
        g[0] += bool(r["correct"])
        g[1] += 1
    order = sorted(groups, key=lambda k: (isinstance(k, str), k))
    return "  ".join(f"{k}: {groups[k][0]}/{groups[k][1]}" for k in order)


headline = []
for run_dir in sorted(p for p in ROOT.glob("*/*/*/*") if p.is_dir()):
    task, version, model = run_dir.parts[-4:-1]
    rows, errored = row_results(run_dir)
    missing = ROWS_PER_TASK - len(rows) - errored
    correct = sum(bool(r["correct"]) for r in rows)
    headline.append((task, version, model, correct, errored + missing))
    print(f"== {task} v{version} {model} (run {run_dir.name})")
    print(f"correct {correct} of {ROWS_PER_TASK}; errored {errored}; missing {missing}")
    print(f"by size      {table(rows, 'size')}")
    print(f"by phrasing  {table(rows, 'phrasing')}")
    if task in ("count-python-tool", "count-python-told"):
        used: dict = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            k = int(r["size"])
            used[k][0] += r.get("tool_calls", 0) > 0
            used[k][1] += 1
        print("tool used    " + "  ".join(f"{k}: {used[k][0]}/{used[k][1]}" for k in sorted(used)))
        skipped = [r for r in rows if r.get("tool_calls", 0) == 0 and r["answer"] is not None]
        wrong = sum(not r["correct"] for r in skipped)
        print(f"tool skipped {len(skipped)} rows: {wrong} of {len(skipped)} wrong")
    cats = collections.Counter(r["category"] for r in rows)
    print("categories   " + "  ".join(f"{k}: {v}" for k, v in cats.most_common()))
    for r in rows:
        if r["category"] in WRONG_FILTER:
            print(f"  {r['case_id']}: sent {r.get('filters')} true {r.get('truth_where')!r} "
                  f"answered {int(r['answer'])} expected {int(r['expected'])}")
    wrong = [r for r in rows if not r["correct"]]
    for r in wrong:
        if r["answer"] is None:
            print(f"  no answer {r['case_id']}: {r.get('error', '')[:160]}")
            continue
        print(f"  wrong {r['case_id']}: answered {int(r['answer'])} expected {int(r['expected'])} "
              f"(off by {int(r['answer']) - int(r['expected']):+d})")
    print()

print("task                 ver  model                          correct  errored")
for task, version, model, correct, bad in sorted(headline):
    print(f"{task:<20} v{version:<3} {model:<30} {correct:>3}/{ROWS_PER_TASK}  {bad:>6}")
