import hashlib
import json
import pathlib
import subprocess
import sqlite_utils
import tempfile

root = pathlib.Path(__file__).parent.resolve()
TMP_PATH = pathlib.Path(tempfile.gettempdir())

# Change the following manually any time the templates have changed
# to a point that all of the screenshots need to be re-taken
# https://github.com/simonw/til/issues/82
SHOT_HASH = "1"


def s3_contents():
    proc = subprocess.run(
        ["s3-credentials", "list-bucket", "til.simonwillison.net"], capture_output=True
    )
    return [item["Key"] for item in json.loads(proc.stdout)]


def jpeg_for_path(path):
    page_html = str(TMP_PATH / "generate-screenshots-page.html")
    # Use datasette to generate HTML
    proc = subprocess.run(["datasette", ".", "--get", path], capture_output=True)
    open(page_html, "wb").write(proc.stdout)
    # Now use shot-scraper to generate a PNG
    proc2 = subprocess.run(
        [
            "shot-scraper",
            "shot",
            page_html,
            "-w",
            "800",
            "-h",
            "400",
            "--retina",
            "--quality",
            "60",
            "-o",
            "-",
        ],
        capture_output=True,
    )
    return proc2.stdout


def generate_screenshots(root):
    db = sqlite_utils.Database(root / "tils.db")

    # If the old 'shot' column exists, drop it
    if "shot" in db["til"].columns_dict:
        db["til"].transform(drop=["shot"])

    # shot_hash incorporates a hash of key templates
    shot_html_hash = hashlib.md5()
    shot_html_hash.update(SHOT_HASH)
    shot_html_hash = shot_html_hash.hexdigest()

    s3_keys = s3_contents()

    for row in db["til"].rows:
        path = row["path"]
        html = row["html"]
        shot_hash = hashlib.md5((shot_html_hash + html).encode("utf-8")).hexdigest()
        shot_filename = "{}.jpg".format(shot_hash)
        if shot_hash != row.get("shot_hash") or shot_filename not in s3_keys:
            jpeg = jpeg_for_path("/{}/{}".format(row["topic"], row["slug"]))
            db["til"].update(path, {"shot_hash": shot_hash}, alter=True)
            # Store it to S3
            subprocess.run(
                [
                    "s3-credentials",
                    "put-object",
                    "til.simonwillison.net",
                    shot_filename,
                    "-",
                    "--content-type",
                    "image/jpeg",
                    "--silent",
                ],
                input=jpeg,
            )
            print(
                "Stored {} byte JPEG for {} shot hash {}".format(
                    len(jpeg), path, shot_hash
                )
            )
        else:
            print("Skipped {} with shot hash {}".format(path, shot_hash))


if __name__ == "__main__":
    generate_screenshots(root)
