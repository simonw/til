# Running Prettier against Django or Jinja templates

I really like auto-formatting tools like Black. I've been hoping to find one that works with Django and Jinja templates for years.

Today I managed to get excellent JavaScript [Prettier](https://prettier.io/) formatter to run against a Jinja template file using the [prettier-plugin-jinja-template](https://github.com/davidodenwald/prettier-plugin-jinja-template) plugin by David Odenwald.

I had a bit of a fiddle getting it to work because I'm still not fluent in `npm`/`npx`, but the recipe I used was the following.

1. Install `prettier` and `prettier-plugin-jinja-template` in a directory somewhere. This command will create a `package.json` and `package-lock.json` and a a whole `node_modules/` folder - the full install adds up to 8.4M:

    ```bash
    npm i prettier prettier-plugin-jinja-template
    ```

3. In that directory run this command:

    ```bash
    npx prettier --plugin=prettier-plugin-jinja-template \
      --parser=jinja-template \
      --write path/to/your/template.html
    ```

    The `--write` option will rewrite the template in place.

I first tried using `npm i -g prettier prettier-plugin-jinja-template` to install the application once, globally, but I couldn't work out how to get the plugin working that way.

Instead, I've added it to my path another way. I already have a `~/.local/bin/` directory that is on my `$PATH`, so I ran the `npm i` command from above in that folder and then added this script there, in a file called `pretty-templates.sh` (created with the help of [Claude](https://claude.ai/)):

```bash
#!/bin/bash

# Check if at least one argument is provided
if [ $# -eq 0 ]; then
    echo "Error: At least one argument is required."
    exit 1
fi

# Store the current directory
original_dir=$(pwd)

# Change directory to ~/.local/bin/
cd ~/.local/bin/ || exit

# Convert all paths to absolute paths
args=()
for arg in "$@"; do
    args+=("$original_dir/$arg")
done

# Run the prettier command with the absolute paths
npx prettier --plugin=prettier-plugin-jinja-template \
    --parser=jinja-template \
    --write "${args[@]}"
```

Now I can run that command from anywhere on my computer:

```bash
prettier-templates.sh templates/team_backups.html
```

## Alternatives

Jeff Triplett [pointed me](https://mastodon.social/@webology/112646633489421925) to two pure Python alternatives:

- [curlylint](https://curlylint.org) is "experimental HTML templates linting for Jinja, Nunjucks, Django templates, Twig, Liquid" - `pip install curlylint` then `curlylint my/templates`
- [DjHTML](https://github.com/rtts/djhtml) is "a pure-Python Django/Jinja template indenter without dependencies" - `pip install djhtml` then `djhtml template.html`
