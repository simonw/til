# Testing things in Fedora using Docker

I got [a report](https://twitter.com/peterjanes/status/1552407491819884544) of a bug with my [s3-ocr tool](https://simonwillison.net/2022/Jun/30/s3-ocr/) running on Fedora.

I attempted to replicate the bug in a Fedora container using Docker, by running this command:

```
docker run -it fedora:latest /bin/bash
```
This downloaded [the official image](https://hub.docker.com/_/fedora) and dropped me into a Bash shell.

It turns out Fedora won't let you run `pip install` with its default Python 3 without first creating a virtual environment:

```
[root@d1146e0061d1 /]# python3 -m pip install s3-ocr
/usr/bin/python3: No module named pip
[root@d1146e0061d1 /]# python3 -m venv project_venv
[root@d1146e0061d1 /]# source project_venv/bin/activate
(project_venv) [root@d1146e0061d1 /]# python -m pip install s3-ocr
Collecting s3-ocr
  Downloading s3_ocr-0.5-py3-none-any.whl (14 kB)
Collecting sqlite-utils
  ...
```
Having done that I could test out my `s3-ocr` command like so:

```
(project_venv) [root@d1146e0061d1 /]# s3-ocr start --help
Usage: s3-ocr start [OPTIONS] BUCKET [KEYS]...

  Start OCR tasks for PDF files in an S3 bucket

      s3-ocr start name-of-bucket path/to/one.pdf path/to/two.pdf
  ...
```
