# Where this stands and what is left (as of 2026-09-28)

Everything needed to finish is in this repo. Nothing depends on the machine it was started on.

## Decision

**Published on dev.to, Medium and LinkedIn; the Kaggle benchmark is Public. Only the optional leaderboard alignment and the Advocu submit are left.** Deadline: 2026-10-11, 11:59 PM PDT.

## What exists

| Thing | Where | State |
|---|---|---|
| Code | https://github.com/xbill9/devto-kaggle (`main`) | Current, and matches the pushed task versions |
| Kaggle tasks | `kaggle.com/benchmarks/tasks/xbillwork/count-engine` (v12), `count-rows-tool` (v5), `count-python-tool` (v9) | **Public**, with backing notebooks. `count-python-told` and `count-in-context` exist but stay private and out of the article |
| Kaggle benchmark | https://www.kaggle.com/benchmarks/xbillwork/count-it-or-compute-it | **Public** since 2026-09-28 (permanent, Apache 2.0). 3 tasks, 10 models. Overall score: *Average of task scores* |
| dev.to article | draft id **4744048**, source `article/devto-count-it-or-compute-it.md` | **Unpublished draft**, updated 2026-09-28 with the benchmark link |
| Cover | `article/devto-cover.d50932c1.jpg` | Done, pushed, referenced by `cover_image:` |
| Evidence | `article/evidence/` | Text files behind every figure; `report.md` is the table source |

## 2026-09-28, night (current): published everywhere

| Where | URL / state |
|---|---|
| dev.to (challenge entry) | https://dev.to/gde/count-it-or-compute-it-when-a-tool-returns-rows-the-models-that-count-them-right-spend-the-tokens-2hae, **published** |
| Medium | https://xbill999.medium.com/count-it-or-compute-it-when-a-tool-returns-rows-the-models-that-count-them-right-spend-the-tokens-e772a07b4621, **published** |
| Kaggle benchmark | https://www.kaggle.com/benchmarks/xbillwork/count-it-or-compute-it, **Public**, description published |
| LinkedIn | https://www.linkedin.com/feed/update/urn:li:activity:7510422856250474497/, **posted** |
| Advocu | saved as a **draft** (My activities -> Drafts); the author submits it |

All links are in `article/devto-count-it-or-compute-it.links.txt`.

**Optional, open:** once the daily quota frees, rerun the three Claude models on `count-rows-tool` v6, then point the benchmark at `count-engine` v13 and `count-rows-tool` v6 so its cells match the article (it shows v12 / v5 / v9 today, all complete).

## 2026-09-28, evening

- **Article rewritten** around tool shape and tokens, no `PENDING` left, `preflight.py --live` passes, dev.to draft 4744048 updated. Not published.
- **Runs:** `count-engine` v13 complete for all 10. `count-rows-tool` v6 complete for the 7 non-Claude models; the Claude v6 runs stopped on the daily quota (24, 6, 1 of 68), so the article takes the Claude rows-tool figures from their 2026-09-25 v2 run (same 68 questions, same tool, checked identical), in `article/evidence/claude-rows-tool-2026-09-25.txt`.
- **Benchmark still points at** `count-engine` v12, `count-rows-tool` v5, `count-python-tool` v9, all complete. Optional once the quota frees: rerun the Claude models on `count-rows-tool` v6, then point the benchmark at v13 / v6 so its cells match the article.
- **Benchmark page Description** is still the unpublished placeholder.

## 2026-09-28, afternoon: reframing around tokens

- **New framing agreed with the author:** agents' tools return rows; the model must count them; it breaks past quick-test sizes with no error; whether it counts right tracks whether it spends tokens counting (reasoning), not size or price; returning the count fixes it for every model at flat cost. The article is being rewritten around this, shorter.
- **Tasks now keep tokens and cost per question** (`in_tokens`, `out_tokens`, `cost_usd` in `rows-*.json`, from the chat's usage). Pushed as `count-engine` v13 and `count-rows-tool` v6; `count-python-tool` stays v9. `report.py` points at 13 / 6 / 9 and prints a tokens-and-cost table.
- **Runs at v13 / v6:** done for Gemini 2.5 / 3.7 / 3.8 Flash, Gemma 4 26B, gpt-oss-20b, GPT-5.4 nano / mini. **Still needed: the three Claude models on both tasks**, deferred because the daily quota was at $6.44 of $10 on 2026-09-28 16:00 EDT:
  ```shell
  kaggle b t run count-engine -m claude-haiku-4-5-20251001 -m claude-sonnet-5-default -m claude-opus-5-default --wait
  kaggle b t run count-rows-tool -m claude-haiku-4-5-20251001 -m claude-sonnet-5-default -m claude-opus-5-default --wait
  ```
- **Then:** on the (Public) benchmark page, point `count-engine` at v13 and `count-rows-tool` at v6 (task `⋮`, or remove and re-add), check the leaderboard, rebuild `report.md`, finish the rewrite, rerun preflight, update the dev.to draft.
- **Benchmark page Description is still the unpublished placeholder.** Write and publish it (the problem, the three tools, the rule).

## 2026-09-28, morning

- **All runs complete, and the leaderboard shows scores.** The leaderboard shows each model's *latest* run, not its best: a batch started 2026-09-27 14:00 UTC after the quota ran out had left empty latest runs for 18 pairs, so those were rerun. `report.py` and `pending.py` now judge each pair by its latest run too, so the article's tables match `kaggle b leaderboard xbillwork/count-it-or-compute-it -s` (checked for every model).
- **Never start a run that might hit the quota** on a pair whose latest run is good: a failed run becomes the one the leaderboard shows.
- Within the 6-row allowance: gpt-oss-20b has 1 errored Python-tool row. `pending.py` still lists Flash-Lite, the Qwen models and the private tasks; those are outside the lineup.
- `report.md`, `scores-all-versions.txt`, `python-tool-wrong-answers.txt` and the article are rebuilt from the latest runs. Both `PENDING` lines now hold the benchmark URL; `preflight.py` passes. The dev.to draft is updated with this version (2026-09-28).
- The benchmark URL returns 200 signed out (from 2026-09-28 11:25 EDT, about 15 minutes after going Public). `preflight.py --live` passes: facts, prose, article, links.
- Steps 1–6 are done (benchmark Public, overall score switched from *Percentage of tasks passed*, which ignores numeric scores, to *Average of task scores*), and step 7 is done up to publishing. Left: `preflight.py --live` and `check-links.py` (benchmark URL must return 200 signed out), then `--publish 4744048` on the author's go.

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
