# Search across all loaded resources in Firefox

You can search for a string in any resource loaded by a page (including across HTML, JavaScript and CSS) in the Debugger pane by hitting Command+Shift+F.

<img alt="Screenshot of search interface" src="https://raw.githubusercontent.com/simonw/til/main/firefox/search-across-all-resources.jpg" width="600">

This view doesn't search the body of any JSON assets that were fetched by code, presumably because JSON isn't automatically loaded into memory by the browser.

But ([thanks, @digitarald](https://twitter.com/digitarald/status/1257748744352567296)) the Network pane DOES let you search for content in assets fetched via Ajax/fetch() etc - though you do have to run the search before you trigger the requests that the search should cover. Again, the shortcut is Command+Shift+F.

<img alt="Screenshot of search interface" src="https://raw.githubusercontent.com/simonw/til/main/firefox/search-across-all-resources-2.jpg" width="600">
