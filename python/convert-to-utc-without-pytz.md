# Convert a datetime object to UTC without using pytz

I wanted to convert a datetime object (from GitPython) to UTC without adding the `pytz` dependency.

```python
from datetime import timezone
import git


repo = git.Repo(".", odbt=git.GitDB)
commit = list(repo.iter_commits(ref))[0]
dt = commit.committed_datetime
# This was 2020-04-19T07:55:08-07:00
dt_in_utc = dt.astimezone(timezone.utc)

# Now use .isoformat() to convert to a string
print(dt_in_utc.isoformat())
# Came out as 2020-04-19T14:55:08+00:00
```
