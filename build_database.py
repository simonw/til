from bs4 import BeautifulSoup
from datetime import datetime, timezone
import httpx
import os
import pathlib
import subprocess
from urllib.parse import urlencode
import sqlite_utils
from sqlite_utils.db import NotFoundError
import time

root = pathlib.Path(__file__).parent.resolve()


def first_paragraph_text_only(html):
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.find("p").stripped_strings)


def get_file_times(repo_path, filepath):
    """Get created and updated times for a file, following renames."""
    # Get all commit dates for this file, following renames
    # First line is most recent (updated), last line is oldest (created)
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%cI", "--", filepath],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    if not output:
        return None
    dates = output.split("\n")
    updated_dt = datetime.fromisoformat(dates[0])
    created_dt = datetime.fromisoformat(dates[-1])
    return {
        "created": created_dt.isoformat(),
        "created_utc": created_dt.astimezone(timezone.utc).isoformat(),
        "updated": updated_dt.isoformat(),
        "updated_utc": updated_dt.astimezone(timezone.utc).isoformat(),
    }


def build_database(repo_path):
    db = sqlite_utils.Database(repo_path / "tils.db")
    table = db.table("til", pk="path")
    for filepath in root.glob("*/*.md"):
        fp = filepath.open()
        title = fp.readline().lstrip("#").strip()
        body = fp.read().strip()
        path = str(filepath.relative_to(root))
        slug = filepath.stem
        url = "https://github.com/simonw/til/blob/main/{}".format(path)
        # Do we need to render the markdown?
        path_slug = path.replace("/", "_")
        try:
            row = table.get(path_slug)
            previous_body = row["body"]
            previous_html = row["html"]
        except (NotFoundError, KeyError):
            previous_body = None
            previous_html = None
        record = {
            "path": path_slug,
            "slug": slug,
            "topic": path.split("/")[0],
            "title": title,
            "url": url,
            "body": body,
        }
        if (body != previous_body) or not previous_html:
            retries = 0
            response = None
            while retries < 3:
                headers = {}
                if os.environ.get("MARKDOWN_GITHUB_TOKEN"):
                    headers = {
                        "authorization": "Bearer {}".format(
                            os.environ["MARKDOWN_GITHUB_TOKEN"]
                        )
                    }
                response = httpx.post(
                    "https://api.github.com/markdown",
                    json={
                        # mode=gfm would expand #13 issue links and suchlike
                        "mode": "markdown",
                        "text": body,
                    },
                    headers=headers,
                )
                if response.status_code == 200:
                    record["html"] = response.text
                    print("Rendered HTML for {}".format(path))
                    break
                elif response.status_code == 401:
                    assert False, "401 Unauthorized error rendering markdown"
                else:
                    print(response.status_code, response.headers)
                    print("  sleeping 60s")
                    time.sleep(60)
                    retries += 1
            else:
                assert False, "Could not render {} - last response was {}".format(
                    path, response.headers
                )
        # Populate summary
        record["summary"] = first_paragraph_text_only(
            record.get("html") or previous_html or ""
        )
        # Get created/updated times, following renames
        file_times = get_file_times(repo_path, path)
        if file_times:
            record.update(file_times)
        with db.conn:
            table.upsert(record, alter=True)

    table.enable_fts(
        ["title", "body"], tokenize="porter", create_triggers=True, replace=True
    )


if __name__ == "__main__":
    build_database(root)
