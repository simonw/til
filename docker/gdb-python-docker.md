# Running gdb against a Python process in a running Docker container

While investigating [Datasette issue #1268](https://github.com/simonw/datasette/issues/1268) I found myself with a Python process that was hanging, and I decided to try running `gdb` against it based on tips in [Debugging of CPython processes with gdb](https://www.podoliaka.org/2016/04/10/debugging-cpython-gdb/)

Here's the recipe that worked:

1. Find the Docker container ID using `docker ps` - in my case it was `16197781a7b5`
2. Attach a new bash shell to that process in privileged mode (needed to get `gdb` to work): `docker exec --privileged -it 16197781a7b5 bash`
3. Install `gdb` and the Python tooling for using it: `apt-get install gdb python3-dbg`
4. Use `top` to find the pid of the running Python process that was hanging. It was `20` for me.
5. Run `gdb /usr/bin/python3 -p 20` to launch `gdb` against that process
6. In the `(gdb)` prompt run `py-bt` to see a backtrace.

I'm sure there's lots more that can be done in `gdb` at this point, but that's how I got to a place where I could interact with the Python process that was running in the Docker container.
