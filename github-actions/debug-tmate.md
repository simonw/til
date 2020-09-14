# Open a debugging shell in GitHub Actions with tmate

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
