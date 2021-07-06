# Installing different PostgreSQL server versions in GitHub Actions

The GitHub Actions `ubuntu-latest` default runner currently includes an installation of PostgreSQL 13. The server is not running by default but you can interact with it like this:
```
$ /usr/lib/postgresql/13/bin/postgres --version
postgres (PostgreSQL) 13.3 (Ubuntu 13.3-1.pgdg20.04+1)
```
You can install alternative PostgreSQL versions by following the [PostgreSQL Ubuntu instructions](https://www.postgresql.org/download/linux/ubuntu/) - like this:
```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgresql-12
```
This works with `postgresql-10` and `postgresql-11` as well as `postgresql-12`.

I wanted to use a GitHub Actions matrix to run my tests against all four versions of PostgreSQL. Here's [my complete workflow](https://github.com/simonw/django-sql-dashboard/blob/1.0.1/.github/workflows/test.yml) - the relevant sections are below:
```yaml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        postgresql-version: [10, 11, 12, 13]
    steps:
    - name: Install PostgreSQL
      env:
        POSTGRESQL_VERSION: ${{ matrix.postgresql-version }}
      run: |
        sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
        sudo apt-get update
        sudo apt-get -y install "postgresql-$POSTGRESQL_VERSION"
    - name: Run tests
      env:
        POSTGRESQL_VERSION: ${{ matrix.postgresql-version }}
      run: |
        export POSTGRESQL_PATH="/usr/lib/postgresql/$POSTGRESQL_VERSION/bin/postgres"
        export INITDB_PATH="/usr/lib/postgresql/$POSTGRESQL_VERSION/bin/initdb"
        pytest
```
I modified my tests to call the `postgres` and `initdb` binaries specified by the `POSTGRESQL_PATH` and `INITDB_PATH` environment variables.
