# Open a debugging shell in GitHub Actions with tmate

> :warning: **17 Feb 2022: There have been reports of running tmate causing account suspensions**. See [this issue](https://github.com/mxschmitt/action-tmate/issues/104) for details. Continue with caution.
>
> **23 Sep 2023**: I've been using this trick very occasionally for nearly two years now without negative consequences.

Thanks to [this Twitter conversation](https://twitter.com/harrymarr/status/1304820879268950021) I found out about [mxschmitt/action-tmate](https://github.com/mxschmitt/action-tmate), which uses https://tmate.io/ to open an interactive shell session running inside the GitHub Actions environment.

I created a `.github/workflows/tmate.yml` file in my repo containing the following:

```yaml
name: tmate session

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup tmate session
      uses: mxschmitt/action-tmate@v3
```
Clicking the "Run workflow" button in the GitHub Actions interface then gave me the following in the GitHub Actions log output:
```
WebURL: https://tmate.io/t/JA69KaB2avRPRZSkRb8JPa9Gd

SSH: ssh JA69KaB2avRPRZSkRb8JPa9Gd@nyc1.tmate.io
```
I ran `ssh JA69KaB2avRPRZSkRb8JPa9Gd@nyc1.tmate.io` and got a direction connection to the Action, with my project files all available thanks to the `- uses: actions/checkout@v2` step.

Once I'd finish testing things out in that environment, I typed `touch continue` and the session ended itself.

## Starting a shell just for test failures on manual runs

I had a tricky test failure that I wanted to debug interactively. Here's a recipe for starting a tmate shell ONLY if the previous step failed, and only if the run was triggered manually (using `workflow_dispatch`) - because I don't want an accidental test opening up a shell and burning up my GitHub Actions minutes allowance.

```yaml
    steps:
    - name: Run tests
      run: pytest
    - name: tmate session if tests fail
      if: failure() && github.event_name == 'workflow_dispatch'
      uses: mxschmitt/action-tmate@v3
```
