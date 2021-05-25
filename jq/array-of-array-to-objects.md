# Turning an array of arrays into objects with jq

Input:
```json
[
    ["mm.domus.SW230"," A LA RONDE","Buildings:Houses:Medium houses",50.642781,-3.405508],
    ["mm.domus.SW193"," ALEXANDER KEILLER MUSEUM","Archaeology:Prehistory",51.427927,-1.857344],
    ["mm.domus.SE416"," ANNE OF CLEVES HOUSE MUSEUM","Buildings:Houses:Medium houses",50.869227,0.005329],
]
```
I want an array of objects. Here's what I came up with, using [jqplay.org](https://jqplay.org/):

```jq
[.[] | {id: .[0], name: .[1], category: .[2], latitude: .[3], longitude: .[4]}]
```
This outputs:
```json
[
  {
    "id": "mm.domus.SW230",
    "name": " A LA RONDE",
    "category": "Buildings:Houses:Medium houses",
    "latitude": 50.642781,
    "longitude": -3.405508
  },
  {
    "id": "mm.domus.SW193",
    "name": " ALEXANDER KEILLER MUSEUM",
    "category": "Archaeology:Prehistory",
    "latitude": 51.427927,
    "longitude": -1.857344
  },
  {
    "id": "mm.domus.SE416",
    "name": " ANNE OF CLEVES HOUSE MUSEUM",
    "category": "Buildings:Houses:Medium houses",
    "latitude": 50.869227,
    "longitude": 0.005329
  }
]
```
If you remove the outer `[` and `]` and use the "Compact output" option you get back this instead:
```
{"id":"mm.domus.SW230","name":" A LA RONDE","category":"Buildings:Houses:Medium houses","latitude":50.642781,"longitude":-3.405508}
{"id":"mm.domus.SW193","name":" ALEXANDER KEILLER MUSEUM","category":"Archaeology:Prehistory","latitude":51.427927,"longitude":-1.857344}
{"id":"mm.domus.SE416","name":" ANNE OF CLEVES HOUSE MUSEUM","category":"Buildings:Houses:Medium houses","latitude":50.869227,"longitude":0.005329}

```
