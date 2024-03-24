# Google Chrome --headless mode

In the README for [monolith](https://github.com/Y2Z/monolith) (a new Rust CLI tool for archiving HTML pages along with their images and assets) I spotted this tip for using Chrome in headless mode to execute JavaScript and output the resulting DOM:

```bash
chromium --headless --incognito --dump-dom https://github.com \
  | monolith - -I -b https://github.com -o github.html
```
I didn't know about that `--headless` option, so I had a poke around to see if it works on macOS. And it does!

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --dump-dom \
  https://github.com
```
That spits out the rendered DOM from the GitHub home page. The `--incognito` flag doesn't seem to be necessary - it didn't use my existing cookies when I ran it without.

Add `> /tmp/github.html` to write that output to a file.

## Screenshots and PDFs

I found more documentation in [Getting Started with Headless Chrome](https://developer.chrome.com/blog/headless-chrome/), a blog entry published when they released the feature in 2017.

Here's how to take a screenshot:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --screenshot=/tmp/shot1.png \
  https://simonwillison.net
```

![Screenshot of the frontpage of simonwillison.net](https://github.com/simonw/til/assets/9599/d60f7fc8-f610-4731-b71a-3010863c4e50)

And here's a screenshot with a custom width and height:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --window-size=375,667 \
  --screenshot=/tmp/shot2.png \
  https://simonwillison.net
```

<img src="https://github.com/simonw/til/assets/9599/3da856c8-4b22-4f5a-8b7f-3fe7c75392a4" alt="Screenshot of the frontpage of simonwillison.net at a mobile width" width="400">

For a multi-page PDF of the full length page:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --print-to-pdf=/tmp/page.pdf \
  https://simonwillison.net
```
Here's [the output PDF for that](https://static.simonwillison.net/static/2024/chrome-headless-page.pdf).

## --repl doesn't work for me

The documentation mentioned this option as something that would start a REPL prompt for interacting with the page using JavaScript:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --repl \
  https://simonwillison.net
```
This didn't work for me. Maybe they removed that feature?

## More documentation

[@dayson](https://twitter.com/dayson) pointed me to [Chrome’s Headless mode gets an upgrade: introducing --headless=new](https://developer.chrome.com/docs/chromium/new-headless) providing further documentation of the most recent changes.

Frustratingly that documentation doesn't include a clear date, but it mentions features that are new in Chrome 112 which I found was released in March 2023.

I don't know if you still need to run `--headless=new` for these new features. The two that caught my eye were `--timeout 1000` for capturing the page after the specified number of milliseconds, and the intriguing alternative `--virtual-time-budget=5000` which fakes the internal clock in Chrome to behave as if five seconds have passed and take the screenshot then, while not actually waiting those five seconds.

## Comparison to shot-scraper

I didn't know about this `--headless` mode when I built my [shot-scraper](https://shot-scraper.datasette.io/) tool for headless screenshotting and scraping of web pages using [Playwright](https://playwright.dev/), which drives Chromium (and other browsers) under the hood.

`shot-scraper` is a lot more ergonomic and has a lot more features, but it's also quite a bit slower if you just want to take a single screenshot.

The `shot-scraper` equivalent of the above commands would be:

```bash
# Full-page screenshot
shot-scraper 'https://simonwillison.net' -o /tmp/shot3.png

# Custom size screenshot
shot-scraper 'https://simonwillison.net' -o /tmp/shot4.png --width 375 --height 667

# HTML snapshot
shot-scraper html 'https://simonwillison.net'

# PDF
shot-scraper pdf 'https://simonwillison.net' -o /tmp/page2.pdf
```
The more exciting features of `shot-scraper` are its ability to [take multiple screenshots defined in a YAML file](https://shot-scraper.datasette.io/en/stable/multi.html):

```bash
echo '- output: example.com.png
  url: http://www.example.com/
- output: w3c.org.png
  url: https://www.w3.org/' | shot-scraper multi -
```

And its ability to [scrape data from a page](https://shot-scraper.datasette.io/en/stable/javascript.html) by executing JavaScript and returning the result as JSON:

```bash
shot-scraper javascript https://til.simonwillison.net/chrome/headless "
async () => {
  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
  return (new readability.Readability(document)).parse();
}"
```
