# Using DuckDB in Python to access Parquet data

Did a quick experiment with [DuckDB](https://duckdb.org/) today, inspired by the [bmschmidt/hathi-binary](https://github.com/bmschmidt/hathi-binary) repo.

That repo includes 3GB of data in 68 parquet files. Those files are 45MB each.

DuckDB can run queries against Parquet data _really fast_.

I checked out the repo like this:

    cd /tmp
    git clone https://github.com/bmschmidt/hathi-binary
    cd hathi-binary

To install it:

    pip install duckdb

Then in a Python console:

```pycon
>>> import duckdb
>>> db = duckdb.connect() # No need to pass a file name, we will use a VIEW
>>> db.execute("CREATE VIEW hamming AS SELECT * FROM parquet_scan('parquet/*.parquet')")
<duckdb.DuckDBPyConnection object at 0x110eab530>
>>> db.execute("select count(*) from hamming").fetchall()
[(17123746,)]
>>> db.execute("select sum(A), sum(B), sum(C) from hamming").fetchall()
[(19478990546114240096822710, 16303362475198894881395004, 43191807707832192976154883)]
```
There are 17,123,746 records in the 3GB of Parquet data.

I switched to iPython so I could time a query. First I ran a query to see what a record looks like, using `.df().to_dict()` to convert the result into a DataFrame and then a Python dictionary:

```
In [17]: db.execute("select * from hamming limit 1").df().to_dict()
Out[17]: 
{'htid': {0: 'uc1.b3209520'},
 'A': {0: -3968610387004385723},
 'B': {0: 7528965001168362882},
 'C': {0: 5017761927246436345},
 'D': {0: 2866021664979717155},
 'E': {0: -8718458467632335109},
 'F': {0: 3783827906913154091},
 'G': {0: -883843087282811188},
 'H': {0: 4045142741717613284},
 'I': {0: -9144138405661797607},
 'J': {0: 3285280333149952194},
 'K': {0: -3352555231043531556},
 'L': {0: 2071206943103704211},
 'M': {0: -5859914591541496612},
 'N': {0: -4209182319449999971},
 'O': {0: 2040176595216801886},
 'P': {0: 860910514658882647},
 'Q': {0: 3505065119653024843},
 'R': {0: -3110594979418944378},
 'S': {0: -8591743965043807123},
 'T': {0: -3262129165685658773}}
```
Then I timed an aggregate query using `%time`:
```
In [18]: %time db.execute("select sum(A), sum(B), sum(C) from hamming").fetchall()
CPU times: user 1.13 s, sys: 488 ms, total: 1.62 s
Wall time: 206 ms
Out[18]: 
[(19478990546114240096822710,
  16303362475198894881395004,
  43191807707832192976154883)]
```
206ms to sum three columns across 17 million records is pretty fast!
