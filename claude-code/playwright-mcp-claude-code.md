# Using Playwright MCP with Claude Code

Inspired [by Armin](https://simonwillison.net/2025/Jun/29/agentic-coding/), I decided to figure out how to use the official [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) Playwright MCP server with Claude Code.

Short version: run this before starting `claude`:
```bash
claude mcp add playwright npx '@playwright/mcp@latest'
```
That's it! Now when you run `claude` Playwright will be available. You can say things like:

> `Use playwright mcp to open a browser to example.com`

And a visible Chrome browser window, controlled by Claude Code, will open in front of you.

I found I needed to explicitly say "playwright mcp" the first time, otherwise it might try to use Bash to run Playwright instead.

The `claude mcp add` command will persist but will only affect the directory in which you run it.

It took me a while to figure out how that works - eventually I tracked it down to a JSON file `~/.claude.json` which includes a `"projects"` key with objects for each directory I had used with Claude Code in the past. That object includes MCPs and allowed commands as well.

## Authenticating

Since Claude uses a visible browser window when interacting with Playwright, authentication is easy: have it show you a login page, then login yourself with your own credentials and tell it what to do next. Cookies will persist for the duration of the session.

## Available tools

With the MCP loaded you can run `/mcp` and then navigate to `playwright` to view all available tools. Here's the full list:

1. `browser_close` (read-only)
2. `browser_resize` (read-only)
3. `browser_console_messages` (read-only)
4. `browser_handle_dialog`
5. `browser_file_upload`
6. `browser_install`
7. `browser_press_key`
8. `browser_navigate`
9. `browser_navigate_back` (read-only)
10. `browser_navigate_forward` (read-only)
11. `browser_network_requests` (read-only)
12. `browser_pdf_save` (read-only)
13. `browser_take_screenshot` (read-only)
14. `browser_snapshot` (read-only)
15. `browser_click`
16. `browser_drag`
17. `browser_hover` (read-only)
18. `browser_type`
19. `browser_select_option`
20. `browser_tab_list` (read-only)
21. `browser_tab_new` (read-only)
22. `browser_tab_select` (read-only)
23. `browser_tab_close`
24. `browser_generate_playwright_test` (read-only)
25. `browser_wait_for` (read-only)

You don't have to reference these by name, Claude should usually be smart enough to pick the right one for the task at hand.
