# Publish releases to PyPI from GitHub Actions without a password or token

I published a package to [PyPI](https://pypi.org) today using their [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) mechanism for the first time.

Trusted Publishers provides a mechanism for configuring PyPI to allow a specific GitHub Actions workflow to publish releases to PyPI without needing to use a password or token.

It's based on OpenID Connect, but you don't need to know the details of that at all.

It took me [a few iterations](https://github.com/datasette/datasette-build/issues/9) to get it to work, but now that I've done it once I plan to use it for all of my PyPI packages going forward.

It only takes three steps:

1. Tell PyPI which GitHub repository should be allowed to publish a package with a specific name
2. Configure a GitHub Actions publish workflow to use the `pypa/gh-action-pypi-publish@release/v1` action
3. Publish a release to GitHub that triggers the workflow

In the past I've had to create a token on PyPI and paste it into a GitHub Actions secret. That's no longer necessary with this approach.

## Adding a new trusted publisher on PyPI

This process differs slightly depending on if you are planning on publishing a brand new package or updating an existing one to use Trusted Publishers going forward.

I haven't tried updating an existing package yet, but [the instructions for that are here](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).

When publishing a brand new package you can instead use [a special mechanism called "pending publishers"](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).

This also lets you reserve a package name before you publish the first version. I like this - in the past I've attempted to publish a package only to discover that someone else had already reserved a too-similar name.

You can create a new pending publisher from this page: https://pypi.org/manage/account/publishing/

You need to provide the PyPI project name, the GitHub repository owner and name, the workflow name (the name of a YAML file) and an optional environment name.

Here's how I filled out that form for my new [datasette/datasette-build](https://github.com/datasette/datasette-build) repository:

![GitHub. Read more about GitHub Actions's OpenID Connect support here. PyPI Project Name (required): datasette-build. The project (on PyPI) that will be created when this publisher is used. Owner (required): datasette. The GitHub organization name or GitHub username that owns the repository. Repository name (required): datasette-build. The name of the GitHub repository that contains the publishing workflow. Workflow name (required): publish.ym! The filename of the publishing workflow. This file should exist in the github/workflows/ directory in the repository configured above. Environment name (optional): release. The name of the GitHub Actions environment that the above workflow uses for publishing. This should be configured under the repository's settings. While not required, a dedicated publishing environment is strongly encouraged, especially if your repository has maintainers with commit access who shouldn't have PyPI publishing access.](https://static.simonwillison.net/static/2024/datasette-build-pending.png)

I used `publish.yml` as the name of my workflow file.

I also set the environment to `release`. I don't fully understand [GitHub Actions environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) yet, but the PyPI documentation suggested this was a good idea and I think it gives me more flexibility for setting extra permissions in the future.

PyPI says:

> While not required, a dedicated publishing environment is strongly encouraged, especially if your repository has maintainers with commit access who shouldn't have PyPl publishing access.

## Creating the GitHub Actions environment

Since we specified the environment on PyPI we need to create that environment. That can be done in the settings area for the repository - in my case that page was here:

https://github.com/datasette/datasette-build/settings/environments/new

Environments just have a name. I called mine `release`.

## Configuring the workflow

This took me the most time to figure out. I already have a `publish.yml` workflow I use for my other projects, which uses `twine` and a PyPI token to upload packages, after first running the tests.

Here's [the workflow](https://github.com/datasette/datasette-build/blob/main/.github/workflows/publish.yml) I eventually landed, in `.github/workflows/publish.yml`:

```yaml
name: Publish Python Package

on:
  release:
    types: [created]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: pip
        cache-dependency-path: '**/pyproject.toml'
    - name: Install dependencies
      run: |
        pip install -e '.[test]'
    - name: Run tests
      run: |
        pytest
  deploy:
    runs-on: ubuntu-latest
    needs: [test]
    environment: release
    permissions:
      id-token: write
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: pip
        cache-dependency-path: '**/pyproject.toml'
    - name: Install dependencies
      run: |
        pip install setuptools wheel build
    - name: Build
      run: |
        python -m build
    - name: Publish
      uses: pypa/gh-action-pypi-publish@release/v1
```
The `test` job is pretty standard - it sets up a matrix to run the tests against multiple Python versions, then runs `pytest`.

It's set to trigger by this block:
```yaml
on:
  release:
    types: [created]
```
This ensures the workflow runs any time a new GitHub release is created for the repository.

Where things get interesting is the `deploy` job. It runs `python -m build` to build the `.tar.gz` and `.whl` files, then uses the `pypa/gh-action-pypi-publish@release/v1` action to publish the package.

Breaking that down a bit:

```yaml
  deploy:
    runs-on: ubuntu-latest
    needs: [test]
    environment: release
    permissions:
      id-token: write
```
The `environment: release` key is needed because we configured an environment in PyPI. I think that can be omitted entirely if the PyPI environment field was left blank.

The `permissions` block there is essential - it's required for the OpenID Connect token authentication to work.

`needs: [test]` means that this job waits for the `test` job to pass before it runs.

```yaml
    - name: Publish
      uses: pypa/gh-action-pypi-publish@release/v1
```
This is the key line. It uses the [pypa/gh-action-pypi-publish](https://pypa/gh-action-pypi-publish) action to publish the package.

Note that it doesn't need any settings - it just works, provided the trusted publisher on PyPI has been configured.

## Publishing a release

With all this in place, all that's needed to ship a package is to ensure the `version` is set correctly in the `pyproject.toml` file (or `setup.py` file if you're using that instead), then create a new release on GitHub.

For my repo I create a release using this form: https://github.com/datasette/datasette-build/releases/new

Creating the release triggers the workflow, which runs the tests, builds the package and then publishes it to PyPI.

Here's the resulting package: [pypi.org/project/datasette-build/](https://pypi.org/project/datasette-build/)
