# Where this stands and what is left (as of 2026-09-28)

Everything needed to finish is in this repo. Nothing depends on the machine it was started on.

## Decision

**Runs are complete and the article matches them. Check the leaderboard shows scores, make the benchmark Public, fill the two `PENDING` links, then publish.** Deadline: 2026-10-11, 11:59 PM PDT.

## What exists

| Thing | Where | State |
|---|---|---|
| Code | https://github.com/xbill9/devto-kaggle (`main`) | Current. Scoring task is now first in every `tasks/count_*.py` (not yet pushed to Kaggle) |
| Kaggle tasks | `kaggle.com/benchmarks/tasks/xbillwork/count-engine` (v7), `count-rows-tool` (v2), `count-python-tool` (v6) | **Public**, with backing notebooks. `count-python-told` and `count-in-context` exist but stay private and out of the article |
| Kaggle benchmark | https://www.kaggle.com/benchmarks/xbillwork/count-it-or-compute-it | **Private**. 3 tasks, 10 models added. Leaderboard cells blank (see below) |
| dev.to article | draft id **4744048**, source `article/devto-count-it-or-compute-it.md` | **Unpublished draft**. Two `PENDING` lines need the benchmark link |
| Cover | `article/devto-cover.d50932c1.jpg` | Done, pushed, referenced by `cover_image:` |
| Evidence | `article/evidence/` | Text files behind every figure; `report.md` is the table source |

## 2026-09-28 (current)

- **All runs complete** for the 10-model lineup at `count-engine` v12, `count-rows-tool` v5, `count-python-tool` v9. Within the 6-row allowance: Claude Opus 5 has 2 errored rows-tool rows, gpt-oss-20b 2 errored Python-tool rows. `pending.py` still lists Flash-Lite, the Qwen models and the private tasks; those are outside the lineup.
- `report.py` points at those versions; `report.md`, `scores-all-versions.txt` and `python-tool-wrong-answers.txt` are rebuilt, and the article's tables and prose are updated from them. `check-prose`, `check-facts` and `check-article` pass. The dev.to draft is **not yet updated** (`--update 4744048`).
- Steps 1–5 are done. Start at step 6.

## 2026-09-27

- **Leaderboard fixed.** Kaggle shows one task per notebook, picked with `%choose`; every task file now ends with `# %choose <task>`. `%choose` deletes the per-question run files, so `summarize()` writes the completed rows to `rows-<label>.json`, which `kaggle b t download` fetches and `report.py` / `summarize.py` / `pending.py` read.
- **Versions on the benchmark:** `count-engine` v12, `count-rows-tool` v5, `count-python-tool` v9 (old versions removed). Benchmark still **Private**.
- **Runs done:** `count-engine` v12, all 10 models. `count-rows-tool` v5, all 10, but `claude-sonnet-5-default` has 8 errored rows (needs a rerun). `count-python-tool` v9: `gemini-3.7-flash` and `gpt-oss-20b` done; the other 8 hit the daily quota on 2026-09-27 08:41 EDT and need reruns (`python3 tasks/pending.py results` lists them).
- **Quota** behaves as a rolling 24 h window, not a midnight reset.
- If the CLI says "Authentication required" while `kaggle auth login` says you are logged in, run `kaggle auth login --force`.

## Remaining steps (1–5 are done; start at 6)

1. **Setup on a new PC (skip if same machine).** Ask before installing anything.
   - `pip install kaggle` into the normal Python (no venv), then `kaggle auth login` (account **xbillwork**).
   - dev.to key in `~/.devto.key` for the publish script; publishing kit at `~/publishing-kit` (`scripts/publish-devto.py`, `check-*.py`).
   - `results/` is not in git (85 MB). Re-download with `kaggle b t download <slug> -o results` when needed.
2. **Confirm quota is back.** The model picker on any Kaggle benchmark page shows `Daily AI Quota $x used / $10.00` and `Monthly AI Quota $x / $100.00` (monthly was $20.07 on 2026-09-25). `kaggle b t run probe-max-tokens -m gemini-3.5-flash-lite --wait` answering 7 also works. The daily quota released within the day on 2026-09-25, so it is not strictly a midnight reset.
3. **Re-push the three tasks** (each push also runs once on `gemini-3.7-flash`):
   ```shell
   python3 tasks/check.py
   kaggle b t push count-engine -f tasks/count_engine.py --wait
   kaggle b t push count-rows-tool -f tasks/count_rows_tool.py --wait
   kaggle b t push count-python-tool -f tasks/count_python_tool.py --wait
   kaggle b t status count-engine   # must say Completed, not Errored; if Errored on a 429, push again
   ```
   If a push's own run errors, the task is `Errored` and `kaggle b t run` submits nothing. Push again.
4. **Run the 10 models on each task** (one task at a time; about $5–7 in total by 2026-09-25 costs, Claude Opus 5 is the priciest):
   ```shell
   M="-m gemini-2.5-flash -m gemini-3.8-flash -m claude-haiku-4-5-20251001 -m claude-sonnet-5-default -m claude-opus-5-default -m gpt-5.4-nano-2026-03-17 -m gpt-5.4-mini-2026-03-17 -m gemma-4-26b-a4b-it -m gpt-oss-20b"
   kaggle b t run count-engine $M --wait
   kaggle b t run count-rows-tool $M --wait
   kaggle b t run count-python-tool $M --wait
   ```
   (`gemini-3.7-flash` is covered by the push run.) Rows that hit a 429 are retried inside the task; a model with more than 6 errored rows needs its run repeated.
5. **Download and rebuild the tables.** Update `VERSIONS` in `tasks/report.py` to count-engine 12, count-rows-tool 5, count-python-tool 9 first.
   ```shell
   for t in count-engine count-rows-tool count-python-tool; do kaggle b t download $t -o results; done
   python3 tasks/report.py results > article/evidence/report.md
   python3 tasks/summarize.py results > article/evidence/scores-all-versions.txt
   ```
   The article's tables and figures come from the 2026-09-25 runs. If the new runs differ, update the article from `report.md` (every table there maps to one in the article) and re-run the fact check.
6. **Check the benchmark page.** The tasks in the benchmark must point at the new versions (open each task's `⋮` on the benchmark page, or remove and re-add them via *Add Tasks*), and the leaderboard cells must show scores. Then Settings → visibility **Public**.
7. **Finish the article.** Replace both `PENDING` lines with the benchmark URL, then:
   ```shell
   K=~/publishing-kit/skills/publishing/scripts
   python3 $K/check-prose.py article/devto-count-it-or-compute-it.md
   python3 $K/check-facts.py article/devto-count-it-or-compute-it.md --evidence article/evidence
   python3 $K/check-article.py article/devto-count-it-or-compute-it.md --repo-root .
   python3 $K/publish-devto.py --update 4744048 article/devto-count-it-or-compute-it.md
   python3 $K/publish-devto.py --publish 4744048     # only on the author's go
   python3 $K/publish-devto.py --list               # confirm it is live
   ```
   Required by the challenge: the submission template headings (present), tag `#kagglechallenge` (present), and the Kaggle benchmark link.

## Lineup notes (already stated in the article)

- 10 models in the tables: Gemini 2.5 / 3.7 / 3.8 Flash, Gemma 4 26B A4B, Claude Haiku 4.5 / Sonnet 5 / Opus 5, GPT-5.4 nano / mini, gpt-oss-20b.
- Left out: GPT-6 Astra (proxy refuses function tools with reasoning on), Gemini 3.5 Flash-Lite and both Qwen 3 Next 80B models (429 / 503 on most calls).
