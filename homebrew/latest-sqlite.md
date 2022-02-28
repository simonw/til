# Running the latest SQLite in Datasette using Homebrew

I made a pleasant discovery today: Homebrew are very quick to update to the latest SQLite release (here's [their formula](https://github.com/Homebrew/homebrew-core/blob/master/Formula/sqlite.rb)), and since [Datasette](https://datasette.io/) when installed via Homebrew uses that version, this means you can use `brew update sqlite` to ensure you are running the most recent SQLite version within Datasette.

If you've installed Datasette using Homebrew:

    brew install datasette

You can see the version of SQLite it uses either by running `datasette` and navigating to http://127.0.0.1:8001/-/versions - or you can see it from the command-line using:

    % datasette --get /-/versions.json | jq .sqlite.version
    "3.37.2"

To upgrade SQLite, run the following:

    brew upgrade sqlite

After doing that I ran the above command again and confirmed I had been upgraded to SQLite 3.38.0:

    % datasette --get /-/versions.json | jq .sqlite.version
    "3.38.0"
