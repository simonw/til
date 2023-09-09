# Summarizing Hacker News discussion themes with Claude and LLM

I've been experimenting with the combination of [Claude](https://claude.ai/) and my [LLM CLI tool](https://llm.datasette.io/) to give me quick summaries of long discussions on [Hacker News](https://news.ycombinator.com/).

I only use this occasionally: usually I'll follow the conversation directly, but sometimes it can be neat to get a quick summary of the key themes in a huge 100+ comment thread.

I'm using Claude for this because both of the current Claude models (Claude Instant, cheaper and faster and Claude 2, better) can handle up to 100,000 tokens.

My Bash script for this does the following:

- Fetch the entire conversation as JSON from the [Hacker News Algolia API](https://hn.algolia.com/api)
- Use `jq` to process the recursive JSON structure into a flat list of just the comment text
- Pipe that to Claude via my LLM tool to generate a summary

I'm using LLM with the [llm-claude](https://github.com/tomviner/llm-claude) plugin, which requires an API key from Anthropic. Prior to obtaining that key I used [llm-openrouter](https://github.com/simonw/llm-openrouter) which provides access to Claude via a paid endpoint.

In both cases I had set the `claude` alias in my local LLM install using `llm aliases set claude longer-model-id`.

After several rounds of iteration, I settled on the following prompt:

> HACKER NEWS CONTENT HERE Summarize the themes of the opinions expressed here, including quotes where appropriate.

This is beginning to work quite well. Here's the summary it generated for this thread on [Teaching with AI](https://news.ycombinator.com/item?id=37340314) with 316 comments:

> Here is a summary of some of the key themes that emerged from the discussion on using AI systems like ChatGPT for education:
> 
> On potential benefits:
> 
> - Several people mentioned how AI tutors could provide personalized instruction and support learning through interactive dialogues. As one commenter said, "The reality is that effective LLMs, combined with some kind of knowledge retrieval, are coming close to becoming the idealized individual tutor."
> - Some saw AI as a useful tool for generating educational content like lesson plans, quizzes, and study guides. For example: "Those prompts 4 "AI teacher" is pretty good for learning group theory at least."
> - Others highlighted the potential for AI to support language learning through conversation practice and grammatical corrections. "I'm surprised languages aren't more of a focus in the LLM hype. They're like if Rosetta Stone ads were true."
> 
> On risks and limitations:
> 
> - Many expressed concerns about the system hallucinating incorrect information. As one person warned, "Teachers should be very careful using a vanilla LLM for education without some kinds of extra guardrails or extra verification."
> - Some argued students could become over reliant on AI, preventing deeper learning. For example: "If students rely on an LLM, they will never get a chance to practice this essential skill, and, in my opinion, will be a lot dumber as a result."
> - Several comments emphasized the need to rethink testing and assessment to evaluate true understanding versus an AI's capabilities. As one said, "Assignments are usually just a proxy for the skill which we're actually trying to teach or evaluate."
> 
> On implementation challenges: 
> 
> - A number of people discussed issues around student motivation and gaming the system. As one comment put it: "The main issue that is not addressed is that students need points to pass their subjects and get a high school diploma. LLMs are a magical shortcut to these points for many students."
> - Some raised concerns about teachers lacking the skills to effectively integrate AI, with one stating: "I think it's great what you two did, maybe it would be more effective if you did a small article or video on it? Many would be honored to be able to get help from your insights, it's needed."
> 
> In summary, the discussion highlighted both opportunities and challenges in leveraging AI for education, with many calling for careful implementation and rethinking of learning objectives, assessments, and the role of teachers.

A quick spot-check on the quoted comments found them on the page, so if it's hallucinating any I haven't caught it yet.

I'm using the Claude API for free for non-commercial purposes. This mechanism can use a LOT of tokens, so if you're going to try this keep an eye on how much it might cost you.

Here's the Bash script I wrote (with a skeleton by GPT-4, hence the argument validation) called `hn-summary.sh`:

```bash
#!/bin/bash

# Validate that the argument is an integer
if [[ ! $1 =~ ^[0-9]+$ ]]; then
  echo "Please provide a valid integer as the argument."
  exit 1
fi

# Make API call, parse and summarize the discussion
curl -s "https://hn.algolia.com/api/v1/items/$1" | \
  jq -r 'recurse(.children[]) | .text' | \
  llm -m claude 'Summarize the themes of the opinions expressed here, including quotes where appropriate.'

```
I run it like this:
```bash
hn-summary.sh 37340314
```

## Follow-up questions

Since this is using LLM, I can ask follow-up questions directly after running the script using `llm -c` (for `--continue`):

```bash
llm -c 'More detail and quotes about student motivation'
```
LLM replied:

> Here are some additional details and quotes about the theme of student motivation and learning when using AI systems like ChatGPT in education:
>
> Several comments expressed concerns that students would use ChatGPT simply to get grades or test scores, without actually learning:
>
> - "The main issue that is not addressed is that students need points to pass their subjects and get a high school diploma. LLMs are a magical shortcut to these points for many students, and therefore very tempting to use, for a number of normal reasons (time-shortage, laziness, fatigue, not comprehending, insecurity, parental pressure, status, etc.)."
> - "If people don’t want to learn, let them cheat themselves. Just that grades (and what determines whether a student gets to go to a good university) should be graded 100% in person."
> - "I can’t imagine I’d have bothered engaging with any subject I wasn’t interested in if ChatGPT existed back then."
>
> However, some argued that intrinsic motivation matters more than grades:
>
> - "Students definitely love to learn. They do not like to be stuffed in a chair and lectured at and forced to do rote activities. But who does?"
> - "Those who really desire to understand how things work will be undeterred by the temptation of AI. There are two types of people: those who care to know and really understand and those who don’t." 
>
> And that students would still need to learn fundamentals:
>
> - "It’s like trying to rely on a calculator before you learn how to do addition by hand... and the calculator sometimes misfires. They don’t know enough to debug the stuff coming out, because they still don’t yet have the fundamental problem-solving skills or understand the core programming techniques."
>
> The overall concern was that easy access to ChatGPT could negatively impact student motivation to deeply engage with course material.

Follow-up questions could get expensive as well, since they require re-submitting the entire prompt to Claude every time.

## Everything gets logged

Every prompt and response run through LLM is logged to a SQLite database. You can access the last 3 logged messages with:

```bash
llm logs -n 3
```
Or run [Datasette](https://datasette.io/) against the full log database like this:
```bash
datasette "$(llm logs path)"
```
## Price estimates

I found [this PDF](https://www-files.anthropic.com/production/images/model_pricing_july2023.pdf) of Claude's July 2023 pricing:

- Claude Instant: $1.63/million prompt tokens, $5.51/million completion tokens
- Claude 2: $11.02/million tokens prompt tokens, $32.68/million completion tokens

The [Anthropic logs](https://console.anthropic.com/account/logs) listed my initial prompt (with all of the comments) as 38,254 prompt tokens returning 410 completion tokens.

At those prices ([using Code Interpreter](https://chat.openai.com/share/8ca9d751-d59e-4a15-bd59-183281659dd2) a the world's most-over-powered calculator) that would have cost me:

- $0.06461 or 6.5 cents for Claude Instant
- $0.43496 or 43.5 cents for Claude 2
