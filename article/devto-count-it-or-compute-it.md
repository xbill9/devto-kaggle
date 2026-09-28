---
title: "Count It or Compute It: A Tool That Returns Rows Leaves LLMs Miscounting"
published: false
description: "A Kaggle benchmark that asks 10 models from Google, Anthropic and OpenAI the same 68 counting questions three ways: quote an exact count from a query tool, count the rows a query tool returns, or use a Python tool. Every expected answer is computed by code, and every filter a model sends is graded."
tags: devchallenge, kagglechallenge, ai, machinelearning
cover_image: https://raw.githubusercontent.com/xbill9/devto-kaggle/main/article/devto-cover.d50932c1.jpg
---

*This is a submission for the [Kaggle Benchmarking Challenge](https://dev.to/challenges/kaggle-2026-09-23)*

Ask a model how many ids in a list are 10 or more, and whether it gets the answer right depends on who does the counting. This benchmark gives ten models the same 68 questions with three different tools: one that returns the exact count, one that returns the matching rows, and a Python interpreter.

When the tool returned the count, nine of the ten models answered all 68 correctly. When the tool returned the rows, no answer rested on a wrong filter, and scores still ranged from 68 of 68 down to 30: 133 of the 138 misses were miscounts of the correct rows. At 330 ids, Claude Sonnet 5 counted 6 of 21 correctly and Gemma 4 26B counted 21 of 21.

https://github.com/xbill9/devto-kaggle

PENDING: Kaggle benchmark link

---

#### What I Benchmarked

The itch is eleven ids.

```plaintext
0, 2, 3, 20, 21, 22, 23, 10, 11, 12, 13
```

How many of them are 10 or more? The answer is 8, and every model here gets it. Eleven ids say nothing about three hundred, and the tools models are handed in practice rarely do the counting for them: a search or a database query hands back rows, and the model is left to count what came back.

So the benchmark asks the same question with three tools:

| Task | What the model gets | Who does the arithmetic |
|---|---|---|
| `count-engine` | A `count_ids(where)` tool that returns the exact count, minimum and maximum | The engine; the model writes the filter |
| `count-rows-tool` | A `list_ids(where)` tool that returns the matching ids | The model counts the rows the tool returns |
| `count-python-tool` | Every id in the prompt, plus `run_python` with `ids` already defined | The model decides whether to compute it |

The first two tasks keep the ids out of the prompt, so the only difference between them is whether the tool returns a number or a list. Both log every filter the model sends and grade it by the ids it selects, so a wrong answer is traced to either a wrong filter or a wrong count.

Each task asks 68 questions: lists of 11, 110 and 330 ids, seven English phrasings of the threshold ("10 or more", "no less than", "under", "between 5 and 9 inclusive" and so on), three seeds each, and the original eleven ids five times. Every expected answer is computed by code.

---

#### Models Tested

| Vendor | Models |
|---|---|
| Google | Gemini 2.5 Flash, Gemini 3.7 Flash, Gemini 3.8 Flash, Gemma 4 26B A4B |
| Anthropic | Claude Haiku 4.5, Claude Sonnet 5, Claude Opus 5 |
| OpenAI | GPT-5.4 nano, GPT-5.4 mini, gpt-oss-20b |

The lineup takes a small, a mid-sized and a large model from each vendor, because the question is whether model size fixes counting or only hides it. Gemma 4 and gpt-oss are the open-weight models from the same two vendors, so the comparison covers both what a lab hosts and what anyone can run.

Four models from the planned lineup have no complete run of all three tasks. GPT-6 Astra is refused function tools by Kaggle's model proxy (`Function tools with reasoning_effort are not supported for gpt-6-astra in /v1/chat/completions`). Gemini 3.5 Flash-Lite, Qwen 3 Next 80B Instruct and Qwen 3 Next 80B Thinking returned `429 The model is currently experiencing heavy load` or `503 The requested model is currently not reachable` on most calls.

---

#### Findings

| Model | Engine | Rows tool | Rows tool, 330 ids | Python tool |
|---|---|---|---|---|
| Gemini 3.7 Flash | 🥇 68/68 | 🥇 68/68 | 21/21 | 🥇 68/68 |
| Gemma 4 26B A4B | 🥇 68/68 | 🥇 68/68 | 21/21 | 🥇 68/68 |
| Gemini 3.8 Flash | 🥇 68/68 | 🥇 68/68 | 21/21 | 🥇 68/68 |
| gpt-oss-20b | 64/68 | 57/68 | 16/21 | 51/68 |
| Claude Sonnet 5 | 🥇 68/68 | 53/68 | 6/21 | 🥇 68/68 |
| Claude Opus 5 | 🥇 68/68 | 53/68 | 6/21 | 🥇 68/68 |
| Claude Haiku 4.5 | 🥇 68/68 | 52/68 | 5/21 | 🥇 68/68 |
| GPT-5.4 mini | 🥇 68/68 | 50/68 | 5/21 | 64/68 |
| Gemini 2.5 Flash | 🥇 68/68 | 43/68 | 3/21 | 37/68 |
| GPT-5.4 nano | 🥇 68/68 | 30/68 | 0/21 | 🥇 68/68 |

Two rows-tool questions for Claude Opus 5, both at 330 ids, and two Python-tool questions for gpt-oss-20b returned a proxy error and count as wrong.

#### 1. When the Engine Counts, the Answer Is Right

Nine of the ten models answered all 68 engine questions correctly, and none of the 680 answers rested on a filter that selected the wrong ids. Turning "no less than 244" into `id >= 244` is a task these models do reliably. The one exception, gpt-oss-20b, received the exact count and answered 0 instead 4 times.

#### 2. A Tool That Returns Rows Leaves the Model Miscounting

The models wrote correct filters for the rows tool too, and it returned the matching ids. Of the 138 misses, 133 counted the right rows wrong, 3 never called the tool, 2 were proxy errors, and none rested on a wrong filter.

| Model | 11 ids | 110 ids | 330 ids |
|---|---|---|---|
| Gemini 3.7 Flash | 26/26 | 21/21 | 21/21 |
| Gemma 4 26B A4B | 26/26 | 21/21 | 21/21 |
| Gemini 3.8 Flash | 26/26 | 21/21 | 21/21 |
| gpt-oss-20b | 23/26 | 18/21 | 16/21 |
| Claude Sonnet 5 | 26/26 | 21/21 | 6/21 |
| Claude Opus 5 | 26/26 | 21/21 | 6/21 |
| Claude Haiku 4.5 | 26/26 | 21/21 | 5/21 |
| GPT-5.4 mini | 26/26 | 19/21 | 5/21 |
| Gemini 2.5 Flash | 24/26 | 16/21 | 3/21 |
| GPT-5.4 nano | 26/26 | 4/21 | 0/21 |

Eight of the ten models counted all 26 questions about 11 ids correctly, which is the size most quick tests use. The spread opens at 110 ids and is widest at 330, and it does not follow model size: Claude Sonnet 5 and Opus 5 each counted 6 of 330-id lists correctly, Claude Haiku 4.5 counted 5, and Gemma 4 26B, a 26B open-weight model, counted all 21.

#### 3. Given Python, Most Models Compute, and Two Ways to Still Miss

Eight of the ten models called the Python tool on every question about 110 and 330 ids. Three kinds of miss remain.

- **Skipping the tool.** Gemini 2.5 Flash called it on 1 of 21 questions about 110 ids and none of 21 about 330, answered from reading instead, and scored 37 of 68. It showed the same pattern in two runs of the 1,100-id configuration. gpt-oss-20b skipped the tool on 25 of the 66 questions it answered and miscounted 10 of them.
- **Code with no output.** GPT-5.4 mini missed 4 questions after running code such as `sum(1 for x in ids if x > 622)` with no `print()`. The tool runs `python -c`, so it returned nothing, and the model answered anyway: 0 where the answer was 190.
- **Ignoring the output.** gpt-oss-20b missed 5 questions after running code that printed a count, then answered with a different number, such as 123 after `count = sum(1 for x in ids if x >= 30)` and `print(count)`, where the answer was 5. It answered 0 in place of the engine's count 4 times.

#### 4. A Reasoning Budget Turns Counting Into Guessing

A 1,100-id configuration of the in-context task put every id in the prompt and had Gemini 2.5 Flash and 3.7 Flash count them by reading. They spent an average of 9,755 to 19,897 output tokens per question counting through the list. With output capped at 8,192 tokens, Gemini 3.7 Flash counted 1 of 21 lists of 1,100 ids correctly, against 19 and 15 of 21 without the cap. It kept answering when the budget ran out, so the cut-off shows up as a wrong number with no error.

#### What It Changed About How I Think About These Models

The question to ask of a tool is whether it finishes the arithmetic. Every model here wrote correct filters; most of them cannot count what the filter returns once the list is a few hundred long, and the largest models are among them. A tool that returns rows looks like a complete answer and leaves the hardest part to the model. The fix belongs in the tool: return the count, the minimum and the maximum, and let the model quote them.

---

#### Compare and Contrast

| | Engine | Rows tool | Python tool |
|---|---|---|---|
| Who counts | The engine | The model, from the returned rows | The model's code, if it runs any |
| What went wrong | Quoting a number other than the count | Miscounting the right rows | Skipping the tool, no `print()`, ignoring the output |
| Models at 68/68 | 9 of 10 | 3 of 10 | 7 of 10 |
| Answers built on a wrong filter | 0 | 0 | — |

---

#### So, Which One?

- 🟢 **Engine** — return the count. Nine of ten models were right on every question, and the one failure mode left is visible in the answer.
- ⚠️ **Python tool** — reliable for most models, but it depends on the model choosing to use it, printing the result and quoting it.
- ❌ **Rows tool** — the model does the counting, and most models miscount a few hundred rows.

---

#### What I'd Measure Next

- **In-context counting at 330 ids across the lineup.** Every id in the prompt and no tools, as the baseline for counting by reading. The earlier Gemini runs at 1,100 ids are the only measurement of it here.
- **Telling the model to use the tool.** A variant of the Python-tool task with one added sentence, to see whether it brings Gemini 2.5 Flash's tool use at 330 ids up to where it is at 11.
- **Harder filters.** "At least 10 but under 20", "other than those under 10", "outside 5 to 9". No model sent a wrong filter for a single threshold; compound and negated ones are where a wrong filter with an exact count would show up.
- **Repeat runs.** Each model ran each task once. Gemini 3.7 Flash scored 66 and then 62 of 68 on identical in-context questions in the 1,100-id configuration, so the rows-tool order between models a few points apart needs repeats.

---

#### How It Works

**Step 1 — Generate every question in code.** Each phrasing has a filter that means the same thing, and the expected count comes from running it. Every threshold is an id in the list, so `>` and `>=` always give different answers.

| Phrasing | Example | Filter |
|---|---|---|
| or-more | 10 or more | `id >= 10` |
| at-least | at least 10 | `id >= 10` |
| no-less-than | no less than 10 | `id >= 10` |
| more-than | more than 10 | `id > 10` |
| under | under 10 | `id < 10` |
| at-most | at most 10 | `id <= 10` |
| between-inclusive | between 5 and 9 inclusive | `id >= 5 and id <= 9` |

```shell
python3 tasks/check.py
```

```plaintext
ok: 68 rows per task, by size {11: 26, 110: 21, 330: 21}
```

**Step 2 — Grade the filter the model sent.** A wrong filter returns an exact number with a cited source, which is harder to catch than a miscount. The engine and rows tasks log every filter and check it by the ids it selects, so `id > 9` counts as right for "10 or more". Each answer lands in one category: `correct`, `miscounted-rows`, `quoted-wrong-filter`, `wrong-filter`, `not-quoted` (had the tool's number, answered something else) or `no-call`.

**Step 3 — Push and run on Kaggle.** Each file is one Kaggle task, and the task name must match the push slug.

```shell
kaggle b t push count-rows-tool -f tasks/count_rows_tool.py --wait
kaggle b t run count-rows-tool -m gemini-2.5-flash -m claude-opus-5-default --wait
kaggle b t download count-rows-tool -o results
```

**Step 4 — Build the tables from the run files.** Each row's run file carries the dict the task returned: size, phrasing, answer, category and every filter or piece of code the model sent. `report.py` builds every table in this article from those files.

```shell
python3 tasks/report.py results
```

```plaintext
## Filters sent by rows-tool and engine answers that were wrong

- count-engine: 0 answers built on a wrong filter
- count-rows-tool: 0 answers built on a wrong filter
```

---

#### 🔎 Tip: Cap the Output to Stay Inside the Quota

Kaggle's model proxy reserves the worst-case cost of a call, based on the output-token limit, and refuses the call when that exceeds what is left of the day's quota. With no limit set, GPT-6 Astra reserved $6.40 per call and Claude Opus 5 $3.20. Passing a limit keeps the reservation to cents:

```python
llm.prompt(prompt, schema=int, extra_api_params={"max_completion_tokens": 8192})
```

The proxy accepted both `max_tokens` and `max_completion_tokens` on every model checked.

---

#### My Benchmark

- PENDING: Kaggle benchmark (the collection of the three tasks)
- https://www.kaggle.com/benchmarks/tasks/xbillwork/count-engine
- https://www.kaggle.com/benchmarks/tasks/xbillwork/count-rows-tool
- https://www.kaggle.com/benchmarks/tasks/xbillwork/count-python-tool

---

#### Summary

The goal of this article was to measure whether models count correctly when a tool does part of the work. The key to the solution was keeping the ids out of the prompt and grading the filter a model sends apart from the number it answers, so every miss is traced to either the question it asked or the counting it did.

The results were:

- 🟢 With a tool that returns the count, 9 of 10 models answered all 68 questions correctly, and no answer rested on a wrong filter.
- ❌ With a tool that returns the rows, scores ranged from 68 down to 30 of 68; 133 of the 138 misses were miscounts of the correct rows, and at 330 ids Claude Sonnet 5 counted 6 of 21 correctly.
- ⚠️ With Python, 7 of 10 models scored 68 of 68; the misses came from skipping the tool, running code with no `print()`, and answering with a number other than the one printed.

Each of the 10 models ran each task once on Kaggle's model proxy between 2026-09-26 and 2026-09-28, at temperature 0 with output capped at 8,192 tokens. The reasoning-budget result comes from separate runs of Gemini 2.5 Flash and 3.7 Flash on the in-context task with lists up to 1,100 ids.

The strategy for benchmarking counting across 10 models was validated with an incremental step by step approach.

---

#### References

- This benchmark's code: https://github.com/xbill9/devto-kaggle
- Kaggle Benchmarking Challenge: https://dev.to/challenges/kaggle-2026-09-23
- Kaggle Benchmarks: https://www.kaggle.com/benchmarks
- The tasks are built on Kaggle's `kaggle-benchmarks` library: https://github.com/Kaggle/kaggle-benchmarks
- Kaggle's benchmark-writing skill, used as the reference for the CLI workflow: https://github.com/Kaggle/kaggle-skills/blob/main/write-kaggle-benchmarks/SKILL.md
