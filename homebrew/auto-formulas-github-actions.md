# Automatically maintaining Homebrew formulas using GitHub Actions

I previously wrote about [Packaging a Python CLI tool for Homebrew](https://til.simonwillison.net/homebrew/packaging-python-cli-for-homebrew). I've now figured out a pattern for automatically updating those formulas over time, using GitHub Actions.

## Background on Homebrew formulas and taps

A [Homebrew](https://brew.sh/) formula tells Homebrew how to install a particular piece of software, along with all of its dependencies. [Python for Formula Authors](https://docs.brew.sh/Python-for-Formula-Authors) explains how these work.

I use it to package Python command-line tools so they can be installed by Homebrew users who aren't familiar with `pip` and `pipx` and other parts of the Python packaging ecosystem.

Homebrew has a nice pattern for this: each Python tool gets its own virtual environment with stable, tested versions of its dependencies. This means you can be sure they won't clash with each other.

When you run `brew install sqlite-utils` you install packages using formulas from the [homebrew-core](https://github.com/Homebrew/homebrew-core) repository. This is managed by the Homebrew team and any updates to formulas need to go through pull requests to them.

You can also create a "tap" - a separate GitHub repository with formulas that users can then install directly, without needing to go through that review process.

A tap is simply a GitHub repository with the name `username/homebrew-something` that contains a `Formula` directory with formulas in it.

I wanted to make my rapidly evolving family of [LLM](https://llm.datasette.io/) CLI tools easy to install. There are four of those at the moment: `llm`, `strip-tags`, `symbex` and `ttok`.

I created a new repository to act as a tap for them: https://github.com/simonw/homebrew-llm

This means my tools can now be installed like this:
```bash
brew install simonw/llm/llm
brew install simonw/llm/strip-tags
brew install simonw/llm/symbex
brew install simonw/llm/ttok
```
## A simple formula

Here's the simplest of my formulas, for [symbex](https://github.com/simonw/symbex) - which currently only has a single package dependency, [Click](https://click.palletsprojects.com/):

```ruby
class Symbex < Formula
  include Language::Python::Virtualenv

  desc "Find the Python code for specified symbols"
  homepage "https://github.com/simonw/symbex"
  url "https://files.pythonhosted.org/packages/04/5c/b127cccf4454ba2db390395b6181684693194e7840e59afd705eec8ef6bb/symbex-0.6.tar.gz"
  sha256 "745499062c2c9d94fe9c6c51037d7d55bf44d6404df7d692ae12b9836595c850"

  depends_on "python3"

  resource "click" do
    url "https://files.pythonhosted.org/packages/59/87/84326af34517fca8c58418d148f2403df25303e02736832403587318e9e8/click-8.1.3.tar.gz"
    sha256 "7682dc8afb30297001674575ea00d1814d808d6a36af415a82bd481d37ba7b8e"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    assert_match "symbex, version", shell_output("#{bin}/symbex --version")
  end
end
```
Most of this is boiler-plate. The `url` tells it what Python package to download, then the `resource` blocks repeat that for the dependencies.

Importantly, dependencies need to be installed from `.tar.gz` source archives. Homebrew packaging culture doesn't like wheels.

## Generating the formula

I wrote about this in [Packaging a Python CLI tool for Homebrew](https://til.simonwillison.net/homebrew/packaging-python-cli-for-homebrew): there's a tool which can do almost all of the work of generating one of these formulas, including figuring out the URLs and SHA hashes for all of the dependencies.

You can run that tool in a fresh virtual environment like so:
```bash
pip install symbex homebrew-pypi-poet
poet -f symbex > symbex.rb
```
Here's what that produces:
```ruby                                        
class Symbex < Formula
  include Language::Python::Virtualenv

  desc "Shiny new formula"
  homepage "https://github.com/simonw/symbex"
  url "https://files.pythonhosted.org/packages/04/5c/b127cccf4454ba2db390395b6181684693194e7840e59afd705eec8ef6bb/symbex-0.6.tar.gz"
  sha256 "745499062c2c9d94fe9c6c51037d7d55bf44d6404df7d692ae12b9836595c850"

  depends_on "python3"

  resource "click" do
    url "https://files.pythonhosted.org/packages/59/87/84326af34517fca8c58418d148f2403df25303e02736832403587318e9e8/click-8.1.3.tar.gz"
    sha256 "7682dc8afb30297001674575ea00d1814d808d6a36af415a82bd481d37ba7b8e"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    false
  end
end
```
As you can see, it's almost exactly what you need - the only thing missing is the `desc` string and the implementation of that `test do` block.

## Generating the formula using GitHub Actions

I wanted a button I could click that would regenerate the formula for me.

I love using GitHub Actions for this kind of thing - see [Git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/).

After some iteration, I came up with this workflow definition - saved in [.github/workflows/symbex.yaml](https://github.com/simonw/homebrew-llm/blob/main/.github/workflows/symbex.yaml):

```yaml
name: Publish symbex

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  regenerate:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - name: Create a fresh virtual environment and generate formula
      run: |
        python3 -m venv venv
        source venv/bin/activate
        venv/bin/pip install symbex homebrew-pypi-poet
        poet -f symbex > Formula/symbex.rb
        deactivate
        rm -rf venv
    - name: Replace description and test
      run: |
        python3 -c "
        import re
        content = open('Formula/symbex.rb').read()
        content = re.sub(r'desc \"Shiny new formula\"', 'desc \"Find the Python code for specified symbols\"', content)
        content = re.sub(
            r'test do.*?end',
            'test do\\n    assert_match \"symbex, version\", shell_output(\"#{bin}/symbex --version\")\\n  end',
            content,
            flags=re.DOTALL
        )
        open('Formula/symbex.rb', 'w').write(content)
        "
        cat Formula/symbex.rb
    - name: Commit and push
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add -A
        timestamp=$(date -u)
        git commit -m "Update symbex: ${timestamp}" || exit 0
        git pull --rebase
        git push
```
The most interesting piece here is the "Replace description and test" block, which runs a little `python -c` shell one-liner to fix the two problems listed above.

The workflow then commits the result back to the repo.

This means any time I ship a new release of one of my Python packages I can head over to [simonw/homebrew-llm/actions](https://github.com/simonw/homebrew-llm/actions) and manually trigger the relevant workflow to update the formula in my tap.

## A Formula with Rust-compiled dependencies

The above pattern worked perfectly for `llm` and `strip-tags` and `symbex` - but it failed for `ttok`.

That's because `ttok` depends on the `tiktoken` package, and it turns out that needs a Rust compiler in order to be built from source.

I [eventually figured out](https://github.com/simonw/homebrew-llm/issues/1) a solution for this - I added those build dependencies to the formula like this:

```ruby
  depends_on "python3"
  # To build tiktoken:
  depends_on "pkg-config" => :build
  depends_on "rust" => :build
```

I also updated my `ttok.rb` workflow to also [add that block](https://github.com/simonw/homebrew-llm/blob/baa67dd2552f3b5334d05d8fbbabc7d3e13956c4/.github/workflows/ttok.yaml#L28-L33) to the formula that was generated by the `poet` command.
