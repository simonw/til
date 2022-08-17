# Sort by number of JSON intersections

This [post on Reddit](https://www.reddit.com/r/sqlite/comments/wr0wp0/i_have_a_sqlite_database_of_recipes_i_would_like/) asked how to run a query that takes a list of items (in this case ingredients) as the input and returns all rows with at least one of those items in a JSON list, ordered by the most matches.

I jumped on this as a great opportunity to demonstrate [Datasette Lite](https://lite.datasette.io/) as a tool for answering SQL questions.

## Creating an example database in Datasette Lite

I started with the following SQL to create the demo table:
```sql
create table recipes (id integer primary key, name text, ingredients text);
insert into recipes values (1, 'Cake', '["flour", "sugar", "eggs"]');
insert into recipes values (2, 'Pancakes', '["flour", "eggs", "butter"]');
insert into recipes values (3, 'Waffles', '["flour", "milk", "eggs"]');
insert into recipes values (4, 'Pizza', '["flour", "sugar", "eggs", "cheese"]');
```
I actually got GitHub Copilot to write most of that for me:

<img alt="In GitHub Copilot, I start with:  create table recipes (id integer primary key, name text, ingredients text);  I type &quot;insert into&quot; and it autocompletes to:  insert into recipes values (1, 'Pizza', 'Tomato Sauce, Cheese, and Pizza');  I  edit that to 'Cake' instead and it fills in &quot;flour, sugar, eggs, butter'  Then I edit that to be a JSON array instead  It completes (with a few tweaks from me) with:  insert into recipes values (2, 'Pancakes', '[&quot;flour&quot;, &quot;sugar&quot;, &quot;eggs&quot;, &quot;butter&quot;]'); insert into recipes values (3, 'Pizza', '[&quot;vegetables&quot;, &quot;cheese&quot;, &quot;tomatoes&quot;, &quot;sauce&quot;]'); insert into recipes values (4, 'Spaghetti', '[&quot;pasta&quot;, &quot;tomatoes&quot;, &quot;sauce&quot;]');" src="https://user-images.githubusercontent.com/9599/185261271-cf8aff79-67dc-4359-89a2-5f8a857e944a.gif">

I saved that [to a gist](https://gist.github.com/simonw/1f8a91123ccefd8844187225b1832d7a) and opened it in Datasette Lite with this URL:

https://lite.datasette.io/?sql=https://gist.githubusercontent.com/simonw/1f8a91123ccefd8844187225b1832d7a/raw/5069075b86aa79358fbab3d4482d1d269077d632/recipes.sql

## Solving the problem

Here's the SQL recipe I came up with to solve the question:

```sql
select id, name, ingredients, (
  select json_group_array(value) from json_each(ingredients)
  where value in (select value from json_each(:p0))
) as matching_ingredients
from recipes
where json_array_length(matching_ingredients) > 0
order by json_array_length(matching_ingredients) desc
```
[Example of that query](https://lite.datasette.io/?sql=https://gist.githubusercontent.com/simonw/1f8a91123ccefd8844187225b1832d7a/raw/5069075b86aa79358fbab3d4482d1d269077d632/recipes.sql#/data?sql=select+id%2C+name%2C+ingredients%2C+%28%0A++select+json_group_array%28value%29+from+json_each%28ingredients%29%0A++where+value+in+%28select+value+from+json_each%28%3Ap0%29%29%0A%29+as+matching_ingredients%0Afrom+recipes%0Awhere+json_array_length%28matching_ingredients%29+%3E+0%0Aorder+by+json_array_length%28matching_ingredients%29+desc&p0=%5B%22sugar%22%2C+%22cheese%22%5D) with an input for `p0` of `["sugar", "cheese"]`, which returns:

|   id | name   | ingredients                          | matching_ingredients   |
|------|--------|--------------------------------------|------------------------|
|    4 | Pizza  | ["flour", "sugar", "eggs", "cheese"] | ["sugar","cheese"]     |
|    1 | Cake   | ["flour", "sugar", "eggs"]           | ["sugar"]              |

The key trick here is the bit that creates that `matching_ingredients` column, which uses a sub-select like this:
```sql
select json_group_array(value) from json_each(ingredients)
where value in (select value from json_each(:p0))
```
`json_group_array(value)` is an aggregation function that turns the results into a JSON array.

`where value in (select value from json_each('["sugar", "cheese"]')` is the bit that calculates the intersection of the two JSON arrays.

Then at the end I use `json_array_length()` to remove rows with no overlap and then sort with the most matching ingredients first.
