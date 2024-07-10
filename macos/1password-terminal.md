# Accessing 1Password items from the terminal

I save things like API keys in [1Password](https://1password.com/). Today I figured out how to access those from macOS terminal scripts.

My initial goal was to make a [Fly.io](https://fly.io/) API key available in an environment variable, without copying and pasting it.

Claude pointed me to the `op` 1Password terminal app. Here are the [official installation instructions](https://developer.1password.com/docs/cli/get-started/), which boil down to:

```bash
brew install 1password-cli
```
Then open 1Password and find the Developer tab in settings and enable the 1Password CLI option:

![1Password developer settings have a clear CLI enabling checkbox](https://github.com/simonw/til/assets/9599/5d96abaf-e148-4090-ab33-2d9c365eeaf3)

Having done this, the `op` command is ready to use. To see a list of vaults:

```bash
op vault list
```
This asked me for my Touch ID before running:

![1Password access requested - a Touch ID prompt](https://github.com/simonw/til/assets/9599/b51b2450-ea97-409d-9b76-46d7809cc6fe)

I only have one vault, so I got back this:
```
ID                            NAME
db6xmelzrupwlyrfbiy5ltrnfy    Personal
```
There are a few ways to access items. One is to find the item ID using `op items list` and `grep`:

```bash
op items list | grep 'Datasette Cloud Dev'
```
This displayed:
```
uv4maokwxaaymkmoxawwcyfeve    Datasette Cloud Dev Simon     Personal     4 minutes ago
```
You can then access the item using `op item get` and that ID:

```bash
op item get uv4maokwxaaymkmoxawwcyfeve
```
This output what looked like YAML:
```yaml
ID:          uv4maokwxaaymkmoxawwcyfeve
Title:       Datasette Cloud Dev Simon
Vault:       Personal (db6xmelzrupwlyrfbiy5ltrnfy)
Created:     27 minutes ago
Updated:     5 minutes ago by Simon Willison
Favorite:    false
Version:     2
Category:    LOGIN
Fields:
  username:    fly token
  password:    FlyV1 fm2_...
```
You can also use the direct title of the item, like this:
```bash
op item get 'Datasette Cloud Dev Simon'
```
We just want the password, to write into an environment variable. Using `--fields password` nearly gets us that:
```bash
op item get 'Datasette Cloud Dev Simon' --fields password
```
Output:
```
"FlyV1 fm2_..."
```
This is wrapped in double quotes. The easiest way I found to strip those was to pipe it through `jq -r` - where the `-r` tells `jq` to output the raw value:
```bash
op item get 'Datasette Cloud Dev Simon' --fields password | jq -r
```
Output:
```
FlyV1 fm2_...
```
Then I assigned it to an environment variable like this:

```bash
export FLY_API_KEY=$(op item get 'Datasette Cloud Dev Simon' --field password | jq -r)
```
And used that key in an API call like this:
```bash
curl 'https://api.machines.dev/v1/apps?org_slug=datasette-cloud-dev' \ 
  -H "Authorization: $FLY_API_KEY"
```
Which output:
```json
{"total_apps":0,"apps":[]}
```
