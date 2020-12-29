# Installing and upgrading Datasette plugins with pipx

If you installed `datasette` using `pipx install datasette` you can install additional plugins with `pipx inject` like so:

    $ datasette plugins
    []

    $ pipx inject datasette datasette-json-html
      injected package datasette-json-html into venv datasette
    done! ✨ 🌟 ✨

    $ datasette plugins
    [
        {
            "name": "datasette-json-html",
            "static": false,
            "templates": false,
            "version": "0.6"
        }
    ]

Thanks [Matthew Somerville](https://twitter.com/dracos/status/1257351655907090437).

I then had to figure out how to upgrade them. Thanks to https://github.com/pipxproject/pipx/issues/79 I figured out the following recipe using `pipx runpip datasette install -U name-of-plugin`: 

    % datasette plugins
    [
        {
            "name": "datasette-vega",
            "static": true,
            "templates": false,
            "version": "0.6"
        }
    ]

    $ pipx runpip datasette install -U datasette-vega
    Collecting datasette-vega
    Downloading datasette_vega-0.6.2-py3-none-any.whl (1.8 MB)
        |████████████████████████████████| 1.8 MB 2.0 MB/s
    ...
    Installing collected packages: datasette-vega
    Attempting uninstall: datasette-vega
        Found existing installation: datasette-vega 0.6
        Uninstalling datasette-vega-0.6:
        Successfully uninstalled datasette-vega-0.6
    Successfully installed datasette-vega-0.6.2

    $ datasette plugins
    [
        {
            "name": "datasette-vega",
            "static": true,
            "templates": false,
            "version": "0.6.2"
        }
    ]

I added all of this to the Datasette docs here: https://docs.datasette.io/en/latest/installation.html#using-pipx
(see https://github.com/simonw/datasette/issues/756).
