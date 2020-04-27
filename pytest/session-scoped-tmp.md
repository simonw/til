# Session-scoped temporary directories in pytest

I habitually use the `tmpdir` fixture in pytest to get a temporary directory that will be cleaned up after each test, but that doesn't work with `scope="session"` - which can be used to ensure an expensive fixture is run only once per test session and the generated content is used for multiple tests.

To get a temporary directory that works with `scope="session"`, use the `tmp_path_factory` built-in pytest fixture like this:

```python
import pytest


@pytest.fixture(scope="session")
def template_dir(tmp_path_factory):
    template_dir = tmp_path_factory.mktemp("page-templates")
    pages_dir = template_dir / "pages"
    pages_dir.mkdir()
    (pages_dir / "about.html").write_text("ABOUT!", "utf-8")
    (pages_dir / "request.html").write_text("request", "utf-8")
    return template_dir


def test_about(template_dir):
    assert "ABOUT!" == (template_dir / "pages" / "about.html").read_text()


def test_request(template_dir):
    assert "request" == (template_dir / "pages" / "request.html").read_text()
```

Example: https://github.com/simonw/datasette/blob/1b7b66c465e44025ec73421bd69752e42f108321/tests/test_custom_pages.py#L16-L45
