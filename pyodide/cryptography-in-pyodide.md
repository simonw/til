# Cryptography in Pyodide

Today I was evaluating if the Python [cryptography](https://cryptography.io/) package was a sensible depedency for one of my projects.

It's clearly the most responsible package to use for implementing encryption in Python, but I was nervous about adding it as a dependency to a project that could work without using it at all (with some design changes).

My key concern: I want this project to work running in Pyodide in WebAssembly in the future, and was nervous that `cryptography`, being written partially in Rust, wouldn't work in that environment.

It turns out it works just fine!

I tested it in the Pyodide REPL at https://pyodide.org/en/stable/console.html

![Welcome to the Pyodide terminal emulator 🐍 Python 3.11.3 (main, Sep 25 2023 20:45:01) on WebAssembly/Emscripten Type 'help', 'copyright', 'credits' or 'license' for more information. >>> import micropip >>> await micropip.install('cryptography') >>> from cryptography.fernet import Fernet >>> key = Fernet.generate_key() >>> cipher_suite = Fernet(key) >>> encrypted_text = cipher_suite.encrypt(b'Secret message') >>> encrypted_text b'gAAAAABlY7AZ-OuJAEv1J4KufF8vpreyehPeejdPqluXwD0G_mfFg-Zl1AvEza6F2DXb WMEkIcKc4B0Hb0qJ457pje5FhO5Vyw==' >>> decrypted_text = cipher_suite.decrypt(encrypted_text) >>> decrypted_text b'Secret message' - then on the right the DevTools Network panel shows that this worked by loading a 4.27MB file called cryptography-39.0.2-cp311-cp311-emscripten_3_1_45_wasm32.whl from the Pyodide CDN package.
](https://github.com/simonw/til/assets/9599/94440423-af87-4c78-b413-35a31dd0a894)

The following import code worked without errors:
```python
import micropip
await micropip.install("cryptography")
from cryptography.fernet import Fernet
```
Then I tested it like this:
```python
key = Fernet.generate_key()
cipher_suite = Fernet(key)
encrypted_text = cipher_suite.encrypt(b"Secret message")
print(encrypted_text)
# b'gAAAAABlY7AZ-OuJAEv1J4KufF8vpreyehPeejdPqluXwD0G_mfFg-Zl1AvEza6F2DXbWMEkIcKc4B0Hb0qJ457pje5FhO5Vyw=='
decrypted_text = cipher_suite.decrypt(encrypted_text)
print(decrypted_text)
# b'Secret message'
```

From sniffing around in the browser DevTools network panel, it turns out Pyodide provides its own packaged version of the Cryptography package in a file called `cryptography-39.0.2-cp311-cp311-emscripten_3_1_45_wasm32.whl`.

I found the source of this custom package in the Pyodide repository, in the [packages/cryptography](https://github.com/pyodide/pyodide/tree/main/packages/cryptography) folder.

## More packages

That [packages/](https://github.com/pyodide/pyodide/tree/main/packages) folder has a whole bunch of other useful modules that have been custom packaged to work with Pyodide. A few that caught my eye:

- `Jinja2`
- `Pillow`
- `Pygments`
- `biopython`
- `fastparquet`
- `ffmpeg`
- `gdal`
- `geopandas`
- `geos`
- `html5lib`
- `jsonschema`
- `libheif`
- `libwebp`
- `lxml`
- `msgpack`
- `shapely`
- `sqlalchemy`
- `xgboost`
- `sqlite3`

Each of these comes with a `meta.yaml` file that defines how it should be compiled, plus a test Python module to verify it and optionally a set of patches to apply before compilation.

Here's what [packages/sqlite3/meta.yaml](https://github.com/pyodide/pyodide/blob/main/packages/sqlite3/meta.yaml) looks like:

```yaml
package:
  name: sqlite3
  version: 1.0.0 # Nonsense
  tag:
    - always
  top-level:
    - sqlite3
    - _sqlite3
source:
  sha256: $(PYTHON_ARCHIVE_SHA256)
  url: $(PYTHON_ARCHIVE_URL)
build:
  type: cpython_module
  script: |
    export FILES=(
      "Modules/_sqlite/blob.c"
      "Modules/_sqlite/connection.c"
      "Modules/_sqlite/cursor.c"
      "Modules/_sqlite/microprotocols.c"
      "Modules/_sqlite/module.c"
      "Modules/_sqlite/prepare_protocol.c"
      "Modules/_sqlite/row.c"
      "Modules/_sqlite/statement.c"
      "Modules/_sqlite/util.c"
    )

    embuilder build sqlite3 --pic

    for file in "${FILES[@]}"; do
      emcc $STDLIB_MODULE_CFLAGS -c "${file}" -o "${file/.c/.o}"  \
        -sUSE_SQLITE3 -DMODULENAME=sqlite
    done

    OBJECT_FILES=$(find Modules/_sqlite/ -name "*.o")
    emcc $OBJECT_FILES -o $DISTDIR/_sqlite3.so $SIDE_MODULE_LDFLAGS \
       -sUSE_SQLITE3 -lsqlite3

    cd Lib && tar --exclude=test -cf - sqlite3 | tar -C $DISTDIR -xf -
```
One thing I don't understand is why some pure-Python packages such as Click also [get this treatment](https://github.com/pyodide/pyodide/blob/main/packages/click/meta.yaml) - since those should work if installed directly from PyPI using `micropip.install()`.
