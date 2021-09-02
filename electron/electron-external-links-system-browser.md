# Open external links in an Electron app using the system browser

For [Datasette.app](https://github.com/simonw/datasette-app) I wanted to ensure that links to external URLs would [open in the system browser](https://github.com/simonw/datasette-app/issues/34).

This recipe works:

```javascript
function postConfigure(window) {
  window.webContents.on("will-navigate", function (event, reqUrl) {
    let requestedHost = new URL(reqUrl).host;
    let currentHost = new URL(window.webContents.getURL()).host;
    if (requestedHost && requestedHost != currentHost) {
      event.preventDefault();
      shell.openExternal(reqUrl);
    }
  });
}
```
The `will-navigate` event fires before any in-browser navigations, which means they can be intercepted and cancelled if necessary.

I use the `URL()` class to extract the `.host` so I can check if the host being navigated to differs from the host that the application is running against (which is probably `localhost:$port`).

Initially I was using `require('url').URL` for this but that doesn't appear to be necessary - Node.js ships with `URL` as a top-level class these days.

`event.preventDefault()` cancels the navigation and `shell.openExternal(reqUrl)` opens the URL using the system default browsner.

I call this function on any new window I create using `new BrowserWindow` - for example:

```javascript
mainWindow = new BrowserWindow({
  width: 800,
  height: 600,
  show: false,
});
mainWindow.loadFile("loading.html");
mainWindow.once("ready-to-show", () => {
  mainWindow.show();
});
postConfigure(mainWindow);
```

