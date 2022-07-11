# Conditionally running a second job in a GitHub Actions workflow

My [simonwillisonblog-backup workflow](https://github.com/simonw/simonwillisonblog-backup/blob/main/.github/workflows/backup.yml) periodically creates a JSON backup of my  blog's PostgreSQL database, using [db-to-sqlite](https://datasette.io/tools/db-to-sqlite) and [sqlite-diffable](https://datasette.io/tools/sqlite-diffable). It then commits any changes back to the repo using this pattern:

```yaml
    - name: Commit any changes
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add simonwillisonblog
        timestamp=$(date -u)
        git commit -m "Latest data: ${timestamp}" |
| exit 0
        git push
```

I decided to upgrade it to also build and deploy a SQLite database of the content to [datasette.simonwillison.net](https://datasette.simonwillison.net/) - but only if a change had been detected.

I figured out the following pattern for doing that:

```yaml
        git commit -m "Latest data: ${timestamp}" || exit 0
        git push
        echo "::set-output name=change_detected::1"

  build_and_deploy:
    runs-on: ubuntu-latest
    needs: backup
    if: ${{ inputs.force_deploy || needs.backup.outputs.change_detected }}
    steps:
```
I'm taking advantage of the `|| exit 0` I already had, which ends that step early.

Then I added this line to run after that point:

    echo "::set-output name=change_detected::1"

This defines a [job output](https://docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs) for that job - a job with the name of `backup`.

I define a second job called `build_and_deploy` and specify that it `needs: backup` - so it should run directly after that backup job completes.

That new job has an `if:` expression which looks at `needs.backup.outputs.change_detected` to read the variable that was set by my `echo "::set-output` line.

I'm also checking `inputs.force_deploy` here. That's a separate mechanism, which allows me to trigger the workflow with manually and specify that a deploy should happen even if no changes were detected - useful for when I alter the code that configures the deployed Datasette instance.

The `force_deploy` variable comes from this section at the start of the YAML:

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
    inputs:
      force_deploy:
        description: 'Deploy even if no changes detected'
        required: false 
        type: boolean
```

This configuration adds the following UI which I can use to manually trigger the workflow:

![Screenshot of the UI showing the force_deploy checkbox](https://user-images.githubusercontent.com/9599/178353732-77e58ddd-c78c-4032-aeea-cb388bac8ec6.jpg)
