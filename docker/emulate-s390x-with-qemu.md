# Emulating a big-endian s390x with QEMU

I got [a bug report](https://github.com/simonw/sqlite-fts4/issues/6) concerning my [sqlite-fts4](https://github.com/simonw/sqlite-fts4) project running on PPC64 and s390x architectures.

The s390x is an [IBM mainframe architecture](https://en.wikipedia.org/wiki/Linux_on_IBM_Z), which I found glamorous!

The bug related to those machines being big-endian v.s. my software being tested on little-endian machines. My first attempt at fixing it (see [this TIL](https://til.simonwillison.net/python/struct-endianness)) turned out not to be correct. I really needed a way to test agaist an emulated s390x machine with big-endian byte order.

I figured out how to do that using Docker for Mac and QEMU.

## multiarch/qemu-user-static:register

This is the first command to run. It does something magical to your Docker installation:

    docker run --rm --privileged multiarch/qemu-user-static:register --reset

The [qemu-user-static README](https://github.com/multiarch/qemu-user-static/blob/master/README.md) says:

> `multiarch/qemu-user-static` and `multiarch/qemu-user-static:register` images execute the register script that registers below kind of `/proc/sys/fs/binfmt_misc/qemu-$arch` files for all supported processors except the current one in it when running the container.

It continues:

> The `--reset` option is implemented at the register script that executes find `/proc/sys/fs/binfmt_misc -type f -name 'qemu-*' -exec sh -c 'echo -1 > {}' \;` to remove `binfmt_misc` entry files before register the entry.

I don't understand what this means. But running this command was essential for the next command to work.

## multiarch/ubuntu-core:s390x-focal

Having run that command, the following command drops you into a shell in an emulated s390x machine running Ubuntu Focal:

    docker run -it multiarch/ubuntu-core:s390x-focal /bin/bash

Using `-focal` gives you Python 3.8. I previously tried `s390x-bionic` but that gave me Python 3.6.

You don't actually get Python until you install it, like so:

    apt-get -y update && apt-get -y install python3

This will take a while. I think it's slower because the hardware is being emulated.

Now you can check the Python version and confirm that the byte order is big-endian like this:

```
root@ea63e288ce49:/# python3 --version
Python 3.8.10
root@ea63e288ce49:/# python3 -c 'import sys; print(sys.byteorder)'
big
```

## Doing this in GitHub Actions

I figured out the [following recipe](https://github.com/simonw/playing-with-actions-2/blob/4408f8136b8b37160685e8961742eb11589b3f66/.github/workflows/qemu.yml) for running this in GitHub Actions.

In this example I'm cloning my `sqlite-fts4` repo and running the tests in it as well:

```yaml
name: QEMU to run s390x-focal

on:
  push:
  workflow_dispatch:

jobs:
  one:
    runs-on: ubuntu-latest
    steps:
    - name: Setup multiarch/qemu-user-static
      run: |
        docker run --rm --privileged multiarch/qemu-user-static:register --reset
    - name: ubuntu-core:s390x-focal
      uses: docker://multiarch/ubuntu-core:s390x-focal
      with:
        args: >
          bash -c
          "uname -a &&
          lscpu | grep Endian &&
          apt-get -y update &&
          apt-get -y install python3 git python3.8-venv &&
          python3 --version &&
          python3 -c 'import sys; print(sys.byteorder)' &&
          git clone https://github.com/simonw/sqlite-fts4 &&
          cd sqlite-fts4 &&
          python3 -m venv venv &&
          source venv/bin/activate &&
          pip install -e '.[test]' &&
          pytest
          "
```
