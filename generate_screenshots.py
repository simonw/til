import hashlib
import pathlib
import subprocess
import sqlite_utils
import tempfile

root = pathlib.Path(__file__).parent.resolve()
TMP_PATH = pathlib.Path(tempfile.gettempdir())
SHOT_HASH_PATHS = [
    (root / "templates" / "row.html"),
    (root / "templates" / "til_base.html"),
]


def png_for_path(path):
    page_html = str(TMP_PATH / "generate-screenshots-page.html")
    # Use datasette to generate HTML
    proc = subprocess.run(["datasette", ".", "--get", path], capture_output=True)
    open(page_html, "wb").write(proc.stdout)
    # Now use puppeteer screenshot to generate a PNG
    proc2 = subprocess.run(
        [
            "puppeteer",
            "screenshot",
            page_html,
            "--viewport",
            "800x400",
            "--full-page=false",
        ],
        capture_output=True,
    )
    png_bytes = proc2.stdout
    return png_bytes


def generate_screenshots(root):
    db = sqlite_utils.Database(root / "tils.db")

    # The shot_hash incorporates a hash of all of row.html

    shot_html_hash = hashlib.md5()
    for filepath in SHOT_HASH_PATHS:
        shot_html_hash.update(filepath.read_text().encode("utf-8"))
    shot_html_hash = shot_html_hash.hexdigest()

    for row in db["til"].rows:
        path = row["path"]
        html = row["html"]
        shot_hash = hashlib.md5((shot_html_hash + html).encode("utf-8")).hexdigest()
        if shot_hash != row.get("shot_hash"):
            png = png_for_path("/{}/{}".format(row["topic"], row["slug"]))
            db["til"].update(path, {"shot": png, "shot_hash": shot_hash}, alter=True)
            print(
                "Got {} byte PNG for {} shot hash {}".format(len(png), path, shot_hash)
            )
        else:
            print("Skipped {} with shot hash {}".format(path, shot_hash))


if __name__ == "__main__":
    generate_screenshots(root)
