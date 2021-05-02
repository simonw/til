# Running Datasette on Replit

I figured out how to run Datasette on https://replit.com/

The trick is to start a new Python project and then drop the following into the `main.py` file:

```python
import uvicorn
from datasette.app import Datasette

ds = Datasette(memory=True, files=[])


if __name__ == "__main__":
    uvicorn.run(ds.app(), host="0.0.0.0", port=8000)
```
Replit is smart enough to automatically create a `pyproject.toml` file with `datasette` and `uvicorn` as dependencies. It will also notice that the application is running on port 8000 and set `https://name-of-prject.your-username.repl.co` to proxy to that port. Plus it will restart the server any time it recieves new traffic (and pause it in between groups of requests).

To serve a database file, download it using `wget` in the Replit console and add it to the `files=[]` argument. I ran this:

    wget https://datasette.io/content.db

Then changed that first line to:

```python
ds = Datasette(files=["content.db"])
```
And restarted the server.
