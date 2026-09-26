# %% [markdown]
# # Count It or Compute It: engine-computed
#
# The ids stay in the engine and never appear in the prompt. The model gets a
# `count_ids` tool that takes a filter and returns the exact count. The model
# only has to write the right filter and quote the number.
#
# Every filter the model sends is logged and checked against the question.
# A wrong filter returns an exact number too, so the category breakdown
# separates "right filter" from "quoted a wrong filter's count".

# %%
import json

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


def prompt_with_retry(llm, prompt, make_tools=None, attempts=6, **kw):
    """llm.prompt in a fresh chat per attempt, retrying the proxy's 429s.

    Returns (answer, tool_log, error). The output cap keeps the proxy's cost
    reservation small. Proxy errors (quota, overload) raise so the row is
    rerun; any other failure, such as a reply cut off at the cap that does not
    parse as a number, returns answer None with the error text.
    The tool log is rebuilt on every attempt, so a retried row only records
    the calls from the attempt that answered.
    """
    kw.setdefault("extra_api_params", {"max_completion_tokens": MAX_OUTPUT_TOKENS})
    for attempt in range(attempts):
        log: list = []
        if make_tools is not None:
            kw["tools"] = [make_tools(log)]
        try:
            with kbench.chats.new(f"attempt-{attempt}"):
                return llm.prompt(prompt, **kw), log, ""
        except Exception as e:
            if not type(e).__module__.startswith("openai"):
                return None, log, f"{type(e).__name__}: {str(e)[:300]}"
            if type(e).__name__ != "RateLimitError" or attempt == attempts - 1:
                raise
            time.sleep(min(60, 5 * 2 ** attempt) + random.random())


ROWS = build_rows()
# ---- end shared ----

# %%
def make_count_ids(ids: list[int], log: list[dict]):
    def count_ids(where: str) -> str:
        """Count rows in the ids table that match a filter. The table has one integer column, `id`. `where` is clauses like `id >= 10`, `id < 5`, `id = 7`, `id != 3` or `id between 5 and 9` (inclusive), joined with `and`. An empty string counts every row. Returns the exact count and the minimum and maximum matching id."""
        try:
            result = count_where(ids, where)
        except ValueError as e:
            log.append({"where": where, "error": str(e)})
            return json.dumps({"error": f"{e}. Use clauses like `id >= 10` joined with `and`."})
        log.append(result)
        return json.dumps(result)
    return count_ids


def classify(answer: int, expected: int, truth_where: str, ids: list[int], log: list[dict]) -> str:
    calls = [c for c in log if "error" not in c]
    if not calls:
        return "correct-no-call" if answer == expected else "no-call"
    quoted = [c for c in calls if c["count"] == answer]
    if not quoted:
        return "correct-not-quoted" if answer == expected else "not-quoted"
    if any(same_filter(c["where"], truth_where, ids) for c in quoted):
        return "correct"
    if any(not c["where"].strip() for c in quoted):
        return "quoted-no-filter"
    return "correct-wrong-filter" if answer == expected else "quoted-wrong-filter"


# %%
@kbench.task(name="count-engine")
def count_engine(llm) -> float:
    runs = count_engine_row.evaluate(
        llm=[llm], evaluation_data=pd.DataFrame(ROWS), n_jobs=4, on_failure="continue")
    return summarize(runs, len(ROWS), "engine")


# %%
@kbench.task(name="count-engine-row", store_task=False)
def count_engine_row(llm, case_id, size, phrasing, ids, question, truth_where, expected) -> dict:
    ids = [int(x) for x in ids]
    prompt = (
        f"A table of {len(ids)} rows with one integer column `id` is loaded in a query engine. "
        "Use the `count_ids` tool to answer.\n\n"
        f"{question} Answer with just the number."
    )
    answer, log, error = prompt_with_retry(llm, prompt, make_tools=lambda log: make_count_ids(ids, log), schema=int)
    answer = None if answer is None else int(answer)
    correct = answer == int(expected)
    kbench.assertions.assert_equal(int(expected), answer, expectation=f"{case_id}: {truth_where}")
    return dict(case_id=case_id, size=int(size), phrasing=phrasing, answer=answer,
                expected=int(expected), correct=correct,
                category="no-answer" if answer is None else classify(answer, int(expected), truth_where, ids, log),
                filters=[c.get("where") for c in log], truth_where=truth_where, error=error)


count_engine.run(kbench.llm)

# %%
# Keep only the scoring task's task and run files: the leaderboard shows
# one task per notebook. Jupytext turns this comment into the magic.
# %choose count_engine
