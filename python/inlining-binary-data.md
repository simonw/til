# A simple pattern for inlining binary content in a Python script

For [simonw/til issue #82](https://github.com/simonw/til/issues/82) I needed to embed some binary content directly in a Python script.

I wanted to wrap that content to fit within 80 columns.

Here's the format I ended up using:
```python
binary_data = (
    b"x\x9c\xb5VQo\xdb6\x10~\xf7\xaf\xb8*\xc8d\xaf\xae\x94\xd6\xd9V\xb8\xb6"
    b"\xb0\xa0\r\xb0\x01\xc5\x1e\x96\x02{(\x06\x83\x16i\x93+E\xaa$\xd5\xccu\x0c"
    # ...
)
```
This takes advantage of the fact that Python will automatically join adjacent string or byte literals together if they are separated just by whitespace.

But how best to split the binary string into roughly 80 character chunks?

It turns out the [pprint module](https://docs.python.org/3/library/pprint.html) from the Python standard library can do this for you:

```python
from pprint import pprint

binary_string = open("binary_file", "rb").read()
pprint(binary_string)
```

Here's that as a more convenient shell one-liner that uses content piped into Python:

```bash
cat binary_file | python -c 'from pprint import pprint; import sys; pprint(sys.stdin.buffer.read())'
```
For example, against [this PNG](https://github.com/simonw/datasette/blob/1.0a3/datasette/static/favicon.png):
```bash
cat datasette/static/favicon.png | python -c '
from pprint import pprint
import sys
pprint(sys.stdin.buffer.read())
'
```
The ouput is:
```
(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 '
 b'\x04\x03\x00\x00\x00\x81Tg\xc7\x00\x00\x00\x18PLTE\x00\x00\x00'
 b'\xff\xff\xff\xff\xff\xff\xb7\xb9\xdc\xb1\xb2\xd8\xa9\xaa\xc9\x05'
 b'\x00\x82\x04\x00u\xef\x11B\x8f\x00\x00\x00\x02tRNS\x00\x13\xf2-\x8c\xe6\x00'
 b'\x00\x00eIDATx\xdac\xc0\x04liH \x81\x81\x811\xd9\x18\t\x98\x01\x15\x18\xa3'
 b'\x80\x04,\x02i(\x00(\xa0\xa4\xe4\xa4d\xa4\xa4\x0c\xa2T\x94\x94 \x02 6'
 b')\x02\xe5\xe5\xe9@XV\x0e!\x90TP\xdd\xd0 \xacZ\x8c\x88\x16(/\x83'
 b'\x1b\x9a\x86\xe4Re\x0c-\xa4\x08`\x0fS\x92\xcc`HB\xd6\xa2\x86\x1e\xd9\x89'
 b"\x98\x89\x01\x00b\xe6g\xc5_\xc3\xfa'\x00\x00\x00\x00IEND\xaeB`\x82")
```
## It works for strings too

Sometimes when I include a long string in a test I like to wrap it in a similar way.

```python
from pprint import pprint

s = "This image shows a Brown Pelican perched on some rocky shoreline or jetty. The pelican is backlit, creating a slight glowing effect around its head and body, particularly noticeable around its neck area. The bird has its distinctive long beak and characteristic pelican profile. In the background, you can see what appears to be boats or vessels docked in a marina or harbor, slightly out of focus. The pelican's feathers appear to be a grayish-brown color, and you can see its typical robust body structure. The lighting in the photo creates a nice contrast between the bird and its surroundings, highlighting the pelican's silhouette against the marine background."
pprint(s)
```
Outputs:
```python
('This image shows a Brown Pelican perched on some rocky shoreline or jetty. '
 'The pelican is backlit, creating a slight glowing effect around its head and '
 'body, particularly noticeable around its neck area. The bird has its '
 'distinctive long beak and characteristic pelican profile. In the background, '
 'you can see what appears to be boats or vessels docked in a marina or '
 "harbor, slightly out of focus. The pelican's feathers appear to be a "
 'grayish-brown color, and you can see its typical robust body structure. The '
 'lighting in the photo creates a nice contrast between the bird and its '
 "surroundings, highlighting the pelican's silhouette against the marine "
 'background.')
```
