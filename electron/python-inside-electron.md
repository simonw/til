# Bundling Python inside an Electron app

For [Datasette Desktop](https://datasette.io/desktop) I chose to bundle a full version of Python 3.9 inside my `Datasette.app` application. I did this in order to support installation of plugins via `pip install` - you can read more about my reasoning in [Datasette Desktop—a macOS desktop application for Datasette](https://simonwillison.net/2021/Sep/8/datasette-desktop/).

I used [python-build-standalone](https://github.com/indygreg/python-build-standalone) for this, which provides a version of Python that is designed for easy of bundling - it's also used by [PyOxidize](https://github.com/indygreg/PyOxidizer). Both projects are created and maintained by Gregory Szorc.

## In development mode

In my Electron app's root folder I ran the following:
```
wget https://github.com/indygreg/python-build-standalone/releases/download/20210724/cpython-3.9.6-x86_64-apple-darwin-install_only-20210724T1424.tar.gz
tar -xzvf cpython-3.9.6-x86_64-apple-darwin-install_only-20210724T1424.tar.gz                                                                          
```
This gave me a `python/` subfolder containing a full standalone Python, ready to run on my Mac.

Running `python/bin/python3.9 --version` confirms that this is working correctly.

## Calling Python from Electron

I used the Node.js `child_process.execFile()` function to execute Python scripts from inside Electron, like this:

```javascript
const cp = require("child_process");
const util = require("util");
const execFile = util.promisify(cp.execFile);

await execFile(path_to_python, ["-m", "random"]);
```
`path_to_python` needs to be the path to that `python3.9` executable. I wrote a `findPython()` function to find that, like so:

```javascript
const fs = require("fs");

function findPython() {
  const possibilities = [
    // In packaged app
    path.join(process.resourcesPath, "python", "bin", "python3.9"),
    // In development
    path.join(__dirname, "python", "bin", "python3.9"),
  ];
  for (const path of possibilities) {
    if (fs.existsSync(path)) {
      return path;
    }
  }
  console.log("Could not find python3, checked", possibilities);
  app.quit();
}
```
The `resourcesPath` bit here works for the packaged and deployed application.

## Packaging the app

I needed that `python` folder to be bundled up as part of the `Datasette.app` application bundle. I achieved that by adding the following to my `"build"` section in `package.json`:

```json
    "extraResources": [
      {
        "from": "python",
        "to": "python",
        "filter": [
          "**/*"
        ]
      }
    ]
```
This causes `electron-builder` to copy the contents of that `python` folder into `Datasette.app/Contents/Resources/python` in the packaged application.

My `findPython()` function earlier knows to look for it there by creating a path to it starting with `process.resourcesPath`.

## Signing and notarizing

I wrote extensive notes on signing and notarizing in [Signing and notarizing an Electron app for distribution using GitHub Actions](https://til.simonwillison.net/electron/sign-notarize-electron-macos), which includes details on how I signed the Python binaries that ended up included in the package due to this pattern.
