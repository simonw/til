# Testing against Python 3.11 preview using GitHub Actions

I decided to run my CI tests against the Python 3.11 preview, to avoid the problem I had when Python 3.10 came out with [a bug that affected Datasette](https://simonwillison.net/2021/Oct/9/finding-and-reporting-a-bug/).

I used the new [GitHub Code Search](https://cs.github.com/) to figure out how to do this. I searched for:

    3.11 path:workflows/*.yml

And found [this example](https://github.com/urllib3/urllib3/blob/7bec77e81aa0a194c98381053225813f5347c9d2/.github/workflows/ci.yml#L60) from `urllib3` which showed that the version tag to use is:

    3.11-dev

> **Update 28th Noveber 2022**: `3.12-dev` now works for Python 3.12 preview

I added that to my test matrix like so:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.7", "3.8", "3.9", "3.10", "3.11-dev"]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    # ...
```
Here's the [full workflow](https://github.com/simonw/datasette/blob/a9d8824617268c4d214dd3be2174ac452044f737/.github/workflows/test.yml).

