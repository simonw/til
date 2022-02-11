# Today I Learned

My Today I Learned snippets. Inspired by [jbranchaud/til](https://github.com/jbranchaud/til), which I spotted [on Hacker News](https://news.ycombinator.com/item?id=22908044).

Search these TILs at https://til.simonwillison.net/

<!-- count starts -->242<!-- count ends --> TILs so far. <a href="https://til.simonwillison.net/til/feed.atom">Atom feed here</a>.

<!-- index starts -->
## github-actions

* [Only run GitHub Action on push to master / main](https://github.com/simonw/til/blob/main/github-actions/only-master.md) - 2020-04-19
* [Dump out all GitHub Actions context](https://github.com/simonw/til/blob/main/github-actions/dump-context.md) - 2020-04-19
* [Set environment variables for all steps in a GitHub Action](https://github.com/simonw/til/blob/main/github-actions/set-environment-for-all-steps.md) - 2020-04-19
* [Commit a file if it changed](https://github.com/simonw/til/blob/main/github-actions/commit-if-file-changed.md) - 2020-04-19
* [Running different steps on a schedule](https://github.com/simonw/til/blob/main/github-actions/different-steps-on-a-schedule.md) - 2020-04-20
* [Updating a Markdown table of contents with a GitHub Action](https://github.com/simonw/til/blob/main/github-actions/markdown-table-of-contents.md) - 2020-07-22
* [Using grep to write tests in CI](https://github.com/simonw/til/blob/main/github-actions/grep-tests.md) - 2020-08-19
* [Skipping a GitHub Actions step without failing](https://github.com/simonw/til/blob/main/github-actions/continue-on-error.md) - 2020-08-22
* [Open a debugging shell in GitHub Actions with tmate](https://github.com/simonw/til/blob/main/github-actions/debug-tmate.md) - 2020-09-14
* [Talking to a PostgreSQL service container from inside a Docker container](https://github.com/simonw/til/blob/main/github-actions/service-containers-docker.md) - 2020-09-18
* [Using Prettier to check JavaScript code style in GitHub Actions](https://github.com/simonw/til/blob/main/github-actions/prettier-github-actions.md) - 2020-12-31
* [Running tests against PostgreSQL in a service container](https://github.com/simonw/til/blob/main/github-actions/postgresq-service-container.md) - 2021-02-23
* [Installing different PostgreSQL server versions in GitHub Actions](https://github.com/simonw/til/blob/main/github-actions/different-postgresql-versions.md) - 2021-07-05
* [Attaching a generated file to a GitHub release using Actions](https://github.com/simonw/til/blob/main/github-actions/attach-generated-file-to-release.md) - 2021-09-07
* [Storing files in an S3 bucket between GitHub Actions runs](https://github.com/simonw/til/blob/main/github-actions/s3-bucket-github-actions.md) - 2021-12-07
* [Testing against Python 3.11 preview using GitHub Actions](https://github.com/simonw/til/blob/main/github-actions/python-3-11.md) - 2022-02-02

## python

* [Convert a datetime object to UTC without using pytz](https://github.com/simonw/til/blob/main/python/convert-to-utc-without-pytz.md) - 2020-04-19
* [macOS Catalina sort-of includes Python 3](https://github.com/simonw/til/blob/main/python/macos-catalina-sort-of-ships-with-python3.md) - 2020-04-21
* [Generated a summary of nested JSON data](https://github.com/simonw/til/blob/main/python/generate-nested-json-summary.md) - 2020-04-28
* [Installing and upgrading Datasette plugins with pipx](https://github.com/simonw/til/blob/main/python/installing-upgrading-plugins-with-pipx.md) - 2020-05-04
* [Use setup.py to install platform-specific dependencies](https://github.com/simonw/til/blob/main/python/platform-specific-dependencies.md) - 2020-05-05
* [Build the official Python documentation locally](https://github.com/simonw/til/blob/main/python/build-official-docs.md) - 2020-05-08
* [Introspecting Python function parameters](https://github.com/simonw/til/blob/main/python/introspect-function-parameters.md) - 2020-05-27
* [Password hashing in Python with pbkdf2](https://github.com/simonw/til/blob/main/python/password-hashing-with-pbkdf2.md) - 2020-07-13
* [How to call pip programatically from Python](https://github.com/simonw/til/blob/main/python/call-pip-programatically.md) - 2020-08-11
* [Outputting JSON with reduced floating point precision](https://github.com/simonw/til/blob/main/python/json-floating-point.md) - 2020-08-21
* [Debugging a Click application using pdb](https://github.com/simonw/til/blob/main/python/debug-click-with-pdb.md) - 2020-09-03
* [Understanding option names in Click](https://github.com/simonw/til/blob/main/python/click-option-names.md) - 2020-09-22
* [Explicit file encodings using click.File](https://github.com/simonw/til/blob/main/python/click-file-encoding.md) - 2020-10-16
* [Decorators with optional arguments](https://github.com/simonw/til/blob/main/python/decorators-with-optional-arguments.md) - 2020-10-28
* [Running Python code in a subprocess with a time limit](https://github.com/simonw/til/blob/main/python/subprocess-time-limit.md) - 2020-12-06
* [Controlling the style of dumped YAML using PyYAML](https://github.com/simonw/til/blob/main/python/style-yaml-dump.md) - 2020-12-07
* [Relinquishing control in Python asyncio](https://github.com/simonw/til/blob/main/python/yielding-in-asyncio.md) - 2020-12-29
* [Packaging a Python app as a standalone binary with PyInstaller](https://github.com/simonw/til/blob/main/python/packaging-pyinstaller.md) - 2021-01-04
* [Handling CSV files with wide columns in Python](https://github.com/simonw/til/blob/main/python/csv-error-column-too-large.md) - 2021-02-15
* [Using io.BufferedReader to peek against a non-peekable stream](https://github.com/simonw/til/blob/main/python/io-bufferedreader.md) - 2021-02-15
* [Tracing every executed Python statement](https://github.com/simonw/til/blob/main/python/tracing-every-statement.md) - 2021-03-21
* [Check spelling using codespell](https://github.com/simonw/til/blob/main/python/codespell.md) - 2021-08-03
* [Find local variables in the traceback for an exception](https://github.com/simonw/til/blob/main/python/find-local-variables-in-exception-traceback.md) - 2021-08-09
* [Using Fabric with an SSH public key](https://github.com/simonw/til/blob/main/python/fabric-ssh-key.md) - 2021-10-06
* [Using the sqlite3 Python module in Pyodide - Python WebAssembly](https://github.com/simonw/til/blob/main/python/sqlite-in-pyodide.md) - 2021-10-18
* [Planning parallel downloads with TopologicalSorter](https://github.com/simonw/til/blob/main/python/graphlib-topologicalsorter.md) - 2021-11-16
* [Using cog to update --help in a Markdown README file](https://github.com/simonw/til/blob/main/python/cog-to-update-help-in-readme.md) - 2021-11-18
* [Ignoring a line in both flake8 and mypy](https://github.com/simonw/til/blob/main/python/ignore-both-flake8-and-mypy.md) - 2021-11-30
* [__init_subclass__](https://github.com/simonw/til/blob/main/python/init-subclass.md) - 2021-12-03
* [Using C_INCLUDE_PATH to install Python packages](https://github.com/simonw/til/blob/main/python/using-c-include-path-to-install-python-packages.md) - 2021-12-09
* [Safely outputting JSON](https://github.com/simonw/til/blob/main/python/safe-output-json.md) - 2021-12-17
* [Annotated explanation of David Beazley's dataklasses](https://github.com/simonw/til/blob/main/python/annotated-dataklasses.md) - 2021-12-19
* [Streaming indented output of a JSON array](https://github.com/simonw/til/blob/main/python/output-json-array-streaming.md) - 2022-01-17

## zeit-now

* [Running a Python ASGI app on Vercel](https://github.com/simonw/til/blob/main/zeit-now/python-asgi-on-now-v2.md) - 2020-04-19
* [Redirecting all paths on a Vercel instance](https://github.com/simonw/til/blob/main/zeit-now/redirecting-all-paths-on-vercel.md) - 2021-03-27

## sqlite

* [Lag window function in SQLite](https://github.com/simonw/til/blob/main/sqlite/lag-window-function.md) - 2020-04-19
* [Null case comparisons in SQLite](https://github.com/simonw/til/blob/main/sqlite/null-case.md) - 2020-04-21
* [Compile a new sqlite3 binary on Ubuntu](https://github.com/simonw/til/blob/main/sqlite/compile-sqlite3-ubuntu.md) - 2020-04-30
* [List all columns in a SQLite database](https://github.com/simonw/til/blob/main/sqlite/list-all-columns-in-a-database.md) - 2020-05-06
* [Using LD_PRELOAD to run any version of SQLite with Python](https://github.com/simonw/til/blob/main/sqlite/ld-preload.md) - 2020-06-17
* [SQLite BLOB literals](https://github.com/simonw/til/blob/main/sqlite/blob-literals.md) - 2020-07-29
* [Enabling WAL mode for SQLite database files](https://github.com/simonw/til/blob/main/sqlite/enabling-wal-mode.md) - 2020-08-09
* [Compiling the SQLite spellfix.c module on macOS](https://github.com/simonw/til/blob/main/sqlite/compile-spellfix-osx.md) - 2020-09-19
* [Figuring out if a text value in SQLite is a valid integer or float](https://github.com/simonw/til/blob/main/sqlite/text-value-is-integer-or-float.md) - 2020-09-27
* [Replicating SQLite with rqlite](https://github.com/simonw/til/blob/main/sqlite/replicating-rqlite.md) - 2020-12-28
* [Identifying column combination patterns in a SQLite table](https://github.com/simonw/til/blob/main/sqlite/column-combinations.md) - 2021-01-12
* [Fixing broken text encodings with sqlite-transform and ftfy](https://github.com/simonw/til/blob/main/sqlite/fixing-column-encoding-with-ftfy-and-sqlite-transform.md) - 2021-01-18
* [Splitting on commas in SQLite](https://github.com/simonw/til/blob/main/sqlite/splitting-commas-sqlite.md) - 2021-02-01
* [Querying for items stored in UTC that were created on a Thursday in PST](https://github.com/simonw/til/blob/main/sqlite/utc-items-on-thursday-in-pst.md) - 2021-03-12
* [Using pysqlite3 on macOS](https://github.com/simonw/til/blob/main/sqlite/pysqlite3-on-macos.md) - 2021-07-10
* [Importing CSV data into SQLite with .import](https://github.com/simonw/til/blob/main/sqlite/import-csv.md) - 2021-07-13
* [SQLite aggregate filter clauses](https://github.com/simonw/til/blob/main/sqlite/sqlite-aggregate-filter-clauses.md) - 2021-08-04
* [Building a specific version of SQLite with pysqlite on macOS/Linux](https://github.com/simonw/til/blob/main/sqlite/build-specific-sqlite-pysqlite-macos.md) - 2021-08-14
* [Track timestamped changes to a SQLite table using triggers](https://github.com/simonw/til/blob/main/sqlite/track-timestamped-changes-to-a-table.md) - 2021-08-19
* [json_extract() path syntax in SQLite](https://github.com/simonw/til/blob/main/sqlite/json-extract-path.md) - 2022-01-18
* [Ordered group_concat() in SQLite](https://github.com/simonw/til/blob/main/sqlite/ordered-group-concat.md) - 2022-02-06

## presenting

* [Using macOS stickies to display a workshop link on the screen](https://github.com/simonw/til/blob/main/presenting/stickies-for-workshop-links.md) - 2020-04-20

## macos

* [Running pip install -e .[test] in zsh on macOS Catalina](https://github.com/simonw/til/blob/main/macos/zsh-pip-install.md) - 2020-04-21
* [Get Skitch working on Catalina](https://github.com/simonw/til/blob/main/macos/skitch-catalina.md) - 2020-04-21
* [Close terminal window on Ctrl+D for macOS](https://github.com/simonw/til/blob/main/macos/close-terminal-on-ctrl-d.md) - 2020-04-21
* [Fixing "compinit: insecure directories" error](https://github.com/simonw/til/blob/main/macos/fixing-compinit-insecure-directories.md) - 2020-04-26
* [Finding the largest SQLite files on a Mac](https://github.com/simonw/til/blob/main/macos/find-largest-sqlite.md) - 2020-08-19
* [Shrinking PNG files with pngquant and oxipng](https://github.com/simonw/til/blob/main/macos/shrinking-pngs-with-pngquant-and-oxipng.md) - 2021-02-07
* [Running Docker on an M1 Mac](https://github.com/simonw/til/blob/main/macos/running-docker-on-remote-m1.md) - 2021-05-25
* [Using lsof on macOS](https://github.com/simonw/til/blob/main/macos/lsof-macos.md) - 2021-12-11

## cloudrun

* [Use labels on Cloud Run services for a billing breakdown](https://github.com/simonw/til/blob/main/cloudrun/use-labels-for-billing-breakdown.md) - 2020-04-21
* [How to deploy a folder with a Dockerfile to Cloud Run](https://github.com/simonw/til/blob/main/cloudrun/ship-dockerfile-to-cloud-run.md) - 2020-08-04
* [Using the gcloud run services list command](https://github.com/simonw/til/blob/main/cloudrun/gcloud-run-services-list.md) - 2020-09-01
* [Listing files uploaded to Cloud Build](https://github.com/simonw/til/blob/main/cloudrun/listing-cloudbuild-files.md) - 2021-04-14
* [Switching between gcloud accounts](https://github.com/simonw/til/blob/main/cloudrun/multiple-gcloud-accounts.md) - 2021-05-18
* [Increasing the time limit for a Google Cloud Scheduler task](https://github.com/simonw/til/blob/main/cloudrun/increase-cloud-scheduler-time-limit.md) - 2021-07-08
* [Tailing Google Cloud Run request logs and importing them into SQLite](https://github.com/simonw/til/blob/main/cloudrun/tailing-cloud-run-request-logs.md) - 2021-08-09
* [Using build-arg variables with Cloud Run deployments](https://github.com/simonw/til/blob/main/cloudrun/using-build-args-with-cloud-run.md) - 2021-11-19

## tailscale

* [Restricting SSH connections to devices within a Tailscale network](https://github.com/simonw/til/blob/main/tailscale/lock-down-sshd.md) - 2020-04-23

## pytest

* [Session-scoped temporary directories in pytest](https://github.com/simonw/til/blob/main/pytest/session-scoped-tmp.md) - 2020-04-26
* [How to mock httpx using pytest-mock](https://github.com/simonw/til/blob/main/pytest/mock-httpx.md) - 2020-04-29
* [Asserting a dictionary is a subset of another dictionary](https://github.com/simonw/til/blob/main/pytest/assert-dictionary-subset.md) - 2020-05-28
* [Registering temporary pluggy plugins inside tests](https://github.com/simonw/til/blob/main/pytest/registering-plugins-in-tests.md) - 2020-07-21
* [Code coverage using pytest and codecov.io](https://github.com/simonw/til/blob/main/pytest/pytest-code-coverage.md) - 2020-08-15
* [Start a server in a subprocess during a pytest session](https://github.com/simonw/til/blob/main/pytest/subprocess-server.md) - 2020-08-31
* [Using VCR and pytest with pytest-recording](https://github.com/simonw/til/blob/main/pytest/pytest-recording-vcr.md) - 2021-11-02
* [Quick and dirty mock testing with mock_calls](https://github.com/simonw/til/blob/main/pytest/pytest-mock-calls.md) - 2021-11-02
* [Writing pytest tests against tools written with argparse](https://github.com/simonw/til/blob/main/pytest/pytest-argparse.md) - 2022-01-08
* [Testing a Click app with streaming input](https://github.com/simonw/til/blob/main/pytest/test-click-app-with-streaming-input.md) - 2022-01-09
* [Opt-in integration tests with pytest --integration](https://github.com/simonw/til/blob/main/pytest/only-run-integration.md) - 2022-01-26

## github

* [Accessing repository dependencies in the GitHub GraphQL API](https://github.com/simonw/til/blob/main/github/dependencies-graphql-api.md) - 2020-04-30
* [Paginating through the GitHub GraphQL API with Python](https://github.com/simonw/til/blob/main/github/graphql-pagination-python.md) - 2020-07-09
* [Searching for repositories by topic using the GitHub GraphQL API](https://github.com/simonw/til/blob/main/github/graphql-search-topics.md) - 2020-10-09
* [Bulk fetching repository details with the GitHub GraphQL API](https://github.com/simonw/til/blob/main/github/bulk-repo-github-graphql.md) - 2021-01-17
* [Syntax highlighting Python console examples with GFM](https://github.com/simonw/til/blob/main/github/syntax-highlighting-python-console.md) - 2021-01-18
* [Transferring a GitHub issue from a private to a public repository](https://github.com/simonw/til/blob/main/github/transfer-issue-private-to-public.md) - 2021-12-22
* [Configuring Dependabot for a Python project with dependencies in setup.py](https://github.com/simonw/til/blob/main/github/dependabot-python-setup.md) - 2022-01-14

## node

* [Constant-time comparison of strings in Node](https://github.com/simonw/til/blob/main/node/constant-time-compare-strings.md) - 2020-05-01

## firefox

* [Search across all loaded resources in Firefox](https://github.com/simonw/til/blob/main/firefox/search-across-all-resources.md) - 2020-05-05

## markdown

* [Converting HTML and rich-text to Markdown](https://github.com/simonw/til/blob/main/markdown/converting-to-markdown.md) - 2020-05-09
* [Rendering Markdown with the GitHub Markdown API](https://github.com/simonw/til/blob/main/markdown/github-markdown-api.md) - 2020-08-22
* [Useful Markdown extensions in Python](https://github.com/simonw/til/blob/main/markdown/markdown-extensions-python.md) - 2021-04-03

## pypi

* [Adding project links to PyPI](https://github.com/simonw/til/blob/main/pypi/project-links.md) - 2020-05-11

## asgi

* [Writing tests for the ASGI lifespan protocol with HTTPX](https://github.com/simonw/til/blob/main/asgi/lifespan-test-httpx.md) - 2020-06-29

## heroku

* [Using heroku pg:pull to restore a backup to a macOS laptop](https://github.com/simonw/til/blob/main/heroku/pg-pull.md) - 2020-07-10
* [Upgrading a Heroku PostgreSQL database with pg:copy](https://github.com/simonw/til/blob/main/heroku/pg-upgrade.md) - 2020-07-20
* [Programatically accessing Heroku PostgreSQL from GitHub Actions](https://github.com/simonw/til/blob/main/heroku/programatic-access-postgresql.md) - 2020-08-18

## javascript

* [Implementing a "copy to clipboard" button](https://github.com/simonw/til/blob/main/javascript/copy-button.md) - 2020-07-23
* [Working around the size limit for nodeValue in the DOM](https://github.com/simonw/til/blob/main/javascript/working-around-nodevalue-size-limit.md) - 2020-08-21
* [Dynamically loading multiple assets with a callback](https://github.com/simonw/til/blob/main/javascript/dynamically-loading-assets.md) - 2020-08-21
* [Minifying JavaScript with npx uglify-js](https://github.com/simonw/til/blob/main/javascript/minifying-uglify-npx.md) - 2020-08-30
* [Manipulating query strings with URLSearchParams](https://github.com/simonw/til/blob/main/javascript/manipulating-query-params.md) - 2020-10-04
* [Writing JavaScript that responds to media queries](https://github.com/simonw/til/blob/main/javascript/javascript-that-responds-to-media-queries.md) - 2020-10-21
* [Dropdown menu with details summary](https://github.com/simonw/til/blob/main/javascript/dropdown-menu-with-details-summary.md) - 2020-10-31
* [Using Jest without a package.json](https://github.com/simonw/til/blob/main/javascript/jest-without-package-json.md) - 2020-12-30
* [Scroll page to form if there are errors](https://github.com/simonw/til/blob/main/javascript/scroll-to-form-if-errors.md) - 2021-05-08
* [Preventing double form submissions with JavaScript](https://github.com/simonw/til/blob/main/javascript/preventing-double-form-submission.md) - 2021-07-08
* [Loading lit from Skypack](https://github.com/simonw/til/blob/main/javascript/lit-with-skypack.md) - 2021-09-21
* [Using Tesseract.js to OCR every image on a page](https://github.com/simonw/til/blob/main/javascript/tesseract-ocr-javascript.md) - 2021-11-09
* [JavaScript date objects](https://github.com/simonw/til/blob/main/javascript/javascript-date-objects.md) - 2022-01-16

## django

* [PostgreSQL full-text search in the Django Admin](https://github.com/simonw/til/blob/main/django/postgresql-full-text-search-admin.md) - 2020-07-25
* [Adding extra read-only information to a Django admin change page](https://github.com/simonw/til/blob/main/django/extra-read-only-admin-information.md) - 2021-02-25
* [Writing tests for the Django admin with pytest-django](https://github.com/simonw/til/blob/main/django/testing-django-admin-with-pytest.md) - 2021-03-02
* [Show the timezone for datetimes in the Django admin](https://github.com/simonw/til/blob/main/django/show-timezone-in-django-admin.md) - 2021-03-02
* [Pretty-printing all read-only JSON in the Django admin](https://github.com/simonw/til/blob/main/django/pretty-print-json-admin.md) - 2021-03-07
* [How to almost get facet counts in the Django admin](https://github.com/simonw/til/blob/main/django/almost-facet-counts-django-admin.md) - 2021-03-11
* [Efficient bulk deletions in Django](https://github.com/simonw/til/blob/main/django/efficient-bulk-deletions-in-django.md) - 2021-04-09
* [Enabling the fuzzystrmatch extension in PostgreSQL with a Django migration](https://github.com/simonw/til/blob/main/django/migration-postgresql-fuzzystrmatch.md) - 2021-04-18
* [Usable horizontal scrollbars in the Django admin for mouse users](https://github.com/simonw/til/blob/main/django/django-admin-horizontal-scroll.md) - 2021-04-20
* [Filter by comma-separated values in the Django admin](https://github.com/simonw/til/blob/main/django/filter-by-comma-separated-values.md) - 2021-04-21
* [Django Admin action for exporting selected rows as CSV](https://github.com/simonw/til/blob/main/django/export-csv-from-django-admin.md) - 2021-04-25
* [migrations.RunSQL.noop for reversible SQL migrations](https://github.com/simonw/til/blob/main/django/migrations-runsql-noop.md) - 2021-05-02
* [Enabling a gin index for faster LIKE queries](https://github.com/simonw/til/blob/main/django/enabling-gin-index.md) - 2021-05-16
* [Django data migration using a PostgreSQL CTE](https://github.com/simonw/til/blob/main/django/migration-using-cte.md) - 2021-05-17

## docker

* [Attaching a bash shell to a running Docker container](https://github.com/simonw/til/blob/main/docker/attach-bash-to-running-container.md) - 2020-08-10
* [Running gdb against a Python process in a running Docker container](https://github.com/simonw/til/blob/main/docker/gdb-python-docker.md) - 2021-03-21
* [Installing packages from Debian unstable in a Docker image based on stable](https://github.com/simonw/til/blob/main/docker/debian-unstable-packages.md) - 2021-03-22
* [Docker Compose for Django development](https://github.com/simonw/til/blob/main/docker/docker-compose-for-django-development.md) - 2021-05-24

## homebrew

* [Packaging a Python CLI tool for Homebrew](https://github.com/simonw/til/blob/main/homebrew/packaging-python-cli-for-homebrew.md) - 2020-08-11
* [Browsing your local git checkout of homebrew-core](https://github.com/simonw/til/blob/main/homebrew/homebrew-core-local-git-checkout.md) - 2020-08-27
* [Upgrading Python Homebrew packages using pip](https://github.com/simonw/til/blob/main/homebrew/upgrading-python-homebrew-packages.md) - 2020-10-14
* [Running a MySQL server using Homebrew](https://github.com/simonw/til/blob/main/homebrew/mysql-homebrew.md) - 2021-06-11

## zsh

* [Customizing my zsh prompt](https://github.com/simonw/til/blob/main/zsh/custom-zsh-prompt.md) - 2020-08-12

## readthedocs

* [Pointing a custom subdomain at Read the Docs](https://github.com/simonw/til/blob/main/readthedocs/custom-subdomain.md) - 2020-08-14
* [Read the Docs Search API](https://github.com/simonw/til/blob/main/readthedocs/readthedocs-search-api.md) - 2020-08-16
* [Using custom Sphinx templates on Read the Docs](https://github.com/simonw/til/blob/main/readthedocs/custom-sphinx-templates.md) - 2020-12-07
* [Promoting the stable version of the documentation using rel=canonical](https://github.com/simonw/til/blob/main/readthedocs/documentation-seo-canonical.md) - 2022-01-20
* [Linking from /latest/ to /stable/ on Read The Docs](https://github.com/simonw/til/blob/main/readthedocs/link-from-latest-to-stable.md) - 2022-01-20

## ics

* [Providing a "subscribe in Google Calendar" link for an ics feed](https://github.com/simonw/til/blob/main/ics/google-calendar-ics-subscribe-link.md) - 2020-08-21

## svg

* [Creating a dynamic line chart with SVG](https://github.com/simonw/til/blob/main/svg/dynamic-line-chart.md) - 2020-08-22

## linux

* [Piping echo to a file owned by root using sudo and tee](https://github.com/simonw/til/blob/main/linux/echo-pipe-to-file-su.md) - 2020-08-24
* [Basic strace to see what a process is doing](https://github.com/simonw/til/blob/main/linux/basic-strace.md) - 2020-09-07

## jq

* [Converting Airtable JSON for use with sqlite-utils using jq](https://github.com/simonw/til/blob/main/jq/reformatting-airtable-json.md) - 2020-08-28
* [Loading radio.garden into SQLite using jq](https://github.com/simonw/til/blob/main/jq/radio-garden-jq.md) - 2021-02-17
* [Flattening nested JSON objects with jq](https://github.com/simonw/til/blob/main/jq/flatten-nested-json-objects-jq.md) - 2021-03-11
* [Converting no-decimal-point latitudes and longitudes using jq](https://github.com/simonw/til/blob/main/jq/convert-no-decimal-point-latitude-jq.md) - 2021-03-11
* [Turning an array of arrays into objects with jq](https://github.com/simonw/til/blob/main/jq/array-of-array-to-objects.md) - 2021-05-25
* [Extracting objects recursively with jq](https://github.com/simonw/til/blob/main/jq/extracting-objects-recursively.md) - 2021-07-24

## bash

* [Looping over comma-separated values in Bash](https://github.com/simonw/til/blob/main/bash/loop-over-csv.md) - 2020-09-01
* [Escaping strings in Bash using !:q](https://github.com/simonw/til/blob/main/bash/escaping-a-string.md) - 2020-10-01
* [Escaping a SQL query to use with curl and Datasette](https://github.com/simonw/til/blob/main/bash/escaping-sql-for-curl-to-datasette.md) - 2020-12-08
* [Skipping CSV rows with odd numbers of quotes using ripgrep](https://github.com/simonw/til/blob/main/bash/skip-csv-rows-with-odd-numbers.md) - 2020-12-11
* [Finding CSV files that start with a BOM using ripgrep](https://github.com/simonw/til/blob/main/bash/finding-bom-csv-files-with-ripgrep.md) - 2021-05-28

## typescript

* [Very basic tsc usage](https://github.com/simonw/til/blob/main/typescript/basic-tsc.md) - 2020-09-06

## aws

* [Display EC2 instance costs per month](https://github.com/simonw/til/blob/main/aws/instance-costs-per-month.md) - 2020-09-06
* [Recovering data from AWS Lightsail using EC2](https://github.com/simonw/til/blob/main/aws/recovering-lightsail-data.md) - 2021-01-16
* [Adding a CORS policy to an S3 bucket](https://github.com/simonw/til/blob/main/aws/s3-cors.md) - 2022-01-04
* [Helper function for pagination using AWS boto3](https://github.com/simonw/til/blob/main/aws/helper-for-boto-aws-pagination.md) - 2022-01-19

## jinja

* [Turning on Jinja autoescaping when using Template() directly](https://github.com/simonw/til/blob/main/jinja/autoescape-template.md) - 2020-09-18

## selenium

* [Installing Selenium for Python on macOS with ChromeDriver](https://github.com/simonw/til/blob/main/selenium/selenium-python-macos.md) - 2020-10-02
* [Using async/await in JavaScript in Selenium](https://github.com/simonw/til/blob/main/selenium/async-javascript-in-selenium.md) - 2020-10-02

## digitalocean

* [Running Datasette on DigitalOcean App Platform](https://github.com/simonw/til/blob/main/digitalocean/datasette-on-digitalocean-app-platform.md) - 2020-10-06

## datasette

* [Redirects for Datasette](https://github.com/simonw/til/blob/main/datasette/redirects-for-datasette.md) - 2020-11-25
* [Serving MBTiles with datasette-media](https://github.com/simonw/til/blob/main/datasette/serving-mbtiles.md) - 2021-02-03
* [Querying for GitHub issues open for less than 60 seconds](https://github.com/simonw/til/blob/main/datasette/issues-open-for-less-than-x-seconds.md) - 2021-03-12
* [Running Datasette on Replit](https://github.com/simonw/til/blob/main/datasette/datasette-on-replit.md) - 2021-05-02
* [Searching all columns of a table in Datasette](https://github.com/simonw/til/blob/main/datasette/search-all-columns-trick.md) - 2021-08-23
* [Reusing an existing Click tool with register_commands](https://github.com/simonw/til/blob/main/datasette/reuse-click-for-register-commands.md) - 2021-11-29

## jupyter

* [Embedding JavaScript in a Jupyter notebook](https://github.com/simonw/til/blob/main/jupyter/javascript-in-a-jupyter-notebook.md) - 2021-01-22

## cookiecutter

* [Testing cookiecutter templates with pytest](https://github.com/simonw/til/blob/main/cookiecutter/pytest-for-cookiecutter.md) - 2021-01-27
* [Conditionally creating directories in cookiecutter](https://github.com/simonw/til/blob/main/cookiecutter/conditionally-creating-directories.md) - 2021-01-27

## gis

* [Downloading MapZen elevation tiles](https://github.com/simonw/til/blob/main/gis/mapzen-elevation-tiles.md) - 2021-02-04

## sphinx

* [Using sphinx.ext.extlinks for issue links](https://github.com/simonw/til/blob/main/sphinx/sphinx-ext-extlinks.md) - 2021-02-17
* [Adding Sphinx autodoc to a project, and configuring Read The Docs to build it](https://github.com/simonw/til/blob/main/sphinx/sphinx-autodoc.md) - 2021-08-10

## postgresql

* [Show the SQL schema for a PostgreSQL database](https://github.com/simonw/til/blob/main/postgresql/show-schema.md) - 2021-02-23
* [Granting a PostgreSQL user read-only access to some tables](https://github.com/simonw/til/blob/main/postgresql/read-only-postgresql-user.md) - 2021-02-26
* [Closest locations to a point](https://github.com/simonw/til/blob/main/postgresql/closest-locations-to-a-point.md) - 2021-03-22
* [Using unnest() to use a comma-separated string as the input to an IN query](https://github.com/simonw/til/blob/main/postgresql/unnest-csv.md) - 2021-04-10
* [Using json_extract_path in PostgreSQL](https://github.com/simonw/til/blob/main/postgresql/json-extract-path.md) - 2021-04-13
* [Constructing GeoJSON in PostgreSQL](https://github.com/simonw/til/blob/main/postgresql/constructing-geojson-in-postgresql.md) - 2021-04-24

## mediawiki

* [How to run MediaWiki with SQLite on a macOS laptop](https://github.com/simonw/til/blob/main/mediawiki/mediawiki-sqlite-macos.md) - 2021-03-06

## azure

* [Writing an Azure Function that serves all traffic to a subdomain](https://github.com/simonw/til/blob/main/azure/all-traffic-to-subdomain.md) - 2021-03-27

## vscode

* [Language-specific indentation settings in VS Code](https://github.com/simonw/til/blob/main/vscode/language-specific-indentation-settings.md) - 2021-04-04
* [Search and replace with regular expressions in VS Code](https://github.com/simonw/til/blob/main/vscode/vs-code-regular-expressions.md) - 2021-08-02

## wikipedia

* [The Wikipedia page stats API](https://github.com/simonw/til/blob/main/wikipedia/page-stats-api.md) - 2021-05-13

## vega

* [Vega-Lite bar charts in the same order as the data](https://github.com/simonw/til/blob/main/vega/bar-chart-ordering.md) - 2021-05-15

## spatialite

* [KNN queries with SpatiaLite](https://github.com/simonw/til/blob/main/spatialite/knn.md) - 2021-05-16
* [Creating a minimal SpatiaLite database with Python](https://github.com/simonw/til/blob/main/spatialite/minimal-spatialite-database-in-python.md) - 2021-12-17

## sql

* [Finding duplicate records by matching name and nearby distance](https://github.com/simonw/til/blob/main/sql/finding-dupes-by-name-and-distance.md) - 2021-05-19
* [Building a Markdown summary of Django group permissions](https://github.com/simonw/til/blob/main/sql/django-group-permissions-markdown.md) - 2021-06-03
* [Cumulative total over time in SQL](https://github.com/simonw/til/blob/main/sql/cumulative-total-over-time.md) - 2021-09-13

## amplitude

* [Exporting Amplitude events to SQLite](https://github.com/simonw/til/blob/main/amplitude/export-events-to-datasette.md) - 2021-06-06

## vim

* [Mouse support in vim](https://github.com/simonw/til/blob/main/vim/mouse-support-in-vim.md) - 2021-06-19

## reddit

* [Scraping Reddit via their JSON API](https://github.com/simonw/til/blob/main/reddit/scraping-reddit-json.md) - 2021-06-21

## nginx

* [Using nginx to proxy to a Unix domain socket](https://github.com/simonw/til/blob/main/nginx/proxy-domain-sockets.md) - 2021-07-10

## tesseract

* [Using the tesseract CLI tool](https://github.com/simonw/til/blob/main/tesseract/tesseract-cli.md) - 2021-07-18

## imagemagick

* [Set a GIF to loop using ImageMagick](https://github.com/simonw/til/blob/main/imagemagick/set-a-gif-to-loop.md) - 2021-08-03
* [Compressing an animated GIF with gifsicle or ImageMagick mogrify](https://github.com/simonw/til/blob/main/imagemagick/compress-animated-gif.md) - 2021-08-05

## observable-plot

* [Histogram with tooltips in Observable Plot](https://github.com/simonw/til/blob/main/observable-plot/histogram-with-tooltips.md) - 2021-08-21

## purpleair

* [Calculating the AQI based on the Purple Air API for a sensor](https://github.com/simonw/til/blob/main/purpleair/purple-air-aqi.md) - 2021-08-31

## electron

* [Using the Chrome DevTools console as a REPL for an Electron app](https://github.com/simonw/til/blob/main/electron/electron-debugger-console.md) - 2021-08-31
* [Open external links in an Electron app using the system browser](https://github.com/simonw/til/blob/main/electron/electron-external-links-system-browser.md) - 2021-09-02
* [Signing and notarizing an Electron app for distribution using GitHub Actions](https://github.com/simonw/til/blob/main/electron/sign-notarize-electron-macos.md) - 2021-09-08
* [Bundling Python inside an Electron app](https://github.com/simonw/til/blob/main/electron/python-inside-electron.md) - 2021-09-08
* [Configuring auto-update for an Electron app](https://github.com/simonw/til/blob/main/electron/electrion-auto-update.md) - 2021-09-13

## googlecloud

* [Publishing to a public Google Cloud bucket with gsutil](https://github.com/simonw/til/blob/main/googlecloud/gsutil-bucket.md) - 2021-09-20

## git

* [Removing a git commit and force pushing to remove it from history](https://github.com/simonw/til/blob/main/git/remove-commit-and-force-push.md) - 2021-10-22

## web-components

* [Understanding Kristofer Joseph's Single File Web Component](https://github.com/simonw/til/blob/main/web-components/understanding-single-file-web-component.md) - 2021-10-27

## kubernetes

* [Basic Datasette in Kubernetes](https://github.com/simonw/til/blob/main/kubernetes/basic-datasette-in-kubernetes.md) - 2021-11-05
* [kubectl proxy](https://github.com/simonw/til/blob/main/kubernetes/kubectl-proxy.md) - 2021-12-28

## deno

* [Annotated code for a demo of WebSocket chat in Deno Deploy](https://github.com/simonw/til/blob/main/deno/annotated-deno-deploy-demo.md) - 2021-11-06

## fly

* [Assigning a custom subdomain to a Fly app](https://github.com/simonw/til/blob/main/fly/custom-subdomain-fly.md) - 2021-11-20
* [Using the undocumented Fly GraphQL API](https://github.com/simonw/til/blob/main/fly/undocumented-graphql-api.md) - 2022-01-21

## caddy

* [Pausing traffic and retrying in Caddy](https://github.com/simonw/til/blob/main/caddy/pause-retry-traffic.md) - 2021-11-24

## npm

* [Publishing a Web Component to npm](https://github.com/simonw/til/blob/main/npm/publish-web-component.md) - 2021-11-28
* [Annotated package.json for idb-keyval](https://github.com/simonw/til/blob/main/npm/annotated-package-json.md) - 2022-02-10

## pluggy

* [Registering the same Pluggy hook multiple times in a single file](https://github.com/simonw/til/blob/main/pluggy/multiple-hooks-same-file.md) - 2021-12-16

## cloudflare

* [Adding a robots.txt using Cloudflare workers](https://github.com/simonw/til/blob/main/cloudflare/robots-txt-cloudflare-workers.md) - 2021-12-21

## webauthn

* [WebAuthn browser support](https://github.com/simonw/til/blob/main/webauthn/webauthn-browser-support.md) - 2021-12-29

## pixelmator

* [Pixel editing a favicon with Pixelmator](https://github.com/simonw/til/blob/main/pixelmator/pixel-editing-favicon.md) - 2022-01-20

## graphql

* [get-graphql-schema](https://github.com/simonw/til/blob/main/graphql/get-graphql-schema.md) - 2022-02-01
<!-- index ends -->
