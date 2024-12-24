# Named Entity Resolution with dslim/distilbert-NER

I was exploring the original BERT model from 2018, which is mainly useful if you fine-tune a model on top of it for a specific task.

[dslim/distilbert-NER](https://huggingface.co/dslim/distilbert-NER) by David S. Lim is a popular implementation of this, with around 20,000 downloads from Hugging Face every month.

I tried the demo from the README but it didn't quite work - it complained about an incompatibility with Numpy 2.0.

So I used `uv run --with 'numpy<2.0'` to run it in a temporary virtual environment. Here's a Bash one-liner that demonstrated the model:

```bash
uv run --with 'numpy<2.0' --with transformers python -c '
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json
model = AutoModelForTokenClassification.from_pretrained("dslim/distilbert-NER")
tokenizer = AutoTokenizer.from_pretrained("dslim/distilbert-NER")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)
text = "This is an example sentence about Simon Willison who lives in Half Moon Bay"
print(json.dumps(nlp(text), indent=2, default=repr))'
```
The first time you run this it will download 250MB to your `~/.cache/huggingface/hub/models--dslim--distilbert-NER` folder.

Example output:

```json
[
  {
    "entity": "B-PER",
    "score": "0.9982101",
    "index": 7,
    "word": "Simon",
    "start": 34,
    "end": 39
  },
  {
    "entity": "I-PER",
    "score": "0.99835676",
    "index": 8,
    "word": "Willis",
    "start": 40,
    "end": 46
  },
  {
    "entity": "I-PER",
    "score": "0.9977602",
    "index": 9,
    "word": "##on",
    "start": 46,
    "end": 48
  },
  {
    "entity": "B-LOC",
    "score": "0.99432063",
    "index": 13,
    "word": "Half",
    "start": 62,
    "end": 66
  },
  {
    "entity": "I-LOC",
    "score": "0.99325883",
    "index": 14,
    "word": "Moon",
    "start": 67,
    "end": 71
  },
  {
    "entity": "I-LOC",
    "score": "0.9919292",
    "index": 15,
    "word": "Bay",
    "start": 72,
    "end": 75
  }
]
```
