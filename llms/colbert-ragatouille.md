# Exploring ColBERT with RAGatouille

I've been trying to get my head around [ColBERT](https://github.com/stanford-futuredata/ColBERT).

> ColBERT is a fast and accurate retrieval model, enabling scalable BERT-based search over large text collections in tens of milliseconds.

But what does that mean?

I understand [embedding models](https://simonwillison.net/2023/Oct/23/embeddings/) pretty well now. They let you take some text and turn that into a fixed length array of floating point numbers, which can then be checked for cosine similarity against other such arrays to find content that is semantically similar.

ColBERT doesn't exactly fit my mental model here. After some [back and forth on Twitter](https://twitter.com/simonw/status/1751411977279390141) with Mark Tenenholtz I think I understand how it differs now.

With a regular embedding model you store a single vector for each document, and get back a single numeric score showing how well that document matches your query.

ColBERT is slightly different: it provides a list of vectors showing how each token in the query matches up with each token in the document.

This image [by Jo Kristian Bergum](https://twitter.com/jobergum/status/1751640310642360694) really helped me understand why this is useful:

![ColBERT query-passage scoring interpretability.  Query: Effects of climate change on marine ecosystems. Passage: The changing climate has profound impacts on marine ecosystems. Rising temperatures, ocean acidification, and altered precipitation patterns all contribute to shifts in the distribution and behavior of marine species, influencing the delicate balance of underwater ecosystems. MaxSim Score: 27.71. Estimated Relevance: 86.60%. Contextualised Highlights: The changing climate (those two words in bold) has profound impacts (bold) on marine ecosystems (two bold words). Rising temperatures, ocean acidification, and altered (slight bold) precipitation patterns all contribute to shifts in the distribution and behavior of marine (big bold) species (bold), influencing the delicate balance of under water ecosystems (3 words in bold).](https://static.simonwillison.net/static/2024/colbert-vis-2.jpg)

That's from [colbert.aiserv.cloud](https://colbert.aiserv.cloud/), a really neat visualization tool which loads a ColBERT model directly in the browser and uses it to show highlighted text matches.

ColBERT clearly provides more information than a regular embedding search, because it can show you which of the words in the document are most relevant.

Most ColBERT implementations don't directly visualize the data in that way, but this extra information still plays into its ability to retrieve the best documents. [Mark explained](https://twitter.com/marktenenholtz/status/1751415287709102088):

> At a high level:
>
> You embed the query and the passage and get vector representation for every token in both.
>
> Then, for each query token, you find the token in the passage with the largest dot product (i.e. the largest similarity). This is called the “maxsim” for each token
>
> Finally, the similarity score between the query and the passage is the summation of all the maxsims you just found

## RAGatouille

[RAGatouille](https://github.com/bclavie/RAGatouille) is a relatively new library that aims to make it easier to work with ColBERT.

It's still pretty early, and getting it running on my Mac took a couple of attempts. I believe if you have an NVIDIA GPU it can use PyTorch to both run faster and to provide the ability to train a custom ColBERT model, but that's not necessary to start using ColBERT with a pre-trained model.

I found I needed Python 3.11 - Torch isn't yet available in an easy installed package for Python 3.12.

I ran `pip install ragatouille sqlite-utils` and created a new ColBERT index of the content from my blog using the following Python script:

```python
from ragatouille import RAGPretrainedModel
import re
import sqlite_utils

_tags_re = re.compile(r'<[^>]+>')

def strip_html_tags(text):
    return _tags_re.sub('', text)

def go():
    db = sqlite_utils.Database("simonwillisonblog.db")
    rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
    entries = list(db["blog_entry"].rows)
    entry_texts = [
        entry["title"] + '\n' + strip_html_tags(entry["body"])
        for entry in entries
    ]
    print("len of entry_texts is", len(entry_texts))
    entry_ids = [str(entry["id"]) for entry in entries]
    entry_metadatas = [
        {"slug": entry["slug"], "created": entry["created"]} for entry in entries
    ]
    rag.index(
        collection=entry_texts,
        document_ids=entry_ids,
        document_metadatas=entry_metadatas,
        index_name="blog", 
        max_document_length=180, 
        split_documents=True
    )


if __name__ == "__main__":
    go()
```
I downloaded the 81.7MB `simonwillisonblog.db` file [from the bottom of this page](https://datasette.simonwillison.net/simonwillisonblog).

The above code is lightly adapted from an example in the README. A few important details:

```python
rag = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
```
This loads the pre-trained ColBERT model. The first time this code runs it downloads a pretty large model file - around 419MB. This is stored in `~/.cache/huggingface/hub/models--colbert-ir--colbertv2.0`.

```python
rag.index(
    collection=entry_texts,
    document_ids=entry_ids,
    document_metadatas=entry_metadatas,
    index_name="blog", 
    max_document_length=180, 
    split_documents=True
)
```
This does all of the work. `entry_texts` is a list of strings (the content of my posts), `entry_ids` is a list of text IDs for them and `entry_metadatas` is a list of dictionaries containing metadata for each post.

Running this command took several minutes and used a LOT of CPU and RAM - Activity Monitory showed 380% CPU usage and over 2GB of RAM.

The end result was a folder in the working directory for my script, `.ragatouille/colbert/indexes/blog` - containing 91MB of files:
```
4.5M 0.codes.pt
112B 0.metadata.json
 73M 0.residuals.pt
1.2K avg_residual.pt
1.5K buckets.pt
4.0M centroids.pt
6.0M collection.json
266K docid_metadata_map.json
 36K doclens.0.json
2.8M ivf.pid.pt
3.4K metadata.json
160K pid_docid_map.json
3.4K plan.json
```
Those `.pt` files are PyTorch tensors. ChatGPT helped me come up with this `zsh` code to describe them:

```zsh
for file in *.pt; do
    echo $file
    python -c "print(__import__('torch').load('$file').shape)"
done
```
The output of that was:
```
0.codes.pt
torch.Size([1192394])
0.residuals.pt
torch.Size([1192394, 64])
avg_residual.pt
torch.Size([])
buckets.pt
AttributeError: 'tuple' object has no attribute 'shape'
centroids.pt
torch.Size([16384, 128])
ivf.pid.pt
AttributeError: 'tuple' object has no attribute 'shape'
```
So the index incorporates various 1D and 2D matrices of floating point numbers. Definitely more complex than a single floating point vector per indexed document!

## Querying the index

I queried the index using the Python interpreter like this:

```python
from ragatouille import RAGPretrainedModel
rag = RAGPretrainedModel.from_index(".ragatouille/colbert/indexes/blog/")
docs = rag.search("what is shot scraper?")
```
That `.from_index()` line takes a few seconds to run the first time, but subsequent search queries once it has loaded into memory are _really_ fast. It seems to use around 1GB of RAM on my machine.

`docs` is now an array of 10 dictionaries. They look like this (truncated a bit):

```json
[
  {
    "content": "Running this:\r\n./blog-answer.sh 'What is shot-scraper?'\r\nOutputs this:\r\n\r\nShot-scraper is a Python u...",
    "document_id": "8296",
    "document_metadata": {
      "created": "2023-10-23T13:36:21+00:00",
      "slug": "embeddings"
    },
    "rank": 1,
    "score": 27.532695770263672
  },
  {
    "content": "I can ask questions like \"what is shot-scraper?\" - it's a piece of software I wrote. And the model k...",
    "document_id": "8285",
    "document_metadata": {
      "created": "2023-08-27T14:35:07+00:00",
      "slug": "wordcamp-llms"
    },
    "rank": 2,
    "score": 27.147775650024414
  },
  {
    "content": "First, some demos\r\nI've implemented this pattern against my blog - 3,000 posts going back over twent...",
    "document_id": "8222",
    "document_metadata": {
      "created": "2023-01-13T23:47:30+00:00",
      "slug": "semantic-search-answers"
    },
    "rank": 3,
    "score": 26.7896728515625
  }
]
```
This looks pretty good! The returned items definitely look relevant to my query.

I implemented a very quick and dirty question answering mechanism by running this:

```python
open("/tmp/out.txt", "w").write(
    ' '.join([d['content']
    for d in rag.search("what is shot scraper?")]
))
```
And then running [LLM](https://llm.datasette.io/) in a separate terminal like this:

```bash
cat /tmp/out.txt | llm -m gpt-4-turbo --system 'what is shot-scraper?'
```
Here's the (surprisingly lengthy) result. You can see the [/tmp/out.txt context here](https://gist.githubusercontent.com/simonw/5b94c7a8f26e5470e648990f96c41dc8/raw/cf6a0750306a92efb66f785c73acf9c32822bb07/out.txt).

> Shot-scraper is a versatile and powerful command-line utility developed to automate the process of capturing screenshots of web pages as well as scraping data from them using JavaScript. Built upon the Playwright framework, it offers a simple yet effective approach to automatically grab visual snapshots of web content which can be particularly useful for documentation, monitoring website changes, or capturing dynamic web content for analysis.
> 
> The tool offers dual functionality:
> 1. **Screenshot capture:** Shot-scraper enables users to take screenshots of web pages either as one-off snapshots or by specifying multiple screens to capture in a systematic way through a YAML configuration file. This feature is crucial for developers and content creators who require up-to-date visuals of websites for documentation, tutorials, or quality assurance purposes.
>    
> 2. **Data scraping:** Beyond capturing images, shot-scraper can execute JavaScript on a webpage, allowing users to scrape and extract data dynamically. This is incredibly useful for gathering information from websites where data is rendered or altered through client-side scripts, making traditional scraping methods ineffective.
> 
> It also introduces user-friendly features such as specifying browser options and timeout settings, catering to various needs and enhancing its flexibility. This capacity to combine automated screenshot capture with the execution of JavaScript for data retrieval sets shot-scraper apart as a comprehensive tool for web content capture and analysis.
> 
> The utility is designed with ease of use in mind, featuring both a command-line interface for direct interaction and a YAML-driven configuration mechanism that enables users to define complex screenshot capture scenarios in a reusable manner. This makes it an ideal tool for automating the capture of website screenshots for projects that require consistent and repeatable captures, such as generating up-to-date images for documentation or monitoring visual changes on web pages over time.
> 
> Moreover, the introduction of shot-scraper and its subsequent versions, with added features like custom browser support and improved options for handling timeouts, illustrates its developer's commitment to evolving the tool in response to user needs and practical use cases, such as capturing content that requires specific browser capabilities.
> 
> In summary, shot-scraper bridges the gap between simple screenshot tools and complex web scraping solutions by offering a unified, scriptable interface that leverages the capabilities of Playwright to automate the capture and extraction of web content in a versatile and efficient manner.

## Re-ranking

I spotted one more interesting trick in the RAGatouille examples: [a notebook about reranking queries](https://github.com/bclavie/RAGatouille/blob/main/examples/04-reranking.ipynb).

This is a trick that works without building an index at all. Effectively it lets you run retrieval against some other index - a regular embedding model, or even full-text search - and thn re-rank the results using ColBERT.

I tried that with some documents I had previously loaded for a "What is Datasette?" query like this:

```python
# A fresh colbert with no knowledge of my index
colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
docs = colbert.rerank(query='What is Datasette Lite?', documents=[
    d['content'] for d in docs
], k=5)
```
Effectively I'm asking it for the five most relevant matches to the term "What is Datasette Lite?" from an arbitrary array of strings.

This seems to work really well, and I like that it sidesteps the complex and computationally expensive step of building an index in the first place.

That re-ranking ran in 0.47s against my test set of 10 documents. I imagine it's a lot faster when run against a CUDA GPU.
