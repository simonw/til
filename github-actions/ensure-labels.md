# Ensure labels exist

I wanted to ensure that when [this template repository](https://github.com/simonw/action-transcription) was used to create a new repo that repo would have a specific set of labels.

Here's the workflow I came up with, saved as `.github/workflows/ensure_labels.yml`:

```yaml
name: Ensure labels
on: [push]

jobs:
  ensure_labels:
    runs-on: ubuntu-latest
    steps:
    - name: Create labels
      uses: actions/github-script@v6
      with:
        script: |
          try {
            await github.rest.issues.createLabel({
              ...context.repo,
              name: 'captions'
            });
            await github.rest.issues.createLabel({
              ...context.repo,
              name: 'whisper'
            });
          } catch(e) {
            // Ignore if labels exist already
          }
```
This creates `captions` and `whisper` labels, if they do not yet exist.

It's wrapped in a `try/catch` so that if the labels exist already (as they will on subsequent runs) the error can be ignored.

Note that you need to use `await ...` inside that `try/catch` block or exceptions thrown by those methods will still cause the action run to fail.

The `...context.repo` trick saves on having to pass `owner` and `repo` explicitly.
