# Configuring Dependabot for a Python project with dependencies in setup.py

The [Dependabot setup instructions](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates) don't explicitly mention projects which keep all of their dependency information in `setup.py`.

It works just fine with those kinds of projects. To start it working, create a file in `.github/dependabot.yml` with the following contents:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
```
Then navigate to https://github.com/simonw/s3-credentials/network/updates (but for your project) - that's Insights -> Dependency graph -> Dependabot - to confirm that it worked.
