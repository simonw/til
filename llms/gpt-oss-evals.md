# Running a gpt-oss eval suite against LM Studio on a Mac

OpenAI's [gpt-oss models](https://github.com/openai/gpt-oss/) come with an eval suite, which is described in their [Verifying gpt-oss implementations](https://cookbook.openai.com/articles/gpt-oss/verifying-implementations) cookbook. I figured out how to run it on my Mac against their `gpt-oss-20b` model hosted locally using LM Studio, using [uv](github.com/astral-sh/uv).

TLDR: Here's the recipe that worked for me:

```bash
mkdir /tmp/aime25_openai
OPENAI_API_KEY=x \
  uv run --python 3.13 --with 'gpt-oss[eval]' \
  python -m gpt_oss.evals \
  --base-url http://localhost:1234/v1 \
  --eval aime25 \
  --sampler chat_completions \
  --model openai/gpt-oss-20b \
  --reasoning-effort low \
  --n-threads 2
```
You'll need to install the model in LM Studio first - you can start by clicking the "Use Model in LM Studio" button on their [openai/gpt-oss-20b page](https://lmstudio.ai/models/openai/gpt-oss-20b).

When you load the model make sure to increase the context length available to it - the default, 4096, is too short for some of the exercises.

## The options

Let's break this down a little.

I'm using `uv run` for the benchmark. This means I get all of the dependencies installed automatically without having to worry about setting up a virtual environment myself.

