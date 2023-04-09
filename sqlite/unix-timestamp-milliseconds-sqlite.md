# Unix timestamp in milliseconds in SQLite

I wanted to retrieve the time in milliseconds since the Unix epoch in SQLite.

Fetching seconds since the epoch is easy:

    select strftime('%s', 'now');

Milliseconds is *much more complex*. After some digging around, I found the following recipe:

    select cast(
      (julianday('now') - 2440587.5)
      * 86400 * 1000 as integer
    )

[Try these both here](https://latest.datasette.io/_memory?sql=select%0D%0A++strftime%28%27%25s%27%2C+%27now%27%29+as+seconds_since_epoch%2C%0D%0A++cast%28%28julianday%28%27now%27%29+-+2440587.5%29+*+86400+*+1000+as+integer%29+as+ms_since_epoch%3B).

## How it works

The `julianday('now')` function returns the number of days since the "Julian epoch". The Julian epoch is 12:00 noon on January 1, 4713 BC in the proleptic Julian calendar.

[Wikipedia says](https://en.wikipedia.org/wiki/Julian_day):

> The Julian day is the continuous count of days since the beginning of the Julian period, and is used primarily by astronomers, and in software for easily calculating elapsed days between two events (e.g. food production date and sell by date).[

Crucially, the `julianday` function returns a floating point number of days. This differs from `strftime('%s', 'now')` which returns an integer number of seconds.

`2440587.5` is the number of days between the Julian epoch and the Unix epoch.

There are `86400` seconds in a day.

So... `julianday('now') - 2440587.5` is the number of days since the Unix epoch, and multiplying that by `86400` gives us the floating point number of seconds since the Unix epoch.

Finally, multiplying that by `1000` gives us the number of milliseconds since the Unix epoch.

Finally we multiple by 1000 because we want milliseconds, not seconds - and we cast the result to an integer because that's the type of number I want to store.

See [sqlite-history/issues/6](https://github.com/simonw/sqlite-history/issues/6) for background information on why I needed this.
