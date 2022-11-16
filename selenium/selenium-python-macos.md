# Installing Selenium for Python on macOS with ChromeDriver

I needed to run Selenium on macOS for the first time today. Here's how I got it working.

## Install the chromedriver binary

### If you have homebrew

This is by far the easiest option:

    brew install chromedriver --cask

This also ensures `chromedriver` is on your path, which means you don't need to use an explicit `chromedriver_path` later on.

You still need to run it once in the terminal `chromedriver` to get the macOS error, then allow it in the `Security & Privacy` preferences - see below.

To upgrade an existing installation do this:

    brew upgrade chromedriver --cask

Knowing how to upgrade an existing version is useful if you are seeing an error like this one:

> Message: session not created: This version of ChromeDriver only supports Chrome version 85

### Without using homebrew

ChromeDriver is available from the official website here: https://sites.google.com/a/chromium.org/chromedriver/downloads

I have Chrome 85 so I downloaded the `chromedriver_mac64.zip` file from https://chromedriver.storage.googleapis.com/index.html?path=85.0.4183.87/

Unzipping this gave me a `chromedriver` binary file. I decided to put this in my `~/bin` directory.

### Skipping the error on macOS

The first time I ran it I got an error complaining that the binary has not been signed:

    ~/bin/chromedriver
    # A window displayed on macOS with an error

To fix this, go to `System Preferences -> Security & Privacy` - there was a prompt there about the binary, with an "open this anyway" button. Clicking that worked around the signing issue.

## Installing the Selenium Python driver

I installed Selenium using `pip` for Python 3:

    pip install selenium

Since I was planning to use it from a Jupyter Notebook I actually installed it by running the following in a cell in a notebook:

    %pip install selenium

The benefit of running this in the notebook is that you don't need to know the exact path to pip running in the same virtual environment as Jupyter, so I use this trick a lot.

## Demonstrating that it works

I ran this in a notebook cell:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# This is not needed if chromedriver is already on your path:
chromedriver_path = "/Users/simon/bin/chromedriver"

options = Options()
options.add_argument("--window-size=1920x1080")
options.add_argument("--verbose")
# options.add_argument("--headless")

driver = webdriver.Chrome(options=options, chromedriver_path=executable_path)
driver.get("https://www.example.com")
```
This opened a visible Chrome window to `https://www.example.com/`
```python
print(driver.find_element_by_css_selector('body').text)
```
This output the following, showing that Selenium is fully working:
```
Example Domain
This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.
More information...
```

## Installing geckodriver for Firefox

I got Firefox support working by downloading the `geckodriver` binary from https://github.com/mozilla/geckodriver and copying that to my `~/bin/` directory. Then this worked:
```python
from selenium import webdriver

firefox = webdriver.Firefox(executable_path="/Users/simon/bin/geckodriver")
firefox.get('http://seleniumhq.org/')
print(firefox.find_element_by_css_selector('body').text)
```
I used `wget` for the download (rather than clicking the link in my browser) thanks to the warning here: https://firefox-source-docs.mozilla.org/testing/geckodriver/Notarization.html

An easier option: install it with Homebrew:

    brew install geckodriver

This puts it on the PATH and ensures the code is already signed and does not show a warning. You can then use it like this:

```python
from selenium import webdriver

firefox = webdriver.Firefox()
firefox.get('http://seleniumhq.org/')
```
You can close the Firefox window (and terminate the Firefox process) later like this:
```python
firefox.close()
```
