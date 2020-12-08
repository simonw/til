# Escaping a SQL query to use with curl and Datasette

I used this pattern to pass a SQL query to Datasette's CSV export via curl and output the results, stripping off the first row (the header row) using `tail -n +2`.

SQL queries need to be URL-encoded - I did that be echoing the SQL query and piping it to a Python one-liner that calls the `urllib.parse.quote()` function.

```bash
curl -s "https://github-to-sqlite.dogsheep.net/github.csv?sql=$(echo '
select
  full_name
from
  repos
where
  rowid in (
    select
      repos.rowid
    from
      repos,
      json_each(repos.topics) j
    where
      j.value = "datasette-io"
  )
  and rowid in (
    select
      repos.rowid
    from
      repos,
      json_each(repos.topics) j
    where
      j.value = "datasette-plugin"
  )
order by
  updated_at desc
' | python3 -c \
  'import sys; import urllib.parse; print(urllib.parse.quote(sys.stdin.read()))')" \
  | tail -n +2
```
Here's [that SQL query](https://github-to-sqlite.dogsheep.net/github?sql=select%0D%0A++full_name%0D%0Afrom%0D%0A++repos%0D%0Awhere%0D%0A++rowid+in+%28%0D%0A++++select%0D%0A++++++repos.rowid%0D%0A++++from%0D%0A++++++repos%2C%0D%0A++++++json_each%28repos.topics%29+j%0D%0A++++where%0D%0A++++++j.value+%3D+%22datasette-io%22%0D%0A++%29%0D%0A++and+rowid+in+%28%0D%0A++++select%0D%0A++++++repos.rowid%0D%0A++++from%0D%0A++++++repos%2C%0D%0A++++++json_each%28repos.topics%29+j%0D%0A++++where%0D%0A++++++j.value+%3D+%22datasette-plugin%22%0D%0A++%29%0D%0Aorder+by%0D%0A++updated_at+desc) in the Datasette web UI.

The output from the bash one-liner looks like this:
```
simonw/datasette-edit-schema
simonw/datasette-import-table
simonw/datasette-dateutil
simonw/datasette-seaborn
simonw/datasette-backup
simonw/datasette-yaml
simonw/datasette-schema-versions
simonw/datasette-graphql
simonw/datasette-insert
simonw/datasette-copyable
simonw/datasette-auth-passwords
simonw/datasette-glitch
simonw/datasette-block-robots
simonw/datasette-saved-queries
simonw/datasette-psutil
simonw/datasette-auth-tokens
simonw/datasette-permissions-sql
simonw/datasette-media
simonw/datasette-atom
simonw/datasette-vega
simonw/datasette-jellyfish
simonw/datasette-leaflet-geojson
simonw/datasette-template-sql
simonw/datasette-render-markdown
simonw/datasette-auth-github
simonw/datasette-mask-columns
simonw/datasette-jq
simonw/datasette-cluster-map
simonw/datasette-upload-csvs
simonw/datasette-publish-fly
simonw/datasette-render-images
simonw/datasette-render-timestamps
simonw/datasette-configure-fts
simonw/datasette-search-all
simonw/datasette-render-html
simonw/datasette-show-errors
simonw/datasette-column-inspect
simonw/datasette-ics
simonw/datasette-json-html
simonw/datasette-pretty-json
simonw/datasette-sqlite-fts4
simonw/datasette-bplist
simonw/datasette-render-binary
simonw/datasette-rure
simonw/datasette-haversine
```
