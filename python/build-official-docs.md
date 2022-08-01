# Build the official Python documentation locally

First, checkout the cpython repo:

    $ git clone git@github.com:python/cpython

cd into the `Doc` directory:

    $ cd cpython/Doc

To get a virtual environment with Sphinx and other required tools, run `make venv` like this:

    $ make venv
    python3 -m venv ./venv
    ./venv/bin/python3 -m pip install -U pip setuptools
    ...
    Installing collected packages: snowballstemmer, sphinxcontrib-jsmath, sphinxcontrib-devhelp, sphinxcontrib-serializinghtml, pyparsing, six, packaging, sphinxcontrib-applehelp, sphinxcontrib-qthelp, alabaster, docutils, MarkupSafe, Jinja2, pytz, babel, imagesize, chardet, certifi, urllib3, idna, requests, Pygments, sphinxcontrib-htmlhelp, Sphinx, blurb, python-docs-theme
        Running setup.py install for python-docs-theme ... done
    Successfully installed Jinja2-2.11.2 MarkupSafe-1.1.1 Pygments-2.6.1 Sphinx-2.2.0 alabaster-0.7.12 babel-2.8.0 blurb-1.0.7 certifi-2020.4.5.1 chardet-3.0.4 docutils-0.16 idna-2.9 imagesize-1.2.0 packaging-20.3 pyparsing-2.4.7 python-docs-theme-2020.1 pytz-2020.1 requests-2.23.0 six-1.14.0 snowballstemmer-2.0.0 sphinxcontrib-applehelp-1.0.2 sphinxcontrib-devhelp-1.0.2 sphinxcontrib-htmlhelp-1.0.3 sphinxcontrib-jsmath-1.0.1 sphinxcontrib-qthelp-1.0.3 sphinxcontrib-serializinghtml-1.1.4 urllib3-1.25.9
    The venv has been created in the ./venv directory

Now running `make html` will build the docs:

    $ make html

Run `open build/html/index.html` to view them in a browser.
