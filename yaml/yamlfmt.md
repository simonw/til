# Auto-formatting YAML files with yamlfmt

I decided to see if there was an equivalent of [Black](https://pypi.org/project/black/) or [Prettier](https://prettier.io/) for YAML files. I found [yamlfmt](https://github.com/google/yamlfmt) from Google.

## Installation

They suggest this:
```bash
go install github.com/google/yamlfmt/cmd/yamlfmt@latest
```
This worked on my machine because I had Go installed via Homebrew (`go version go1.20.4 darwin/arm64` according to `go version`).

I wasn't sure where it had been installed - it turns out that if you don't have a `GOPATH` environment variable set then tools installed like this default to landing in `~/go/bin`.

If you don't have Go installed, you can instead download a compiled binary from [google/yamlfmt/releases](https://github.com/google/yamlfmt/releases).

## Usage

You need to pass files to it explicitly - unlike Black it doesn't just operate on everything in the current directory:

```bash
~/go/bin/yamlfmt .github/workflows/*.yml
```
The default format looked like this:
```yaml
name: Publish Python Package
on:
  release:
    types: [created]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
```

## Configuration

It removed some of my whitespace (I had newlines in front of those `on:` and `jobs:` keys), and I _really_ didn't like the way it handled lists - adding an unnecessary additional two spaces of indent before each list item.

You can pass it [configuration to fix this](https://github.com/google/yamlfmt/blob/main/docs/config-file.md#basic-formatter).

Here's what I ended up with:
```bash
~/go/bin/yamlfmt \
  -formatter indentless_arrays=true,retain_line_breaks=true \
  .github/workflows/*.yml
```
The order of this matters: you can't put `-formatter` after the list of files or it will be silently ignored.

This gave me:
```yaml
name: Publish Python Package

on:
  release:
    types: [created]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
```
There's also a mechanism where you can put configuration options in a `.yamlfmt` file, or a file passed using `--conf` - those are [explained here](https://github.com/google/yamlfmt/blob/main/docs/config-file.md).
