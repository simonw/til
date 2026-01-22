# Previewing Claude Code for web branches with GitHub Pages

I'm a big user of [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), Anthropic's poorly named cloud-based version of Claude Code which can be driven via the web or their native mobile and desktop applications.

I mostly use it through the Claude iPhone app.

The biggest downside of this way of working is that, beyond CLI tools or code libraries, it's difficult to preview its work while it is iterating on the code.

I've started using GitHub Pages against private repositories to work around this limitation recently  - at least for HTML projects - and it's working really well.

Here's how I'll spin up a new experimental prototype such that I can preview it on my phone.

1. Create a new private repository at https://github.com/new - include an empty README here to ensure the repo has been initialized.
2. Start a task in Claude Code against that repo - you may need to restart the app to ensure it picks up the newly created repo.
3. Tell Claude Code what to build, using a variation on "self-contained HTML file, vanilla JavaScript, no build step, load any dependencies from a CDN" - this ensures that the code it writes will run directly in a browser without needing to mess with npm

Claude Code will get to work, and after a few minutes will create a branch in your repository. Here's the clever bit:

4. Navigate to the Pages area of your repository settings, make sure "Deploy from a branch" is selected (the default) and then open the branch picker and select the `claude/...` branch that Claude Code just created

Wait about a minute for the deploy to complete and your new preview should become available at this (secret) URL:

    https://your-username.github.io/your-repo/index.html

This will serve the full static contents of your repository so you can also reuse the same private repository for other projects like this in the future, though you'll have to manually select the new branch that Claude creates each time.

Crucially, your Claude Code for web session is still running. You can request changes from Claude - and even drop in screenshots of what it's built so far - and Claude will make changes and then push them to the existing branch, which means they'll be available in your preview shortly afterwards.

I've not found a limit on how long these Claude sessions stay available - it's possible you could keep that session and PR running indefinitely, continually pushing changes to your deployed environment for many weeks to come.

When you land the PR don't forget to update the Pages settings to point back to the main branch.

Unlike Claude's own Artifacts feature there are no  CSP restrictions on what apps deployed to GitHub Pages can do, which means they can interact directly with JSON APIs hosted on other domains.

There are other good options for deploying previews of branches - I've used [Cloudflare Pages](https://pages.cloudflare.com/) for this in the past - but it's nice to be able to get this done using GitHub alone.
