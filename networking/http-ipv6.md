# Making HTTP calls using IPv6

Tiny TIL today: I learned how to make an HTTP call to an IPv6 address. The trick is to enclose the address in the URL in square braces:

    http://[2a09:8280:1::1:2741]

Here's that working as a request to www.pillarpointstewards.com (hosted on [Fly.io](https://fly.io/) which issues IPv6 addresses) using the [httpx](https://www.python-httpx.org/) Python library:
```pycon
>>> httpx.get("http://[2a09:8280:1::1:2741]", headers={"host": "www.pillarpointstewards.com"}).text
'<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>Pillar Point Tidepool Stewards</title>\n<meta
```
