# Language-specific indentation settings in VS Code

When I'm working with Python I like four space indents, but for JavaScript or HTML I like two space indents.

Today I figured out how to teach VS Code those defaults.

1. Hit `Shift+Command+P` to bring up the action menu
2. Search for the `Preferences: Configure Language Specific Settings...` item
3. Select the language, e.g. `HTML` or `Python`
4. Add `"editor.tabSize": 2` to the corresponding JSON object
5. Save that file

I ended up with the following in my JSON (plus a bunch of other stuff I've edited out):

```json
{
    "[html]": {
        "editor.tabSize": 2,
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[javascript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[typescript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.tabSize": 2
    },
    "[python]": {
        "editor.tabSize": 4,
        "editor.wordBasedSuggestions": false
    }
}
```
This file is stored on my machine at `~/Library/Application Support/Code/User/settings.json`.
