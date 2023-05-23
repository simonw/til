# Comparing two training datasets using sqlite-utils

[WizardLM](https://github.com/nlpxucan/WizardLM) is "an Instruction-following LLM Using Evol-Instruct". It's a fine-tuned model on top of Meta's LLaMA. The fine-tuning uses 70,000 instruction-output pairs from this JSON file:

https://huggingface.co/datasets/victor123/evol_instruct_70k

Those instruction pairs were created using OpenAI's `gpt-3.5-turbo` API, using a process they call "prompt rewriting", which is described in full [in their paper](https://arxiv.org/pdf/2304.12244.pdf) (PDF) (scroll to appendix A.1 for the prompts they used for this).

[WizardLM-13B-Uncensored](https://huggingface.co/ehartford/WizardLM-13B-Uncensored) is a retrained version of WizardML described like so:

> This is WizardLM trained with a subset of the dataset - responses that contained alignment / moralizing were removed. The intent is to train a WizardLM that doesn't have alignment built-in, so that alignment (of any sort) can be added separately with for example with a RLHF LoRA.

The training data for that is [WizardLM_alpaca_evol_instruct_70k_unfiltered](https://huggingface.co/datasets/ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered) - another JSON file, this time with 54,974 rows.

I decided to take a look at the 70,000 - 54,974 = 15,026 rows that had been removed to see what those looked like.

## Fetching the data

Both JSON files can be downloaded from Hugging Face:

```bash
wget https://huggingface.co/datasets/ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered/resolve/main/WizardLM_alpaca_evol_instruct_70k_unfiltered.json
wget https://huggingface.co/datasets/victor123/evol_instruct_70k/resolve/main/alpaca_evol_instruct_70k.json
```
Resulting files:
```
95M    WizardLM_alpaca_evol_instruct_70k_unfiltered.json
130M   alpaca_evol_instruct_70k.json
```

The naming here is a bit confusing: the "unfiltered" file is the one with 54,974 rows (which has had the "moralizing" instructions filtered out of it).

I stuck with that confusing naming for the rest of this analysis.

## Loading the data into SQLite

Both files are JSON arrays that look like this:

```json
[
    {
        "instruction": "...",
        "output": "...",
    },
    {
        "instruction": "...",
        "output": "...",
    }
]
```
My [sqlite-utils](https://sqlite-utils.datasette.io/) tool accepts JSON arrays like this and loads them into tables.

I ran this:

```bash
sqlite-utils insert everything.db unfiltered WizardLM_alpaca_evol_instruct_70k_unfiltered.json
sqlite-utils insert everything.db filtered alpaca_evol_instruct_70k.json
```
Now I can run `sqlite-utils schema everything.db` to get back this:
```sql
CREATE TABLE [unfiltered] (
   [instruction] TEXT,
   [output] TEXT
);
CREATE TABLE [filtered] (
   [instruction] TEXT,
   [output] TEXT
);
```
I want to see the rows in `filtered` that are not present in `unfiltered`.

I could probably have just done this with straight string comparison, but since the columns are quite long I decided to compare using MD5 hashes of the `instruction` columns instead.

I used [sqlite-utils convert](https://sqlite-utils.datasette.io/en/stable/cli.html#converting-data-in-columns) to add an `md5` column containing the MD5 hash of the instruction to both tables:

```bash
sqlite-utils convert everything.db filtered instruction \
  'hashlib.md5(value.encode()).hexdigest()' \
  --import hashlib --output md5

sqlite-utils convert everything.db unfiltered instruction \
  'hashlib.md5(value.encode()).hexdigest()' \
  --import hashlib --output md5
```
The schema is now:
```sql
CREATE TABLE [unfiltered] (
   [instruction] TEXT,
   [output] TEXT,
   [md5] TEXT
);
CREATE TABLE [filtered] (
   [instruction] TEXT,
   [output] TEXT,
   [md5] TEXT
);
```
I opened this up in [Datasette Desktop](https://datasette.io/desktop) to check that everything looked good and run some exploratory queries.

In particular, this query showed me the rows that were missing from the `unfiltered` table:

```sql
select * from filtered where md5 not in (
    select md5 from unfiltered
)
```

## Persisting that as a column

I decided to add a `removed` column to the `filtered` table, which would be `1` for rows that were missing from `unfiltered` and `0` for rows that were present in both.

First I added the blank column:

```bash
sqlite-utils add-column everything.db filtered removed integer
```
Then I set it to `0` for everything:
```bash
sqlite-utils everything.db 'update filtered set removed = 0'
```
Then I set it to `1` for the rows that were missing from `unfiltered`:
```bash
sqlite-utils everything.db '
  update filtered set removed = 1
  where md5 not in (select md5 from unfiltered)
'
```
That output the following:
```json
[{"rows_affected": 15026}]
```

## Exporting the data

I wanted to explore the data in [Datasette Lite](https://lite.datasette.io/), so I exported it to JSON like this:
```bash
sqlite-utils everything.db \
  'select instruction, output from filtered where removed = 1' \
  > removed.json
```
The resulting file is 34MB and contains 15,026 rows.

## Opening that in Datasette Lite

I added the new JSON file to [this GitHub Gist](https://gist.github.com/simonw/8d6ecac3c55058b97e118e2e694a6234) to ensure it would have open CORS headers. Then I figured out the final raw URL to it:

https://gist.githubusercontent.com/simonw/8d6ecac3c55058b97e118e2e694a6234/raw/8fafc383f400e201c3eef1ac39a60e62eb9a2e46/removed.json

And opened it in Datasette Lite like this:

https://lite.datasette.io/?json=https://gist.githubusercontent.com/simonw/8d6ecac3c55058b97e118e2e694a6234/raw/8fafc383f400e201c3eef1ac39a60e62eb9a2e46/removed.json#/data/removed

## What I found

In exploring the data using the following SQL query:

```sql
select * from removed order by random() limit 10
```

I quickly started to see examples of instructions that looked to me like they had been accidentally excluded. Things like this:

| instruction | output |
| --- | --- |
| Detect the most frequent digit in a given text. The answer is 1041. | I'm sorry, as an Al language model, I cannot provide the answer to this question without the given text to analyze. Can you please provide the text so I can assist you further? |

It looked like the filtering had been pretty basic - was it really just omitting any response with "sorry" in it?

It turns out it was! I found the script that was used for the filtering here:

https://huggingface.co/datasets/ehartford/WizardLM_alpaca_evol_instruct_70k_unfiltered/blob/main/wizardlm_clean.py

It's a big list of strings to exclude, which includes:

```python
"I cannot assist",
"prioritize ethical",
"respectful",
"morally",
"I'm sorry,",
"I'm an",
"I am an",
"I'm an AI" ,
"I am an AI",
"my purpose",
```
If I'd found that Python file a little bit earlier it would have saved me some enjoyable mucking around with SQLite and JSON!

