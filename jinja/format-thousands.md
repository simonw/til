# Formatting thousands in Jinja

Here's how to format a number in Jinja with commas for thousands, without needing any custom filters or template functions:

    {{ "{:,}".format(row_count) }}

Output looks like this:

    179,119 rows

Bonus: here's how to display a different pluralization of "row" if there is a single row:

    {{ "{:,}".format(row_count) }} row{{ "" if row_count == 1 else "s" }}

