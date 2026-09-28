# %% [markdown]
# # Count It or Compute It: Python tool, told to use it
#
# The Python-tool task with one added sentence telling the model to use the
# tool. Everything else is identical, so the difference in tool use between
# the two tasks is the effect of that sentence.

# %%
import subprocess
import sys

import kaggle_benchmarks as kbench
import pandas as pd

# %%
# ---- shared: identical in every task file (check.py enforces it) ----
import random
import re
import time

SIZES = [11, 110, 330]
SEEDS_PER_CELL = 3
ORIGINAL_REPEATS = 5
ORIGINAL_IDS = [0, 2, 3, 20, 21, 22, 23, 10, 11, 12, 13]

# (key, English phrase, canonical filter). The filter is the ground truth.
PHRASINGS = [
    ("or-more", "{a} or more", "id >= {a}"),
    ("at-least", "at least {a}", "id >= {a}"),
    ("no-less-than", "no less than {a}", "id >= {a}"),
    ("more-than", "more than {a}", "id > {a}"),
    ("under", "under {a}", "id < {a}"),
    ("at-most", "at most {a}", "id <= {a}"),
    ("between-inclusive", "between {a} and {b} inclusive", "id >= {a} and id <= {b}"),
]

_CLAUSE = re.compile(r"^id\s*(>=|<=|!=|==|=|>|<)\s*(-?\d+)$", re.IGNORECASE)
_BETWEEN = re.compile(r"id\s+between\s+(-?\d+)\s+and\s+(-?\d+)", re.IGNORECASE)
_OPS = {
    ">=": lambda x, v: x >= v,
    "<=": lambda x, v: x <= v,
    ">": lambda x, v: x > v,
    "<": lambda x, v: x < v,
    "=": lambda x, v: x == v,
    "==": lambda x, v: x == v,
    "!=": lambda x, v: x != v,
}


def parse_where(where: str) -> list[tuple[str, int]]:
    """Parse `id >= 10 and id < 20` style filters. Empty means no filter."""
    text = _BETWEEN.sub(r"id >= \1 and id <= \2", (where or "").strip())
    if not text:
        return []
    clauses = []
    for part in re.split(r"\s+and\s+", text, flags=re.IGNORECASE):
        m = _CLAUSE.match(part.strip())
        if not m:
            raise ValueError(f"cannot parse clause {part!r}")
        clauses.append((m.group(1), int(m.group(2))))
    return clauses


def matches(clauses: list[tuple[str, int]], x: int) -> bool:
    return all(_OPS[op](x, v) for op, v in clauses)


def count_where(ids: list[int], where: str) -> dict:
    clauses = parse_where(where)
    hits = [x for x in ids if matches(clauses, x)]
    return {
        "where": where,
        "count": len(hits),
        "min": min(hits) if hits else None,
        "max": max(hits) if hits else None,
    }


def same_filter(where_a: str, where_b: str, ids: list[int]) -> bool:
    """True if both filters select the same integers around the data's range."""
    a, b = parse_where(where_a), parse_where(where_b)
    domain = range(min(ids) - 2, max(ids) + 3)
    return all(matches(a, x) == matches(b, x) for x in domain)


