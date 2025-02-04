# Running pytest against a specific Python version with uv run

While [working on this issue](https://github.com/simonw/datasette/issues/2461) I figured out a neat pattern for running the tests for my project locally against a specific Python version using [uv run](https://docs.astral.sh/uv/guides/scripts/):

```bash
uv run --python 3.12 --with '.[test]' pytest
```
The new-to-me trick here is that `--with '.[test]` works for adding the project dependencies _and_ the test dependencies from the `setup.py` or `pyproject.toml` file in the current project directory.

This makes it trivial to try running the test suite against different Python versions on demand without needing to worry about manually creating a virtual environment for each one.

This pattern works for more complex scenarios too. My project's GitHub Actions CI runs an additional variant that uses the `pytest-cov` plugin to generate coverage reports. I could simulate that locally by including that as another `--with pytest-cov` option - here I'm also adding the `-Werror` flag so any warnings would be treated as errors:

```bash
uv run --python 3.12 \
  --with pytest-cov \
  --with '.[test]' pytest \
    -Werror \
    --cov=datasette \
    --cov-config=.coveragerc \
    --cov-report xml:coverage.xml \
    --cov-report term  
```
