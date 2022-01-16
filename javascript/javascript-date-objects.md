# JavaScript date objects

A few notes on JavaScript `Date` object, based on trying to do some basic things with them in Observable notebooks.

## Parsing ISO format strings into a Date object

I had date times that looked like this:

`2022-03-05 14:35`

Passing this string to the `Date()` constructor breaks in interesting ways: it assumes they are in the browser's current timezone, and it breaks in Safari producing an `Invalid Date` error.

This worked instead:

```javascript
new Date(o.datetime.replace(" ", "T") + ":00Z"))
```
Safari requires dates to look like this - without the `T` you get `Invalid Date`:

`2022-03-05T14:35:00Z`

Adding the trailing `Z` causes the date to be treated as if it was UTC. This can be helpful if you plan to work with them in a mostly timezone-unaware fashion, though see the note about using `{timeZone: "UTC"}` with the formatting methods later in this document.

## Timezones

JavaScript date objects REALLY want to be helpful with timezones. Consider the following examples, here using `.toString()`:

```javascript
(new Date("2021-01-15T14:31:00")).toString()
"Fri Jan 15 2021 14:31:00 GMT-0800 (Pacific Standard Time)"

(new Date("2021-01-15T14:31:00Z")).toString()
"Fri Jan 15 2021 06:31:00 GMT-0800 (Pacific Standard Time)"
```
In both cases the `.toString()` method converts to my current timezone, Pacific Standard Time. Note how the one with the `Z` gets displayed as `06:31:00` while the one without the `Z` is shown as `14:31:00`.

## Differences between dates

I wanted to calculate the number of minutes difference between a start date and an end date. Subtracting the two gives you a difference between them as in integer number of milliseconds! So this gives you minutes:

```javascript
let diff = end.getTime() - start.getTime();
let minutes = Math.round(diff / 60 * 1000);
```

## Displaying dates

The closest JavaScript gets to Python's handy [strftime() method](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) is the much more unwieldly `toLocaleDateString()` method. Some examples:

```javascript
(new Date).toLocaleDateString("en-US", {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
})
"Sunday, January 16, 2022"
(new Date).toLocaleTimeString("en-US")
"12:12:29 PM"
```
These are also timezone aware. Passing `timeZone: "UTC"` to them can be useful, for example:
```javascript
// This outputs in my timezone, PST:
(new Date("2021-01-22T15:03:00Z")).toLocaleTimeString("en-US")
"7:03:00 AM"
// This keeps the output in UTC:
(new Date("2021-01-22T15:03:00Z")).toLocaleTimeString(
    "en-US", {timeZone: "UTC"}
)
"3:03:00 PM"
```
MDN documentation:

- [toLocaleDateString()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString)
- [toLocaleTimeString()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleTimeString)

## Discussion

Lots of useful comments on this in [replies on Twitter](https://twitter.com/simonw/status/1482810703123607552), including recommendations for these libraries:

- [Intl.DateTimeFormat()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat) for even more advanced formatting options in the browser standards
- [Luxon](https://moment.github.io/luxon/) - the more modern alternative to the [no longer recommended](https://momentjs.com/docs/#/-project-status/) Moment.js
- [date-fns](https://date-fns.org/) as a more modular modern alternative
- GitHub's [time-elements](https://github.com/github/time-elements) web components
