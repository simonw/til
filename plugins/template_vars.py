from datasette import hookimpl
from bs4 import BeautifulSoup as Soup
import html
import re

non_alphanumeric = re.compile(r"[^a-zA-Z0-9\s]")
multi_spaces = re.compile(r"\s+")


def first_paragraph(html):
    soup = Soup(html, "html.parser")
    return str(soup.find("p"))


def highlight(s):
    s = html.escape(s)
    s = s.replace("b4de2a49c8", "<strong>").replace("8c94a2ed4b", "</strong>")
    return s


@hookimpl
def extra_template_vars(request, datasette):
    async def related_tils(til):
        path = til["path"]
        sql = """
        select
          til.topic, til.slug, til.title, til.created
        from til
          join similarities on til.path = similarities.other_id
        where similarities.id = :path
        order by similarities.score desc limit 10
        """
        result = await datasette.get_database().execute(
            sql,
            {"path": til["path"]},
        )
        return result.rows

    return {
        "q": request.args.get("q", ""),
        "highlight": highlight,
        "first_paragraph": first_paragraph,
        "related_tils": related_tils,
    }


@hookimpl
def prepare_connection(conn):
    conn.create_function("first_paragraph", 1, first_paragraph)
