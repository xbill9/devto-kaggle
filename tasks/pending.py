"""Print the `kaggle b t run` commands still needed for the full lineup.

A (task, model) pair is done when the downloaded run for the task's current
version on Kaggle (from `kaggle b t status`) has all 68 rows completed.
Tasks are listed cheapest first, so a day's quota goes to the engine task
before the in-context one.

    for t in count-engine count-rows-tool count-python-tool count-python-told count-in-context; do kaggle b t download $t -o results; done
    python3 tasks/pending.py [results]
"""
import json
import pathlib
import re
import subprocess
import sys

ROWS_PER_TASK = 68
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results")
TASKS = ["count-engine", "count-rows-tool", "count-python-tool", "count-python-told", "count-in-context"]  # cheapest first
LINEUP = [
    "gemini-3.5-flash-lite", "gemini-2.5-flash", "gemini-3.7-flash", "gemini-3.8-flash",
    "claude-haiku-4-5-20251001", "claude-sonnet-5-default", "claude-opus-5-default",
    "gpt-5.4-nano-2026-03-17", "gpt-5.4-mini-2026-03-17", "gpt-6-astra",
    "gemma-4-26b-a4b-it", "gpt-oss-20b",
    "qwen3-next-80b-a3b-instruct", "qwen3-next-80b-a3b-thinking",
]

# Kaggle's proxy rejects function tools for these models: "Function tools with
# reasoning_effort are not supported for gpt-6-astra in /v1/chat/completions".
# They run the in-context task only.
NO_TOOLS = {"gpt-6-astra"}


def completed_rows(run_dir: pathlib.Path) -> int:
    # %choose versions write the completed rows to rows-<label>.json.
    for f in run_dir.glob("rows-*.json"):
        return len(json.loads(f.read_text()))
    return sum(
        json.loads(f.read_text()).get("state") == "BENCHMARK_TASK_RUN_STATE_COMPLETED"
        for f in run_dir.glob("*-row-run_param_id_*.run.json")
    )


todo = 0
for task in TASKS:
    status = subprocess.run(["kaggle", "b", "t", "status", task], capture_output=True, text=True).stdout
    m = re.search(r"^Version:\s+(\d+)", status, re.MULTILINE)
    if not m:
        sys.exit(f"cannot read the current version of {task} from `kaggle b t status`")
    version = int(m.group(1))
    latest = ROOT / task / str(version)
    need = []
    for model in LINEUP:
        if model in NO_TOOLS and task != "count-in-context":
            continue
        best = max((completed_rows(d) for d in (latest / model).glob("*")), default=0)
        if best < ROWS_PER_TASK:
            need.append((model, best))
    summary = ", ".join(f"{m} {n}/{ROWS_PER_TASK}" for m, n in need) or "complete"
    print(f"# {task} v{version}: {summary}")
    if need:
        todo += len(need)
        print(f"kaggle b t run {task} " + " ".join(f"-m {m}" for m, _ in need) + " --wait")
print(f"# {todo} run(s) pending")
