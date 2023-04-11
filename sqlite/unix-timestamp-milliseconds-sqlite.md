# Unix timestamp in milliseconds in SQLite

I wanted to retrieve the time in milliseconds since the Unix epoch in SQLite.

Fetching seconds since the epoch is easy:
```sql
select strftime('%s', 'now');
```
Milliseconds is *much more complex*. After some digging around, I found the following recipe:
```sql
select cast(
  (julianday('now') - 2440587.5)
  * 86400 * 1000 as integer
)
```
[Try these both here](https://latest.datasette.io/_memory?sql=select%0D%0A++strftime%28%27%25s%27%2C+%27now%27%29+as+seconds_since_epoch%2C%0D%0A++cast%28%28julianday%28%27now%27%29+-+2440587.5%29+*+86400+*+1000+as+integer%29+as+ms_since_epoch%3B).

## Displaying them as human readable strings

This fragment of SQL turns them back into a readable UTC value:
```sql
select strftime('%Y-%m-%d %H:%M:%S', :timestamp_ms / 1000, 'unixepoch')
```
The output looks like this: `2023-04-09 05:04:24` - [try that out here](https://latest.datasette.io/_memory?sql=select+strftime%28%27%25Y-%25m-%25d+%25H%3A%25M%3A%25S%27%2C+%3Atimestamp_ms+%2F+1000%2C+%27unixepoch%27%29%0D%0A&timestamp_ms=1681016664769).

## Why not multiply seconds by 1000?

An alternative way of getting milliseconds since the epoch is to do this:
```sql
select strftime('%s', 'now') * 1000
```
The problem with this is that seconds there is an integer - so if I multiply by 1000 I'll always get a number ending in ...000 -  but I want millisecond precision on my timestamps here, so that's not useful.

## How it works

The `julianday('now')` function returns the number of days since the "Julian epoch". The Julian epoch is 12:00 noon on January 1, 4713 BC in the proleptic Julian calendar.

[Wikipedia says](https://en.wikipedia.org/wiki/Julian_day):

> The Julian day is the continuous count of days since the beginning of the Julian period, and is used primarily by astronomers, and in software for easily calculating elapsed days between two events (e.g. food production date and sell by date).

The significance of 4713 BC? It was chosen as a date before any existing historical record.

Crucially, the `julianday` function returns a floating point number of days. This differs from `strftime('%s', 'now')` which returns an integer number of seconds.

`2440587.5` is the number of days between the Julian epoch and the Unix epoch.

There are `86400` seconds in a day.

So... `julianday('now') - 2440587.5` is the number of days since the Unix epoch, and multiplying that by `86400` gives us the floating point number of seconds since the Unix epoch.

Finally we multiply by `1000` because we want milliseconds, not seconds - and we cast the result to an integer because that's the type of number I want to store.

See [sqlite-history/issues/6](https://github.com/simonw/sqlite-history/issues/6) for background information on why I needed this.

## Alternative approach using fractional seconds

[mgr on the SQLite Forum](https://sqlite.org/forum/forumpost/1f173cd9ea810bd0) pointed out an alternative way of solving this, using the `%f` format code for `strftime()` which returns the number of seconds as a floating point number of seconds at millisecond accuracy:

> `%f` fractional seconds: `SS.SSS`

For example 18.412 for 18s and 412ms past the minute.

They suggested this:

```sql
select 1000*(strftime('%s','now')+mod(strftime('%f','now'),1));
```
The `mod()` function isn't available on all SQLite installations though. I found this pattern works instead:

```sql
select
  (1000 * (strftime('%s', 'now'))) + cast(
    substr(
      strftime('%f', 'now'),
      instr(strftime('%f', 'now'), '.') + 1
    ) as integer
  ) as timestamp_ms
```
[Try that here](https://latest.datasette.io/_memory?sql=select%0D%0A++(1000+*+(strftime(%27%25s%27%2C+%27now%27)))+%2B+cast(%0D%0A++++substr(%0D%0A++++++strftime(%27%25f%27%2C+%27now%27)%2C%0D%0A++++++instr(strftime(%27%25f%27%2C+%27now%27)%2C+%27.%27)+%2B+1%0D%0A++++)+as+integer%0D%0A++)+as+timestamp_ms).

The `substr('18.413', instr('18.413', '.') + 1)` part returns just the characters after the first `.` character, which are then cast to integer to get the milliseconds fraction of that second. These are added to `1000 * ` the unix timestamp in seconds.
