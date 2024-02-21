# Running a scheduled function on Val Town to import Atom feeds into Datasette Cloud

[Val Town](https://www.val.town/) is a neat service for hosting short server-side JavaScript programs online - reminiscent of a combination of Glitch and Observable Notebooks.

Today I figured out how to use it to run an hourly task (a "Val") that fetches data from an Atom feed, parses it and then submits the resulting parsed data to a table running on [Datasette Cloud](https://www.datasette.cloud/) via the [Datasette JSON write API](https://docs.datasette.io/en/latest/json_api.html#the-json-write-api).

## Configuring secrets in environment variables

Because this Val needs to be able to call the Datasette Cloud API with an API token, I needed to figure out Val Town secrets. These are pretty straight-forward: you can set multiple environment variables for your account on this page:

https://www.val.town/settings/environment-variables

Those variables are then made available to your Vals through `Deno.env.get("VARIABLE_NAME")`.

## Scheduling a Val

The Val Town logged in homepage looks like this:

![Create a val. Options are: Email handler, Scheduled function, HTTP handler, Templates...](https://github.com/simonw/til/assets/9599/777a7d9b-a98f-4703-a299-a0aa113a92cc)

Clicking "Scheduled function" creates a new private Val with a random name that looks like this:

![coraCicado - Interval - v0, private - runs every 1 hrs - export default async function (interval: Interval) {}](https://github.com/simonw/til/assets/9599/927a0765-347c-4beb-81e3-471482b29478)

The cog next to "Runs every 1hr" can be used to set a different interval.

## Writing the code

After some experimentation I landed on this as the content of my Val:

```javascript
export default async function(interval: Interval) {
  const { default: Parser } = await import("npm:rss-parser");
  let parser = new Parser();
  let feed = await parser.parseURL("https://simonwillison.net/atom/everything/");
  const token = Deno.env.get("DATASETTE_CLOUD_SIMON_FEED_WRITE");
  const url = "https://simon.datasette.cloud/data/feed/-/insert";
  const body = {
    "rows": feed.items,
    "replace": true,
  };
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (response.ok) {
    const responseData = await response.json();
    console.log("Response data:", responseData);
  } else {
    console.error("Request failed:", response.statusText);
  }
}
```
- Any NPM module can be imported directly into a Val using `await import("npm:name-of-package")`
- I used [rss-parser](https://www.npmjs.com/package/rss-parser) to parse the feed - it was the first option I tried and provided exactly what I wanted
- As mentioned earlier, `Deno.env.get()` provides access to configured environment variables
- Deno's [fetch() function](https://deno.land/api@v1.40.5?s=fetch) is modeled on the browser standard
- `console.log()` and `console.error()` log to a dedicated log for that Val, visible beneath it

The blue "Run" button can be clicked any time to try out the Val. Once I got it working I left it running, and it's been executing once an hour ever since.
