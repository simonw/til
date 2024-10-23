# The most basic possible Hugo site

With [Claude's help](https://gist.github.com/simonw/6f7b6a40713b36749da845065985bb28) I figured out what I think is the most basic version of a static site generated using [Hugo](https://gohugo.io/).

I wanted a base template that set out a common layout, then two example of pages that used that layout to render content with a custom title.

This is my first time ever trying out Hugo so it's quite possible there's an even simpler approach, but this is what I got to.

## The layouts

Hugo uses a directory called `layouts` to define its templates. I created three files in this directory:

### layouts/_default/baseof.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ .Title }}</title>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
    {{ .Content }}
    <footer>
        <p>My Site Footer</p>
    </footer>
</body>
</html>
```
### layouts/_default/single.html

```html
{{ define "main" }}
    {{ .Content }}
{{ end }}
```
### layouts/index.html

```html
{{ define "main" }}
    {{ .Content }}
{{ end }}
```

Note that `index.html` and `single.html` are identical. I'm not sure why Hugo needed both - the `index.html` file is used for the homepage.

## The content

I created a `content` directory with two files in it:

### content/_index.md

```markdown
---
title: Welcome
---
# Welcome to my site

This is my homepage content in Markdown.
```

### content/about.html

```html
---
title: About
---
<h1>About Us</h1>
<p>This is the about page, written directly in HTML.</p>
```

Note that both of these have frontmatter at the top to define the title. This seems to be the right pattern for combining HTML content and Markdown content in the same project.

According to the [Hugo documentation](https://gohugo.io/content-management/organization/#index-pages-_indexmd):

> `_index.md` has a special role in Hugo. It allows you to add front matter and content to `home`, `section`, `taxonomy`, and `term` pages.

Since I'm not using the `taxonomy` and `term` features yet this probably isn't relevant to me.

## Getting Hugo working

Here's a Bash script that, when run, will create the directories and files listed above:

```bash
mkdir hugo-site
cd hugo-site
mkdir -p layouts/_default content
cat > layouts/_default/baseof.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>{{ .Title }}</title>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
    {{ .Content }}
    <footer>
        <p>My Site Footer</p>
    </footer>
</body>
</html>
EOF
cat > layouts/_default/single.html <<EOF
{{ define "main" }}
    {{ .Content }}
{{ end }}
EOF
cat > layouts/index.html <<EOF
{{ define "main" }}
    {{ .Content }}
{{ end }}
EOF
cat > content/_index.md <<EOF
---
title: Welcome
---
# Welcome to my site

This is my homepage content in Markdown.
EOF
cat > content/about.html <<EOF
---
title: About
---
<h1>About Us</h1>
<p>This is the about page, written directly in HTML.</p>
EOF
```

Having created these files (in a `hugo-site` folder) we can initialize a Hugo site like this:

```bash
hugo new site . --force
```
The `--force` flag is needed because we are creating the site in a directory that already contains files.

Now run this to preview the site in a browser:
```bash
hugo server
```
And visit `http://localhost:1313/` to see the site.

The About page is now located at `/about/` and the homepage is at `/`.

## Building the site for deployment

Running this command builds a static version of the site in the `public` directory:

```bash
hugo build
```
When I ran it I got this non-fatal warning:

```
WARN  found no layout file for "html" for kind "taxonomy": You should create a template file which matches Hugo Layouts Lookup Rules for this combination.
```
Since I wasn't using the `taxonomy` feature I added the following to the `hugo.conf` file that had been generated for me:

```toml
disableKinds = ['taxonomy', 'term']
```
After this, `hugo build` ran without warnings.

The `public` folder contained these files:

```
public
public/index.html
public/index.xml
public/about
public/about/index.html
public/sitemap.xml
```

`index.yml` is an RSS 2.0 feed, and `sitemap.xml` is a [Sitemap](https://www.sitemaps.org/).

Both of these had `example.org` hard-coded into them, e.g. `sitemap.xml` looked like this:

```xml
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.org/about/</loc>
  </url><url>
    <loc>https://example.org/</loc>
  </url>
</urlset>
```
The fix for that is to update `hugo.toml` to set the domain name where the site will be deployed:
```toml
baseURL = 'https://example.simonwillison.net/'
languageCode = 'en-us'
title = 'My example site'
disableKinds = ['taxonomy', 'term']
```
Running `hugo build` rewrites the `sitemap.xml` and `index.xml` files to use the correct domain name.

I haven't actually deployed a Hugo site yet, but I expect I'll try this using either [GitHub Pages](https://pages.github.com/) or [Netlify](https://www.netlify.com/) or [Cloudflare Pages](https://pages.cloudflare.com/) soon.
