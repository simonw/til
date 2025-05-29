# Redirecting a domain using Cloudflare Pages

I wanted to redirect https://global-power-plants.datasettes.com/ to https://datasette.io/ - I decided to spin up a Cloudflare Pages site to do the work.

I created a GitHub repo at https://github.com/simonw/cloudflare-redirects which I plan to use for other such sites, and created these files:

`global-power-plants.datasettes.com/index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="0; url=https://datasette.io/global-power-plants">
</head>
<body>
    <p>Redirecting to <a href="https://datasette.io/global-power-plants">datasette.io/global-power-plants</a></p>
</body>
</html>
```
(I'm not sure if this will ever be served though, thanks to the other file:)

`global-power-plants.datasettes.com/_redirects`
```
/global-power-plants* https://datasette.io/global-power-plants*:splat 301
/* https://datasette.io/global-power-plants 301
```
Claude [helped with this](https://claude.ai/share/881d85ae-0e15-43ca-b130-d70ff7c17955).  Cloudflare redirects are executed in order, so the more specific one sending anything that starts with `/global-power-plants` to `https://datasette.io/global-power-plants` comes before the catch-all one for the top level.

## Configuring it on Cloudflare

All that was left was to tell Cloudflare to deploy it from GitHub.

Cloudflare want you to use Workers instead of Pages now, but I ignored them and clicked around until I found the old Pages interface.

Click "Workers & Pages" in the menu, then the blue "Create" button:

![Screenshot of Cloudflare Workers & Pages dashboard showing the main page title "Workers & Pages" with a left navigation menu containing various Cloudflare services and a prominent blue "Create" button in the top right of the main content area.](https://github.com/user-attachments/assets/9ae1271b-d9b4-4781-9e47-0c4c64cc49e6)

Swich to the "Pages" tab:

![Screenshot of Cloudflare "Get started" page with "Back to Compute (Workers) overview" link at top, main heading "Get started" followed by "Get started with Workers. How would you like to begin?", tabs for "Workers" and "Pages" with Pages selected, a blue informational banner about recommending Cloudflare Workers for new projects with links to "Cloudflare Workers" and "compatibility matrix", and two option cards: "Import an existing Git repository" with description "Start by importing an existing Git repository" and blue "Get started" button, and "Use direct upload" with description "Upload your site's assets including HTML, CSS, and JS files directly from your computer" and blue "Get started" button.](https://github.com/user-attachments/assets/8160d0b0-ef2b-4165-8470-0369cc29527c)

Select "Import an existing GitHub repository" and fill out this form:

![Screenshot of Cloudflare "Set up builds and deployments" configuration page showing form fields including Project name "global-power-plants" with deployment URL "global-power-plants.pages.dev", Production branch dropdown set to "main", Build settings section with "Configuring builds" link, Framework preset dropdown set to "None", empty Build command field, Build output directory field with "/" prefix, expandable "Root directory (advanced)" section with Path field containing "global-power-plants.datasettes.com", expandable "Environment variables (advanced)" section, and bottom navigation with "Change repository" link on left and blue "Save and Deploy" button on right.](https://github.com/user-attachments/assets/590f4333-5e35-4b9c-9dde-93901bf610ea)

Because my site is static HTML I just needed to provide a project name and the path to the folder with my `index.html` and `_redirects` files in it.

And that was the configuration! It showed me a reassuring log file, including noting that my redirect rules were valid:

![Screenshot of Cloudflare deployment console showing "Deploying to Cloudflare's global network" with "9s" elapsed time, "Download log" and "Copy log" buttons, timestamped deployment log entries from 19:35:01 to 19:35:13 including repository cloning from "https://github.com/simonw/cloudflare-redirects", build steps, "Parsed 2 valid redirect rules", "Validating asset output directory", file uploading progress showing "Success! Uploaded 1 files (1.50 sec)" and "Upload complete!", with a blue "Cancel deployment" button at bottom right.](https://github.com/user-attachments/assets/2c7935cb-746a-4ee4-aa9f-9f21e37b9302)

Finally I navigated to the "Custom Domains" tab and entered the subdomain and domain I wanted.

![Two-step process with "1 Enter domain" and "2 Configure DNS", "Add a custom domain" section with description "Enter in a registered domain or subdomain you own" and "Custom domains" link, empty Domain input field with placeholder text "e.g. example.com, www.example.com, shop.example.com", and "Cancel" and blue "Continue" buttons at bottom.](https://github.com/user-attachments/assets/1ce3cbb7-d859-41bd-8173-2a7dd8b18dc8)

Because the DNS was managed by Cloudflare they configured the required CNAME for me automatically:

![Step 2 "Configure DNS" with "Enter domain" link, heading "Confirm new DNS record", explanation that Cloudflare will update DNS record to activate "global-power-plants.datasettes.com", existing record table showing CNAME type, "global-power-plants" name, "ghs.googlehosted.com" content, and "Auto" TTL, arrow pointing down to new record table showing CNAME type, "global-power-plants" name, "global-power-plants.pages.dev" content, and "Auto" TTL, note about visitors accessing "https://global-power-plants.datasettes.com" once updated, and blue "Activate domain" button.](https://github.com/user-attachments/assets/7a2fb42a-619c-49db-bbc3-3754bd9a0973)
