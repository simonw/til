# Attaching a generated file to a GitHub release using Actions

For [Datasette Desktop](https://github.com/simonw/datasette-app) I wanted to run an action which, when I created a release, would build an asset for that release and then upload and attach it.

I triggered my action on the creation of a new release, like so:

```yaml
on:
  release:
    types: [created]
```

Assuming previous steps that create a file called `app.zip` in the root of the checkout, here's the final action step which worked for me:

```yaml
      - name: Upload release attachment
        uses: actions/github-script@v4
        with:
          script: |
            const fs = require('fs');
            const tag = context.ref.replace("refs/tags/", "");
            // Get release for this tag
            const release = await github.repos.getReleaseByTag({
              owner: context.repo.owner,
              repo: context.repo.repo,
              tag
            });
            // Upload the release asset
            await github.repos.uploadReleaseAsset({
              owner: context.repo.owner,
              repo: context.repo.repo,
              release_id: release.data.id,
              name: "app.zip",
              data: await fs.readFileSync("app.zip")
            });
```
It uses [actions/github-script](https://github.com/actions/github-script) which provides a pre-configured [octokit/rest.js](https://octokit.github.io/rest.js/) client object.

The `uploadReleaseAsset()` method needs the `owner`, `repo`, `release_id`, `name` (filename) and the file data.

These are mostly available, with the exception of `release_id`. That can be derived for the current release based on the `context.ref` value - strip that down to just the tag, then use `getReleaseByTag()` to get a release object. `release.data.id` will then be the numeric release ID.

My full workflow is at https://github.com/simonw/datasette-app/blob/0.1.0/.github/workflows/release.yml
