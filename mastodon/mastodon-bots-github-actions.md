# Building Mastodon bots with GitHub Actions and toot

Twitter announced today that they'll be ending free API access for bots.

My [@covidsewage](https://twitter.com/covidsewage) Twitter bot posts a screenshot of the latest Covid sewage data for parts of the San Francisco Bay Area every morning. I decided to port it to Mastodon.

It's now up and running in its new home at https://fedi.simonwillison.net/@covidsewage - here's how the new bot works.

## toot - a Mastodon command line client

The bot uses [toot](https://toot.readthedocs.io/) to send a message with an attached image to Mastodon.

Here's the command that does that:
```
toot post "Latest Covid sewage charts for the SF Bay Area https://covid19.sccgov.org/dashboard-wastewater" \
  --media /tmp/covid.png \
  --description "Screenshot of the latest Covid charts"
```
You can pass the combination of `--media` and `--description` up to four times.

The alt text here is terrible - I've had an [open issue to fix that](https://github.com/simonw/covidsewage-bot/issues/2) for a while, but it's not an easy thing to implement properly.

## Authentication

The `toot post` command only works if you authenticate first.

Toot authentication is _really nice_. All you have to do is run:

```
toot auth
```
It will ask for your Mastodon instance (my private one is `fedi.simonwillison.net`) and spit out a link to click on.

Click that link and your Mastodon server will ask you if you want to authorize the tool.

If you say yes, it gives you an authorization code which you then paste back into the command.

Toot then creates a file in `~/.config/toot/config.json`. My file (redacted) looks like this:

```json
{
 "active_user": "covidsewage@fedi.simonwillison.net",
 "apps": {
  "fedi.simonwillison.net": {
   "base_url": "https://fedi.simonwillison.net",
   "client_id": "cTQfcJy9EhlIUSGPRx90PRnMx_RroBuLUw8WcMvguD0",
   "client_secret": "... redacted ...",
   "instance": "fedi.simonwillison.net"
  }
 },
 "users": {
  "covidsewage@fedi.simonwillison.net": {
   "access_token": "... redacted ...",
   "instance": "fedi.simonwillison.net",
   "username": "covidsewage"
  }
 }
}
```
Toot can support multiple authenticated users and let you switch between them, but for this bot we just need the one.

## Taking the screenshot

I'm using my [shot-scraper](https://shot-scraper.datasette.io/) tool to take the screenshot, like this:

```
shot-scraper https://covid19.sccgov.org/dashboard-wastewater \
  -s iframe \
  --wait 3000 \
  -b firefox \
  --retina \
  -o /tmp/covid.png
```
This loads the https://covid19.sccgov.org/dashboard-wastewater page in a headless (no visible window) Firefox instance. It waits 3 seconds, then takes a screenshot of JUST the first `iframe` on the page (`-s` means "selector").

The screenshot is taken in retina mode (2x the pixel density) and saved to a file called `/tmp/covid.png`.

Read more about `shot-scraper` in [shot-scraper: automated screenshots for documentation, built on Playwright](https://simonwillison.net/2022/Mar/10/shot-scraper/).

## Running this in GitHub Actions

My entire bot is implemented as a GitHub Actions scheduled workflow.

The workflow runs once a day and does the following:

1. Installs its dependencies (`shot-scraper` and `toot`)
2. Takes the screenshot and writes it to a temporary file
3. Creates that `~/.config/toot/config.json` file from a GitHub Actions secret
4. Uses `toot post` to post that screenshot to Mastodon
5. Writes [this file](https://github.com/simonw/covidsewage-bot/blob/main/latest-toot.md) back to the GitHub repository so I can see when it last ran.

I pasted the entire JSON authentication file into a new Actions secret for the repository called `MASTODON_TOOT_CONFIG`.

Here's [the workflow file](https://github.com/simonw/covidsewage-bot/blob/main/.github/workflows/toot.yml):

```yaml
name: Toot

on:
  # Run when I click "run workflow"
  # in the GitHub UI - for debugging
  workflow_dispatch:
  schedule:
  # Run at 14:13 UTC every day
  # which is 6:13am Pacific time
  - cron: '13 14 * * *'

jobs:
  scheduled:
    runs-on: ubuntu-latest
    steps:
    - name: Check out this repo
      uses: actions/checkout@v3
      with:
        fetch-depth: 0
    - name: Configure Python with pip cache
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
        cache: 'pip'
    # shot-scraper uses Playwright, which
    # needs to download a custom copy of
    # Firefox. We cache this here so it
    # isn't downloaded every time we run.
    - name: Cache Playwright browsers
      uses: actions/cache@v3
      with:
        path: ~/.cache/ms-playwright/
        key: ${{ runner.os }}-browsers
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Install Playwright browser
      run: |
        shot-scraper install -b firefox
    - name: Configure Git for commits
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
    - name: Generate screenshot with shot-scraper
      # This screenshots the first iframe
      # on the page after a 3s wait
      run: |-
        shot-scraper https://covid19.sccgov.org/dashboard-wastewater \
          -s iframe --wait 3000 -b firefox --retina -o /tmp/covid.png
    - name: Toot the new image
      env:
        TOOT_CONFIG: ${{ secrets.MASTODON_TOOT_CONFIG }}
      # Write that JSON to the config file
      run: |-
        mkdir -p ~/.config/toot
        echo $TOOT_CONFIG > ~/.config/toot/config.json
        toot post "Latest Covid sewage charts for the SF Bay Area https://covid19.sccgov.org/dashboard-wastewater" \
          --media /tmp/covid.png --description "Screenshot of the latest Covid charts" > latest-toot.md
    # So we can see what it last did:
    - name: Commit latest-toot.md
      run: |-
        git add -A
        timestamp=$(date -u)
        git commit -m "${timestamp}" || exit 0
        git push
```
And the `requirements.txt` file:
```
shot-scraper
toot
```