- `OPENAI_API_KEY=x` - the OpenAI client library insisted on an API key even though LM Studio doesn't need one. I set it to `x` before running the script.
- `--python 3.13` - use Python 3.13
- `--with 'gpt-oss[eval]'` - install the `gpt-oss` package with the `eval` extras - [defined here](https://github.com/openai/gpt-oss/blob/cf427a62e2d80b33b87cbd1ab715730910f5aad0/pyproject.toml#L30) - that gives me the full set of dependencies needed to run the eval suite, defined as `"pandas", "numpy", "openai", "jinja2", "tqdm", "blobfile"`.
- `python -m gpt_oss.evals` - runs the `main()` function in [gpt_oss/evals/__main__.py](https://github.com/openai/gpt-oss/blob/main/gpt_oss/evals/__main__.py)
- `--base-url http://localhost:1234/v1` - the eval suite needs an OpenAI-compatible API to talk to. LM Studio runs one on port 1234.
- `--eval aime25` - the eval suite to run. Here I'm running the AIME 2025 eval, derived from the  American Invitational Mathematics Examination.
- `--sampler chat_completions` - it should use the OpenAI chat completions API format - the other option here is `responses` for their newer Responses API.
- `--model openai/gpt-oss-20b` - the model to use, which I have installed in LM Studio.
- `--reasoning-effort low` - the reasoning effort to use, one of `low`, `medium` or `high`. I chose `low` on the assumption that it would be faster.
- `--n-threads 2` - this defaults to 1584, which is presumably a great idea if you want fast results and have an entire cluster to run this against! I dropped it to 2 to see if LM Studio could process two requests at a time, but as far as I can tell it only handles one so a value of 1 here would have provided basically the same performance.

## The results

The script wrote out three files to my `/tmp/aime25_openai` directory. I've shared them here:

- [gpt-oss-20b-low_temp1.0_20250816_094011.html](https://static.simonwillison.net/static/2025/gpt-oss-20b-aime25/gpt-oss-20b-low_temp1.0_20250816_094011.html) - this 2MB HTML file contained the full prompt and response for every executed question - example below.
- [gpt-oss-20b-low_temp1.0_20250816_094011_allresults.json](https://static.simonwillison.net/static/2025/gpt-oss-20b-aime25/gpt-oss-20b-low_temp1.0_20250816_094011_allresults.json) - those results as JSON - this file is 4.1MB because it includes both the raw JSON and the rendered HTML for each test.
- [gpt-oss-20b-low_temp1.0_20250816_094011.json](https://static.simonwillison.net/static/2025/gpt-oss-20b-aime25/gpt-oss-20b-low_temp1.0_20250816_094011.json) - 124 bytes of summary JSON.

Here's that summary JSON in full:

```json
{
  "chars": 7282.25,
  "chars:std": 4356.9365532638485,
  "score": 0.45416666666666666,
  "score:std": 0.4978948740000801
}
```
That `score` is the most important number - the eval suite assigs a `1` for each correct answer and a `0` for incorrect answers and then displays the average across all questions, which here is 45.4%. `chars` is the average length of response, whitespace included. The `:std` things show the standard deviation of each.

## An example benchmark question

Here's one example of a shorter question and answer from the HTML document:

<blockquote><strong>user</strong>
<pre>Find the sum of all integer bases $b&gt;9$ for which $17_{b}$ is a divisor of $97_{b}$.
Please reason step by step, and put your final answer within \boxed{}.</pre>
<strong>assistant</strong>
<pre>We need in base b: numbers: 17_b = 1*b+7 = b+7. 97_b=9*b+7.

Condition: (b+7) divides (9b+7). Compute division: 9b+7 = 9(b+7)-56? Let&#39;s compute: 9(b+7)=9b+63 so difference: (9b+7)-(9b+63)= -56. So 9b+7 ≡ -56 mod (b+7). Therefore divisibility requires b+7 divides 56.

Because remainder is -56; so need b+7 | 56.

Also base&gt;9, and digits must be less than base: in 97_b digit 9 &lt; b =&gt; b≥10. Already &gt;9.

So let d = b+7 positive divisor of 56. Divisors of 56: 1,2,4,7,8,14,28,56. Then b = d-7. Need b&gt;9 so d-7&gt;9 → d&gt;16. So d in divisors &gt;16: 28 and 56.

Check b=21 and b=49. Both base≥10. Also digits 1,7,9 okay (since b&gt;9). So bases 21 and 49.

Sum = 70.In base \(b\) we have  

\[
17_{b}=1\cdot b+7=b+7,\qquad 
97_{b}=9\cdot b+7=9b+7 .
\]

For \(17_b\) to divide \(97_b\),

\[
(b+7)\mid (9b+7).
\]

Compute the remainder of \(9b+7\) upon division by \(b+7\):

\[
9b+7 = 9(b+7)-56 .
\]

Hence

\[
9b+7 \equiv -56 \pmod{\,b+7}.
\]

Thus we require  

\[
b+7 \mid 56.
\]

Let \(d=b+7\).  
\(d\) must be a positive divisor of \(56\):

\[
1,\;2,\;4,\;7,\;8,\;14,\;28,\;56 .
\]

The base must satisfy \(b&gt;9\), i.e. \(d-7&gt;9 \Rightarrow d&gt;16\).  
From the list, the eligible divisors are \(28\) and \(56\).

Therefore

\[
b = 28-7 = 21,\qquad b = 56-7 = 49.
\]

Both bases satisfy the digit condition (\(9&lt;b\)).  

The sum of all such integer bases is

\[
21+49=70 .
\]

\[
\boxed{70}
\]</pre>
<p>Correct Answer: 70</p>
<p>Extracted Answer: 70</p>
<p>Score: 1.0</p>
</blockquote>

All of the questions end with the exact same text, which is [added by this prompt template](https://github.com/openai/gpt-oss/blob/cf427a62e2d80b33b87cbd1ab715730910f5aad0/gpt_oss/evals/aime_eval.py#L12-L15):

> `Please reason step by step, and put your final answer within \boxed{}.`

(Love that we're saying "please" to these thing!)

Each question in the benchmark has an expected correct answer, and the test harness compares that to [the extracted](https://github.com/openai/gpt-oss/blob/cf427a62e2d80b33b87cbd1ab715730910f5aad0/gpt_oss/evals/aime_eval.py#L20-L32) `\boxed{X}` value.

## The implementation of the eval

The [gpt_oss/evals/aime_eval.py](https://github.com/openai/gpt-oss/blob/cf427a62e2d80b33b87cbd1ab715730910f5aad0/gpt_oss/evals/aime_eval.py) Python file is less than 100 lines long.

It loads two separate newline-delimited JSON files and combines them into one collection of questions:

- https://huggingface.co/datasets/opencompass/AIME2025/raw/main/aime2025-I.jsonl - 15 questions
- https://huggingface.co/datasets/opencompass/AIME2025/raw/main/aime2025-II.jsonl - 15 more questions

Yes, it turns out this eval is just 30 questions total! Each line in those files looks something like this:

```json
{"question": "Find the sum of all integer bases $b>9$ for which $17_{b}$ is a divisor of $97_{b}$.", "answer": "70"}
```

So why did the eval take 3.5 hours to run? Because the questions are each run eight times for that specific eval, as defined by [this code here](https://github.com/openai/gpt-oss/blob/cf427a62e2d80b33b87cbd1ab715730910f5aad0/gpt_oss/evals/__main__.py#L136-L141), for a total of 240 prompts.

## Problems I had getting this to work

Unfortunately the eval only writes results to disk at the end of the run, so it's possible to only find out about problems after it has been chugging away for hours!

- `No such file or directory: '/tmp/aime25_openai/gpt-...` - I got this error at the *end* of my first 3.5 hour run - the script tried to write the results to disk and failed because the expected directory did not exist yet.
- `Reached context length of 4096 tokens with model (arch: gpt-oss) that does not currently support mid-generation context overflow` - I saw this error a bunch of times when I was using the default 4096 context length, before I increased it.
