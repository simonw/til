# Fixing broken text encodings with sqlite-transform and ftfy

I was working with a database table that included values that were clearly in the wrong character encoding - values like this:

    Rue LÃ©opold I

I used my [sqlite-transform](https://github.com/simonw/sqlite-transform) tool with the [ftfy Python library](https://pypi.org/project/ftfy/) to fix that by running the following:

```bash
sqlite-transform lambda chiens.db espaces-pour-chiens-et-espaces-interdits-aux-chiens namefr \
  --code 'ftfy.fix_encoding(value)' \
  --import ftfy
```

That's the database file, the table and the column, then `--code` and `--import` to specify the transformation.

Since I had installed `sqlite-transform` using `pipx install sqlite-transform` I needed to first install the `ftfy` library into the correct virtual environment. The recipe for doing that is:

```bash
pipx inject sqlite-transform ftfy
```
