# Quickly testing code in a different Python version using pyenv

I had [a bug](https://github.com/simonw/llm/issues/82#issuecomment-1629735729) that was only showing up in CI against Python 3.8.

I used the following pattern with [pyenv](https://github.com/pyenv/pyenv) to quickly run the tests against that specific version.

(I had previously installed `pyenv` using `brew install pyenv`.)

## Seeing what versions I had already

```bash
pyenv versions
```
This outputs (on my machine):
```
  system
  3.7.16
  3.8.17
```
To see all possible versions:
```bash
pyenv install --list
```
That's a long list! I grepped it for 3.8:
```bash
pyenv install --list | grep '3.8'
```
```
  3.8.0
  3.8-dev
  3.8.1
  3.8.2
  ...
  3.8.14
  3.8.15
  3.8.16
  3.8.17
  ...
```
## Installing a specific version

I installed 3.8.17 like this:
```bash
pyenv install 3.8.17
```
This took a long time, because it compiled it from scratch.

## Using that version via a virtual environment

I decided to use that version of Python directly. The binary was installed here:
```bash
~/.pyenv/versions/3.8.17/bin/python
```
I created a temporary virtual environment in `/tmp` like this:
```bash
~/.pyenv/versions/3.8.17/bin/python -m venv /tmp/py38env
```
Then installed my current project into that environment like so:
```bash
/tmp/py38env/bin/pip install -e '.[test]'
```
Now I can run the tests like this:
```bash
/tmp/py38env/bin/pytest
```
