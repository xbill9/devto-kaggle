## Engine, rows tool and Python tool, every model with all three runs

| Model | Engine | Rows tool | Rows tool, 330 ids | Python tool | Python tool used, 110 / 330 ids |
|---|---|---|---|---|---|
| Gemini 3.8 Flash | 68/68 | 68/68 | 21/21 | 68/68 | 21/21 / 21/21 |
| Gemini 3.7 Flash | 68/68 | 67/68 | 20/21 | 68/68 | 21/21 / 21/21 |
| Gemma 4 26B A4B | 68/68 | 67/68 | 20/21 | 68/68 | 21/21 / 21/21 |
| gpt-oss-20b | 62/68 | 54/68 | 15/21 | 56/68 (1 errored) | 18/21 / 16/20 |
| GPT-5.4 mini | 68/68 | 52/68 | 5/21 | 64/68 | 21/21 / 21/21 |
| Gemini 2.5 Flash | 68/68 | 45/68 | 0/21 | 37/68 | 1/21 / 0/21 |
| GPT-5.4 nano | 68/68 | 31/68 | 0/21 | 68/68 | 21/21 / 21/21 |

## Rows tool by list size

| Model | 11 ids | 110 ids | 330 ids |
|---|---|---|---|
| Gemini 3.8 Flash | 26/26 | 21/21 | 21/21 |
| Gemini 3.7 Flash | 26/26 | 21/21 | 20/21 |
| Gemma 4 26B A4B | 26/26 | 21/21 | 20/21 |
| gpt-oss-20b | 24/26 | 15/21 | 15/21 |
| GPT-5.4 mini | 26/26 | 21/21 | 5/21 |
| Gemini 2.5 Flash | 25/26 | 20/21 | 0/21 |
| GPT-5.4 nano | 26/26 | 5/21 | 0/21 |

## Output tokens and cost per question, engine against rows tool

Mean over the questions that answered; tokens and cost are as Kaggle's model proxy reports them.

| Model | Size | Engine correct | Engine out tokens | Engine $ | Rows correct | Rows out tokens | Rows $ |
|---|---|---|---|---|---|---|---|
| Gemini 3.8 Flash | 11 | 26/26 | 130 | 0.0010 | 26/26 | 312 | 0.0020 |
| Gemini 3.8 Flash | 110 | 21/21 | 133 | 0.0010 | 21/21 | 1,286 | 0.0065 |
| Gemini 3.8 Flash | 330 | 21/21 | 140 | 0.0010 | 21/21 | 2,742 | 0.0146 |
| Gemini 3.7 Flash | 11 | 26/26 | 123 | 0.0009 | 26/26 | 294 | 0.0018 |
| Gemini 3.7 Flash | 110 | 21/21 | 122 | 0.0009 | 21/21 | 1,194 | 0.0057 |
| Gemini 3.7 Flash | 330 | 21/21 | 130 | 0.0010 | 20/21 | 2,785 | 0.0133 |
| Gemma 4 26B A4B | 11 | 26/26 | 266 | 0.0002 | 26/26 | 394 | 0.0003 |
| Gemma 4 26B A4B | 110 | 21/21 | 297 | 0.0003 | 21/21 | 2,145 | 0.0014 |
| Gemma 4 26B A4B | 330 | 21/21 | 311 | 0.0003 | 20/21 | 8,153 | 0.0052 |
| gpt-oss-20b | 11 | 24/26 | 402 | 0.0001 | 24/26 | 394 | 0.0001 |
| gpt-oss-20b | 110 | 19/21 | 382 | 0.0001 | 15/21 | 1,043 | 0.0003 |
| gpt-oss-20b | 330 | 19/21 | 451 | 0.0001 | 15/21 | 2,684 | 0.0007 |
| GPT-5.4 mini | 11 | 26/26 | 35 | 0.0007 | 26/26 | 36 | 0.0007 |
| GPT-5.4 mini | 110 | 21/21 | 35 | 0.0007 | 21/21 | 36 | 0.0008 |
| GPT-5.4 mini | 330 | 21/21 | 35 | 0.0007 | 5/21 | 39 | 0.0013 |
| Gemini 2.5 Flash | 11 | 26/26 | 194 | 0.0006 | 25/26 | 302 | 0.0009 |
| Gemini 2.5 Flash | 110 | 21/21 | 200 | 0.0006 | 20/21 | 591 | 0.0016 |
| Gemini 2.5 Flash | 330 | 21/21 | 196 | 0.0006 | 0/21 | 580 | 0.0017 |
| GPT-5.4 nano | 11 | 26/26 | 35 | 0.0002 | 26/26 | 35 | 0.0002 |
| GPT-5.4 nano | 110 | 21/21 | 35 | 0.0002 | 5/21 | 35 | 0.0002 |
| GPT-5.4 nano | 330 | 21/21 | 35 | 0.0002 | 0/21 | 35 | 0.0003 |

## At 330 ids: rows tool against engine

| Model | Rows tool correct | Output tokens per question, rows tool | Engine correct | Output tokens per question, engine | Rows-tool cost per question vs engine |
|---|---|---|---|---|---|
| Gemma 4 26B A4B | 20/21 | 8,153 | 21/21 | 311 | 18.6x |
| Gemini 3.7 Flash | 20/21 | 2,785 | 21/21 | 130 | 13.5x |
| Gemini 3.8 Flash | 21/21 | 2,742 | 21/21 | 140 | 14.3x |
| gpt-oss-20b | 15/21 | 2,684 | 19/21 | 451 | 5.2x |
| Gemini 2.5 Flash | 0/21 | 580 | 21/21 | 196 | 2.6x |
| GPT-5.4 mini | 5/21 | 39 | 21/21 | 35 | 1.9x |
| GPT-5.4 nano | 0/21 | 35 | 21/21 | 35 | 1.7x |

## Categories

- count-engine: correct 470, not-quoted 5, no-call 1
- count-rows-tool: correct 384, miscounted-rows 88, no-call 3, no-answer 1
- count-python-tool: correct-tool 406, miscount-no-tool 37, correct-no-tool 23, wrong-tool 9

## Filters sent by rows-tool and engine answers that were wrong

- count-engine: 0 answers built on a wrong filter
- count-rows-tool: 0 answers built on a wrong filter

## Left out (no complete run of all three tasks)

- Gemini 3.5 Flash-Lite: complete in none
- Claude Haiku 4.5: complete in count-engine, count-python-tool
- Claude Sonnet 5: complete in count-engine, count-python-tool
- Claude Opus 5: complete in count-engine, count-python-tool
- GPT-6 Astra: complete in none
- Qwen 3 Next 80B Instruct: complete in none
- Qwen 3 Next 80B Thinking: complete in none
