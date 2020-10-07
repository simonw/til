# Running Datasette on DigitalOcean App Platform

[App Platform](https://www.digitalocean.com/docs/app-platform/) is the new PaaS from DigitalOcean. I figured out how to run Datasette on it.

The bare minimum needed is a GitHub repository with two files: `requirements.txt` and `Procfile`.

`requirements.txt` can contain a single line:
```
datasette
```
`Procfile` needs this:
```
web: datasette . -h 0.0.0.0 -p $PORT --cors
```

Your web process needs to listen on `0.0.0.0` and on the port in the `$PORT` environment variable.

Connect this GitHub repository up to DigitalOcean App Platform and it will deploy the application - detecting that it's a Python application (due to the `requirements.txt` file), installing those requirements and then starting up the process in the `Procfile`.

Any SQLite `.db` files that you add to the root of the GitHub repository will be automatically served by Datasette when it starts up.

Because Datasette is run using `datasette .` it will also automatically pick up a `metadata.json` file or anything in custom `templates/` or `plugins/` folders, as described in [Configuration directory mode](https://docs.datasette.io/en/stable/config.html#configuration-directory-mode) in the documentation.

## Building database files

I don't particularly like putting binary SQLite files in a GitHub repository - I prefer to store CSV files or SQL text files and build them into a database file as part of the deployment process.

The best way I've found to do this in a DigitalOcean App is to create a `build.sh` script that builds the database, then execute it using a `Build Command`.

I've not yet figured out a neat way to configure build scripts entirely in the repository, but you can instead use the DigitalOcean App Platform web interface to set one. Visit the "Components" tab end click "Edit" in the Commands section, then set the "Buld Command" to `. build.sh`. Now any code you add to a `build.sh` script in your repo will be executed as part of the deployment.

I started with a `build.sh` script that looked like this:

```
wget https://latest.datasette.io/fixtures.db
```
And this resulted in the `fixtures.db` folder being served at `/fixtures` under my app's subdomain.

