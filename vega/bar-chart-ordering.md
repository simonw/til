# Vega-Lite bar charts in the same order as the data

I've been puzzling over this one for a couple of years now, and I finally figured out the solution.

The Vega-Lite charting library can generate bar charts using a JSON definition that looks like this:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "A simple bar chart with embedded data.",
  "data": {
    "values": [
      {"bar_label": "startups", "bar_quantity": 157},
      {"bar_label": "webdevelopment", "bar_quantity": 166},
      {"bar_label": "quora", "bar_quantity": 1003},
      {"bar_label": "conferences", "bar_quantity": 152},
      {"bar_label": "datasette", "bar_quantity": 111}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {
      "field": "bar_label",
      "title": "Label",
      "type": "nominal",
      "axis": {"labelAngle": 90}
    },
    "y": {"field": "bar_quantity", "title": "Quantity", "type": "quantitative"}
  }
}
```
There's just one catch: Vega-Lite defaults to sorting the bars alphabetically by their nominal label.

<img width="840" alt="Vega_Editor" src="https://user-images.githubusercontent.com/9599/118381682-46acef00-b5a2-11eb-994c-65b8aed11be4.png">

But sometimes you might want to control that sort order - to have the order that the bars are displayed in directly reflect the order of the data that you passed in.

To do this, pass `"sort": null` as an option to the `x` encoding:

<img width="830" alt="Vega_Editor" src="https://user-images.githubusercontent.com/9599/118381690-5debdc80-b5a2-11eb-93db-bbd847afae81.png">

[Open this example in the Vega Editor](https://vega.github.io/editor/#/url/vega-lite/N4IgJAzgxgFgpgWwIYgFwhgF0wBwqgegIDc4BzJAOjIEtMYBXAI0poHsDp5kTykBaADZ04JAKyUAVhDYA7EABoQAEzjQATjRyZ289AEEABBBoIcguIaZJ1h2DcyGA7nRiHETOMtXLDypJhUiioBKKigxEiCDGpoANqg1uoA+oJInoJoIBCB6pgMeMFJyQCODEiyOpgAnmgAjGIA7AC+Cok2qelwmehOcEyqpIJsOAhwlUUdZRVVtah1AGwLre0paRlZZWzqKErF05V0c3UADCcAzCsgxevdWVByAGZw6uNQsXtT5Yc19WIATFcbl0eiFAhA4Ng4JMUgdZvU6nVmgBdVogZDqADWWSSwTebGUNFkZDQoAAHqSQI8aN1lDiOrdMkoqhYsgAZEHBGo4aHoWRsBBEqLBJBkmgQSmM-TE1moACcJzRMjyaFkDEEgjRc1A1Np9Nh33hzLospAAEVDUcudUeZtLYEdKQQM0XUA)

Vega-Lite [Sorting documentation](https://vega.github.io/vega-lite/docs/sort.html).
