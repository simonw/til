# actions/setup-python caching for setup.py projects

I used to use a combination of `actions/setup-python` and `actions/cache` in all of my Python GitHub Actions projects in order to install Python dependencies via a cache, rather than hitting PyPI to download copies every time.

[actions/setup-python added built-in caching](https://github.com/actions/setup-python#caching-packages-dependencies) a while ago, but it wasn't obvious to me from the documentation how I could use that with `setup.py` based projects (as opposed to projects that install dependencies via `Pipfile` or `requirements.txt`).

The trick is to use `cache: pip` and `cache-dependency-path: setup.py` as arguments to the `actions/setup-python` action.

Here's the pattern I found that works:

```yaml
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: pip
        cache-dependency-path: setup.py
    - name: Install dependencies
      run: |
        pip install -e '.[test]'
```

And here's a full `.github/workflows/test.yml` configuration that uses a matrix to run tests against five currently supported Python versions:

```yaml
name: Test

on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.7", "3.8", "3.9", "3.10", "3.11"]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: pip
        cache-dependency-path: setup.py
    - name: Install dependencies
      run: |
        pip install -e '.[test]'
    - name: Run tests
      run: |
        pytest
```
I updated my various cookiecutter templates to use this new pattern in [this issue](https://github.com/simonw/click-app/issues/6).
