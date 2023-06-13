# Running OpenAI's large context models using llm

OpenAI [announced new models](https://openai.com/blog/function-calling-and-other-api-updates) today. Of particular interest to me is the new `gpt-3.5-turbo-16k` model, which provides GPT 3.5 with a 16,000 token context window (up from 4,000) priced at 1/10th of GPT-4 - $0.003 per 1K input tokens and $0.004 per 1K output tokens.

I couldn't see that model listed in the GPT Playground interface, but it turns out I did have access to it via the API. This worked for me using my [llm](https://github.com/simonw/llm) tool (see [llm, ttok and strip-tags—CLI tools for working with ChatGPT and other LLMs](https://simonwillison.net/2023/May/18/cli-tools-for-llms/)).

```
curl -s 'https://simonwillison.net/' | strip-tags -m | llm --system 'Summarize' -s
```
This returns an error:

> This model's maximum context length is 4097 tokens. However, your messages resulted in 15038 tokens. Please reduce the length of the messages.

But... specifying `-m gpt-3.5-turbo-16k` fixes that:

```
curl -s 'https://simonwillison.net/' | strip-tags -m | llm --system 'Summarize' -s -m gpt-3.5-turbo-16k
```

> Simon Willison’s Weblog is a website where Simon Willison, a software engineer and entrepreneur, shares his thoughts and experiences on various topics related to web development, data management, and technology. In his recent entries, he discusses topics such as understanding GPT tokenizers, the challenges of working with closed models' training data, and the use of command-line tools for working with ChatGPT and other language models. Simon also shares updates on his own projects, including building tools for working with tokens, stripping HTML tags, and sending prompts to the OpenAI API. Overall, Simon's weblog provides valuable insights and resources for anyone interested in web development and working with language models.

## And that works for gpt-4-32k-0613 too

I thought I didn't have access to GPT-4 with the 32,000 token context (a much more expensive model) because it never showed up for me in the Playground. But it turns out I do have access to that, and this works:

```bash
curl -s 'https://railsatscale.com/2023-06-12-rewriting-the-ruby-parser/' | strip-tags -m | \
  llm --system 'summarize as bullets' -m 'gpt-4-32k-0613' -s
```
Output (which cost me about 6 cents):

> - Shopify has been developing a new Ruby parser called YARP (Yet Another Ruby Parser), which can parse a semantically equivalent syntax tree to Ruby 3.3 on every Ruby file in Shopify’s codebase, GitHub’s main codebase, CRuby, and the top 100 most popular gems downloaded from rubygems.org.
> - The project tackled four main issues with the current CRuby parser: insufficient maintainability, suboptimal error tolerance, portability limitations, and inadequate performance. 
> - YARP is designed to be easier to maintain, with extensive documentation and testing, and a more tolerant design that allows for ongoing parsing even in the presence of syntax errors.
> - The new parser is entirely self-contained, making it more portable and capable of being used outside of the CRuby base.
> - Performance improvements are underway for YARP, which currently parses around 50,000 of Shopify’s Ruby files in approximately 4.49 seconds, using a maximum of 10.94 Mb of memory. 
> - Shopify has begun integrating YARP into other runtimes and tools to validate its design, and has experimented in generating the same syntax tree as the parser and ruby_parser gems for compatibility across tools. 
> - The company plans to focus on several improvements, including error tolerance, memory usage, and performance. They also plan to release YARP as a library with Ruby 3.3.
