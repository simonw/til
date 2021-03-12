# Querying for GitHub issues open for less than 60 seconds

While [writing this thread](https://twitter.com/simonw/status/1370390336514658310) about my habit of opening issues and closing them a few seconds later just so I could link to them in a commit message I decided to answer the question "How many of my issues were open for less than 60 seconds?"

Thanks to [github-to-sqlite](https://datasette.io/tools/github-to-sqlite) I have an [issues database table](https://github-to-sqlite.dogsheep.net/github/issues) containing issues from all of my public projects.

I needed to figure out how to calculate the difference between `closed_at` and `created_at` in seconds. This works:

```sql
select strftime('%s',issues.closed_at) - strftime('%s',issues.created_at) as duration_open_in_seconds ...
```
I wanted to be able to input the number of seconds as a parameter. I used this:
```sql
duration_open_in_seconds < CAST(:max_duration_in_seconds AS INTEGER)
```
This is the full query - [try it out here](https://github-to-sqlite.dogsheep.net/github?sql=select%0D%0A++json_object%28%0D%0A++++%27label%27%2C+repos.full_name+%7C%7C+%27+%23%27+%7C%7C+issues.number%2C%0D%0A++++%27href%27%2C+%27https%3A%2F%2Fgithub.com%2F%27+%7C%7C+repos.full_name+%7C%7C+%27%2Fissues%2F%27+%7C%7C+issues.number%0D%0A++%29+as+link%2C%0D%0A++strftime%28%27%25s%27%2Cissues.closed_at%29+-+strftime%28%27%25s%27%2Cissues.created_at%29+as+duration_open_in_seconds%2C%0D%0A++issues.number+as+issue_number%2C%0D%0A++issues.title%2C%0D%0A++users.login%2C%0D%0A++issues.closed_at%2C%0D%0A++issues.created_at%2C%0D%0A++issues.body%2C%0D%0A++issues.type%0D%0Afrom%0D%0A++issues+join+repos+on+issues.repo+%3D+repos.id%0D%0A++join+users+on+issues.user+%3D+users.id%0D%0A++where+issues.closed_at+is+not+null+and+duration_open_in_seconds+%3C+CAST%28%3Amax_duration_in_seconds+AS+INTEGER%29%0D%0Aorder+by%0D%0A++issues.closed_at+desc&max_duration_in_seconds=60):

```sql
select
  json_object(
    'label', repos.full_name || ' #' || issues.number,
    'href', 'https://github.com/' || repos.full_name || '/issues/' || issues.number
  ) as link,
  strftime('%s',issues.closed_at) - strftime('%s',issues.created_at) as duration_open_in_seconds,
  issues.number as issue_number,
  issues.title,
  users.login,
  issues.closed_at,
  issues.created_at,
  issues.body,
  issues.type
from
  issues join repos on issues.repo = repos.id
  join users on issues.user = users.id
  where issues.closed_at is not null and duration_open_in_seconds < CAST(:max_duration_in_seconds AS INTEGER)
order by
  issues.closed_at desc
```