def build_rows() -> list[dict]:
    rows = []
    for r in range(ORIGINAL_REPEATS):
        rows.append(dict(
            case_id=f"original-r{r}", size=len(ORIGINAL_IDS), phrasing="or-more",
            ids=list(ORIGINAL_IDS), question="How many of the ids are 10 or more?",
            truth_where="id >= 10", expected=count_where(ORIGINAL_IDS, "id >= 10")["count"],
        ))
    for size in SIZES:
        for key, phrase, truth in PHRASINGS:
            for seed in range(SEEDS_PER_CELL):
                rng = random.Random(f"{size}-{key}-{seed}")
                ids = rng.sample(range(4 * size), size)
                ordered = sorted(ids)
                # Thresholds are ids that occur in the data, so > and >= differ.
                ia = rng.randint(size * 3 // 10, size * 6 // 10)
                ib = rng.randint(ia + 1, max(ia + 1, size * 9 // 10))
                a, b = ordered[ia], ordered[ib]
                where = truth.format(a=a, b=b)
                rows.append(dict(
                    case_id=f"{size}-{key}-s{seed}", size=size, phrasing=key, ids=ids,
                    question=f"How many of the ids are {phrase.format(a=a, b=b)}?",
                    truth_where=where, expected=count_where(ids, where)["count"],
                ))
    return rows


def summarize(runs, total: int, label: str) -> float:
    done = runs.completed_runs.as_dataframe()
    results = pd.DataFrame(list(done["result"])) if len(done) else pd.DataFrame(
        columns=["size", "phrasing", "category", "correct"])
    errored = total - len(results)
    # %choose keeps only the scoring task's run file, so the per-question
    # results go to their own file, which `kaggle b t download` also fetches.
    results.to_json(f"/kaggle/working/rows-{label}.json", orient="records")
    correct = int(results["correct"].sum()) if len(results) else 0
    print(f"[{label}] correct {correct} of {total} (errored {errored})")
    if len(results):
        print(results.groupby("size")["correct"].agg(["sum", "count"]).to_string())
        print(results.groupby("phrasing")["correct"].agg(["sum", "count"]).to_string())
        print(results["category"].value_counts().to_string())
    return correct / total


MAX_OUTPUT_TOKENS = 8192


def usage_of(chat) -> dict:
    if chat is None:
        return dict(in_tokens=None, out_tokens=None, cost_usd=None)
    u = chat.usage
    cost = u.total_cost_nanodollars
    return dict(in_tokens=u.input_tokens, out_tokens=u.output_tokens,
                cost_usd=None if cost is None else cost / 1e9)


def prompt_with_retry(llm, prompt, make_tools=None, attempts=6, **kw):
    """llm.prompt in a fresh chat per attempt, retrying the proxy's 429s.

    Returns (answer, tool_log, error, usage). usage holds the answering
    attempt's tokens and cost as the proxy reports them, so the per-question
    cost of each tool shape is kept in the
    row results. The output cap keeps the proxy's cost
    reservation small. Proxy errors (quota, overload) raise so the row is
    rerun; any other failure, such as a reply cut off at the cap that does not
    parse as a number, returns answer None with the error text.
    The tool log is rebuilt on every attempt, so a retried row only records
    the calls from the attempt that answered.
    """
    kw.setdefault("extra_api_params", {"max_completion_tokens": MAX_OUTPUT_TOKENS})
    for attempt in range(attempts):
        log: list = []
        chat = None
        if make_tools is not None:
            kw["tools"] = [make_tools(log)]
        try:
            with kbench.chats.new(f"attempt-{attempt}") as chat:
                answer = llm.prompt(prompt, **kw)
                return answer, log, "", usage_of(chat)
        except Exception as e:
            if not type(e).__module__.startswith("openai"):
                return None, log, f"{type(e).__name__}: {str(e)[:300]}", usage_of(chat)
            if type(e).__name__ != "RateLimitError" or attempt == attempts - 1:
                raise
            time.sleep(min(60, 5 * 2 ** attempt) + random.random())


ROWS = build_rows()
# ---- end shared ----

# %%
def make_run_python(ids: list[int], log: list[str]):
    def run_python(code: str) -> str:
        """Run Python 3 code and return its stdout and stderr. The variable `ids`, a list of ints, is already defined. Use print() to see results."""
        log.append(code)
        try:
            p = subprocess.run([sys.executable, "-c", f"ids = {ids!r}\n{code}"],
                               capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return "error: timed out after 30 s"
        return (p.stdout + p.stderr)[-4000:] or "(no output)"
    return run_python


# %%
@kbench.task(name="count-python-told")
def count_python_told(llm) -> float:
    runs = count_python_told_row.evaluate(
        llm=[llm], evaluation_data=pd.DataFrame(ROWS), n_jobs=4, on_failure="continue")
    return summarize(runs, len(ROWS), "python-told")


# %%
@kbench.task(name="count-python-told-row", store_task=False)
def count_python_told_row(llm, case_id, size, phrasing, ids, question, truth_where, expected) -> dict:
    ids = [int(x) for x in ids]
    prompt = (
        f"Here is a list of {len(ids)} ids:\n{', '.join(map(str, ids))}\n\n"
        "You have a `run_python` tool. In it, the variable `ids` already holds this exact list.\n"
        "Use the `run_python` tool to compute the answer; do not count by reading.\n\n"
        f"{question} Answer with just the number."
    )
    answer, log, error, usage = prompt_with_retry(llm, prompt, make_tools=lambda log: make_run_python(ids, log), schema=int)
    answer = None if answer is None else int(answer)
    correct = answer == int(expected)
    kbench.assertions.assert_equal(int(expected), answer, expectation=f"{case_id}: {truth_where}")
    if answer is None:
        category = "no-answer"
    elif not log:
        category = "correct-no-tool" if correct else "miscount-no-tool"
    else:
        category = "correct-tool" if correct else "wrong-tool"
    return dict(case_id=case_id, size=int(size), phrasing=phrasing, answer=answer,
                expected=int(expected), correct=correct, category=category,
                tool_calls=len(log), code=log[-1] if log else "", error=error, **usage)


count_python_told.run(kbench.llm)

# %%
# Keep only the scoring task's task and run files: the leaderboard shows
# one task per notebook. Jupytext turns this comment into the magic.
# %choose count_python_told
