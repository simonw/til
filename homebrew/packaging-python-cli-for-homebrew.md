# Packaging a Python CLI tool for Homebrew

I finally figured out how to package [Datasette](https://github.com/simonw/datasette) for installation with Homebrew. My package was accepted into Homebrew core, which means you can now install it like this:

    brew install datasette

Prior to being accepted, you needed to install it from my own Homebrew tap like this:

    brew install simonw/datasette/datasette
    # wait a bit...
    datasette --version

Here's my code that makes this work: https://github.com/simonw/homebrew-datasette

The [Python for Formula Authors](https://docs.brew.sh/Python-for-Formula-Authors) documentation provides useful background.

## Creating a "tap"

Homebrew taps are just naming conventions. Creating a tap is as simple as creating a GitHub repository with the `homebrew-` prefix. `https://github.com/simonw/homebrew-datasette` is the repo that gets tapped when someone runs `brew tap simonw/datasette`.

The repository needs a [Formula/](https://github.com/simonw/homebrew-datasette/tree/main/Formula) folder. This contains your formulas, which are Ruby `.rb` files.

## Creating the formula

The first working version of the `datasette.rb` formula can be seen here: https://github.com/simonw/homebrew-datasette/blob/e6b71b1aa308d7307f75a6458681fe49f5659098/Formula/datasette.rb

The shape of the formula is this:

```ruby
class Datasette < Formula
  include Language::Python::Virtualenv
  desc "An open source multi-tool for exploring and publishing data"
  homepage "https://datasette.io/"
  url "https://files.pythonhosted.org/packages/96/e2/abc76ee41d9895145e43323c591aa77f2b27959deb640278fc1a43f6b222/datasette-0.46.tar.gz"
  version "0.46"
  sha256 "eb5e5dcb8a0957ed1def841108576afb15a38ce61d222bf54a25d827999ad521"

  depends_on "python@3.8"

  resource "aiofiles" do
    url "https://files.pythonhosted.org/packages/2b/64/437053d6a4ba3b3eea1044131a25b458489320cb9609e19ac17261e4dc9b/aiofiles-0.5.0.tar.gz"
    sha256 "98e6bcfd1b50f97db4980e182ddd509b7cc35909e903a8fe50d8849e02d815af"
  end

  # ... many more resource blocks ...

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"datasette", "--help"
  end
end
```
Every dependency needs to be listed as a resource. They all need to be available as `sdist` packages - I made sure all of my dependencies had an `sdist` on PyPI.

Then I used the [homebrew-pypi-poet](https://github.com/tdsmith/homebrew-pypi-poet) tool to construct the formula.

This **must be installed in a fresh virtual environment**. If you install it into an environment with other packages those packages will be included in the formula even if they are not used by that tool.

Create a fresh virtual environment like this:

```bash
cd /tmp
mkdir fresh
cd fresh
python -m venv venv
source venv/bin/activate
```
I'll demonstrate installing [strip-tags](https://github.com/simonw/strip-tags) here since it is not yet packaged for Homebrew, unlike Datasette.

Install both `strip-tags` and the `homebrew-pypi-poet` package:
```bash
pip install strip-tags homebrew-pypi-poet
```
Next, run `poet -f` to create the formula:
```bash
poet -f strip-tags > strip-tags.rb
```
You can test installing the formula like this:
```bash
HOMEBREW_NO_INSTALL_FROM_API=1 brew install --build-from-source --verbose --debug strip-tags.rb
```

If this works, you'll be able to run `strip-tags` - use `which strip-tags` to check where it was installed.

Now add `strip-tags.rb` to the `Formula` folder in your repository, then do `brew uninstall strip-tags` and then `brew install yourname/yourtap/strip-tags` to test installing from the formula in the GitHub repository.

## Implementing the test block

https://docs.brew.sh/Formula-Cookbook#add-a-test-to-the-formula says:

> We want tests that don't require any user input and test the basic functionality of the application. For example `foo build-foo input.foo` is a good test and (despite their widespread use) `foo --version` and `foo --help` are bad tests. However, a bad test is better than no test at all.

Here's the test block I ended up using for Datasette:

```ruby
  test do
    assert_match "15", shell_output("#{bin}/datasette --get '/:memory:.csv?sql=select+3*5'")
    assert_match "<title>Datasette:", shell_output("#{bin}/datasette --get '/'")
  end
```

And here's my test for `sqlite-utils`:

```ruby
  test do
    assert_match "15", shell_output("#{bin}/sqlite-utils :memory: 'select 3 * 5'")
  end
```
And for `llm`:
```ruby
  test do
    assert_match "llm, version", shell_output("#{bin}/llm --version")
  end
```

## Iterating on this

I found running `brew install datasette`, seeing if it worked, then running `brew uninstall datasette`, modifying the `.rb` file on GitHub and running `datasette install datasette` again worked fine during development.

If you get any errors, `brew install datasette --debug` shows more information and drops you into an interactive debugging session when an error occurs.

## Submitting to homebrew-core

If your package gets accepted into [homebrew-core](https://github.com/Homebrew/homebrew-core) users will be able to install it just by running `brew install packagename`.

More importantly: Homebrew maintain "bottle" versions of all of those core packages. These are pre-compiled bundles of assets (a separate `.tar.gz` for each recent macOS operating system) which install MUCH faster than regular Homebrew, which has to compile everything.

The Homebrew [CONTRIBUTING](https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md) document tells you how to do this. For Python packages the import things to remember are:

- Add a `license`, e.g. `license "Apache 2.0" - [example](https://github.com/Homebrew/homebrew-core/blob/99c3304fbe89996ae8d72b5357b14fbe8983680c/Formula/datasette.rb#L7).
- Run `brew audit --new-formula datasette` and fix any warnings ([see here](https://github.com/simonw/homebrew-datasette/issues/7)).
- Submit a PR with the new formula and a title of e.g. `datasette 0.47.1 (new formula)` - here's [mine for Datasette](https://github.com/Homebrew/homebrew-core/pull/59494) and [for sqlite-utils](https://github.com/Homebrew/homebrew-core/pull/59533).
