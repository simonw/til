from datasette import hookimpl
from datasette_render_markdown import render_markdown

def _render_markdown(s):
    return render_markdown(
        s,
        extra_tags=["img", "hr", "br", "details", "summary", "input", "div", "span"],
        extra_attrs={
            "input": ["type", "disabled", "checked"],
            "img": ["src"],
            "div": ["class"],
            "span": ["class"],
        },
        extensions=["mdx_gfm:GithubFlavoredMarkdownExtension"],
    )


@hookimpl
def prepare_connection(conn):
    conn.create_function("render_markdown", 1, _render_markdown)
