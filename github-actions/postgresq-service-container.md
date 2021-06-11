# Running tests against PostgreSQL in a service container

I wanted to run some Django tests - using `pytest-django` and with Django configured to pick up the `DATABASE_URL` environment variable via [dj-database-url](https://github.com/jacobian/dj-database-url) - against a PostgreSQL server running in GitHub Actions.

It took a while to figure out the right pattern. The trick was to define a `postgres:` service and then set the `DATABASE_URL` environment variable to the following:

    postgres://postgres:postgres@127.0.0.1:${{ job.services.postgres.ports['5432'] }}/dbname

Here's my full `.github/workflows/test.yml`:

```yaml
name: Run tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: dbname
        options:
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
        ports:
        - 5432:5432
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - uses: actions/cache@v2
      name: Configure pip caching
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@127.0.0.1:${{ job.services.postgres.ports['5432'] }}/dbname
      run: |
        cd myproject
        pytest
```

## And against MySQL

I had to figure this out against MySQL as well for `db-to-sqlite` - here's [the workflow test.yml file](https://github.com/simonw/db-to-sqlite/blob/1.4/.github/workflows/test.yml) I ended up with. Key extract here:

```yaml
    services:
      mysql:
        image: mysql
        env:
          MYSQL_ALLOW_EMPTY_PASSWORD: yes
          MYSQL_DATABASE: test_db_to_sqlite
        options: >-
          --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
        ports:
          - 3306:3306
    # ...
    - name: Run tests
      env:
        MYSQL_TEST_DB_CONNECTION: mysql://root@127.0.0.1:${{ job.services.mysql.ports['3306'] }}/test_db_to_sqlite
      run: pytest -vv
```
