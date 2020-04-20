from datasette import hookimpl
from datasette_render_markdown import render_markdown


@hookimpl
def prepare_connection(conn):
    conn.create_function("render_markdown", 1, render_markdown)
