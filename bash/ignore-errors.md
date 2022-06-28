# Ignoring errors in a section of a Bash script

For [simonw/museums#32](https://github.com/simonw/museums/issues/32) I wanted to have certain lines in my Bash script ignore any errors: lines that used `sqlite-utils` to add columns and configure FTS, but that might fail with an error if the column already existed or FTS had already been configured.

[This tip](https://stackoverflow.com/a/60362732) on StackOverflow lead me to the [following recipe](https://github.com/simonw/museums/blob/d94410440a5c81a5cb3a0f0b886a8cd30941b8a9/build.sh):

```bash
#!/bin/bash
set -euo pipefail

yaml-to-sqlite browse.db museums museums.yaml --pk=id
python annotate_nominatum.py browse.db
python annotate_timestamps.py
# Ignore errors in following block until set -e:
set +e
sqlite-utils add-column browse.db museums country 2>/dev/null
sqlite3 browse.db < set-country.sql
sqlite-utils disable-fts browse.db museums 2>/dev/null
sqlite-utils enable-fts browse.db museums \
  name description country osm_city \
  --tokenize porter --create-triggers 2>/dev/null
set -e
```
Everything between the `set +e` and the `set -e` lines can now error without the Bash script itself failing.

The failing lines were still showing a bunch of Python tracebacks. I fixed that by redirecting their standard error output to `/dev/null` like this:
```bash
sqlite-utils disable-fts browse.db museums 2>/dev/null
```
