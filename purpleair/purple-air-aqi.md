# Calculating the AQI based on the Purple Air API for a sensor

[Purple Air](https://www.purpleair.com/) sensors have an API at `https://www.purpleair.com/map.json?show=SENSOR-ID-HERE`, which returns JSON that looks something like this:

```json
{
  "mapVersion": "0.26",
  "baseVersion": "7",
  "mapVersionString": "",
  "results": [
    {
      "ID": 123,
      "Label": "Sensor label",
      "DEVICE_LOCATIONTYPE": "outside",
      "THINGSPEAK_PRIMARY_ID": "123",
      "THINGSPEAK_PRIMARY_ID_READ_KEY": "xxx",
      "THINGSPEAK_SECONDARY_ID": "1234",
      "THINGSPEAK_SECONDARY_ID_READ_KEY": "xxx",
      "Lat": 37.5,
      "Lon": -122.4,
      "PM2_5Value": "8.75",
      "LastSeen": 1630438756,
      "Type": "PMS5003+PMS5003+BME280",
      "Hidden": "false",
      "Flag": 1,
      "DEVICE_BRIGHTNESS": "15",
      "DEVICE_HARDWAREDISCOVERED": "2.0+OPENLOG+15476 MB+DS3231+BME280+PMSX003-B+PMSX003-A",
      "DEVICE_FIRMWAREVERSION": "6.01",
      "Version": "6.01",
      "LastUpdateCheck": 1630436115,
      "Created": 1622588142,
      "Uptime": "2701447",
      "RSSI": "-56",
      "Adc": "0.01",
      "p_0_3_um": "849.53",
      "p_0_5_um": "251.67",
      "p_1_0_um": "78.49",
      "p_2_5_um": "17.79",
      "p_5_0_um": "6.95",
      "p_10_0_um": "5.54",
      "pm1_0_cf_1": "3.58",
      "pm2_5_cf_1": "8.75",
      "pm10_0_cf_1": "14.04",
      "pm1_0_atm": "3.58",
      "pm2_5_atm": "8.75",
      "pm10_0_atm": "14.04",
      "isOwner": 0,
      "humidity": "48",
      "temp_f": "74",
      "pressure": "1005.56",
      "AGE": 1,
      "Stats": "{\"v\":8.75,\"v1\":9.4,\"v2\":10.22,\"v3\":10.96,\"v4\":14.17,\"v5\":15.51,\"v6\":12.53,\"pm\":8.75,\"lastModified\":1630438756184,\"timeSinceModified\":120110}"
    }
  ]
}
```
There's just one problem with this: it doesn't give you the AQI number that is displayed on their site! Instead it gives you the raw numbers that can be used to calculate that AQI number.

I figured someone must have solved this, so I ran a GitHub code search for [purpleair.com map json](https://github.com/search?q=purpleair.com+map+json&type=code) and found [zakj/scriptable](https://github.com/zakj/scriptable) with [code for decoding that](https://github.com/zakj/scriptable/blob/d42a2d7727a2642ad6ee880c15ae65dca4232fe4/purpleAir.js). I adapted it to the following:

```javascript
// Adapted from https://github.com/zakj/scriptable by Zak Johnson
async function fetchAqi(sensorId) {
  const response = await fetch(
    `https://www.purpleair.com/json?show=${sensorId}`
  );
  const json = await response.json();
  const stats = json.results
    .filter((r) => !(r.Flag || r.A_H))
    .map((r) => JSON.parse(r.Stats));
  const pm2_5 = stats.reduce((acc, { v }) => acc + v, 0) / stats.length;
  const trend = stats[0].v1 - stats[0].v3;
  return {
    current: aqiFromPm(pm2_5),
    trend: Math.abs(trend) > 5 ? trend : 0,
    details: json,
  };
}

function aqiFromPm(pm) {
  const table = [
    [0.0, 12.0, 0, 50],
    [12.1, 35.4, 51, 100],
    [35.5, 55.4, 101, 150],
    [55.5, 150.4, 151, 200],
    [150.5, 250.4, 201, 300],
    [250.5, 500.4, 301, 500],
  ];
  const computeAqi = (concI, [concLo, concHi, aqiLo, aqiHi]) =>
    Math.round(
      ((concI - concLo) / (concHi - concLo)) * (aqiHi - aqiLo) + aqiLo
    );
  const values = table.find(([concLo, concHi, aqiLo, aqiHi]) => pm <= concHi);
  return values ? computeAqi(pm, values) : 500;
}
```
I used this to build a simple demo at https://til.simonwillison.net/tools/aqi
