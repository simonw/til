# Skipping CSV rows with odd numbers of quotes using ripgrep

I'm working with several huge CSV files - over 5 million rows total - and I ran into a problem: it turned out there were a few lines in those files that imported incorrectly because they were not correctly escaped.

Here's an example of an invalid line:

    SAI Exempt,"Patty B"s Hats & Tees,LLC",,26 Broad St

The apostrophe in `Patty B's Hats & Tees` is incorrectly represented here as a double quote, and since that's in a double quoted string it breaks that line of CSV.

I decided to filter out any rows that had an odd number of quotation marks in them - saving those broken lines to try and clean up later.

## Finding rows with odd numbers of quotes

StackOverflow [offered this regular expression](https://stackoverflow.com/a/16863999) for finding lines with an odd number of quotation marks:

```
[^"]*"   # Match any number of non-quote characters, then a quote
(?:      # Now match an even number of quotes by matching:
 [^"]*"  #  any number of non-quote characters, then a quote
 [^"]*"  #  twice
)*       # and repeat any number of times.
[^"]*    # Finally, match any remaining non-quote characters
```

I translated this into a `ripgrep` expression, adding `^` to the beginning and `$` to the end in order to match whole strings.

This command counted the number of invalid lines:

    rg '^[^"]*"(?:[^"]*"[^"]*")*[^"]*$' --glob '*.csv' --count

    04.csv:52
    03.csv:42
    02.csv:24
    01.csv:29

Adding `--invert-match` showed me the count of lines that did NOT have an odd number of quotes:

    rg '^[^"]*"(?:[^"]*"[^"]*")*[^"]*$' --glob '*.csv' --count --invert-match

    05.csv:2829
    04.csv:812351
    03.csv:961311
    02.csv:994265
    01.csv:995404

This shows that the invalid lines are a tiny subset of the overall files.

Removing `--count` shows the actual content.

## Importing into SQLite with sqlite-utils

I used this for loop to import only the valid lines into a SQLite database:

```bash
for file in *.csv;
    do rg --invert-match '^[^"]*"(?:[^"]*"[^"]*")*[^"]*$' $file | \
    sqlite-utils insert my.db rows - --csv;
done;
```

## Saving the broken lines for later

To save the lines that contained odd numbers of double quotes I used this command:

```bash
rg '^[^"]*"(?:[^"]*"[^"]*")*[^"]*$' \
  --glob '*.csv' \
  --no-line-number \
  --no-filename > saved.txt
```
Since I don't actually care which file they lived in - all of these CSV files share the same structure - I used `--no-filename` to omit the filename from the results and `--no-line-number` to omit the line number. The result is a `saved.txt` file containing just the raw CSV data that I skipped from the import.
