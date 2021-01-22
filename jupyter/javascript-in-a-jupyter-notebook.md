# Embedding JavaScript in a Jupyter notebook

I recently found out modern browsers include a JavaScript API for creating public/private keys for cryptography.

I used this as an opportunity to figure out how to run JavaScript in a Jupyter notebook cell, using the [IPython.display.Javascript](https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.Javascript) mechanism.

This mechanism allows you to execute JavaScript that will be used to render a cell. It includes a copy of jQuery and makes a `element` variable available corresponding to the cell your code is running in. It also provides a `IPython.notebook.kernel.execute()` method which can be used to execute Python code from JavaScript.

Here's what I came up with:

```python
from IPython.display import Javascript, display

display(Javascript("""
function generateKey() {
  window.crypto.subtle
    .generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256",
      },
      true,
      ["encrypt", "decrypt"]
    )
    .then((keyPair) => {
      crypto.subtle.exportKey("jwk", keyPair.privateKey).then((v) => {
        element.find("textarea:first").val(JSON.stringify(v, null, 4));
        IPython.notebook.kernel.execute(
          "private_key = " + JSON.stringify(JSON.stringify(v, null, 4))
        );
      });
      crypto.subtle.exportKey("jwk", keyPair.publicKey).then((v) => {
        element.find("textarea:last").val(JSON.stringify(v, null, 4));
        IPython.notebook.kernel.execute(
          "public_key = " + JSON.stringify(JSON.stringify(v, null, 4))
        );
      });
    });
}
element.append(`
<h2>Generate a public/private key in JavaScript</h2>
<p><button>Generate key</button></p>
<h3>Private key</h3>
<textarea style="width: 100%; height: 20em"></textarea>
<h3>Public key</h3>
<textarea style="width: 100%; height: 20em"></textarea>
`);
element.find("button").click(generateKey);
"""))
```

This works! I get a new cell in the document containing the HTML from that backtick string at the end of the JavaScript code. When I click the button it runs my `generateKey` function which generates a new key, displays it in the two textareas and makes that key available to the Jupyter environment as the `public_key` and `private_key` variables. I can then use them in subsequent cells from Python like this:

```python
import json
private = json.loads(private_key)
public = json.loads(public_key)
```
