# Testing Electron apps with Playwright and GitHub Actions

Yesterday [I figured out (issue 133)](https://github.com/simonw/datasette-app/issues/133) how to use Playwright to run tests against my Electron app, and then execute those tests in CI using GitHub Actions, for my [datasett-app](https://github.com/simonw/datasette-app) repo for my [Datasette Desktop](https://datasette.io/desktop) macOS application.

## Installing @playwright/test

You need to install the `@playwright/test` package. You can do that like so:

    npm i -D @playwright/test

This adds it to `devDependencies` in your `package.json`, something like this:

```
  "devDependencies": {
    "@playwright/test": "^1.23.2",
```

## Writing a test

I dropped the following into a `test/spec.mjs` file:

```javascript
import { test, expect } from '@playwright/test';
import { _electron } from 'playwright';

test('App launches and quits', async () => {
  const app = await _electron.launch({args: ['main.js']);
  const window = await app.firstWindow();
  await expect(await window.title()).toContain('Loading');
  await app.close();
});
```
The `.mjs` extension is necessary in order to use `import`, since it lets Node.js know that this file is a JavaScript module.

The test can be run using `playwright test`.

I later added it to my `package.json` section like this:
```json
  "scripts": {
    "test": "playwright test"
  }
```
Now I can run the Playwright tests using `npm test`.

## Recording video of the tests

Recording videos of the test runs turns out to be easy: change the `_electron.launch()` line to look like this:

```javascript
  const app = await _electron.launch({
    args: ['main.js'],
    recordVideo: {dir: 'test-videos'}
  });
```
This creates the videos as `.webm` files in the `test-videos` directory.

These videos can be opened in Chrome, or can be converted to `mp4` using `ffmpeg` (available on macOS via `brew install ffmpeg`):

    ffmpeg -i bc74c2a51bd91fe6f6cb815e6b99b6c7.webm bc74c2a51bd91fe6f6cb815e6b99b6c7.mp4

Converting to `.mp4` means you can drag and drop them onto a GitHub Issues thread and get an embedded video player. [Here's an example](https://github.com/simonw/datasette-app/issues/133#issuecomment-1182530789) I recorded.

## Custom timeouts

Playwright has a default 30s timeout on every action it takes. This turned out to be a bit too short for one of my tests, which installs a Python interpreter and a bunch of Python packages and can take 57s. Here's how I fixed that so the test could pass:

```javascript
test('App launches and quits', async () => {
  // This disables the global 30s timeout
  test.setTimeout(0);
  const app = await _electron.launch({
    args: ['main.js'],
    recordVideo: {dir: 'test-videos'}
  });
  const window = await app.firstWindow();
  // This sets a timeout of 90s for the page to load and the
  // element with id="run-sql-link" to appear in the DOM:
  await window.waitForSelector('#run-sql-link', {
    timeout: 90000
  });
  await app.close();
});
```

## Running it in GitHub Actions

I'm using the `macos-latest` image in my GitHub Actions workflow. The relevant configuration in my `.github/workflows/test.yml` file looks like this:

```yaml
name: Test

on: push

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure Node caching
        uses: actions/cache@v3
        env:
          cache-name: cache-node-modules
        with:
          path: ~/.npm
          key: ${{ runner.os }}-build-${{ env.cache-name }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-build-${{ env.cache-name }}-
            ${{ runner.os }}-build-
            ${{ runner.os }}-
      - name: Install Node dependencies
        run: npm install
      - name: Run tests
        run: npm test
        timeout-minutes: 5
      - name: Upload test videos
        uses: actions/upload-artifact@v3
        with:
          name: test-videos
          path: test-videos/
```
This workflow configures NPM caching to avoid downloading everything every time, installs the dependencies, runs the tests, and then uploads the videos at the end.

Those videos end up attached to the workflow run as an artifact that can be downloaded and viewed locally.

