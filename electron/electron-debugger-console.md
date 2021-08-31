# Using the Chrome DevTools console as a REPL for an Electron app

I figured out how to use the Chrome DevTools to execute JavaScript interactively inside the Electron main process. I always like having a REPL for exploring APIs, and this means I can explore the Electron and Node.js APIs interactively.

<img width="945" alt="Simon_Willison’s_Weblog_and_DevTools_-_Node_js_and_Inspect_with_Chrome_Developer_Tools" src="https://user-images.githubusercontent.com/9599/131575749-a509c528-6746-42b0-8efd-03cd77f6dc2d.png">

https://www.electronjs.org/docs/tutorial/debugging-main-process#--inspectport says you need to run:

    electron --inspect=5858 your/app

I start Electron by running `npm start`, so I modified my `package.json` to include this:

```json
  "scripts": {
    "start": "electron --inspect=5858 ."
```
Then I ran `npm start`.

To connect the debugger, open Google Chrome and visit `chrome://inspect/` - then click the "Open dedicated DevTools for Node" link.

In that window, select the "Connection" tab and add a connection to `localhost:5858`:

<img width="901" alt="8_31_21__2_08_PM" src="https://user-images.githubusercontent.com/9599/131576143-03b28fd7-fab4-495a-8060-662b0247eabd.png">

Switch back to the "Console" tab and you can start interacting with the Electron environment.

I tried this and it worked:

```javascript
const { app, Menu, BrowserWindow, dialog } = require("electron");
new BrowserWindow({height: 100, width: 100}).loadURL("https://simonwillison.net/");
```
