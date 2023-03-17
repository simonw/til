# A simple Python implementation of the ReAct pattern for LLMs

A popular nightmare scenario for AI is giving it access to tools, so it can make API calls and execute its own code and generally break free of the constraints of its initial environment.

Let's do that now!

The ReAct pattern is [described in this paper](https://react-lm.github.io/). It's a pattern where you implement additional actions that an LLM can take - searching Wikipedia or running calculations for example - and then teach it how to request that those actions are run, then feed their results back into the LLM.

Matt Webb wrote a great piece about that here: [The surprising ease and effectiveness of AI in a loop](https://interconnected.org/home/2023/03/16/singularity). In it Matt points out that the 1/10 price reduction on ChatGPT compared to GPT-3 makes it an ideal candidate for cheaply implementing this pattern.

Matt used [langchain](https://github.com/hwchase17/langchain) for his implementation. I decided to try building it from scratch on top of my [tiny Python wrapper](https://til.simonwillison.net/gpt3/chatgpt-api) for the ChatGPT API.

Here's my first attempt at a very rough implementation. It gains access to three new actions:

* `wikipedia: <search term>` - searche Wikipedia and returns the snippet of the first result
* `simon_blog_search: <search term>` - searche my blog and return the truncated text of the first result
* `calculate: <expression>` - evaluate an expression using Python's `eval()` function (so dangerous! This should absolutely use something like [a WebAssembly sandbox](https://til.simonwillison.net/webassembly/python-in-a-wasm-sandbox) instead)

## Some examples

Here are some (very cherry-picked) examples of my `query()` function running, showing the underlying deliberations of the LLM:

```python
query("What does England share borders with?")
```
```
Thought: I should list down the neighboring countries of England
Action: wikipedia: England
PAUSE
 -- running wikipedia England
Observation: <span class="searchmatch">England</span> is a country that is part of the United Kingdom. It shares land borders with Wales to its west and Scotland to its north. The Irish Sea lies northwest
Answer: England shares borders with Wales and Scotland.
```

```python
query("Has Simon been to Madagascar?")
```
```
Thought: I can try and search on Simon's blog or look up Madagascar on Wikipedia to see if Simon has mentioned it in any of his writings.

Action: simon_blog_search: Madagascar

PAUSE
 -- running simon_blog_search Madagascar
Observation: Weeknotes: More releases, more museums: Lots of small releases this week.
Datasette
I released two bug fix releases for Datasette - 0.30.1 and 0.30.2. Changelog here. My Dogsheep personal analytics project means I&#39;m using Datasette for my own data analysis every day, which inspires me to fix small but annoying bugs much more aggressively.
I&#39;ve also set myself a Streak goal to land a commit to Datasette every day.
I landed a tiny new feature to master yesterday: a ?column__notin=x,y,z filter, working as an inverse of the existing ?column__in=x,y,z filter. See issue #614 for details.
More Niche Museums
I&#39;ve been keeping up my streak of adding at least one new museum to www.niche-museums.com every day. This week I added the Pirates Museum in Antananarivo, Madagascar, the David Rumsey Map Center at Stanford, Galerie de Paléontologie et d’Anatomie comparée in Paris, DEVIL-ish Little Things in Vancouver, Washington, Mardi Gras World in New Orleans, Environmental Volunteers EcoCenter in Palo Alto, the Evergreen A
Observation: According to the blog post searched on Simon's blog, he has visited the Pirates Museum in Antananarivo, Madagascar which is listed as a niche museum on www.niche-museums.com.

Answer: Yes, Simon has been to Madagascar and visited the Pirates Museum located in Antananarivo.
```
```python
query("Fifteen * twenty five")
```
```
Thought: The action required is a calculation
Action: calculate: 15 * 25
PAUSE
 -- running calculate 15 * 25
Observation: 375
Answer: Fifteen times twenty five equals 375.
```

## The code

```python
import openai
import re
import httpx

openai.api_key = "sk-..."
 
class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

simon_blog_search:
e.g. simon_blog_search: Django
Search Simon's blog for that term

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
""".strip()


action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=5):
    i = 0
    bot = ChatBot(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


def simon_blog_search(q):
    results = httpx.get("https://datasette.simonwillison.net/simonwillisonblog.json", params={
        "sql": """
        select
          blog_entry.title || ': ' || substr(html_strip_tags(blog_entry.body), 0, 1000) as text,
          blog_entry.created
        from
          blog_entry join blog_entry_fts on blog_entry.rowid = blog_entry_fts.rowid
        where
          blog_entry_fts match escape_fts(:q)
        order by
          blog_entry_fts.rank
        limit
          1""".strip(),
        "_shape": "array",
        "q": q,
    }).json()
    return results[0]["text"]

def calculate(what):
    return eval(what)

known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "simon_blog_search": simon_blog_search
}
```
This is not a very robust implementation at all - there's a ton of room for improvement. But I love how simple it is - it really does just take a few dozen lines of Python to make these extra capabilities available to the LLM and have it start to use them.
