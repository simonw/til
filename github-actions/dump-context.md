# Dump out all GitHub Actions context

Useful for seeing what's available for `if: ` conditions (see [context and expression syntax](https://help.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions)).

I copied this example action [from here](https://help.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#example-printing-context-information-to-the-log-file) and deployed it [here](https://github.com/simonw/playing-with-actions/blob/master/.github/workflows/dump-context.yml). Here's an [example run](https://github.com/simonw/playing-with-actions/runs/599575180?check_suite_focus=true).

```yaml
on: push

jobs:
  one:
    runs-on: ubuntu-16.04
    steps:
      - name: Dump GitHub context
        env:
          GITHUB_CONTEXT: ${{ toJson(github) }}
        run: echo "$GITHUB_CONTEXT"
      - name: Dump job context
        env:
          JOB_CONTEXT: ${{ toJson(job) }}
        run: echo "$JOB_CONTEXT"
      - name: Dump steps context
        env:
          STEPS_CONTEXT: ${{ toJson(steps) }}
        run: echo "$STEPS_CONTEXT"
      - name: Dump runner context
        env:
          RUNNER_CONTEXT: ${{ toJson(runner) }}
        run: echo "$RUNNER_CONTEXT"
      - name: Dump strategy context
        env:
          STRATEGY_CONTEXT: ${{ toJson(strategy) }}
        run: echo "$STRATEGY_CONTEXT"
      - name: Dump matrix context
        env:
          MATRIX_CONTEXT: ${{ toJson(matrix) }}
        run: echo "$MATRIX_CONTEXT"
```
