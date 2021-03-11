# Converting no-decimal-point latitudes and longitudes using jq

I had some data with weird co-ordinates in it:

```json
{
    "Agency": "F",
    "Address": "S WAYSIDE DR",
    "CrossStreet": "BLK GULF FWY IB",
    "KeyMap": "534C",
    "XCoord": "-95314927",
    "YCoord": "29716075",
    "CombinedResponse": "F",
    "CallTimeOpened": "02/20/2021 22:29",
    "IncidentType": "Ems Event",
    "AlarmLevel": "0",
    "NumberOfUnits": "1",
    "Units": "A023;"
}
```
Note the `"XCoord": "-95314927"` and `"YCoord": "29716075"` in there.

I know that this data refers to somewhere in Houston, and [a few people](https://twitter.com/simonw/status/1369163089636036610) on Twitter pointed out that it's actually really simple: it's just missing the decimal point!

Here's the `jq` recipe I came up with to transform this:

```jq
{
    latitude: (.YCoord  | tonumber / 1000000.0),
    longitude: (.XCoord | tonumber / 1000000.0),
    date: (.CallTimeOpened | strptime("%m/%d/%Y %H:%M") | todate),
    key: (.CallTimeOpened + " " + .XCoord + " " + .YCoord )
} + .
```
The `+ .` at the end adds back on the original object.

Running this example on https://www.jqkungfu.com/ gives the following output:

```json
{
    "Address": "S WAYSIDE DR",
    "Agency": "F",
    "AlarmLevel": "0",
    "CallTimeOpened": "02/20/2021 22:29",
    "CombinedResponse": "F",
    "CrossStreet": "BLK GULF FWY IB",
    "IncidentType": "Ems Event",
    "KeyMap": "534C",
    "NumberOfUnits": "1",
    "Units": "A023;",
    "XCoord": "-95314927",
    "YCoord": "29716075",
    "date": "2021-02-20T22:29:00Z",
    "key": "02/20/2021 22:29 -95314927 29716075",
    "latitude": 29.716075,
    "longitude": -95.314927
}
```
Bonus is this example: I concatenated together a unique primary key for each record in `key`, and I figured out how to use the `strptime()` function to parse a date.
