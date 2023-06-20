# Expanding ChatGPT Code Interpreter with Python packages, Deno and Lua

The ChatGPT Code Interpreter alpha remains incredibly interesting. I wrote about how I was using it [for Python and SQLite benchmarking](https://simonwillison.net/2023/Apr/12/code-interpreter/) a few weeks ago. Today I found a neat pattern for expanding its capabilities with custom binaries.

> **Update:** June 20th 2023 as far as I can tell this trick no longer works - I think they have removed the ability to use `subprocess.call()`.

If you don't yet have access to the alpha, the key thing to know is that it provides ChatGPT with access to a Python interpreter. It doesn't have network access - it can't make outbound HTTP requests, or download packages - but it can do all sorts of interesting things by running code.

## Uploading files

One of the neatest features of Code Interpreter mode is that you can upload files to it.

This opens up a world of possibilities. For example, you can upload CSV files, or Excel files, or even SQLite databases and have it use Python and various baked-in libraries to process them - including rendering charts against data from them using `matplotlib`.

## Installing extra Python packages

Today I found out you can upload Python wheels, too! If there's a package that you want to use you can grab the `.whl` files for it from [PyPI](https://pypi.org/), upload them to ChatGPT and it will install them into its own environment for the duration of that chat session.

If a library has dependencies you have to upload those, too. 
To get my [sqlite-utils](https://sqlite-utils.datasette.io/) library working I had to download and then upload the following files:

- [click_default_group_wheel-1.2.2-py3-none-any.whl](https://files.pythonhosted.org/packages/0b/77/dbf4952b05efe08ab0ef4be14b6137717c00d0504f5a56ee6e80c010e6d0/click_default_group_wheel-1.2.2-py3-none-any.whl)
- [sqlite_fts4-1.0.3-py3-none-any.whl](https://files.pythonhosted.org/packages/51/29/0096e8b1811aaa78cfb296996f621f41120c21c2f5cd448ae1d54979d9fc/sqlite_fts4-1.0.3-py3-none-any.whl)
- [sqlite_utils-3.30-py3-none-any.whl](https://files.pythonhosted.org/packages/0c/d4/4e27f7aeeda5b0ed9da7cacffe81f2e48cd5a4f347c72011390f04267ac4/sqlite_utils-3.30-py3-none-any.whl)

It didn't need `tabulate`, `click` or `python-dateutil` since those were already included in the environment.

## Installing Deno

One of the neat things about the [Deno](https://deno.land/) server-side JavaScript runtime is that it's packaged as a single binary.

Could uploading that binary be enough to grant ChatGPT the ability to run JavaScript?

To my surprise, the answer is yes!

I grabbed this file:

- [deno-x86_64-unknown-linux-gnu.zip](https://github.com/denoland/deno/releases/download/v1.33.1/deno-x86_64-unknown-linux-gnu.zip)

And uploaded it to ChatGPT. Then I told it:

> Extract deno and make the binary executable and check its version

This totally worked! Here's the code it generated and executed:

```python
import zipfile
import os
import subprocess

# Define the file paths
deno_zip_path = '/mnt/data/deno-x86_64-unknown-linux-gnu.zip'
deno_extract_path = '/mnt/data/deno-extracted'

# Extract the Deno ZIP archive
with zipfile.ZipFile(deno_zip_path, 'r') as zip_ref:
    zip_ref.extractall(deno_extract_path)

# Get the path of the Deno binary
deno_binary_path = os.path.join(deno_extract_path, 'deno')

# Make the Deno binary executable
os.chmod(deno_binary_path, 0o755)

# Get the version of the Deno binary
try:
    deno_version_output = subprocess.check_output([deno_binary_path, '--version'], universal_newlines=True)
except Exception as e:
    deno_version_output = str(e)

deno_version_output
```
Which output the following:
```
deno 1.33.1 (release, x86_64-unknown-linux-gnu)
v8 11.4.183.1
typescript 5.0.3
```
Now I can tell it to run JavaScript code using Deno like this:

> Write a hello world Deno program and execute it

It then generates JavaScript, writes it to a file using Python and uses `subprocess.check_output()` to run it using the Deno binary.

## Getting hold of other binaries, such as Lua

Now that I knew I could upload and run binaries, what other programming languages could I play with?

I asked ChatGPT for ideas of programming languages that came bundled as a single binary, and one of its suggestions was Lua.

So now I need a single binary file version of Lua, compiled for the same architecture as the ChatGPT server.

It took some fiddling around, but through asking it questions and watching it run more code I identified that the sandbox ChatGPT had access to ran Ubuntu 20.04.5 LTS, with GLIBC 2.31. The architecture is `x86_64`.

I have a M2 MacBook Pro. I need a way to get hold of Ubuntu x86_64 binaries.

With more help from ChatGPT, I figured out this recipe:

```
docker run -it --platform linux/amd64 \
  -v "$(pwd):/mnt" ubuntu:20.04 bash
```
This uses Docker Desktop on my Mac to start a `bash` session inside a new Ubuntu 20.04 container, emulating amd64 architecture.

It also mounts the current directory to `/mnt` within the container.

Then inside the container I can run this:

```
apt-get update && apt-get install -y lua5.3
cp $(which lua) /mnt
```
The first command installs Lua. The second one copies that `lua` binary to the `/mnt` directory, making it available on my Mac.

I now have a Lua binary that will work in ChatGPT! I can upload that file to it, then tell it:

> Make that executable and run lua -v

And then:

> Write a Python function that takes a string of Lua code, writes it to a temporary file and then uses that lua executable to run it
>
> Then use that function to run a hello world program

Finally, I tried this:

> Use Lua to draw a mandelbrot fractal in ascii art

Here's the code it wrote:

```python
# Define the Lua code to generate a Mandelbrot fractal in ASCII art
lua_mandelbrot_code = """
function mandelbrot(c)
    local z = {re = 0, im = 0}
    for i = 1, 1000 do
        local a = z.re * z.re - z.im * z.im + c.re
        z.im = 2 * z.re * z.im + c.im
        z.re = a
        if z.re * z.re + z.im * z.im > 4 then
            return false
        end
    end
    return true
end

function draw_ascii_mandelbrot()
    local width = 80
    local height = 24
    local scale_x = 3.5 / width
    local scale_y = 2.0 / height
    for y = 1, height do
        for x = 1, width do
            local c = {re = (x - 1) * scale_x - 2.0, im = (y - 1) * scale_y - 1.0}
            if mandelbrot(c) then
                io.write('*')
            else
                io.write(' ')
            end
        end
        io.write('\\n')
    end
end

draw_ascii_mandelbrot()
"""

# Use the function to run the Lua code for drawing the Mandelbrot fractal in ASCII art
mandelbrot_ascii_art = run_lua_code(lua_mandelbrot_code, lua_file_path)

mandelbrot_ascii_art
```
And the (not particularly pretty) result:

```
            **
          ******
         ********
       ************
       ************
       ************
       ************
        **********
        **********
          ******
           ****
            **
```
## This is pretty wild

Honestly, Code Interpreter is by far the most exciting feature I've played with in ChatGPT. I actually think it's more interesting than both ChatGPT Plugins and ChatGPT Browsing - the opportunities it opens up are pretty astonishing.

[Ethan Mollick](https://twitter.com/emollick) has been doing some really interesting explorations with it. [This Twitter search](https://twitter.com/search?q=(from%3Aemollick)%20until%3A2023-05-01&src=typed_query&f=live) should hopefully return some of his recent experiments.
