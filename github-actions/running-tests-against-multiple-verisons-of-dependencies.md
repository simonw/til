# Running tests against multiple versions of a Python dependency in GitHub Actions

My [datasette-export-notebook](https://github.com/simonw/datasette-export-notebook) plugin worked fine in the stable release of Datasette, currently version [0.64.3](https://docs.datasette.io/en/stable/changelog.html#v0-64-3), but failed in the Datasette 1.0 alphas. Here's the [issue describing the problem](https://github.com/simonw/datasette-export-notebook/issues/17).

Here's the pattern I figured out for running the tests in GitHub Actions against both Datasette versions. This is my full `test.yml` from that repository:

```yaml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
        datasette-version: ["<=1.0a0", ">=1.0a0"]
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
        pip install 'datasette${{ matrix.datasette-version }}'
    - name: Run tests
      run: |
        pytest
```
The trick here is to set up a matrix for `datasette-version` (to accompany my existing `python-version` one) defining these two installation specifiers:

```
datasette-version: ["<=1.0a0", ">=1.0a0"]
```
Then later I use those to install the specified version of Datasette like this:

```
pip install 'datasette${{ matrix.datasette-version }}'
```
The single quotes there are important - without them my shell got confused by the `<=` and `>=` symbols.

The end result of this is that tests run against the highest Datasette release in the `0.x` series, and also against the highest release in the `1.x` series, including alphas if no `1.x` stable release is out yet.
