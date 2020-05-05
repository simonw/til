from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datasette import hookimpl
from datasette_render_markdown import render_markdown


def _render_markdown(s):
    return render_markdown(
        s,
        extra_tags=["img", "hr", "br", "details", "summary", "input", "div", "span",],
        extra_attrs={
            "input": ["type", "disabled", "checked"],
            "img": ["src", "alt"],
            "div": ["class"],
            "span": ["class"],
            "a": ["href"],
        },
        extensions=["mdx_gfm:GithubFlavoredMarkdownExtension"],
    )


def rewrite_github_images(html, base_url):
    "Rewrite image src= to be relative to base_url"
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img"):
        img["src"] = urljoin(base_url, img["src"]).replace("/blob/", "/raw/")
    return str(soup.body).replace("<body>", "").replace("</body>", "").strip()


@hookimpl
def prepare_connection(conn):
    conn.create_function("render_markdown", 1, _render_markdown)
    conn.create_function("rewrite_github_images", 2, rewrite_github_images)
