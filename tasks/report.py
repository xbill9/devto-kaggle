"""Markdown result tables for the article, computed from the downloaded run files.

Uses each task's version given below. A model's run counts when at most
MAX_ERRORED rows errored (proxy overload or quota); errored rows count as wrong
and are shown in the table.

    python3 tasks/report.py [results] > article/evidence/report.md
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results")
VERSIONS = {"count-engine": 7, "count-rows-tool": 2, "count-python-tool": 6}
ROWS_PER_TASK = 68
MAX_ERRORED = 6
NAMES = {
    "gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite", "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-3.7-flash": "Gemini 3.7 Flash", "gemini-3.8-flash": "Gemini 3.8 Flash",
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5", "claude-sonnet-5-default": "Claude Sonnet 5",
    "claude-opus-5-default": "Claude Opus 5", "gpt-5.4-nano-2026-03-17": "GPT-5.4 nano",
    "gpt-5.4-mini-2026-03-17": "GPT-5.4 mini", "gpt-6-astra": "GPT-6 Astra",
    "gemma-4-26b-a4b-it": "Gemma 4 26B A4B", "gpt-oss-20b": "gpt-oss-20b",
    "qwen3-next-80b-a3b-instruct": "Qwen 3 Next 80B Instruct",
    "qwen3-next-80b-a3b-thinking": "Qwen 3 Next 80B Thinking",
}


def load(task: str) -> dict:
    """model -> (rows, errored) for the best run of the task's version."""
    out = {}
    for model_dir in (ROOT / task / str(VERSIONS[task])).glob("*"):
        best = None
        for run_dir in model_dir.glob("*"):
            rows, errored = [], 0
            # %choose versions write the completed rows to rows-<label>.json.
            for f in run_dir.glob("rows-*.json"):
                rows = json.loads(f.read_text())
                errored = ROWS_PER_TASK - len(rows)
            for f in run_dir.glob("*-row-run_param_id_*.run.json"):
                d = json.loads(f.read_text())
                if d.get("state") == "BENCHMARK_TASK_RUN_STATE_COMPLETED" and d.get("results"):
                    rows.append(d["results"][0]["dictResult"])
                else:
                    errored += 1
            if best is None or len(rows) > len(best[0]):
                best = (rows, errored)
        if best and best[1] <= MAX_ERRORED and len(best[0]) + best[1] == ROWS_PER_TASK:
            out[model_dir.name] = best
    return out


def score(rows_err) -> str:
    rows, errored = rows_err
    s = f"{sum(bool(r['correct']) for r in rows)}/{ROWS_PER_TASK}"
    return s + (f" ({errored} errored)" if errored else "")


def at(rows_err, size: int, key: str = "correct") -> str:
    rows = [r for r in rows_err[0] if int(r["size"]) == size]
    if key == "tool":
        return f"{sum(r.get('tool_calls', 0) > 0 for r in rows)}/{len(rows)}"
    return f"{sum(bool(r['correct']) for r in rows)}/{len(rows)}"


data = {t: load(t) for t in VERSIONS}
models = [m for m in NAMES if all(m in data[t] for t in VERSIONS)]
dropped = [m for m in NAMES if m not in models]

print("## Engine, rows tool and Python tool, every model with all three runs\n")
print("| Model | Engine | Rows tool | Rows tool, 330 ids | Python tool | Python tool used, 110 / 330 ids |")
print("|---|---|---|---|---|---|")
order = sorted(models, key=lambda m: -sum(bool(r["correct"]) for r in data["count-rows-tool"][m][0]))
for m in order:
    e, r, p = data["count-engine"][m], data["count-rows-tool"][m], data["count-python-tool"][m]
    print(f"| {NAMES[m]} | {score(e)} | {score(r)} | {at(r, 330)} | {score(p)} | {at(p, 110, 'tool')} / {at(p, 330, 'tool')} |")

print("\n## Rows tool by list size\n")
print("| Model | 11 ids | 110 ids | 330 ids |")
print("|---|---|---|---|")
for m in order:
    r = data["count-rows-tool"][m]
    print(f"| {NAMES[m]} | {at(r, 11)} | {at(r, 110)} | {at(r, 330)} |")

print("\n## Categories\n")
for t in VERSIONS:
    total = collections.Counter()
    for m in models:
        total.update(r["category"] for r in data[t][m][0])
    print(f"- {t}: " + ", ".join(f"{k} {v}" for k, v in total.most_common()))

print("\n## Filters sent by rows-tool and engine answers that were wrong\n")
for t in ("count-engine", "count-rows-tool"):
    wrong_filter = sum(r["category"] in ("quoted-wrong-filter", "wrong-filter", "correct-wrong-filter")
                       for m in models for r in data[t][m][0])
    print(f"- {t}: {wrong_filter} answers built on a wrong filter")

print("\n## Left out (no complete run of all three tasks)\n")
for m in dropped:
    have = [t for t in VERSIONS if m in data[t]]
    print(f"- {NAMES[m]}: complete in {', '.join(have) if have else 'none'}")
