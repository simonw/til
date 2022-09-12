# Optimizing PNGs in GitHub Actions using Oxipng

My [datasette-screenshots](https://github.com/simonw/datasette-screenshots) repository generates screenshots of [Datasette](https://datasette.io/) using my [shot-scraper](https://github.com/simonw/shot-scraper) tool, for people who need them for articles or similar.

Jacob Weisz [suggested](https://github.com/simonw/datasette-screenshots/issues/1) optimizing these images as they were quite big. I want them to be as high quality as possible (I even take them using `--retina` mode), but that didn't mean I couldn't use lossless compression on them.

I often use [squoosh.app](https://squoosh.app/) to run a version of [Oxipng](https://github.com/shssoichiro/oxipng) compiled to WebAssembly in my browser. I decided to figure out how to run that same program in GitHub Actions.

## Installing Rust apps using Cargo

Surprisingly there [isn't yet a packaged version](https://github.com/shssoichiro/oxipng/issues/69) of Oxipng for Ubuntu - so I needed another way of installing it.

The [project README suggests](https://github.com/shssoichiro/oxipng/blob/master/README.md#installing) installing it using `cargo install oxipng`.

I used the [tmate trick](https://til.simonwillison.net/github-actions/debug-tmate) to try that out in a GitHub Actions worker - the `cargo` command is available by default but it took over a minute to fetch and compile all of the dependencies.

I didn't want to do this on every run, so I looked into ways to cache the built program. Thankfully the `actions/cache` action documents [how to use it with Rust](https://github.com/actions/cache/blob/main/examples.md#rust---cargo).

The full recipe for installing Oxipng in GitHub Actions looks like this:

```yaml
    - name: Cache Oxipng
      uses: actions/cache@v3
      with:
        path: ~/.cargo/
        key: ${{ runner.os }}-cargo
    - name: Install Oxipng
      run: |
        which oxipng || cargo install oxipng
```

The first time the action runs it does a full compile of Oxipng - but on subsequent runs the `which oxipng` command succeeds and skips the `cargo install` step entirely.

## Running Oxipng in an Action

All of the PNGs that I wanted to optimize were in the root of my checkout, so I added this step:

```yaml
    - name: Optimize PNGs
      run: |-
        oxipng -o 4 -i 0 --strip safe *.png
```
The `-o 4` is the highest recommended level of optimization.

`-i 0` causes it to remove interlacing - "Interlacing can add 25-50% to the size of an optimized image" according to the README.

`--strip safe` strips out any image metadata that is guaranteed not to affect how the image is rendered.

Oxipng updates the specified images in place, hence the `*.png` at the end.

## Testing this in a branch first

I tested this all in a branch first so that I could see if it was working correctly.

Since my workflow usually pushes any changed files back to the same GitHub repository, I added a check to that step which caused it to only run on pushes to the `main` branch:

```yaml
    - name: Commit and push
      if: github.ref == 'refs/heads/main'
      run: |-
        git config user.name "Automated"
        ...
```
But I wanted to preview the generated images - so I added this step in the branch to save them to an artifact zip file that I could then inspect:

```yaml
    - name: Artifacts
      uses: actions/upload-artifact@v3
      with:
        name: screenshots
        path: "*.png"
```

Once I got it working, I squash-merged [this pull request](https://github.com/simonw/datasette-screenshots/pull/2) back into `main`.

## The result

Oxipng worked really well!

It reduced the size of all three of my screenshots:

- [faceting.png](https://github.com/simonw/datasette-screenshots/blob/main/faceting.png) from 305KB to 211KB
- [global-power-plants.png](https://github.com/simonw/datasette-screenshots/blob/main/global-power-plants.png) from 1.14MB to 770KB
- [sql-query.png](https://github.com/simonw/datasette-screenshots/blob/main/sql-query.png) from 235KB to 169KB

[This commit](https://github.com/simonw/datasette-screenshots/commit/0b7ccd8fe1c0fdc3714d768659a88bae1fa69ca4) shows the difference and lets you compare both images.
