from datasette import hookimpl
import html


def highlight(s):
    s = html.escape(s)
    s = s.replace("b4de2a49c8", "<strong>").replace("8c94a2ed4b", "</strong>")
    return s


@hookimpl
def extra_template_vars(request):
    return {
        "q": request.args.get("q", ""),
        "highlight": highlight,
    }
