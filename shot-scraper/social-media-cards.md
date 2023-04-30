# Social media cards generated with shot-scraper

My [TIL website](https://til.simonwillison.net/) has social media card images to make links shared from it look slightly more interesting when shared on sites like Mastodon and Twitter.

I upgraded them today to use higher quality retina JPEG images stored in an S3 bucket - they had previously used smaller PNGs stored directly in the database itself.

Here's an annotated copy of the current version of [the script](https://github.com/simonw/til/blob/21549e289ca8e5f941fab9cd06f7baa470863ceb/generate_screenshots.py) that generates and stores the images. It works by shelling out to my [shot-scraper](https://shot-scraper.datasette.io/) and [s3-credentials](https://s3-credentials.readthedocs.io/) tools.

The images it creates look like this:

![Simon Willison's TILs - Tommy's Margarita - A few years ago I decided to learn how to make some classic cocktails. It is a very rewarding hobby. Of all of the drinks that I have learned to make, by far the biggest crowd pleaser is the Tommy's margarita. It is surprisingly easy, and is guaranteed to delight guests. It's also a great introduction to cocktail making in general.](https://user-images.githubusercontent.com/9599/235336801-57ce5c84-0629-41ac-8589-d26846aaace9.png)


## Initializing the script

```python
import hashlib
import json
import pathlib
import subprocess
import sqlite_utils
import tempfile

root = pathlib.Path(__file__).parent.resolve()
TMP_PATH = pathlib.Path(tempfile.gettempdir())
SHOT_HASH_PATHS = [
    (root / "templates" / "pages" / "{topic}" / "{slug}.html"),
    (root / "templates" / "til_base.html"),
]
```
The script runs in the root of the repository. It needs a temp directory to generate HTML used to create the screenshots.

The image filenames are MD5 hashes that combine the content of the TIL page with the hashed content of the templates used to generate the page.

This means a change to the page content or to any of those templates will cause the relevant images to be re-generated.

## Fetching the list of images already in S3

```python
def s3_contents():
    proc = subprocess.run(
        ["s3-credentials", "list-bucket", "til.simonwillison.net"], capture_output=True
    )
    return [item["Key"] for item in json.loads(proc.stdout)]
```
In order to decide which images are missing from the S3 bucket and need to be generated I shell out to my `s3-credentials`:

    s3-credentials list-bucket til.simonwillison.net

This uses environment variables for the AWS credentials, which are made available in the GitHub Actions workflow.

## Capturing the screenshot JPEGs

```python
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
```
This is the function that generates the screenshots.

It uses two tricks. The first is to generate HTML for the page using Datasette:
```bash
datasette . --get /deno/deno-kv
```
This command runs Datasette against the current directory - automatically picking up the custom templates in the `templates/` folder. It simulates running an HTTP request against the specified path.

The `--get path` option causes Datasette NOT to start running a web server - instead, it simulates that request and writes the HTML to stdout.

The Python script then saves that in the temp directory in a file called `generate-screenshots-page.html`.

The next step is to generate the screenshot, by running this command:

```bash
shot-scraper shot generate-screenshots-page.html \
    -w 800 -h 400 --retina --quality 60 -o -
```
This creates a 800x400 screenshot, but since `--retina` is passed it actually creates it at 1600x800. It saves it as a JPEG with a quality factor of 60 - which actually looks fine since the retina images are scaled down by the browser. `-o -` writes the generated image to standard output, so Python can capture it.

Returning `proc2.stdout` returns the binary JPEG data.

## Generating missing screenshots for every page

The rest of the script figures out which screenshots to generate, generates them and uploads them to S3.

To do this, it looks through all 400+ TILs in the database. For each one, it calculates the `shot_hash` which is an MD5 hash incorporating the HTML content of the TIL from the database, combined with the hash of the templates used to generate it.

It records this hash to the database, then checks to see if there is a file in the S3 bucket for `{shot_hash}.jpg`.

If that file doesn't exist, it calls `jpeg_for_path(path)` to generate the JPEG. Then it uploads that JPEG to the S3 bucket by shelling out to `s3-credentials`:

```bash
s3-credentials put-object til.simonwillison.net shot-hash.jpg - \
    --content-type image/jpeg --silent
```
The `-` argument tells `s3-credentials` to read the binary JPEG data from standard input.

We set the correct Content-Type on it to ensure browsers will render it correctly, and use `--silent` to disable the progress bar.

And that's everything! It's less than 100 lines of Python but it does the job, ensuring every one of my TILs has a high quality social media card image.

The script is run by [this GitHub Actions workflow](https://github.com/simonw/til/blob/main/.github/workflows/build.yml) every time I push a new commit to the repository.

```python
def generate_screenshots(root):
    db = sqlite_utils.Database(root / "tils.db")

    # If the old 'shot' column exists, drop it
    if "shot" in db["til"].columns_dict:
        db["til"].transform(drop=["shot"])

    # shot_hash incorporates a hash of key templates
    shot_html_hash = hashlib.md5()
    for filepath in SHOT_HASH_PATHS:
        shot_html_hash.update(filepath.read_text().encode("utf-8"))
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
```
