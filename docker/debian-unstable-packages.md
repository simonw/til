# Installing packages from Debian unstable in a Docker image based on stable

For [Datasette #1249](https://github.com/simonw/datasette/issues/1249) I wanted to build a Docker image from the `python:3.9.2-slim-buster` base image ("buster" is the current stable release of Debian) but include a single package from "sid", the unstable Debian distribution.

I needed to do this because the latest version of SpatiaLite, version 5, was available in `sid` but not in `buster` (which only has 4.3.0a):

https://packages.debian.org/search?keywords=spatialite

<img width="923" alt="Package libsqlite3-mod-spatialite&#13;&#13;stretch (oldstable) (libs): Geospatial extension for SQLite - loadable module&#13;    4.3.0a-5+b1: amd64 arm64 armel armhf i386 mips mips64el mipsel ppc64el s390x&#13;    buster (stable) (libs): Geospatial extension for SQLite - loadable module&#13;    4.3.0a-5+b2: amd64 arm64 armel armhf i386 mips mips64el mipsel ppc64el s390x&#13;    bullseye (testing) (libs): Geospatial extension for SQLite - loadable module&#13;    5.0.1-2: amd64 arm64 armel armhf i386 mips64el mipsel ppc64el s390x&#13;    sid (unstable) (libs): Geospatial extension for SQLite - loadable module&#13;    5.0.1-2: alpha amd64 arm64 armel armhf hppa i386 m68k mips64el mipsel ppc64 ppc64el riscv64 s390x sh4 sparc64 x32&#13;    experimental (libs): Geospatial extension for SQLite - loadable module&#13;    5.0.0~beta0-1~exp2 [debports]: powerpcspe" src="https://user-images.githubusercontent.com/9599/112061886-5cf77b00-8b1c-11eb-8f4c-91dce388dc33.png">

The recipe that ended up working for me was to install `software-properties-common` to get the `apt-get-repository` command, then use that to install a package from `sid`:

```dockerfile
RUN apt-get update && \
    apt-get -y --no-install-recommends install software-properties-common && \
    add-apt-repository "deb http://httpredir.debian.org/debian sid main" && \
    apt-get update && \
    apt-get -t sid install -y --no-install-recommends libsqlite3-mod-spatialite
```

Here's the full Dockerfile I used:

```dockerfile
FROM python:3.9.2-slim-buster as build

# software-properties-common provides add-apt-repository
RUN apt-get update && \
    apt-get -y --no-install-recommends install software-properties-common && \
    add-apt-repository "deb http://httpredir.debian.org/debian sid main" && \
    apt-get update && \
    apt-get -t sid install -y --no-install-recommends libsqlite3-mod-spatialite && \
    apt clean && \
    rm -rf /var/lib/apt && \
    rm -rf /var/lib/dpkg

RUN pip install datasette && \
    find /usr/local/lib -name '__pycache__' | xargs rm -r && \
    rm -rf /root/.cache/pip

EXPOSE 8001
CMD ["datasette"]
```
