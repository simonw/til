# Using ChatGPT Browse to name a Python package

I needed a name for my new Python CLI tool.

It was originally called `py-grep` because I checked and https://pypi.org/project/py-grep/ was available - but when I tried to push the package to PyPI I got an error because that name was too close to the existing `pygrep` package.

I decided to use ChatGPT Browse to help pick a new name.

Full [transcript is here](https://chat.openai.com/share/2fd78ddd-ad7d-4e3d-be4b-31efe79a65da), but these are the highlights.

## Suggest names based on my README

I started by prompting it like this:

> Come up with 20 alternative name ideas, with short justifications, for this tool `https://github.com/simonw/py-grep`

Since this is ChatGPT Browse, giving it a URL works ([unlike original ChatGPT](https://simonwillison.net/2023/Mar/10/chatgpt-internet-access/)). It went away and inspected [my README](https://github.com/simonw/py-grep) and replied:

<img width="765" alt="Clicked on: GitHub - simonw/py-grep: Find the Python code for specified symbols - Reading content - Finished browsing" src="https://github.com/simonw/til/assets/9599/b72fd770-59b4-4c9c-95ec-d33bb13536ae">

> Based on the information gathered, the tool `py-grep` is a CLI tool primarily designed to be used with Large Language Models (LLM). It allows users to search for names of functions and classes that occur at the top level of a Python file. It can search within specific files or directories and their subdirectories. It can also search for multiple symbols at once and support wildcards. The tool can be used in combination with `llm` command to grab specific class or function and analyze it [^1^](https://github.com/simonw/py-grep)
>
> Here are 20 alternative name ideas for `py-grep` along with short justifications:
>
> 1.  `PySymbolFinder`: Emphasizes the tool's ability to find symbols, such as function or class names, in Python code.
> 2.  `PythonGrep`: A straightforward name indicating it's a grep-like tool for Python.
> 3.  `CodeSearch`

These names were bad, so I hit the "Stop" button and prompted this:

> The names should be lowercase and short so they are quick to type 

This kicked off a round of better suggestions:

> I see, you're looking for lowercase and shorter names. Let's try to make the name suggestions more fitting for your requirements:
>
> 1.  `pysrc`: Short for "Python source", indicating it searches through Python source code.
> 2.  `pylook`: Indicates the tool's function to look for specific elements in Python code.
> 3.  `pyfind`: A direct and simple name indicating the tool's search functionality.
> 4.  `pyseek`: Implies the tool's purpose of seeking out specific elements in Python code.
> 5. ...

These are looking much better! I checked https://pypi.org/projects/pyseek/ and got a 404, so I tried renaming to that and publishing... and then got an error, because I should have checked https://pypi.org/project/pyseek/ (project singular, not plural).

## Getting it to check for availability itself

I tried the following prompt:

> All of those names are taken, more ideas please - you can check if they are taken by checking for https://pypi.org/project/pyseek/

This totally worked! It started churning through ideas, checking each one:

<img width="758" alt="Finished browsing Clicked on: pydex · PyPI Clicked on: pyscan · PyPI Clicked on: pylocator · PyPI Clicked on: pyspotter · PyPI Clicked on: pylocator · PyPI Clicked on: pyfinder · PyPI Clicked on: PyScanner · PyPI Clicked on: PyLookup · PyPI Clicked on: PySpot · PyPI Clicked on: PyLookup · PyPI Clicked on: pylocator · PyPI Clicked on: pyfinder · PyPI Clicked on: pylocator · PyPI Clicked on: pyfinder · PyPI Click failed Finished browsing It seems there was an error fetching the page. This might indicate that the name pysourcefinder is not taken, but it would be safer to verify manually. Here are some additional names to consider:     pysourcelocator     pycodegrep     pycodesearch     pycodefinder     pycodeseeker" src="https://github.com/simonw/til/assets/9599/ed424241-8930-4ef8-b874-aecceed99808">

On the one hand, it's super cool that it's able to check for available names like this!

But wow, it turns out almost every variant of `py*` has already been taken.

## Forget about py then

I said:

> OK we're going to have to ditch the idea of names that start with `py` then - come up with 20 great short options

It started producing options, some of them actually quite good:

> Sure, here are 20 short name suggestions that don't start with `py`:
>
> 1.  **codestalk**: Implies that the tool "stalks" or closely follows code to find the specific symbols.
> 2.  **grepgo**: A combination of "grep" and "go", suggesting the speed and efficiency of the tool.
> 3.  **findsy**: A contraction of "find" and "symbols", which is what the tool does.
> 4.  **dexer**: Short for "indexer", which is what the tool effectively does to find the Python code for specified symbols.
> 5.  **symbex**: A combination of "symbol" and "extract", indicating the tool's function.
> 6.  **zoomdex**: Suggests both speed ("zoom") and indexing ("dex").
> 7.  **funsy**: A play on "function" and "symbols", the two things that the tool primarily searches for.
> 8.  **seekode**: A combination of "seek" and "code", indicating the tool's main function.

And there was the name: **symbex**, short for symbol extraction.

I checked manually if it was available, and it was. So I decided it was good enough and shipped my new package.

## What you can do with symbex

Here's a fun thing you can do combining symbex with my [LLM](https://github.com/simonw/llm) tool. I ran this in a fresh checkout of Datasette:
```bash
symbex 'test*csv*' | llm --system 'based on these tests guess what this tool does'
```
Output:
> This tool seems to be a web application that provides a user interface to query databases and export query results in various formats, including HTML, JSON, and CSV. The tests verify that the tool correctly generates HTML pages with links to export query results in JSON or CSV format, exports tables to CSV format with custom options (such as whether to include labels and nullable labels), and performs streaming of CSV data. The tests also check that the tool sets appropriate HTTP headers, allows CORS, and handles errors and large CSV files gracefully.
