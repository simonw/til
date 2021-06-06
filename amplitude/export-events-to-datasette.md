# Exporting Amplitude events to SQLite

[Amplitude](https://amplitude.com/) offers an "Export Data" button in the project settings page. This can export up to 365 days of events (up to 4GB per export), where the export is a zip file containing `*.json.gz` gzipped newline-delimited JSON.

You can export multiple times, so if you have more than a year of events you can export them by specifying different date ranges. It's OK to overlap these ranges as each event has a uniue `uuid` that can be used to de-duplicate them.

Here's how to import that into a SQLite database using `sqlite-utils`:
```
unzip export # The exported file does not have a .zip extension for some reason
cd DIRECTORY_CREATED_FROM_EXPORT
gzcat *.json.gz | sqlite-utils insert amplitude.db events --nl --alter --pk uuid --ignore -
```
Since we are using `--pk uuid` and `--ignore` it's safe to run this against as many exported `*.json.gz` files as you like, including exports that overlap each other.

Then run `datasette amplitude.db` to browse the results.
