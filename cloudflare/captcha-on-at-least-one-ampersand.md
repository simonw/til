# Cloudflare CAPTCHA on at least one ampersand

I use Cloudflare's CAPTCHA (they call it a "Managed Challenge") on [simonwillison.net/search/](https://simonwillison.net/search/) to prevent crawlers from following every single possible combination of my [faceted search](https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/) UI.

This was getting pretty annoying, since I had to wait for the challenge every time I searched my own site.

I don't particularly care about regular `?q=term` searches. Where things get messy is if a crawler starts hitting every combination of:

- `?q=term&type=entry`
- `?q=term&type=entry&year=2006`
- `?q=term&type=entry&year=2006&tag=browsers`

etc.

I decided to switch the Cloudflare rules around to activating only on hits to `/search/` that included at least one `&` in the query string section.

Here's what that rule expression looks like:

`(http.request.uri.path wildcard r"/search/*" and http.request.uri.query contains "&")`

## Trying the Cloudflare MCP

I originally tried to figure this out using Claude Code and [Cloudflare's MCP server](https://github.com/cloudflare/mcp). I got that working by creating a dedicated folder:
```bash
mkdir cloudflare-dev
cd cloudflare-dev
```
And then setting up the MCP so it would only be active for Claude Code sessions started in that folder:
```bash
echo '{
  "mcpServers": {
    "cloudflare-api": {
      "type": "http",
      "url": "https://mcp.cloudflare.com/mcp"
    }
  }
}' > .mcp.json
mkdir .claude
echo '{
  "enabledMcpjsonServers": [
    "cloudflare-api"
  ]
}' > .claude/settings.local.json
```
(I actually set it up by pasting the MCP JSON into Claude Code and saying "set this up to only work in this project folder", but the above is effectively what it did.)

Then I ran `claude` in the folder and used the `/mcp` command, selected the Cloudflare MCP and used the authenticate option to jump through an OAuth flow.

... which didn't work, because as far as I can tell Cloudflare's MCP doesn't yet implement tools to view and modify the rules in question.

Claude did suggest using the API instead, but I'd need an API token.

## Using the API instead

I created an API token using [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens).

Cloudflare have a template for "Read all resources", and it turns out you can use that as a starting point.

I flipped the "Zone WAF" one to "Edit" and set the key to expire tomorrow. Then I copied the resulting key into a `token.txt` file.

(In the Cloudflare dashboard I believe this feature is called "Web Application Firewall > Custom rules".)

Then I let Claude Code handle the rest. Here's a rough version of what it did, assuming a token in a `$TOKEN` environment variable:

```bash
export TOKEN="$(cat token.txt)"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=simonwillison.net" \
  | jq '{success, errors, zones: [.result[] | {id, name}]}'
```

This got back the zone ID, which is `2ce4f4f41f239d041e25f8320ad3c3fd`.

Then to list the custom WAF rules:

```bash
export ZONE="2ce4f4f41f239d041e25f8320ad3c3fd"
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/rulesets/phases/http_request_firewall_custom/entrypoint" \
  | jq '{success, errors, rules: [.result.rules[]? | {description, action, expression, enabled}]}'
```
This started with:
```json
{
  "success": true,
  "errors": [],
  "rules": [
    {
      "description": "/search/ extra protection",
      "action": "managed_challenge",
      "expression": "(http.request.uri.path wildcard r\"/search/*\")",
      "enabled": true
    },
```
To edit that rule via API we need the ruleset ID and the rule ID:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/rulesets/phases/http_request_firewall_custom/entrypoint" \
  | jq '{ruleset_id: .result.id, rule: (.result.rules[] | select(.description=="/search/ extra protection") | {id, description, action, expression, enabled})}'
```
Returning:
```json
{
  "ruleset_id": "0682fdbd40cc444cbe1e93d136e2b174",
  "rule": {
    "id": "8b2766d7802e4e988163531670976cb9",
    "description": "/search/ extra protection",
    "action": "managed_challenge",
    "expression": "(http.request.uri.path wildcard r\"/search/*\"",
    "enabled": true
  }
}
```
And finally we can update that with the new expression:
```bash
export RS=0682fdbd40cc444cbe1e93d136e2b174
export RULE=8b2766d7802e4e988163531670976cb9

curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/rulesets/$RS/rules/$RULE" \
  --data '{
    "action": "managed_challenge",
    "expression": "(http.request.uri.path wildcard r\"/search/*\" and http.request.uri.query contains \"&\")",
    "description": "/search/ extra protection",
    "enabled": true
  }'
```
