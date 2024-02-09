# Creating GitHub repository labels with an Actions workflow

Newly created GitHub repositories come with a default set of labels. I have several labels I like to add on top of these. The most important is **research**, which I use for issues that are tracking my notes on a research topic relevant to the repository.

I've wanted a fast way to add these to new repositories for ages. Inspired by [this tweet](https://twitter.com/LeaVerou/status/1756085595103793548) by Lea Verou I finally decided to build a system for this.

## Creating labels with a GitHub Actions workflow

I love automating things relating to GitHub using GitHub Actions, because it saves me from having to execute code anywhere else.

I decided to solve this problem with a workflow called `labels.yml`. The idea is that you copy this file into any repository in the `.github/workflows/` directory and it creates the labels for you using the GitHub API.

Because it's running in GitHub Actions you don't need to create an API key for it - it can use the key that is made available automatically to the workflow.

It took a bit of iteration, but eventually I got to the following:

```yaml
name: Update repository labels

on:
  push:
    branches:
    - main
    paths:
    - '.github/workflows/labels.yml'

jobs:
  create-labels:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    env:
      LABELS_JSON: |
        [
          {"name": "research", "color": "ededed", "description": "Research needed"},
          {"name": "ops", "color": "c2e0c6", "description": "Ops task"},
          {"name": "ci", "color": "bfdadc", "description": "Related to GitHub Actions CI"},
          {"name": "demo", "color": "bfdadc", "description": "Demo label"}
        ]
    steps:
    - uses: actions/github-script@v7
      with:
        script: |
          const labels = JSON.parse(process.env.LABELS_JSON);
          for (const label of labels) {
            try {
              await github.rest.issues.createLabel({
                owner: context.repo.owner,
                repo: context.repo.repo,
                name: label.name,
                description: label.description || '',
                color: label.color
              });
            } catch (error) {
              // Check if the error is because the label already exists
              if (error.status === 422) {
                console.log(`Label '${label.name}' already exists. Skipping.`);
              } else {
                // Log other errors
                console.error(`Error creating label '${label.name}': ${error}`);
              }
            }
          }
```
The labels themselves are defined in that `LABELS_JSON` block, which seemed like a relatively easy way to add editable structured data to the workflow file.

The workflow is configured to only run when a push to the repository edits or creates that workflow file itself:

```yaml
on:
  push:
    branches:
    - main
    paths:
    - '.github/workflows/labels.yml'
```

The bulk of the work is done using that [actions/github-script](https://github.com/actions/github-script) step. This is a powerful action that pre-configures a GitHub JavaScript client library for you, with authentication tokens already provided.

The JavaScript loops through the labels from that earlier JSON blob and attempts ot create each one of them. If they already exist it skips them.

(I may update this in the future to update the color and description if they have changed on an existing label.)

One other crucial detail is this bit:

```yaml
permissions:
  issues: write
```
That took me a while to figure out: without it, the API token made available to the `github/script` doesn't have permission to modify the labels attached to the repository.

## The end result

Drop that workflow into any GitHub repository, edit the `LABELS_JSON` to your preferences and it should execute and add labels!

You can see the result in my [create-labels-workflow repo](https://github.com/simonw/create-labels-workflow) - here are [the labels](https://github.com/simonw/create-labels-workflow/labels).
