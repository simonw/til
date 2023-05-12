# Exploring Baseline with Datasette Lite

One of the announcements from Google I/O 2023 was [Baseline](https://web.dev/baseline/), a new initiative to help simplify the challenge of deciding which web platform features are now widely enough supported by modern browsers to be safe to use.

The key idea is to document features that are now supported in "the most recent two versions of major browsers" - I've not found a more precise definition of that yet though. The browsers in question are Chrome, Edge, Firefox and Safari.

## Where's the data?

The initiative is being driven by the W3C [WebDX Community Group](https://www.w3.org/community/webdx/). The key repository for the project is this one:

https://github.com/web-platform-dx/feature-set

In particular, the relevant data is in the YAML files in [the feature-group-definitions directory](https://github.com/web-platform-dx/feature-set/tree/main/feature-group-definitions).

Here's an example, for [border-image.yml](https://github.com/web-platform-dx/feature-set/blob/main/feature-group-definitions/border-image.yml):

```yaml
spec: https://drafts.csswg.org/css-backgrounds-3/#border-images
caniuse: border-image
usage_stats: https://chromestatus.com/metrics/css/timeline/popularity/43
status:
  is_baseline: true
  since: "2017-03-09"
  support:
    chrome: "56"
    edge: "12"
    firefox: "50"
    safari: "9.1"
compat_features:
  - css.properties.border-image
  - css.properties.border-image.fill
  - css.properties.border-image.gradient
  - css.properties.border-image.optional_border_image_slice
  - css.properties.border-image-outset
  - css.properties.border-image-repeat
  - css.properties.border-image-repeat.round
  - css.properties.border-image-repeat.space
  - css.properties.border-image-slice
  - css.properties.border-image-source
  - css.properties.border-image-width
```
The baseline data is in that `status` field.

It took me a while to trick this down... because it turns out there are only 6 files (out of the 46 in that directory) that have this data so far!

## That data as JSON

The project publishes a [web-features package](https://github.com/web-platform-dx/feature-set/tree/main/packages/web-features) to npm which includes all of that data as JSON.

Thanks to [the jsDelivr](https://www.jsdelivr.com/) CDN we can access the built JSON that's included in that package at this URL:

https://cdn.jsdelivr.net/npm/web-features/index.json

This combines the data from all of those YAML files into a single JSON file.

## Exploring the data with Datasette Lite

Since jsDelivr supports CORS, we can use that JSON file as the data source for Datasette Lite:

https://lite.datasette.io/?json=https://cdn.jsdelivr.net/npm/web-features/index.json

(I [added a new feature](https://github.com/simonw/datasette-lite/issues/66) to Datasette Lite to teach it to handle JSON files like this that contain an object at the top level rather than an array.)

This mostly worked, but was slightly confounded by the baseline data existing in a JSON object inside that `status` column.

So... I defined the following SQL view to break that out into separate columns:

```sql
create view baseline as select
  _key,
  spec,
  '' || json_extract(status, '$.is_baseline') as is_baseline,
  json_extract(status, '$.since') as baseline_since,
  json_extract(status, '$.support.chrome') as baseline_chrome,
  json_extract(status, '$.support.edge') as baseline_edge,
  json_extract(status, '$.support.firefox') as baseline_firefox,
  json_extract(status, '$.support.safari') as baseline_safari,
  compat_features,
  caniuse,
  usage_stats,
  status
from
  [index]
```

That `'' || json_extract(...)` line there is needed to convert the boolean integer value into a string - which turned out to be necessary for Datasette's faceting to work correctly against the view.

I [saved this to a Gist](https://gist.github.com/simonw/b71c57ae3b21c85bcb7b23a9af4a2000) in order to take advantage of another Datasette Lite feature: you can tell it to load SQL, which will be executed after the JSON has been imported into a table.

Combining that together provides the following URL:

https://lite.datasette.io/?sql=https://gist.github.com/simonw/b71c57ae3b21c85bcb7b23a9af4a2000&json=https%3A%2F%2Fcdn.jsdelivr.net%2Fnpm%2Fweb-features%2Findex.json#/data/baseline?_filter_column=is_baseline&_filter_op=notnull__1&_filter_value=&_sort=&_facet=is_baseline

This imports the JSON, creates the SQL view and then loads the data from that view. And now you can explore the Baseline data using Datasette Facets!

<img width="1030" alt="Screenshot of Datasette Lite showing 6 rows where is_baseline is not null " src="https://github.com/simonw/til/assets/9599/303e08b7-bdeb-429c-85c6-b80b41b79297">
