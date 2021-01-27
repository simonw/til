# Testing cookiecutter templates with pytest

I added some unit tests to my [datasette-plugin](https://github.com/simonw/datasette-plugin) cookiecutter template today, since the latest features involved adding a `hooks/post_gen_project.py` script.

Here's [the full test script](https://github.com/simonw/datasette-plugin/blob/503e6fef8e1000ab70103a61571d47ce966064ba/tests/test_cookiecutter_template.py) I wrote. It lives in `tests/test_cookiecutter_template.py` in the root of the repository.

To run the tests I have to use `pytest tests` because running just `pytest` gets confused when it tries to run the templated tests that form part of the cookiecutter template.

The pattern I'm using looks like this:

```python
from cookiecutter.main import cookiecutter
import pathlib

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)


def test_static_and_templates(tmpdir):
    generate(
        tmpdir,
        {
            "plugin_name": "foo",
            "description": "blah",
            "include_templates_directory": "y",
            "include_static_directory": "y",
        },
    )
    assert paths(tmpdir) == {
        "datasette-foo",
        "datasette-foo/.github",
        "datasette-foo/.github/workflows",
        "datasette-foo/.github/workflows/publish.yml",
        "datasette-foo/.github/workflows/test.yml",
        "datasette-foo/.gitignore",
        "datasette-foo/datasette_foo",
        "datasette-foo/datasette_foo/__init__.py",
        "datasette-foo/datasette_foo/static",
        "datasette-foo/datasette_foo/templates",
        "datasette-foo/README.md",
        "datasette-foo/setup.py",
        "datasette-foo/tests",
        "datasette-foo/tests/test_foo.py",
    }
    assert (
        'package_data={\n        "datasette_foo": ["static/*", "templates/*"]\n    }'
    ) in read_setup_py(tmpdir)


def generate(directory, context):
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=str(directory),
        no_input=True,
        extra_context=context,
    )


def read_setup_py(tmpdir):
    return (tmpdir / "datasette-foo" / "setup.py").read_text("utf-8")


def paths(directory):
    paths = list(pathlib.Path(directory).glob("**/*"))
    paths = [r.relative_to(directory) for r in paths]
    return {str(f) for f in paths if str(f) != "."}
```
