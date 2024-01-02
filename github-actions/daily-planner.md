# GitHub Actions, Issues and Pages to build a daily planner

I'm trying a new thing: a private daily planner, where each day I note down my goals for the day and make notes on my progress towards them as the day progresses.

I love using GitHub Issues for notes (see [this comment](https://news.ycombinator.com/item?id=38823002#38836569)) so I decided to set something up there.

I want a fresh issue in my private `simonw/planner` repo for every day that I'm working. The issue should have the day's date, and should prompt me for my goals.

So... I needed a mechanism for automatically creating a new issue every day.

## Issue templates and URLs

I created a file `.github/ISSUE_TEMPLATE/day.yml` with the following:`

```yaml
name: Daily Planner Issue
description: Template for daily planning.
title: "[Date] - Daily Plan"
labels: ["daily-planner"]
body:
  - type: markdown
    attributes:
      value: "## Daily Planner"
  - type: textarea
    attributes:
      label: "Priorities"
      description: "List your top priorities for the day."
      placeholder: "1. Priority One\n2. Priority Two\n3. Priority Three"
  - type: textarea
    attributes:
      label: "To-Do List"
      description: "List all tasks that you need to complete today."
      placeholder: "- [ ] Task 1\n- [ ] Task 2\n- [ ] Task 3"
```
This defines an [issue template](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository). By selecting that template I get a form that looks like this:

![Issue: Daily Planner issue. Has a title pre-populated to [Date] - Daily Plan, then a Priorities textarea, then a To-Do List textarea. At the bottom is a Submit new issue button.](https://static.simonwillison.net/static/2024/daily-planner.jpg)

This is a neat starting point, but I can do better than that. It turns out you can pre-populate the title field of an issue by passing `?title=...` in the URL.

`https://github.com/simonw/planner/issues/new?template=day.yml&title=encoded-title-goes-here`

This URL will pre-populate that form with a custom title.

I can link to that page with today's date to create a new issue - but I'd like to be able to automatically jump to the day's issue if it's been created, and only link to the form if it has not.

## A page that creates or redirects to the issue for the day

My repo is private, but private repos can still use GitHub Pages. I decided to solve this problem using a client-side JavaScript page that I could set as the homepage in Firefox, so hitting `Command+N` on my keyboard would open up my daily planner issue, or the pre-populated creation form if it doesn't exist yet.

I got ChatGPT to write the initial version of the following, which I then tweaked to fully meet my evolving requirements:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Daily Planner Issue Redirector</title>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date();
            const formattedToday = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
            fetch(`issue-titles.json?${Math.random()}`)
                .then(response => response.json())
                .then(issues => {
                    const matchingIssue = issues.find(issue => issue.title.startsWith(formattedToday));
                    if (matchingIssue) {
                        window.location.href = matchingIssue.url;
                    } else {
                        const fullDateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                        const fullDateString = today.toLocaleDateString('en-US', fullDateOptions).replace(/,/g, '');
                        const title = `${formattedToday}: ${fullDateString}`;
                        const encodedTitle = encodeURIComponent(title);
                        window.location.href = `https://github.com/simonw/planner/issues/new?template=day.yml&title=${encodedTitle}`;
                    }
                })
                .catch(error => console.error('Error fetching issue titles:', error));
        });
    </script>
</head>
<body>
    <h1>Redirecting...</h1>
</body>
</html>
```
My initial prompt for this was:

> Write an index.html file which runs JavaScript that does the following:
> 
> Generate a string for today's date like this: 2023-12-22 Friday 22nd December
> 
> Fetch issue-titles.json using fetch()
> 
> The format of that will be:
> ```
> [
>   {
>     "title": "2023-12-22 Friday 22nd December",
>     "url": "https://github.com/simonw/planner/issues/1"
>   }
> ]
> ```
> If the calculated title is already there, redirect the user to that url
> 
> Otherwise, send the user to this page:
> 
> https://github.com/simonw/planner/issues/new?template=day.yml&title=
> 
> Fill in the title with the URL a encoded title

As you can see, the trick here is that it expects to be able to load an `issue-titles.json` file with a list of issues in the repo.

The repo may be private, but I'm OK with exposing the issue titles here.

How to create `issue-titles.json`? I can do that using GitHub Actions.

## GitHub Actions workflow to create issue-titles.json

I started with this prompt:

> Write a GitHub Actions workflow which retrieves a list of issue names and URLs for the current repo, converts those into a JSON array and then publishes that as issue-titles.json using GitHub Pages 

I got back this:

```yaml
name: Generate Issues JSON

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *' # Runs every day at midnight

