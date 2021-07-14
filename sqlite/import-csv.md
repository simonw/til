# Importing CSV data into SQLite with .import

I usually use my `sqlite-utils insert blah.db tablename file.csv --csv` command to import CSV data into SQLite, but for large CSV files (like a 750MB one) this can take quite a long time - over half an hour in this case.

SQLite can import CSV data directly, and when I tried it on this file it completed in 45 seconds!

Here's how I scripted that from the command-line:
```bash
sqlite3 data.db <<EOS
.mode csv
.import school.csv schools
.import state.csv states
EOS
```
The `.mode csv` ensures the imported files are treated as CSV, then the `.import filename.csv tablename` lines import the data.

Every column was imported as `TEXT` - so I used `sqlite-utils transform` to transform some of the column types afterwards:
```
sqlite-utils transform data.db schools \
    --type school_nces_id integer \
    --type year integer
```
