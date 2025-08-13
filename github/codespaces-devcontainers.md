# Configuring GitHub Codespaces using devcontainers

[GitHub Codespaces](https://github.com/features/codespaces) provides full development environments in your browser, and is free to use with anyone with a GitHub account. Each environment has a full Linux container and a browser-based UI using VS Code.

I'm a huge fan of Codespaces for running workshops: it means you can skip that awful half hour at the beginning of any workshop where you try to ensure everyone has a working development environment.

With Codespaces a fresh development environment is a case of clicking a button and then waiting for a couple of minutes. If you break it, click the button again to get a new one.

Codespaces generally launch from a GitHub repository, which can be configured to use a specific configuration. Here's the pattern I'm using for these, inspired by [this Python 3.13 example](https://github.com/pamelafox/python-3.13-playground) by [Pamela Fox](https://github.com/pamelafox).

## A Python environment with some VS Code plugins

My [simonw/codespaces](https://github.com/simonw/codespaces) repository contains a very simple configuration that provides Python 3.13 anh Node.js LTS plus VS Code with some useful plugins.

The only required file is [.devcontainer/devcontainer.json](https://github.com/simonw/codespaces/blob/main/.devcontainer/devcontainer.json). Here's that file in full:

```json
{
  "name": "Python 3.13",
  "image": "mcr.microsoft.com/devcontainers/python:3.13-bullseye",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "latest"
    }
  },
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true
      },
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.vscode-python-envs",
        "GitHub.copilot"
      ]
    }
  },
  "postCreateCommand": "pip install uv"
}
```
This would work with just the `name` and `image` fields.

I'm using Microsoft's [Dev Containers](https://github.com/devcontainers) base image for Python 3.13 on Debian Bullseye.

    mcr.microsoft.com/devcontainers/python:3.13-bullseye

There's a full list of those images [in the src/ directory](https://github.com/devcontainers/images/tree/main/src) of their [devcontainers/images](https://github.com/devcontainers/images) repository. They have them for Go, Rust, Java, PHP and more.

It's useful to have Node.js LTS installed so that NPM etc works out of the box. Here I'm using the `"features"` object to add that.

You can find a list of more features in the [devcontainers/features](https://github.com/devcontainers/features) repository, again in the [src/ directory](https://github.com/devcontainers/features/tree/main/src).

That `features/node:1` one is defined by [this install.sh script](https://github.com/devcontainers/features/blob/main/src/node/install.sh).

I copied the `"vscode"` block from Pamela, but I added the `"GitHub.copilot"` extension to enable Copilot in VS Code out of the box.

I also added that last line:

    "postCreateCommand": "pip install uv"

Anything in `postCreateCommand` will be run after the container is first created. Here I'm using `pip` to install `uv`, after which `uv tool install X` etc will be available.

## Providing a link to launch the container

Once you have added a `.devcontainer/devcontainer.json` to a repository you can construct a link that will launch that repository as a Codespace like so:

    https://codespaces.new/simonw/codespaces?quickstart=1

Here's [the documentation](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/setting-up-your-repository/facilitating-quick-creation-and-resumption-of-codespaces#creating-a-link-to-resume-a-codespace) for this feature.

The `?quickstart=1` parameter causes the page to consider any Codespaces you already have running against that repository and suggest using those rather than starting a new one. It's a better option in my opinion.

## Bonus: Installing and configuring LLM

I created a second Codespaces repo, [simonw/codespaces-llm](https://github.com/simonw/codespaces-llm), which is almost identical to the above except the `postCreateCommand` contains the following:

    "postCreateCommand": "pip install uv && uv tool install llm && llm install llm-github-models && llm models default github/gpt-4.1"

Here's that but more readable:
```bash
pip install uv &&
uv tool install llm &&
llm install llm-github-models &&
llm models default github/gpt-4.1
```
This install `uv`, then uses `uv tool install` to install `llm`, then uses the `llm install` command to install the [llm-github-models](https://github.com/tonybaloney/llm-github-models) plugin, and finally sets the default model used by LLM to `github/gpt-4.1`.

The net effect of this is that the user will then be able to run commands like this:

    llm "Fun facts about pelicans"

GitHub Codespaces automatically sets a `GITHUB_TOKEN` environment variable with a token for the current user.

The `llm-github-models` plugin provides access to the [GitHub Models](https://docs.github.com/en/github-models) collection, which can be accessed using that `GITHUB_TOKEN` as an API key.

Usage of GPT-4.1 is free using that key (albeit rate-limited), so setting the default model to `github/gpt-4.1` means users get access to a very competent model for free!
