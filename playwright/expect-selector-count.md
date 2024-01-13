# Using expect() to wait for a selector to match multiple items

In the Playwright tests for [datasette-cluster-map](https://github.com/simonw/datasette-cluster-map) I wanted to assert that two markers had been displayed on a Leaflet map.

Since the map can take a little while to load, I wanted to run an assertion that would keep trying for up to a deadline to see if those elements had become available.

Here's how to do that in a Playwright Python test:

```python
from playwright.sync_api import expect

def test_markers_are_displayed(ds_server, page):
    page.goto(ds_server + "/data/latitude_longitude")
    # There should be two leaflet-marker-icons
    expect(page.locator(".leaflet-marker-icon")).to_have_count(2)
```
The `page` and `ds_server` fixtures are explained [in this TIL](https://til.simonwillison.net/datasette/playwright-tests-datasette-plugin).

`page.locator()` returns a [Locator](https://playwright.dev/python/docs/api/class-locator), described by Playwright's documentation as "the central piece of Playwright's auto-waiting and retry-ability".

Here's the documentation for [to_have_count()](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-count) - it takes an optional second `timeout` floating point argument which defaults to 5.0 seconds.

Initially I tried using the `page.locator(...).all()` method, but this [doesn't wait for matching elements](https://playwright.dev/python/docs/api/class-locator#locator-all) to become available.
