# pytest coverage with context

[This tweet](https://twitter.com/mariatta/status/1499863816489734146) from \@Mariatta tipped me off to the ability to measure "contexts" when [running coverage](https://coverage.readthedocs.io/en/6.3.2/contexts.html#context-reporting) - as a way to tell which tests exercise which specific lines of code.

My [sqlite-utils](https://github.com/simonw/sqlite-utils) project uses `pytest` for the test suite. I decided to figure out how to get this working with [pytest-cov](https://pypi.org/project/pytest-cov/).

After some experimentation, this is the recipe that worked for me:

```
# In the virtual environment, make sure pytest-cov is installed:
% pip install pytest-cov
# First, run pytest to calculate coverage of the `sqlite_utils` package, with context
% pytest --cov=sqlite_utils --cov-context=test
# The .coverage file is actually a SQLite database:
% ls -lah .coverage
-rw-r--r--@ 1 simon  staff   716K Mar  4 16:39 .coverage
# This command generates the HTML coverage report in `htmlcov/`
% coverage html --show-contexts
# Open the report in a browser`
% open htmlcov/index.html
```

Here's what one of the pages looks like, displaying the context for some lines of code:

![The code has an expandable section which reveals which tests executed each individual line.](https://user-images.githubusercontent.com/9599/156860441-66e35994-653a-4ab7-b690-4d901fc57750.png)

## The .coverage schema

Since `.coverage` is a SQLite database, here's the schema - generated using `sqlite-utils schema .coverage`:
```sql
CREATE TABLE coverage_schema (
    -- One row, to record the version of the schema in this db.
    version integer
);
CREATE TABLE meta (
    -- Key-value pairs, to record metadata about the data
    key text,
    value text,
    unique (key)
    -- Keys:
    --  'has_arcs' boolean      -- Is this data recording branches?
    --  'sys_argv' text         -- The coverage command line that recorded the data.
    --  'version' text          -- The version of coverage.py that made the file.
    --  'when' text             -- Datetime when the file was created.
);
CREATE TABLE file (
    -- A row per file measured.
    id integer primary key,
    path text,
    unique (path)
);
CREATE TABLE context (
    -- A row per context measured.
    id integer primary key,
    context text,
    unique (context)
);
CREATE TABLE line_bits (
    -- If recording lines, a row per context per file executed.
    -- All of the line numbers for that file/context are in one numbits.
    file_id integer,            -- foreign key to `file`.
    context_id integer,         -- foreign key to `context`.
    numbits blob,               -- see the numbits functions in coverage.numbits
    foreign key (file_id) references file (id),
    foreign key (context_id) references context (id),
    unique (file_id, context_id)
);
CREATE TABLE arc (
    -- If recording branches, a row per context per from/to line transition executed.
    file_id integer,            -- foreign key to `file`.
    context_id integer,         -- foreign key to `context`.
    fromno integer,             -- line number jumped from.
    tono integer,               -- line number jumped to.
    foreign key (file_id) references file (id),
    foreign key (context_id) references context (id),
    unique (file_id, context_id, fromno, tono)
);
CREATE TABLE tracer (
    -- A row per file indicating the tracer used for that file.
    file_id integer primary key,
    tracer text,
    foreign key (file_id) references file (id)
);
```
