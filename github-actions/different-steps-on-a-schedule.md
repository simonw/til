# Running different steps on a schedule

Say you have a workflow that runs hourly, but once a day you want the workflow to run slightly differently - without duplicating the entire workflow.

Thanks to @BrightRan, here's [the solution](https://github.community/t5/GitHub-Actions/Schedule-once-an-hour-but-do-something-different-once-a-day/m-p/54382/highlight/true#M9168). Use the following pattern in an `if:` condition for a step:

    github.event_name == 'schedule' && github.event.schedule == '20 17 * * *'

Longer example:

```yaml
name: Fetch updated data and deploy

on:
  push:
  schedule:
    - cron: '5,35 * * * *'
    - cron: '20 17 * * *'

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
    # ...
    - name: Download existing .db files
      if: |-
        !(github.event_name == 'schedule' && github.event.schedule == '20 17 * * *')
      env:
        DATASETTE_TOKEN: ${{ secrets.DATASETTE_TOKEN }}
      run: |-
        datasette-clone https://biglocal.datasettes.com/ dbs -v --token=$DATASETTE_TOKEN
```
I used this [here](https://github.com/simonw/big-local-datasette/blob/35e1acd4d9859d3af2feb29d0744ce1550e5faec/.github/workflows/deploy.yml), see [#11](https://github.com/simonw/big-local-datasette/issues/11).
