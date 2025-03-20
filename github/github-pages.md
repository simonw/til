# GitHub Pages: The Missing Manual

[GitHub Pages](https://pages.github.com/) is an excellent free hosting platform, but the documentation is missing out on some crucial details.

I built a [simonw/playing-with-github-pages](https://github.com/simonw/playing-with-github-pages) repo today. This is what I learned:

## Enabling GitHub Pages for a repo

Navigate to **Settings -> Pages** - or use the repository URL plus `/settings/pages` - and tell it which branch to deploy (usually `main`):

![Build and deployment: Source: Deploy from a branch GitHub Pages is currently disabled. Select a source below to enable GitHub Pages for this repository. Save button.](https://github.com/simonw/til/assets/9599/b899b14c-e247-4e52-9157-d2b0c6b0c7c8)

## Add a .nojekyll file to disable Jekyll

GitHub Pages was originally built around the [Jekyll](https://jekyllrb.com/) Ruby static site framework. You can turn that off by adding a `.nojekyll` file to your repository root.

Weirdly, I found that this also fixed an issue where files in a directory called `node_modules/` were serving as a 404. Adding `.nojekyll` fixed that.

## /foo will serve content from foo.html, if it exists

If you create a file called `foo.html` in the repo and visit the page `/foo` you will see content from that file.

- https://simonw.github.io/playing-with-github-pages/ serves `index.html`
- https://simonw.github.io/playing-with-github-pages/foo serves `foo.html`
- https://simonw.github.io/playing-with-github-pages/foo.html serves `foo.html`

## /folder will redirect to /folder/

- https://simonw.github.io/playing-with-github-pages/folder redirects to `/folder/`

This only happens if the folder exists.


## /folder/ will serve folder/index.html

- https://simonw.github.io/playing-with-github-pages/folder/ serves `folder/index.html`
- https://simonw.github.io/playing-with-github-pages/folder/index serves `folder/index.html`
- https://simonw.github.io/playing-with-github-pages/folder/index.html serves `folder/index.html`

## A 404.html file will be used for 404s

Creating a `404.html` file in the root of the directory customizes the page served for a 404 error.

## The .html rule beats the folder redirect rule

I created `folder2.html` and `folder2/index.html`:

- https://simonw.github.io/playing-with-github-pages/folder2 serves `folder2.html` (does not redirect)
- https://simonw.github.io/playing-with-github-pages/folder2/ serves `folder2/index.html`
- https://simonw.github.io/playing-with-github-pages/folder2/index serves `folder2/index.html`
- https://simonw.github.io/playing-with-github-pages/folder2/index.html serves `folder2/index.html`

## index.json works as an index document too

Here's [a StackOverflow post](https://stackoverflow.com/questions/39199042/serve-json-data-from-github-pages/50667394#50667394) about this.

I created `json/index.json`:

- https://simonw.github.io/playing-with-github-pages/json redirects to `/json/`
- https://simonw.github.io/playing-with-github-pages/json/ serves `json/index.json`
- https://simonw.github.io/playing-with-github-pages/json/index serves a 404
- https://simonw.github.io/playing-with-github-pages/json/index.json serves `json/index.json`

Note that `/json/index` served a 404 - so unlike `.html` the `.json` extension is not automatically appended.

## If there is no index.html or index.json a folder will 404

I created `folder-with-no-index` with a `bar.html` file but no `index.html` or `index.json`:

- https://simonw.github.io/playing-with-github-pages/folder-with-no-index redirects to `/folder-with-no-index/`
- https://simonw.github.io/playing-with-github-pages/folder-with-no-index/ serves a 404

## Custom redirects are not supported

There is no mechanism to set your own custom redirects. The suggested alternative is to serve an HTML page with a 200 status code and content that looks like this:

```html
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0;url=https://example.com"/>
    <link rel="canonical" href="https://example.com"/>
    <title>Redirecting to https://example.com</title>
    <style>
        body {
            font-family: sans-serif;
            max-width: 40em;
            margin: 1em auto;
        }
    </style>
</head>
<body>
    <h1>Redirecting to https://example.com</h1>
    <p>This document has moved!</p>
    <p>Redirecting to <a href="https://example.com">https://example.com</a> in 0 seconds.</p>
</body>
</html>
```

I figured this out from [codepo8/github-redirection-demo/](https://github.com/codepo8/github-redirection-demo/) (which uses Jekyll) followed by running `curl -i` against `https://codepo8.github.io/github-redirection-demo/plain-redirect`:

```
% curl -i 'https://codepo8.github.io/github-redirection-demo/plain-redirect'
HTTP/2 200 
server: GitHub.com
content-type: text/html; charset=utf-8
...
```
## These days you can do custom things with GitHub Actions

See [Building and deploying a custom site using GitHub Actions and GitHub Pages](https://til.simonwillison.net/github-actions/github-pages) for a simple example.
