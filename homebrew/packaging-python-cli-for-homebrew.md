# Packaging a Python CLI tool for Homebrew

Today I figured out how to package [Datasette](https://github.com/simonw/datasette) for installation with Homebrew. You can now install it like this:

    brew tap simonw/datasette
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
  homepage "https://datasette.readthedocs.io/"
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

For the initial block you need the URL to a source distribution and the `sha256` code for it. I got these for Datasette by publishing a `sdist` package to PyPI and then clicking [the "View hashes" button](https://pypi.org/project/datasette/0.46/#copy-hash-modal-372b7614-26f5-4356-a89a-3854323983bf) next to the source release.

Every dependency needs to be listed as a resource. They all need to be available as `sdist` packages - I made sure all of my dependencies had an `sdist` on PyPI.

Then I used the [homebrew-pypi-poet](https://github.com/tdsmith/homebrew-pypi-poet) tool to construct the rest of the resource blocks for me. You install that in a fresh virtual environment with the module you are packaging:

```
$ cd /tmp
$ mkdir d
$ cd d
$ pipenv shell
(d) $ pip install datasette homebrew-pypi-poet
...
(d) $ poet 
usage: poet [-h] [--single package [package ...] | --formula package | --resources package] [--also package] [-V]
(d) $ poet datasette
  resource "aiofiles" do
    url "https://files.pythonhosted.org/packages/2b/64/437053d6a4ba3b3eea1044131a25b458489320cb9609e19ac17261e4dc9b/aiofiles-0.5.0.tar.gz"
    sha256 "98e6bcfd1b50f97db4980e182ddd509b7cc35909e903a8fe50d8849e02d815af"
  end

  resource "asgi-csrf" do
    url "https://files.pythonhosted.org/packages/20/19/60188a9d88e5af17cfb91dac465f898d8eccf69bc215ac731d64c49fea5c/asgi-csrf-0.6.1.tar.gz"
    sha256 "4045b8b45c330e068b8b96f914e585ea69228efbfe574ab4a4be2d8c6009a19f"
  end
  ...
```
There's one major gotcha here: `datasette` itself was included as a `resource` block. It's important to *remove this resource block* - if you don't, the `datasette` command-line tool will not be sym-linked from the `/usr/local/bin` directory by Homebrew which means users won't be able to type `datasette` to run it. See [issue #2](https://github.com/simonw/homebrew-datasette/issues/2) for how we figured that out.

But that's it! Publish the new `yourname.rb` file, run the `brew tap yourname/yourtap` and `brew install yourname/yourtap/yourformula`.

## Even better: poet -f

Running `poet datasette` generates the resource stanzas, but leaves you to add the rest of the formula (and manually remove the package itself from that list of resources).

`poet -f datasette` generates the full formula.

You need to fill in the description and the `test` block, but other than that it looks like it should work straight away.

## Iterating on this

I found running `brew install datasette`, seeing if it worked, then running `brew uninstall datasette`, modifying the `.rb` file on GitHub and running `datasette install datasette` again worked fine during development.

If you get any errors, `brew install datasette --debug` shows more information and drops you into an interactive debugging session when an error occurs.
