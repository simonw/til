# Configuring Dependabot for a Python project

GitHub's Dependabot can automatically file PRs with bumps to dependencies when new versions of them are available.

In June 2023 they added support for [Grouped version updates](https://github.blog/changelog/2023-06-30-grouped-version-updates-for-dependabot-public-beta/), so one PR will be filed that updates multiple dependencies at the same time.

The [Dependabot setup instructions](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates) don't explicitly mention projects which keep all of their dependency information in `setup.py`.

It works just fine with those kinds of projects too.

To start it working, create a file in `.github/dependabot.yml` with the following contents:

```yaml
version: 2
updates:
- package-ecosystem: pip
  directory: "/"
  schedule:
    interval: daily
    time: "13:00"
  groups:
    python-packages:
      patterns:
        - "*"
```
Then navigate to https://github.com/simonw/s3-credentials/network/updates (but for your project) - that's Insights -> Dependency graph -> Dependabot - to confirm that it worked.

This should work for projects that use `setup.py` or `pyproject.toml` or `requirements.txt`.
