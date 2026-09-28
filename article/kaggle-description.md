**Does a model count correctly what its tool returns?** An agent's search, database or API tool usually returns a list of records, and when the user asks "how many", the model does the counting. This benchmark asks ten models the same 68 counting questions with three tools and changes only who does the arithmetic:

- **count-engine**: the tool returns the exact count, minimum and maximum. The model writes the filter and quotes the number.
- **count-rows-tool**: the tool returns the matching ids. The model counts them.
- **count-python-tool**: every id is in the prompt, plus a Python tool with the ids already defined.

The questions cover lists of 11, 110 and 330 ids and seven phrasings of the threshold ("10 or more", "no less than", "under", "between 5 and 9 inclusive" and so on). Every expected answer is computed by code, and every filter a model sends is checked by the ids it selects, so a miss is traced to either the query or the count. Each task's score is the share of the 68 questions answered correctly; the overall score is the average of the three tasks.

Code: https://github.com/xbill9/devto-kaggle
