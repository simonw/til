# Avoiding "length" errors in Apache Bench with the -l option

I was using the Apache Bench `ab` command to exercise some new code I'm writing in Datasette and I noticed I was getting a lot of errors:

```
ab -n 1000 -c 10 \
  'http://127.0.0.1:8002/fixtures/compound_primary_key?_extra=count&_size=3&_extra=columns&_extra=primary_keys&_trace=1&_extra=debug'
```
Truncated output:
```
Benchmarking 127.0.0.1 (be patient)
Completed 100 requests
Completed 200 requests
...
Complete requests:      1000
Failed requests:        953
   (Connect: 0, Receive: 0, Length: 953, Exceptions: 0)
```
What's with the 953 failed requests? My server logged a 200 status code for each of them, so it seemed to think they were being returned without errors.

Thanks to [Stack Overflow](https://stackoverflow.com/questions/579450/load-testing-with-ab-fake-failed-requests-length/579466) I learned that by default Apache Bench considers a request a "length" error if it does not match exactly the length of the first recieved page.

This particular Datasette response includes millisecond timing information in the JSON (thanks to the `?_trace=1` option), and since those timings differ the overall length differs between requests.

The solution is to use the `-l` (lower case L) option, as documented in `ab --help` like this:

> Accept variable document length (use this for dynamic pages)

So the following command runs without showing those errors:
```
ab -l -n 1000 -c 10 \
  'http://127.0.0.1:8002/fixtures/compound_primary_key?_extra=count&_size=3&_extra=columns&_extra=primary_keys&_trace=1&_extra=debug'
```
Truncated output:
```
Concurrency Level:      10
Time taken for tests:   1.407 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      2962382 bytes
HTML transferred:       2823382 bytes
Requests per second:    710.53 [#/sec] (mean)
Time per request:       14.074 [ms] (mean)
Time per request:       1.407 [ms] (mean, across all concurrent requests)
Transfer rate:          2055.52 [Kbytes/sec] received
```
