# Configuring auto-update for an Electron app

This is _almost_ really simple. I used https://github.com/electron/update-electron-app for it, the instructions for which are:

- Add it to `packages.json` with `npm i update-electron-app`
- Make sure your `"repository"` field in that file points to your GitHub repository
- Use GitHub releases to release signed versions of your application
- Add `require('update-electron-app')()` somewhere in your `main.js`

I added this... and it didn't work ([#106](https://github.com/simonw/datasette-app/issues/106)).

Then I spotted [this recipe](https://github.com/electron/update.electronjs.org#manual-setup) in the manual setup instructions for the `update.electronjs.org` server that it uses:

```javascript
const server = 'https://update.electronjs.org'
const feed = `${server}/OWNER/REPO/${process.platform}-${process.arch}/${app.getVersion()}`
```
I ran that in the Electron debugger, swapping in `simonw/datasette-app` as the `OWNER/REPO` and got this URL:

`https://update.electronjs.org/simonw/datasette-app/darwin-x64/0.2.0`

Which returned this:

> `No updates found (needs asset matching *{mac,darwin,osx}*.zip in public repository)`

It turns out your asset filename needs to match that pattern!

I renamed the asset I was attaching to the release to `Datasette-mac.app.zip` and the auto-update mechanism started working instantly.

## How it works

That update URL is interesting. If you hit it with the most recent version of the software (`0.2.1` at time of writing) you get this:

```
~ % curl -i 'https://update.electronjs.org/simonw/datasette-app/darwin-x64/0.2.1'
HTTP/1.1 204 No Content
Server: Cowboy
Content-Length: 0
Connection: keep-alive
Date: Tue, 14 Sep 2021 03:54:47 GMT
Via: 1.1 vegur
```
But if you tell it you are running a previous version you get this instead:

```
~ % curl -i 'https://update.electronjs.org/simonw/datasette-app/darwin-x64/0.2.0'
HTTP/1.1 200 OK
Server: Cowboy
Connection: keep-alive
Content-Type: application/json
Date: Tue, 14 Sep 2021 03:55:19 GMT
Content-Length: 740
Via: 1.1 vegur

{"name":"0.2.1","notes":"- Fixed bug where application would not start without a working internet connection. [#115](https://github.com/simonw/datasette-app/issues/115)\r\n- The \"Debug -> Open Chromium DevTools\" menu item no longer shows an error if no windows are focused. [#113](https://github.com/simonw/datasette-app/issues/113)\r\n- Fixed bug where the `datasette-leaflet` plugin could be uninstalled despite being automatically re-installed. [#118](https://github.com/simonw/datasette-app/issues/118)\r\n- Time limit for facet calculations increased from 1 second to 3 seconds. [#114](https://github.com/simonw/datasette-app/issues/114)","url":"https://github.com/simonw/datasette-app/releases/download/0.2.1/Datasette-mac.app.zip"}
```
Which pretty-prints to:

```json
{
  "name": "0.2.1",
  "notes": "- Fixed bug where application would not start without a working internet connection. [#115](https://github.com/simonw/datasette-app/issues/115)\r\n- The \"Debug -> Open Chromium DevTools\" menu item no longer shows an error if no windows are focused. [#113](https://github.com/simonw/datasette-app/issues/113)\r\n- Fixed bug where the `datasette-leaflet` plugin could be uninstalled despite being automatically re-installed. [#118](https://github.com/simonw/datasette-app/issues/118)\r\n- Time limit for facet calculations increased from 1 second to 3 seconds. [#114](https://github.com/simonw/datasette-app/issues/114)",
  "url": "https://github.com/simonw/datasette-app/releases/download/0.2.1/Datasette-mac.app.zip"
}
```
