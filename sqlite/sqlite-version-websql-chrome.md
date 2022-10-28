# Finding the SQLite version used by Web SQL in Chrome

Google Chrome still includes support for [Web SQL](https://www.w3.org/TR/webdatabase/), the long since abandoned proposed standard for shipping a SQL engine in browser JavaScript. I was reminded of its existence today while reading about the new official [sqlite3 wasm build](https://sqlite.org/wasm/doc/tip/about.md).

Out of curiosity, I decided to see what version of SQLite was bundled with Chrome. I assumed it would be a very old version, since Web SQL is an idea from a long time ago now.

I used GitHub Copilot to write the code, so I wouldn't have to look up the APIs myself. I typed these two comments:

```javascript
// Instantiate a new WebSQL database
...
// Execute a SQL query returning sqlite_version()
```
Copilot completed the following:
```javascript
// Instantiate a new WebSQL database
var db = openDatabase('mydb', '1.0', 'Test DB', 2 * 1024 * 1024);
// Execute a SQL query returning sqlite_version()
db.transaction(function (tx) {
  tx.executeSql(
    'SELECT sqlite_version()',
    [],
    function (tx, results) {
      console.log(results.rows.item(0));
    }
  );
});
```
I pasted that into my Chrome DevTools console... and got the following result:
```
{sqlite_version(): '3.39.4'}
```
This surprised my greatly, because [SQLite 3.39.4](https://www.sqlite.org/releaselog/3_39_4.html) is the most recent release, and only came out a month ago on the 29th of September 2022!

I had a look on GitHub and found [this commit from the 30th of September](https://github.com/chromium/chromium/commit/f53a9502a0001792114380c850a25c693ddd6308) which bumps the version of SQLite included in Chromium.

My Chrome is version 107.0.5304.62 - I found the SQLite 3.39.4 upgrade mentioned in [this log of commits](https://chromium.googlesource.com/chromium/src/+log/106.0.5249.119..107.0.5304.68?pretty=fuller&n=10000) between v106 and v107, which was linked to from [this release post](https://chromereleases.googleblog.com/2022/10/stable-channel-update-for-desktop_25.html).
