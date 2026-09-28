## Engine, rows tool and Python tool, every model with all three runs

| Model | Engine | Rows tool | Rows tool, 330 ids | Python tool | Python tool used, 110 / 330 ids |
|---|---|---|---|---|---|
| Gemini 3.7 Flash | 68/68 | 68/68 | 21/21 | 68/68 | 21/21 / 21/21 |
| Gemini 3.8 Flash | 68/68 | 68/68 | 21/21 | 68/68 | 21/21 / 21/21 |
| Gemma 4 26B A4B | 68/68 | 68/68 | 21/21 | 68/68 | 21/21 / 21/21 |
| gpt-oss-20b | 64/68 | 57/68 | 16/21 | 51/68 (2 errored) | 14/20 / 14/21 |
| Claude Sonnet 5 | 68/68 | 53/68 | 6/21 | 68/68 | 21/21 / 21/21 |
| Claude Opus 5 | 68/68 | 53/68 (2 errored) | 6/19 | 68/68 | 21/21 / 21/21 |
| Claude Haiku 4.5 | 68/68 | 52/68 | 5/21 | 68/68 | 21/21 / 21/21 |
| GPT-5.4 mini | 68/68 | 50/68 | 5/21 | 64/68 | 21/21 / 21/21 |
| Gemini 2.5 Flash | 68/68 | 43/68 | 3/21 | 37/68 | 1/21 / 0/21 |
| GPT-5.4 nano | 68/68 | 30/68 | 0/21 | 68/68 | 21/21 / 21/21 |

## Rows tool by list size

| Model | 11 ids | 110 ids | 330 ids |
|---|---|---|---|
| Gemini 3.7 Flash | 26/26 | 21/21 | 21/21 |
| Gemini 3.8 Flash | 26/26 | 21/21 | 21/21 |
| Gemma 4 26B A4B | 26/26 | 21/21 | 21/21 |
| gpt-oss-20b | 23/26 | 18/21 | 16/21 |
| Claude Sonnet 5 | 26/26 | 21/21 | 6/21 |
| Claude Opus 5 | 26/26 | 21/21 | 6/19 |
| Claude Haiku 4.5 | 26/26 | 21/21 | 5/21 |
| GPT-5.4 mini | 26/26 | 19/21 | 5/21 |
| Gemini 2.5 Flash | 24/26 | 16/21 | 3/21 |
| GPT-5.4 nano | 26/26 | 4/21 | 0/21 |

## Categories

- count-engine: correct 676, not-quoted 4
- count-rows-tool: correct 530, miscounted-rows 133, correct-no-filter 12, no-call 3
- count-python-tool: correct-tool 598, miscount-no-tool 41, correct-no-tool 30, wrong-tool 9

## Filters sent by rows-tool and engine answers that were wrong

- count-engine: 0 answers built on a wrong filter
- count-rows-tool: 0 answers built on a wrong filter

## Left out (no complete run of all three tasks)

- Gemini 3.5 Flash-Lite: complete in none
- GPT-6 Astra: complete in none
- Qwen 3 Next 80B Instruct: complete in none
- Qwen 3 Next 80B Thinking: complete in none
