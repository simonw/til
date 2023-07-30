# axe-core and shot-scraper for accessibility audits

I just watched a talk by [Pamela Fox](https://www.pamelafox.org/) at [North Bay Python](https://2023.northbaypython.org/) on Automated accessibility audits. The video should be [up within 24 hours](https://www.youtube.com/@NorthBayPython/videos).

One of the tools Pamela introduced us to was [axe-core](https://github.com/dequelabs/axe-core), which is a JavaScript library at the heart of a whole ecosystem of accessibility auditing tools.

I figured out how to use it to run an accessibility audit using my [shot-scraper](https://shot-scraper.datasette.io/) CLI tool:

```bash
shot-scraper javascript https://datasette.io "
async () => {
  const axeCore = await import('https://cdn.jsdelivr.net/npm/axe-core@4.7.2/+esm');
  return axeCore.default.run();
}
"
```
The first line loads an ESM build of `axe-core` from the jsdelivr CDN. I figured out the URL for this by searching jsdelivr and finding their [axe-core page](https://www.jsdelivr.com/package/npm/axe-core).

The second line calls the `.run()` method, which defaults to returning an enormous JSON object containing the results of the audit.

`shot-scraper` dumps the return value of tha `async()` function to standard output in my terminal.

The output started like this:
```json
{
    "testEngine": {
        "name": "axe-core",
        "version": "4.7.2"
    },
    "testRunner": {
        "name": "axe"
    },
    "testEnvironment": {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/115.0.5790.75 Safari/537.36",
        "windowWidth": 1280,
        "windowHeight": 720,
        "orientationAngle": 0,
        "orientationType": "landscape-primary"
    },
    "timestamp": "2023-07-30T18:32:39.591Z",
    "url": "https://datasette.io/",
    "toolOptions": {
        "reporter": "v1"
    },
    "inapplicable": [
        {
            "id": "accesskeys",
            "impact": null,
            "tags": [
                "cat.keyboard",
                "best-practice"
            ],
```
That `inapplicable` section goes on for a long time, but it's not actually interesting - it shows all of the audit checks that the page passed.

The most interesting section is called `violations`. We can filter to just that using `jq`:

```bash
shot-scraper javascript https://datasette.io "
async () => {
  const axeCore = await import('https://cdn.jsdelivr.net/npm/axe-core@4.7.2/+esm');
  return axeCore.default.run();
}
" | jq .violations
```
Which produced (for my page) an array of four objects, starting like this:
```json
[
  {
    "id": "color-contrast",
    "impact": "serious",
    "tags": [
      "cat.color",
      "wcag2aa",
      "wcag143",
      "ACT",
      "TTv5",
      "TT13.c"
    ],
    "description": "Ensures the contrast between foreground and background colors meets WCAG 2 AA minimum contrast ratio thresholds",
    "help": "Elements must meet minimum color contrast ratio thresholds",
    "helpUrl": "https://dequeuniversity.com/rules/axe/4.7/color-contrast?application=axeAPI",
    "nodes": [
      {
        "any": [
          {
            "id": "color-contrast",
            "data": {
              "fgColor": "#ffffff",
              "bgColor": "#8484f4",
              "contrastRatio": 3.18,
              "fontSize": "10.8pt (14.4px)",
              "fontWeight": "normal",
              "messageKey": null,
              "expectedContrastRatio": "4.5:1",
              "shadowColor": null
            },
            "relatedNodes": [
              {
                "html": "<input type=\"submit\" value=\"Search\">",
                "target": [
                  "input[type=\"submit\"]"
                ]
              }
            ],
            "impact": "serious",
            "message": "Element has insufficient color contrast of 3.18 (foreground color: #ffffff, background color: #8484f4, font size: 10.8pt (14.4px), font weight: normal). Expected contrast ratio of 4.5:1"
          }
        ],
```
I loaded these into a SQLite database using [sqlite-utils](https://sqlite-utils.datasette.io/):

```bash
shot-scraper javascript https://datasette.io "
async () => {
  const axeCore = await import('https://cdn.jsdelivr.net/npm/axe-core@4.7.2/+esm');
  return axeCore.default.run();
}
" | jq .violations \
  | sqlite-utils insert /tmp/v.db violations -                  
```
Then I ran `open /tmp/v.db` to open that database in [Datasette Desktop](https://datasette.io/desktop).

![Datasette running against that new table, faceted by impact and tags](https://github.com/simonw/til/assets/9599/5c55695a-d787-42a7-9f94-dd435e423ca0)
