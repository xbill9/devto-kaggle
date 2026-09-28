# Count It or Compute It

A [Kaggle Benchmarks](https://www.kaggle.com/benchmarks) entry for the [DEV Kaggle Benchmarking Challenge](https://dev.to/challenges/kaggle-2026-09-23). It asks models how many ids in a list meet a threshold, five ways:

| Task | What the model gets |
|---|---|
| `count-in-context` | Every id in the prompt; it counts them |
| `count-python-tool` | The same prompt, plus a `run_python` tool with `ids` already defined |
| `count-python-told` | The same, with one sentence telling it to use the tool |
| `count-rows-tool` | No ids; a `list_ids(where)` tool that returns the matching ids, which the model counts |
| `count-engine` | No ids; a `count_ids(where)` tool that returns the exact count. The filter it sends is graded as well as the number it quotes |

Each task asks 68 questions: lists of 11, 110 and 330 ids, seven phrasings of the threshold, three seeds each, plus the original eleven-id case five times. Every expected answer is computed by code.

## Layout

- `tasks/count_*.py`: the five Kaggle tasks. The block between `# ---- shared:` and `# ---- end shared ----` must be identical in all of them.
- `tasks/check.py`: local checks, no model calls and no `kaggle_benchmarks` needed.
- `tasks/summarize.py`, `tasks/costs.py`: scores and cost per row from downloaded run files.
- `tasks/report.py`: the article's tables, from each model's latest run (the one the Kaggle leaderboard shows).
- `tasks/pending.py`: the `kaggle b t run` commands still needed for the model lineup, judged by each model's latest run.
- `article/`: the dev.to write-up and the text evidence behind every figure in it.

## Run

```shell
python3 tasks/check.py
kaggle b t push count-engine -f tasks/count_engine.py --wait
kaggle b t run count-engine -m gemini-2.5-flash --wait
kaggle b t download count-engine -o results
python3 tasks/summarize.py results
```
