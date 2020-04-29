# Generated a summary of nested JSON data

I was trying to figure out the shape of the JSON object from https://github.com/simonw/coronavirus-data-gov-archive/blob/master/data_latest.json?raw=true - which is 3.2MB and heavily nested, so it's difficult to get a good feel for the shape.

I solved this with a Python `summarize()` function which recursively truncates the nested lists and dictionaries.

```python
def summarize(data, list_limit=5, key_limit=5):
    "Recursively reduce data to just the first X nested keys and list items"
    if not isinstance(data, (list, dict)):
        return data
    if isinstance(data, list):
        return [summarize(item, list_limit, key_limit) for item in data[:list_limit]]
    if isinstance(data, dict):
        all_keys = list(data.keys())
        kept_keys = all_keys[:key_limit]
        truncated_keys = all_keys[key_limit:]
        d = dict([
            (key, summarize(data[key], list_limit, key_limit))
            for key in kept_keys
        ])
        if truncated_keys:
            d["_truncated_keys"] = truncated_keys
        return d
```
Here's how I used it:
```python
import json, requests
data = requests.get(
    "https://github.com/simonw/coronavirus-data-gov-archive/blob/master/data_latest.json?raw=true"
).json()
print(json.dumps(summarize(data, list_limit=2, key_limit=7), indent=4))
```
And the output:
```json
{
    "lastUpdatedAt": "2020-04-28T18:14:22.840234Z",
    "disclaimer": "Lab-confirmed case counts for England and subnational areas are provided by Public Health England. All data on deaths and data for the rest of the UK are provided by the Department of Health and Social Care based on data from NHS England and the devolved administrations. Maps include Ordnance Survey data \u00a9 Crown copyright and database right 2020 and Office for National Statistics data \u00a9 Crown copyright and database right 2020. Daily and total case counts are as of 28 April 2020, Daily and total deaths are as of 27 April 2020. See the About the data page (link at top of this page) for details.",
    "overview": {
        "K02000001": {
            "name": {
                "value": "United Kingdom"
            },
            "totalCases": {
                "value": 161145
            },
            "newCases": {
                "value": 3996
            },
            "deaths": {
                "value": 21678
            },
            "dailyDeaths": [
                {
                    "date": "2020-03-15",
                    "value": 14
                },
                {
                    "date": "2020-03-16",
                    "value": 20
                }
            ],
            "dailyTotalDeaths": [
                {
                    "date": "2020-03-10",
                    "value": 6
                },
                {
                    "date": "2020-03-11",
                    "value": 6
                }
            ]
        }
    },
    "countries": {
        "E92000001": {
            "name": {
                "value": "England"
            },
            "totalCases": {
                "value": 114456
            },
            "deaths": {
                "value": 19294
            },
            "maleCases": [
                {
                    "age": "30_to_34",
                    "value": 2224
                },
                {
                    "age": "40_to_44",
                    "value": 2702
                }
            ],
            "femaleCases": [
                {
                    "age": "20_to_24",
                    "value": 1885
                },
                {
                    "age": "90_to_94",
                    "value": 3580
                }
            ],
            "dailyConfirmedCases": [
                {
                    "date": "2020-01-30",
                    "value": 1
                },
                {
                    "date": "2020-01-31",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-01-30",
                    "value": 1
                },
                {
                    "date": "2020-01-31",
                    "value": 2
                }
            ],
            "_truncated_keys": [
                "dailyDeaths",
                "dailyTotalDeaths",
                "previouslyReportedDailyTotalCases",
                "previouslyReportedDailyTotalCasesAdjusted",
                "previouslyReportedDailyCases",
                "previouslyReportedDailyCasesAdjusted",
                "changeInDailyTotalCases",
                "changeInDailyTotalCasesAdjusted",
                "changeInDailyCases",
                "changeInDailyCasesAdjusted"
            ]
        },
        "N92000002": {
            "name": {
                "value": "Northern Ireland"
            },
            "totalCases": {
                "value": 3408
            },
            "deaths": {
                "value": 309
            },
            "dailyDeaths": [
                {
                    "date": "2020-03-28",
                    "value": 2
                },
                {
                    "date": "2020-03-29",
                    "value": 0
                }
            ],
            "dailyTotalDeaths": [
                {
                    "date": "2020-03-27",
                    "value": 13
                },
                {
                    "date": "2020-03-28",
                    "value": 15
                }
            ]
        },
        "S92000003": {
            "name": {
                "value": "Scotland"
            },
            "totalCases": {
                "value": 10721
            },
            "deaths": {
                "value": 1262
            },
            "dailyDeaths": [
                {
                    "date": "2020-03-28",
                    "value": 7
                },
                {
                    "date": "2020-03-29",
                    "value": 0
                }
            ],
            "dailyTotalDeaths": [
                {
                    "date": "2020-03-27",
                    "value": 33
                },
                {
                    "date": "2020-03-28",
                    "value": 40
                }
            ]
        },
        "W92000004": {
            "name": {
                "value": "Wales"
            },
            "totalCases": {
                "value": 9512
            },
            "deaths": {
                "value": 813
            },
            "dailyDeaths": [
                {
                    "date": "2020-03-28",
                    "value": 4
                },
                {
                    "date": "2020-03-29",
                    "value": 10
                }
            ],
            "dailyTotalDeaths": [
                {
                    "date": "2020-03-27",
                    "value": 34
                },
                {
                    "date": "2020-03-28",
                    "value": 38
                }
            ]
        }
    },
    "regions": {
        "E12000004": {
            "name": {
                "value": "East Midlands"
            },
            "totalCases": {
                "value": 6411
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-21",
                    "value": 1
                },
                {
                    "date": "2020-02-25",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-21",
                    "value": 1
                },
                {
                    "date": "2020-02-25",
                    "value": 2
                }
            ]
        },
        "E12000006": {
            "name": {
                "value": "East of England"
            },
            "totalCases": {
                "value": 9907
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 1
                },
                {
                    "date": "2020-02-28",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 1
                },
                {
                    "date": "2020-02-28",
                    "value": 2
                }
            ]
        },
        "E12000007": {
            "name": {
                "value": "London"
            },
            "totalCases": {
                "value": 23979
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-11",
                    "value": 1
                },
                {
                    "date": "2020-02-13",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-11",
                    "value": 1
                },
                {
                    "date": "2020-02-13",
                    "value": 2
                }
            ]
        },
        "E12000001": {
            "name": {
                "value": "North East"
            },
            "totalCases": {
                "value": 7174
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-02",
                    "value": 1
                },
                {
                    "date": "2020-03-04",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-02",
                    "value": 1
                },
                {
                    "date": "2020-03-04",
                    "value": 2
                }
            ]
        },
        "E12000002": {
            "name": {
                "value": "North West"
            },
            "totalCases": {
                "value": 17823
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-28",
                    "value": 1
                },
                {
                    "date": "2020-03-01",
                    "value": 8
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-28",
                    "value": 1
                },
                {
                    "date": "2020-03-01",
                    "value": 9
                }
            ]
        },
        "E12000008": {
            "name": {
                "value": "South East"
            },
            "totalCases": {
                "value": 16323
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-01-31",
                    "value": 1
                },
                {
                    "date": "2020-02-03",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-01-31",
                    "value": 1
                },
                {
                    "date": "2020-02-03",
                    "value": 2
                }
            ]
        },
        "E12000009": {
            "name": {
                "value": "South West"
            },
            "totalCases": {
                "value": 5986
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 2
                },
                {
                    "date": "2020-02-26",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 2
                },
                {
                    "date": "2020-02-26",
                    "value": 3
                }
            ]
        },
        "_truncated_keys": [
            "E12000005",
            "E12000003"
        ]
    },
    "utlas": {
        "E09000002": {
            "name": {
                "value": "Barking and Dagenham"
            },
            "totalCases": {
                "value": 445
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-08",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-08",
                    "value": 2
                }
            ]
        },
        "E09000003": {
            "name": {
                "value": "Barnet"
            },
            "totalCases": {
                "value": 1170
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-16",
                    "value": 1
                },
                {
                    "date": "2020-02-28",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-16",
                    "value": 1
                },
                {
                    "date": "2020-02-28",
                    "value": 2
                }
            ]
        },
        "E08000016": {
            "name": {
                "value": "Barnsley"
            },
            "totalCases": {
                "value": 590
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 1
                },
                {
                    "date": "2020-03-02",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-03",
                    "value": 1
                },
                {
                    "date": "2020-03-02",
                    "value": 2
                }
            ]
        },
        "E06000022": {
            "name": {
                "value": "Bath and North East Somerset"
            },
            "totalCases": {
                "value": 203
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-11",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 2
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-11",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 3
                }
            ]
        },
        "E06000055": {
            "name": {
                "value": "Bedford"
            },
            "totalCases": {
                "value": 424
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-13",
                    "value": 1
                },
                {
                    "date": "2020-03-17",
                    "value": 2
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-13",
                    "value": 1
                },
                {
                    "date": "2020-03-17",
                    "value": 3
                }
            ]
        },
        "E09000004": {
            "name": {
                "value": "Bexley"
            },
            "totalCases": {
                "value": 596
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-09",
                    "value": 2
                },
                {
                    "date": "2020-03-10",
                    "value": 2
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-09",
                    "value": 2
                },
                {
                    "date": "2020-03-10",
                    "value": 4
                }
            ]
        },
        "E08000025": {
            "name": {
                "value": "Birmingham"
            },
            "totalCases": {
                "value": 2733
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-02",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-02",
                    "value": 2
                }
            ]
        },
        "_truncated_keys": [
            "E06000008",
            "E06000009",
            "E08000001",
            "E06000058",
            "E06000036",
            "E08000032",
            "E09000005",
            "E06000043",
            "E06000023",
            "E09000006",
            "E10000002",
            "E08000002",
            "E08000033",
            "E10000003",
            "E09000007",
            "E06000056",
            "E06000049",
            "E06000050",
            "E09000001",
            "E06000052",
            "E06000047",
            "E08000026",
            "E09000008",
            "E10000006",
            "E06000005",
            "E06000015",
            "E10000007",
            "E10000008",
            "E08000017",
            "E06000059",
            "E08000027",
            "E09000009",
            "E06000011",
            "E10000011",
            "E09000010",
            "E10000012",
            "E08000037",
            "E10000013",
            "E09000011",
            "E09000012",
            "E06000006",
            "E09000013",
            "E10000014",
            "E09000014",
            "E09000015",
            "E06000001",
            "E09000016",
            "E06000019",
            "E10000015",
            "E09000017",
            "E09000018",
            "E06000046",
            "E09000019",
            "E09000020",
            "E10000016",
            "E06000010",
            "E09000021",
            "E08000034",
            "E08000011",
            "E09000022",
            "E10000017",
            "E08000035",
            "E06000016",
            "E10000018",
            "E09000023",
            "E10000019",
            "E08000012",
            "E06000032",
            "E08000003",
            "E06000035",
            "E09000024",
            "E06000002",
            "E06000042",
            "E08000021",
            "E09000025",
            "E10000020",
            "E06000012",
            "E06000013",
            "E06000024",
            "E08000022",
            "E10000023",
            "E10000021",
            "E06000057",
            "E06000018",
            "E10000024",
            "E08000004",
            "E10000025",
            "E06000031",
            "E06000026",
            "E06000044",
            "E06000038",
            "E09000026",
            "E06000003",
            "E09000027",
            "E08000005",
            "E08000018",
            "E06000017",
            "E08000006",
            "E08000028",
            "E08000014",
            "E08000019",
            "E06000051",
            "E06000039",
            "E08000029",
            "E10000027",
            "E06000025",
            "E08000023",
            "E06000045",
            "E06000033",
            "E09000028",
            "E08000013",
            "E10000028",
            "E08000007",
            "E06000004",
            "E06000021",
            "E10000029",
            "E08000024",
            "E10000030",
            "E09000029",
            "E06000030",
            "E08000008",
            "E06000020",
            "E06000034",
            "E06000027",
            "E09000030",
            "E08000009",
            "E08000036",
            "E08000030",
            "E09000031",
            "E09000032",
            "E06000007",
            "E10000031",
            "E06000037",
            "E10000032",
            "E09000033",
            "E08000010",
            "E06000054",
            "E06000040",
            "E08000015",
            "E06000041",
            "E08000031",
            "E10000034",
            "E06000014"
        ]
    },
    "ltlas": {
        "E07000223": {
            "name": {
                "value": "Adur"
            },
            "totalCases": {
                "value": 76
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-19",
                    "value": 1
                },
                {
                    "date": "2020-03-22",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-19",
                    "value": 1
                },
                {
                    "date": "2020-03-22",
                    "value": 2
                }
            ]
        },
        "E07000026": {
            "name": {
                "value": "Allerdale"
            },
            "totalCases": {
                "value": 191
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-12",
                    "value": 1
                },
                {
                    "date": "2020-03-13",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-12",
                    "value": 1
                },
                {
                    "date": "2020-03-13",
                    "value": 2
                }
            ]
        },
        "E07000032": {
            "name": {
                "value": "Amber Valley"
            },
            "totalCases": {
                "value": 133
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-12",
                    "value": 1
                },
                {
                    "date": "2020-03-13",
                    "value": 3
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-12",
                    "value": 1
                },
                {
                    "date": "2020-03-13",
                    "value": 4
                }
            ]
        },
        "E07000224": {
            "name": {
                "value": "Arun"
            },
            "totalCases": {
                "value": 121
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 1
                },
                {
                    "date": "2020-03-18",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 1
                },
                {
                    "date": "2020-03-18",
                    "value": 2
                }
            ]
        },
        "E07000170": {
            "name": {
                "value": "Ashfield"
            },
            "totalCases": {
                "value": 182
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 3
                },
                {
                    "date": "2020-03-15",
                    "value": 3
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 3
                },
                {
                    "date": "2020-03-15",
                    "value": 6
                }
            ]
        },
        "E07000105": {
            "name": {
                "value": "Ashford"
            },
            "totalCases": {
                "value": 403
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-03",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-03",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 2
                }
            ]
        },
        "E07000004": {
            "name": {
                "value": "Aylesbury Vale"
            },
            "totalCases": {
                "value": 301
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-04",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-04",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 2
                }
            ]
        },
        "_truncated_keys": [
            "E07000200",
            "E09000002",
            "E09000003",
            "E08000016",
            "E07000027",
            "E07000066",
            "E07000084",
            "E07000171",
            "E06000022",
            "E06000055",
            "E09000004",
            "E08000025",
            "E07000129",
            "E06000008",
            "E06000009",
            "E07000033",
            "E08000001",
            "E07000136",
            "E06000058",
            "E06000036",
            "E08000032",
            "E07000067",
            "E07000143",
            "E09000005",
            "E07000068",
            "E06000043",
            "E06000023",
            "E07000144",
            "E09000006",
            "E07000234",
            "E07000095",
            "E07000172",
            "E07000117",
            "E08000002",
            "E08000033",
            "E07000008",
            "E09000007",
            "E07000192",
            "E07000106",
            "E07000028",
            "E07000069",
            "E06000056",
            "E07000130",
            "E07000070",
            "E07000078",
            "E07000177",
            "E06000049",
            "E06000050",
            "E07000034",
            "E07000225",
            "E07000005",
            "E07000118",
            "E09000001",
            "E07000071",
            "E07000029",
            "E07000150",
            "E06000052",
            "E07000079",
            "E06000047",
            "E08000026",
            "E07000163",
            "E07000226",
            "E09000008",
            "E07000096",
            "E06000005",
            "E07000107",
            "E07000151",
            "E06000015",
            "E07000035",
            "E08000017",
            "E06000059",
            "E07000108",
            "E08000027",
            "E09000009",
            "E07000009",
            "E07000040",
            "E07000085",
            "E07000242",
            "E07000137",
            "E07000152",
            "E06000011",
            "E07000193",
            "E07000244",
            "E07000061",
            "E07000086",
            "E07000030",
            "E07000207",
            "E09000010",
            "E07000072",
            "E07000208",
            "E07000036",
            "E07000041",
            "E07000087",
            "E07000010",
            "E07000112",
            "E07000080",
            "E07000119",
            "E08000037",
            "E07000173",
            "E07000081",
            "E07000088",
            "E07000109",
            "E07000145",
            "E09000011",
            "E07000209",
            "E09000012",
            "E06000006",
            "E07000164",
            "E09000013",
            "E07000131",
            "E09000014",
            "E07000073",
            "E07000165",
            "E09000015",
            "E07000089",
            "E06000001",
            "E07000062",
            "E07000090",
            "E09000016",
            "E06000019",
            "E07000098",
            "E07000037",
            "E09000017",
            "E07000132",
            "E07000227",
            "E09000018",
            "E07000011",
            "E07000120",
            "E07000202",
            "E06000046",
            "E09000019",
            "E09000020",
            "E07000153",
            "E07000146",
            "E06000010",
            "E09000021",
            "E08000034",
            "E08000011",
            "E09000022",
            "E07000121",
            "E08000035",
            "E06000016",
            "E07000063",
            "E09000023",
            "E07000194",
            "E07000138",
            "E08000012",
            "E06000032",
            "E07000110",
            "E07000074",
            "E07000235",
            "E08000003",
            "E07000174",
            "E06000035",
            "E07000133",
            "E07000187",
            "E09000024",
            "E07000042",
            "E07000203",
            "E07000228",
            "E06000002",
            "E06000042",
            "E07000210",
            "E07000091",
            "E07000175",
            "E08000021",
            "E07000195",
            "E09000025",
            "E07000043",
            "E07000038",
            "E06000012",
            "E07000099",
            "E07000139",
            "E06000013",
            "E07000147",
            "E06000024",
            "E08000022",
            "E07000218",
            "E07000134",
            "E07000154",
            "E06000057",
            "E07000148",
            "E06000018",
            "E07000219",
            "E07000135",
            "E08000004",
            "E07000178",
            "E07000122",
            "E06000031",
            "E06000026",
            "E06000044",
            "E07000123",
            "E06000038",
            "E09000026",
            "E06000003",
            "E07000236",
            "E07000211",
            "E07000124",
            "E09000027",
            "E07000166",
            "E08000005",
            "E07000075",
            "E07000125",
            "E07000064",
            "E08000018",
            "E07000220",
            "E07000212",
            "E07000176",
            "E07000092",
            "E06000017",
            "E07000167",
            "E08000006",
            "E08000028",
            "E07000168",
            "E07000188",
            "E08000014",
            "E07000169",
            "E07000111",
            "E08000019",
            "E06000051",
            "E06000039",
            "E08000029",
            "E07000246",
            "E07000006",
            "E07000012",
            "E07000039",
            "E06000025",
            "E07000044",
            "E07000140",
            "E07000141",
            "E07000031",
            "E07000149",
            "E07000155",
            "E07000179",
            "E07000126",
            "E07000189",
            "E07000196",
            "E08000023",
            "E06000045",
            "E06000033",
            "E09000028",
            "E07000213",
            "E07000240",
            "E08000013",
            "E07000197",
            "E07000198",
            "E07000243",
            "E08000007",
            "E06000004",
            "E06000021",
            "E07000221",
            "E07000082",
            "E08000024",
            "E07000214",
            "E09000029",
            "E07000113",
            "E06000030",
            "E08000008",
            "E07000199",
            "E07000215",
            "E07000045",
            "E06000020",
            "E07000076",
            "E07000093",
            "E07000083",
            "E07000114",
            "E07000102",
            "E06000034",
            "E07000115",
            "E06000027",
            "E07000046",
            "E09000030",
            "E08000009",
            "E07000116",
            "E07000077",
            "E07000180",
            "E08000036",
            "E08000030",
            "E09000031",
            "E09000032",
            "E06000007",
            "E07000222",
            "E07000103",
            "E07000216",
            "E07000065",
            "E07000156",
            "E07000241",
            "E06000037",
            "E07000047",
            "E07000127",
            "E07000142",
            "E07000181",
            "E07000245",
            "E09000033",
            "E08000010",
            "E06000054",
            "E07000094",
            "E06000040",
            "E08000015",
            "E07000217",
            "E06000041",
            "E08000031",
            "E07000237",
            "E07000229",
            "E07000238",
            "E07000007",
            "E07000128",
            "E07000239",
            "E06000014"
        ]
    }
}
```
