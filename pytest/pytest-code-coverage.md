# Code coverage using pytest and codecov.io

I got my [asgi-csrf](https://github.com/simonw/asgi-csrf) Python package up to 100% code coverage. Here's [the pull request](https://github.com/simonw/asgi-csrf/issues/13).

I started by installing and using the [pytest-cov](https://pypi.org/project/pytest-cov/) pytest plugin.

```
pip install pytest-cov
pytest --cov=asgi_csrf
```
This shows the current code coverage percentage for the `asgi_csrf` module in the terminal output:
```
collected 18 items                                                                                                                                                   

test_asgi_csrf.py ..................                                                                                                                           [100%]

---------- coverage: platform darwin, python 3.7.3-final-0 -----------
Name           Stmts   Miss  Cover
----------------------------------
asgi_csrf.py     169     13    92%


========= 18 passed in 0.37s =========
```
To generate an HTML report showing which lines are not covered by tests:
```
pytest --cov=asgi_csrf --cov-report=html
open htmlcov/index.html
```
Here's a hosted copy of that report: https://asgi-csrf-htmlcov-ewca4t9se.vercel.app/asgi_csrf_py.html

## Failing the tests if coverage is below a certain threshold

The `--cov-fail-under=100` option does this:

```
pytest --cov-fail-under=100 --cov asgi_csrf 
======= test session starts =======
platform darwin -- Python 3.7.3, pytest-6.0.1, py-1.9.0, pluggy-0.13.1
rootdir: /Users/simon/Dropbox/Development/asgi-csrf
plugins: cov-2.10.1, asyncio-0.14.0
collected 18 items                                                                                                                                                   

test_asgi_csrf.py ..................                                                                                                                           [100%]

---------- coverage: platform darwin, python 3.7.3-final-0 -----------
Name           Stmts   Miss  Cover
----------------------------------
asgi_csrf.py     169     13    92%

FAIL Required test coverage of 100% not reached. Total coverage: 92.31%
```
I added this to my [GitHub test action](https://github.com/simonw/asgi-csrf/blob/83d2b4f6bb034b746fd3f20f57ebdbaeae007a73/.github/workflows/test.yml#L27-L29):
```yaml
    - name: Run tests
      run: |
        pytest --cov-fail-under=100 --cov asgi_csrf
```
## Pushing results to codecov.io

https://codecov.io/ offers free coverage reporting for open source projects. I authorized it against my GitHub account, then enabled it for the `asgi-csrf` project by navigating to https://codecov.io/gh/simonw/asgi-csrf (hacking the URL saves you from having to paginate through all of your repos looking for the right one).

codecov.io gives you a token - set that as a GitHub repository secret as `CODECOV_TOKEN` - then add the following to the test action configuration:
```yaml
    - name: Upload coverage to codecov.io
      run: bash <(curl -s https://codecov.io/bash)
      if: always()
      env:
        CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```
This will upload your coverage report (no matter if the previous test step failed or succeeded). codecove.io then reports back to pull requests and maintains a dashboard for your project.

codecov.io doesn't detect if you use a `main` or `master` branch so I had to switch the default branch in the settings at https://codecov.io/gh/simonw/asgi-csrf/settings

I also added their badge to my project README, using the following Markdown:
```
[![codecov](https://codecov.io/gh/simonw/asgi-csrf/branch/main/graph/badge.svg)](https://codecov.io/gh/simonw/asgi-csrf)
```