jobs:
  generate-json:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Fetch Issues
      id: get-issues
      uses: actions/github-script@v5
      with:
        script: |
          const response = await github.rest.issues.listForRepo({
            owner: context.repo.owner,
            repo: context.repo.repo,
            state: 'open'
          });
          return response.data.map(issue => ({ title: issue.title, url: issue.html_url }));

    - name: Write JSON File
      run: echo '${{ toJSON(steps.get-issues.outputs.result) }}' > issue-titles.json

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
        publish_branch: gh-pages # The branch GitHub Pages uses
        keep_files: true
```

This is using an older way of deploying to GitHub Pages. I hand-edited the workflow a few times until I got this, stored in `.github/workflows/issues.yml`:

```yaml
name: Generate Issues JSON

permissions:
  contents: write
  issues: read

on:
  workflow_dispatch:
  push:
  issues:
    types: [opened]

jobs:
  generate-json:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Fetch Issues
      id: get-issues
      uses: actions/github-script@v5
      with:
        script: |
          const fs = require('fs');
          const issues = await github.rest.issues.listForRepo({
            owner: context.repo.owner,
            repo: context.repo.repo,
            state: 'all',
            per_page: 100,
            sort: 'created',
            direction: 'desc'
          });
          const issueData = issues.data.map(issue => ({ title: issue.title, url: issue.html_url }));
          fs.writeFileSync('issue-titles.json', JSON.stringify(issueData, null, 2))

    - name: Commit and push if it changed
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add -A
        timestamp=$(date -u)
        git commit -m "Latest data: ${timestamp}" || exit 0
        git push
```
Then I configured GitHub Pages for that repo like this:

![GitHub Pages settings - source is Deploy from a branch, it says my site is now live at simonw.github.io/planner](https://static.simonwillison.net/static/2024/daily-planner-pages-config.jpg)

Adding this all together, I now have a mechanism where any time I open a new issue the `issue-titles.json` file is updated, and then deployed to GitHub Pages along with the `index.html` page that reads it and redirects to an issue or to the form that creates a new one.

My `simonw/planner` private repo now contains the following files:

```
index.html
issue-titles.json
.github/workflows/issues.yml
.github/ISSUE_TEMPLATE/day.yml
```

The generated `issue-titles.json` file currently looks like this:

```json
[
  {
    "title": "2024-01-01: Monday January 1 2024",
    "url": "https://github.com/simonw/planner/issues/5"
  },
  {
    "title": "2023-12-30: Saturday December 30 2023",
    "url": "https://github.com/simonw/planner/issues/4"
  },
  {
    "title": "2023-12-27: Wednesday December 27 2023",
    "url": "https://github.com/simonw/planner/issues/3"
  },
  {
    "title": "2023-12-22: Friday December 22 2023",
    "url": "https://github.com/simonw/planner/issues/2"
  }
]
```

You can visit the deployed site at https://simonw.github.io/planner/ but since you're not logged in as me it will just redirect you to a 404 page.

## It works!

Now, any time I hit `Command+N` in Firefox I get a browser window that loads https://simonw.github.io/planner/ and then either redirects me to the issue for today or sends me to a pre-populated form to create a new issue.

I love throwing together little custom applications like this on top of GitHub Actions and GitHub Pages.

I also love that I didn't have to write much code for this at all - ChatGPT is good enough at both GitHub Actions syntax and HTML and JavaScript that I could get it to do 80% of the work for me.
