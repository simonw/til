from datasette import hookimpl


@hookimpl
def extra_template_vars(request):
    return {"q": request.raw_args.get("q") or ""}
