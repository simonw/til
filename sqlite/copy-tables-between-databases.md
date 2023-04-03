# Copy tables between SQLite databases

I figured out a pattern for doing this today using the `sqlite3` CLI tool - given two SQLite databases in the current folder, called `tils.db` and `simonwillisonblog.db`:

```bash
echo "
attach database 'simonwillisonblog.db' as simonwillisonblog;
attach database 'tils.db' as tils;
drop table if exists simonwillisonblog.til;
create table simonwillisonblog.til as select * from tils.til;
update simonwillisonblog.til set shot = null;
" | sqlite3
```
I'm using that in [this GitHub Actions workflow](https://github.com/simonw/simonwillisonblog-backup/blob/main/.github/workflows/backup.yml).
