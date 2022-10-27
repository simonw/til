# Deploying a live Datasette demo when the tests pass

I've implemented this pattern a bunch of times now - here's the version I've settled on for my [datasette-auth0 plugin](https://github.com/simonw/datasette-auth0) repository.

For publishing to Cloud Run, it needs two GitHub Actions secrets to be configured: `GCP_SA_EMAIL` and `GCP_SA_KEY`.

See below for publishing to Vercel.

In `.github/workflows/test.yml`:

```yaml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.7", "3.8", "3.9", "3.10", "3.11"]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - uses: actions/cache@v3
      name: Configure pip caching
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/setup.py') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    - name: Install dependencies
      run: |
        pip install -e '.[test]'
    - name: Run tests
      run: |
        pytest
  deploy_demo:
    runs-on: ubuntu-latest
    needs: [test]
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: pip
        cache-dependency-path: "**/setup.py"
    - name: Install datasette
      run: pip install datasette
    - name: Set up Cloud Run
      uses: google-github-actions/setup-gcloud@v0
      with:
        version: '275.0.0'
        service_account_email: ${{ secrets.GCP_SA_EMAIL }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    - name: Deploy demo to Cloud Run
      env:
        CLIENT_SECRET: ${{ secrets.AUTH0_CLIENT_SECRET }}
      run: |-
        gcloud config set run/region us-central1
        gcloud config set project datasette-222320
        wget https://latest.datasette.io/fixtures.db
        datasette publish cloudrun fixtures.db \
        --install https://github.com/simonw/datasette-auth0/archive/$GITHUB_SHA.zip \
        --plugin-secret datasette-auth0 domain "datasette.us.auth0.com" \
        --plugin-secret datasette-auth0 client_id "n9eaHS0ckIsujoyZNZ1wVgcPevjAcAXn" \
        --plugin-secret datasette-auth0 client_secret "$CLIENT_SECRET" \
        --about "datasette-auth0" \
        --about_url "https://datasette.io/plugins/datasette-auth0" \
        --service datasette-auth0-demo
```
The first job called `test` runs the Python tests in the repo. The second `deploy_demo` block is where things get interesting.

```yaml
  deploy_demo:
    runs-on: ubuntu-latest
    needs: [test]
    if: github.ref == 'refs/heads/main'
```
The `needs: [test]` bit ensures this only runs if the tests pass first.

`if: github.ref == 'refs/heads/main'` causes the deploy to only run on pushes to the `main` branch.

The most interesting bit of the deploy command is this bit:
```
datasette publish cloudrun fixtures.db \
--install https://github.com/simonw/datasette-auth0/archive/$GITHUB_SHA.zip \
...
```
`$GITHUB_SHA` is the commit hash that triggered the wokrflow. The `--install` line there constructs a URL to the zip archive of that version from the GitHub repository - so that exact version will be treated as a plugin and installed as part of deploying the Datasette demo instance.

## Deploying to Vercel

[This example](https://github.com/simonw/datasette-hashed-urls/blob/659614c23cbc544915079c44b09b09b090400ff8/.github/workflows/test.yml) deploys to Vercel instead. The key difference is this:

```yaml
    - name: Install datasette
      run: pip install datasette datasette-publish-vercel
    - name: Deploy demo to Vercel
      env:
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
      run: |-
        wget https://latest.datasette.io/fixtures.db
        datasette publish vercel fixtures.db \
          --project datasette-hashed-urls \
          --install https://github.com/simonw/datasette-hashed-urls/archive/$GITHUB_SHA.zip \
          --token $VERCEL_TOKEN \
          --scope datasette
```
The `--token $VERCEL_TOKEN` passes a token created in the Vercel dashboard. I needed `--scope datasette` here because I was deploying to a Vercel team of that name - if deploying to your personal account you can leave this off.
