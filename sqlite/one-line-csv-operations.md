# One-liner for running queries against CSV files with SQLite

I figured out how to run a SQL query directly against a CSV file using the `sqlite3` command-line utility:

    sqlite3 :memory: -cmd '.mode csv' -cmd '.import taxi.csv taxi' \
      'SELECT passenger_count, COUNT(*), AVG(total_amount) FROM taxi GROUP BY passenger_count'

This uses the special `:memory:` filename to open an in-memory database. Then it uses two `-cmd` options to turn on CSV mode and import the `taxi.csv` file into a table called `taxi`. Then it runs the SQL query.

You can get `taxi.csv` by downloading the compressed file from [here](https://github.com/multiprocessio/dsq/blob/43e72ff1d2c871082fed0ae401dd59e2ff9f6cfe/testdata/taxi.csv.7z) and running:

    7z e -aos taxi.csv.7z

I figured this out while commenting on [this issue](https://github.com/multiprocessio/dsq/issues/70).

The output looks like this:

```
"",128020,32.2371511482553
0,42228,17.0214016766151
1,1533197,17.6418833067999
2,286461,18.0975870711456
3,72852,17.9153958710923
4,25510,18.452774990196
5,50291,17.2709248175672
6,32623,17.6002964166367
7,2,87.17
8,2,95.705
9,1,113.6
```

Add `-cmd '.mode column'` to output in columns instead:
```
$ sqlite3 :memory: -cmd '.mode csv' -cmd '.import taxi.csv taxi' -cmd '.mode column' \
    'SELECT passenger_count, COUNT(*), AVG(total_amount) FROM taxi GROUP BY passenger_count'
passenger_count  COUNT(*)  AVG(total_amount)
---------------  --------  -----------------
                 128020    32.2371511482553 
0                42228     17.0214016766151 
1                1533197   17.6418833067999 
2                286461    18.0975870711456 
3                72852     17.9153958710923 
4                25510     18.452774990196  
5                50291     17.2709248175672 
6                32623     17.6002964166367 
7                2         87.17            
8                2         95.705           
9                1         113.6            
```
Or use `-cmd '.mode markdown'` to get a Markdown table:

| passenger_count | COUNT(*) | AVG(total_amount) |
|-----------------|----------|-------------------|
|                 | 128020   | 32.2371511482553  |
| 0               | 42228    | 17.0214016766151  |
| 1               | 1533197  | 17.6418833067999  |
| 2               | 286461   | 18.0975870711456  |
| 3               | 72852    | 17.9153958710923  |
| 4               | 25510    | 18.452774990196   |
| 5               | 50291    | 17.2709248175672  |
| 6               | 32623    | 17.6002964166367  |
| 7               | 2        | 87.17             |
| 8               | 2        | 95.705            |
| 9               | 1        | 113.6             |
