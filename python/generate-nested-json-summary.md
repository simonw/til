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
        return dict([
            (key, summarize(value, list_limit, key_limit))
            for key, value in list(data.items())[:key_limit]
        ])
```
Here's how I used it:
```python
import json, requests
data = requests.get(
    "https://github.com/simonw/coronavirus-data-gov-archive/blob/master/data_latest.json?raw=true"
).json()
print(json.dumps(summarize(data, list_limit=2, key_limit=10), indent=4))
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
            "dailyDeaths": [
                {
                    "date": "2020-03-28",
                    "value": 247
                },
                {
                    "date": "2020-03-29",
                    "value": 199
                }
            ],
            "dailyTotalDeaths": [
                {
                    "date": "2020-03-27",
                    "value": 679
                },
                {
                    "date": "2020-03-28",
                    "value": 926
                }
            ],
            "previouslyReportedDailyTotalCases": [
                {
                    "date": "2020-01-30",
                    "value": 1
                },
                {
                    "date": "2020-01-31",
                    "value": 2
                }
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
        "E12000005": {
            "name": {
                "value": "West Midlands"
            },
            "totalCases": {
                "value": 12393
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-02-12",
                    "value": 1
                },
                {
                    "date": "2020-02-23",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-02-12",
                    "value": 1
                },
                {
                    "date": "2020-02-23",
                    "value": 2
                }
            ]
        },
        "E12000003": {
            "name": {
                "value": "Yorkshire and The Humber"
            },
            "totalCases": {
                "value": 9499
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-01-30",
                    "value": 1
                },
                {
                    "date": "2020-02-03",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-01-30",
                    "value": 1
                },
                {
                    "date": "2020-02-03",
                    "value": 2
                }
            ]
        }
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
        "E06000008": {
            "name": {
                "value": "Blackburn with Darwen"
            },
            "totalCases": {
                "value": 293
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-13",
                    "value": 1
                },
                {
                    "date": "2020-03-20",
                    "value": 2
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-13",
                    "value": 1
                },
                {
                    "date": "2020-03-20",
                    "value": 3
                }
            ]
        },
        "E06000009": {
            "name": {
                "value": "Blackpool"
            },
            "totalCases": {
                "value": 388
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-10",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-10",
                    "value": 1
                },
                {
                    "date": "2020-03-12",
                    "value": 2
                }
            ]
        },
        "E08000001": {
            "name": {
                "value": "Bolton"
            },
            "totalCases": {
                "value": 717
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-05",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-01",
                    "value": 1
                },
                {
                    "date": "2020-03-05",
                    "value": 2
                }
            ]
        }
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
        "E07000200": {
            "name": {
                "value": "Babergh"
            },
            "totalCases": {
                "value": 98
            },
            "dailyConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 1
                },
                {
                    "date": "2020-03-15",
                    "value": 1
                }
            ],
            "dailyTotalConfirmedCases": [
                {
                    "date": "2020-03-14",
                    "value": 1
                },
                {
                    "date": "2020-03-15",
                    "value": 2
                }
            ]
        },
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
        }
    }
}
```
