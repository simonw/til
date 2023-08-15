# Building a blog in Django

We launched the [Datasette Cloud blog](https://www.datasette.cloud/blog/) today. The Datasette Cloud site itself is a Django app - it uses Django and PostgreSQL to manage accounts, teams and soon billing and payments, then launches dedicated containers running Datasette for each customer.

It's been a while since I've built a new blog implementation in Django! I decided to make notes for the next time.

## Features

Here are the features I consider to be essential for a blog in 2023 (though they haven't changed much in over a decade):

- Blog posts have a title, summary, body and publication date. Optional: author information, tags
- Posts can be live or draft
- The blog index page shows the most recent entries
- Older entries are available via some kind of archive mechanism
- The blog has an Atom feed
- Entries have social media card metadata, to enhance links to them on Mastodon and Twitter
- Markdown is a nice-to-have for editing the posts

## The models

Here's the Django model for the blog (I generated the first version of this with ChatGPT, then iterated on it):

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags
import markdown
from django.utils.html import mark_safe


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Entry(models.Model):
    title = models.CharField(max_length=200)
    created = models.DateTimeField(default=timezone.now)
    slug = models.SlugField()
    summary = models.TextField()
    body = models.TextField()
    card_image = models.URLField(
        blank=True, null=True, help_text="URL to image for social media cards"
    )
    authors = models.ManyToManyField(User, through="Authorship")
    tags = models.ManyToManyField(Tag, blank=True)

    is_draft = models.BooleanField(
        default=False,
        help_text="Draft entries do not show in index pages but can be visited directly if you know the URL",
    )

    class Meta:
        verbose_name_plural = "entries"

    @property
    def summary_rendered(self):
        return mark_safe(markdown.markdown(self.summary, output_format="html5"))

    @property
    def summary_text(self):
        return strip_tags(markdown.markdown(self.summary, output_format="html5"))

    @property
    def body_rendered(self):
        return mark_safe(markdown.markdown(self.body, output_format="html5"))

    def get_absolute_url(self):
        return "/blog/%d/%s/" % (self.created.year, self.slug)

    def __str__(self):
        return self.title


class Authorship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
```
It's pretty self-explanatory. The most interesting features are the `is_draft` flag and the way it provides `.summary_rendered` and `.body_rendered` properties that return Markdown rendered as HTML.

The URL format for this blog is `/blog/2023/welcome/` - in my experience name-spacing posts by year makes the most sense, since even the most active blogs usually only have a few posts every month.

## The views

Here are the view functions defined the `views.py` module for my `blog/` application:

```python
from django.contrib.syndication.views import Feed
from django.shortcuts import render, get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from .models import Entry, Tag

ENTRIES_ON_HOMEPAGE = 5


def index(request):
    entries = list(
        Entry.objects.filter(is_draft=False).order_by("-created")[
            : ENTRIES_ON_HOMEPAGE + 1
        ]
    )
    has_more = False
    if len(entries) > ENTRIES_ON_HOMEPAGE:
        has_more = True
        entries = entries[:ENTRIES_ON_HOMEPAGE]
    return render(
        request, "blog/index.html", {"entries": entries, "has_more": has_more}
    )


def entry(request, year, slug):
    entry = get_object_or_404(Entry, created__year=year, slug=slug)
    return render(
        request,
        "blog/entry.html",
        {"entry": entry},
    )


def year(request, year):
    entries = Entry.objects.filter(created__year=year, is_draft=False).order_by(
        "-created"
    )
    return render(request, "blog/year.html", {"entries": entries, "year": year})


def archive(request):
    entries = Entry.objects.filter(is_draft=False).order_by("-created")
    return render(request, "blog/archive.html", {"entries": entries})


def tag(request, slug):
    tag = Tag.objects.get(slug=slug)
    entries = tag.entry_set.filter(is_draft=False).order_by("-created")
    return render(request, "blog/tag.html", {"tag": tag, "entries": entries})
```
## The Atom feed

The most interesting part of the `views.py` file is this bit - defining the Atom feed:

```python
class BlogFeed(Feed):
    title = "Datasette Cloud"
    link = "/blog/"
    feed_type = Atom1Feed

    def items(self):
        return Entry.objects.filter(is_draft=False).order_by("-created")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary_rendered + "\n" + item.body_rendered

    def item_link(self, item):
        return "/blog/%d/%s/" % (item.created.year, item.slug)

    def item_author_name(self, item):
        return (
            ", ".join([a.get_full_name() or str(a) for a in item.authors.all()]) or None
        )

    def get_feed(self, obj, request):
        feedgen = super().get_feed(obj, request)
        feedgen.content_type = "application/xml; charset=utf-8"
        return feedgen
```
This is using the [Django syndication feed framework](https://docs.djangoproject.com/en/4.2/ref/contrib/syndication/). The resulting Atom feed can be found here:

https://www.datasette.cloud/blog/feed/

There's one extra trick here: I'm over-riding the default `content-type` header and setting it to `"application/xml; charset=utf-8`.

Django defaults to using `application/atom+xml; charset=utf-8` which is correct... but causes most browsers to trigger a download rather than rendering the XML in the browser directly.

I like to be able to click on a feed link and see the XML before I paste the URL into my feed reader software, so I prefer to use `application/xml` instead.

## Social media cards

It's easy to forget these, but they're really important - with the right markup links to posts shared on Mastodon, Twitter, LinkedIn and Facebook will look MUCH better.

Here's a snipet from my `entry.html` template:
```html+django
{% block extra_head %}
{% if entry.card_image %}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{{ entry.card_image }}">
{% else %}
<meta name="twitter:card" content="summary">
{% endif %}
<meta name="twitter:creator" content="@datasetteproj">
<meta property="og:url" content="https://www.datasette.cloud{{ request.path }}">
<meta property="og:title" content="{{ entry.title }} - Datasette Cloud">
{% if entry.card_image %}<meta property="og:image" content="{{ entry.card_image }}">{% endif %}
<meta property="og:type" content="article">
<meta property="og:description" content="{{ entry.summary_text }}">
{% if entry.is_draft %}
<meta name="robots" content="noindex">
{% endif %}
{% endblock %}
```
There's one other detail in there: if an entry is a draft entry I serve `<meta name="robots" content="noindex">` to prevent it from being accidentally indexed by search engines.

## URL configuration

Here's the URL configuration from `urls.py`:

```python
    # Blog
    path("blog/", blog_views.index),
    path("blog/<int:year>/<slug:slug>/", blog_views.entry),
    path("blog/archive/", blog_views.archive),
    path("blog/<int:year>/", blog_views.year),
    path("blog/tag/<slug:slug>/", blog_views.tag),
    path("blog/feed/", blog_views.BlogFeed()),
```

## Tests

I added a quick suite of tests, mainly to check that `is_draft` was working correctly but also to ensure the Atom feed works.

Testing the feed was particularly important because it's at the highest risk of accidentally breaking without me noticing it - errors that affect the HTML of the blog are much more obvious.

```python
import pytest
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Entry, Tag
from xml.etree import ElementTree as ET


@pytest.fixture
def client():
    from django.test import Client

    return Client()


@pytest.fixture
def five_entries():
    author = User.objects.create_user(username="author")
    all = Tag.objects.get_or_create(name="All", slug="all")[0]
    entries = []
    for i in range(5):
        i += 1
        entry = Entry.objects.create(
            title=f"Test Entry {i}",
            slug=f"test-entry-{i}",
            created=timezone.make_aware(datetime(2023, 5, i), timezone.utc),
            summary=f"This is test entry {i}",
            body=f"This is the body of test entry {i}.",
            is_draft=i == 1,
        )
        entry.authors.add(author)
        entry.tags.add(all)
        entries.append(entry)

    return entries


@pytest.mark.django_db
def test_index_page(client, five_entries):
    response = client.get("/blog/")
    html = response.content.decode("utf-8")

    # Should have five entries without a more link
    for i in range(5):
        i += 1
        if i == 1:
            # It's the draft one
            assert f"Test Entry {i}" not in html
            assert f"This is test entry {i}" not in html
        else:
            assert f"Test Entry {i}" in html
            assert f"This is test entry {i}" in html
    assert "Older entries" not in html

    # Add two more entries to get a more link
    Entry.objects.create(
        title="Test Entry 6", slug="test-entry-6", summary=".", body="."
    )
    Entry.objects.create(
        title="Test Entry 7", slug="test-entry-7", summary=".", body="."
    )
    response2 = client.get("/blog/")
    html2 = response2.content.decode("utf-8")
    assert "Older entries" in html2


@pytest.mark.django_db
def test_entry_page(client, five_entries):
    # Test a draft and a not-draft one
    draft_entry = five_entries[0]
    not_draft_entry = five_entries[1]
    for entry, should_be_draft in (
        (draft_entry, True),
        (not_draft_entry, False),
    ):
        response = client.get(f"/blog/{entry.created.year}/{entry.slug}/")
        html = response.content.decode("utf-8")

        # Check that each entry's title and body are present on their respective page
        assert entry.title in html
        assert entry.body in html

        if should_be_draft:
            assert "(draft)" in html
            assert '<meta name="robots" content="noindex">' in html
        else:
            assert "(draft)" not in html
            assert '<meta name="robots" content="noindex">' not in html


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path", ("/blog/", "/blog/archive/", "/blog/2023/", "/blog/tag/all/")
)
def test_draft_entry_not_visible(client, five_entries, path):
    draft_entry = five_entries[0]
    assert draft_entry.title == "Test Entry 1"
    # It should not be on any of the pages
    response = client.get(path)
    html = response.content.decode("utf-8")
    assert draft_entry.title not in html


@pytest.mark.django_db
def test_atom_feed(client, five_entries):
    response = client.get("/blog/feed/")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/xml; charset=utf-8"
    xml = response.content.decode("utf-8")
    et = ET.fromstring(xml)
    assert "<title>Datasette Cloud</title>" in xml
    expected_entries = [e for e in five_entries if not e.is_draft]
    assert len(expected_entries) == 4
    expected_entries.sort(key=lambda e: e.created, reverse=True)
    # Should have the non-draft entries
    entries = et.findall("{http://www.w3.org/2005/Atom}entry")
    assert len(entries) == 4
    for xml_entry, entry in zip(entries, expected_entries):
        assert xml_entry.find("{http://www.w3.org/2005/Atom}title").text == entry.title
        assert (
            xml_entry.find("{http://www.w3.org/2005/Atom}link").attrib["href"]
            == f"http://testserver/blog/{entry.created.year}/{entry.slug}/"
        )
        assert (
            xml_entry.find(
                "{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name"
            ).text
            == "author"
        )
```

## The finished blog

Check it out at https://www.datasette.cloud/blog/

Consider the code snippets in this TIL licensed under [Apache License, Version 2.0](https://opensource.org/license/apache-2-0/).
