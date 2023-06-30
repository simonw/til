# A Discord bot to expand issue links to a private GitHub repository

I have a private Discord channel and a private GitHub repository.

Every time I paste a URL to an issue in the private GitHub repository I want it to be expanded in the channel.

I ended up solving this by running a custom Discord bot on [Glitch](https://glitch.com/).

## Why Glitch?

I chose Glitch because I needed convenient hosting where the bot process would be running all the time. Discord bots need to stay connected to Discord via a WebSocket, so hosting that scales-to-zero won't work.

I already have a paid Glitch account that lets me "boost" up to five apps - where boosting keeps the apps running all the time. So I decided to use that.

## A Discord bot token

My bot needs a token for talking to Discord and one for talking to GitHub.

I created the Discord one by following the README in this [discord-bot-example](https://glitch.com/~discord-bot-example) by Dan Reeves on Glitch.

I created a new Discord app at https://discordapp.com/developers/applications/me

The token I needed was on the "Bot" page:

<img width="1029" alt="image" src="https://github.com/simonw/til/assets/9599/5afc5378-539a-451a-9c1e-5c62acbaa245">

I clicked "Reset token" and copied out the token, to use later.

I also needed to turn on "message content intent" for my bot, further down that page:

<img width="990" alt="image" src="https://github.com/simonw/til/assets/9599/b21ecf5e-9a92-4061-9f95-ca484f382702">

I needed the "application ID" from the "General Information" page of the bot application. I used that to construct this URL:

    https://discordapp.com/oauth2/authorize?&client_id=<APPLICATION_ID>&scope=bot&permissions=0

Then I visited that page and used it to add the bot to my Datasette Discord server.

## Adding the bot to a channel

I'm still not entirely sure the right way to do this. Clicking "Create invite" in the channel menu doesn't seem to allow a bot to be invited. The only thing that definitely works is scrolling to the very top of a channel and clicking the "Add members or roles" button:

<img width="626" alt="image" src="https://github.com/simonw/til/assets/9599/30c7c39f-96f0-437c-b36d-a0833b9a7a20">

That provided a menu that allowed me to invite my bot.

## A GitHub personal access token

I needed a GitHub API token that could access the issues API for my private repository.

First I tried using the new ability in GitHub to create scoped access tokens that could only access one repo. This seemed to work... but I later found out that my regular GitHub account is highly rate-limited and so that token wasn't able to make very many requests.

Instead, I created a brand new GitHub user account called `datasette-github-bot`. I invited this to my private repository, then created a personal access token for it with permission to read repository data.

## Running the bot on Glitch

I started by remixing the [discord-bot-example](https://glitch.com/~discord-bot-example) project. I added my two API keys to the `.env` panel there:

![CleanShot 2023-06-29 at 22 11 40@2x](https://github.com/simonw/til/assets/9599/37bd2657-74db-47d6-814a-f17e39a2d3a1)

I decided to use `node-fetch` to access the GitHub API. It turns out I needed to use version 2 of that on Glitch, since version 3 uses ES Modules which I don't think are supported yet (or maybe I'm on an older Node version on Glitch?)

I put this in my `package.json` on Glitch:

```json
{
  "name": "discord-1337-bot",
  "version": "0.0.1",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "eris": "^0.16.1",
    "node-fetch": "2.6.7"
  },
  "engines": {
    "node": "16"
  }
}
```
Then I iterated my way towards this code in `server.js`, with a bit of help from ChatGPT 4:

```javascript
const Eris = require("eris");
const fetch = require('node-fetch');

function extractIssueId(input) {
  const match = input.match(
    /https:\/\/github\.com\/simonw\/my-private-repo\/issues\/(\d+)/
  );
  return match ? match[1] : null;
}

async function fetchIssue(id) {
  const response = await fetch(
    "https://api.github.com/repos/simonw/my-private-repo/issues/" + id,
    {
      headers: {
        Authorization: "token " + process.env.GITHUB_PAT_TOKEN,
      },
    }
  );

  if (!response.ok) {
    let text = await response.text();
    return { error: `HTTP error! status: ${response.status} ${text}` };
  }
  return await response.json();
}

const bot = new Eris(process.env.DISCORD_BOT_TOKEN);

bot.on("ready", () => {
  console.log("Ready!");
  console.log(bot.user.id);
});

bot.on("messageCreate", async (msg) => {
  console.log(msg.channel.name, msg.author.username, msg.content);
  if (msg.channel.name == "my-private-channel" && msg.author.id != bot.user.id) {
    let id = extractIssueId(msg.content);
    console.log('issue ID', id);
    if (id) {
      const issue = await fetchIssue(id);
      console.log(issue);
      if (!issue.error) {
        bot.createMessage(msg.channel.id, `${issue.number}: ${issue.title} - ${issue.html_url}`);
      }
    }
  }
});

bot.connect();
```
The great thing about Glitch is the server automatically restarted every time I edited the file in my browser.

And... this works!

Now every time I paste a URL to https://github.com/simonw/my-private-repo/issues/361 into the `#my-private-channel` channel, the bot responds with the title and URL for that issue:

> 361: Discord bot to expand issue links - https://github.com/simonw/my-private-repo/issues/361

And since this whole system is extremely easy to hack on, adding additional features should be very straight-forward.

## Avoiding an infinite loop

I did have one nasty bug while I was putting this together. The fix was this:
```javascript
if (msg.channel.name == "my-private-channel" && msg.author.id != bot.user.id) {
```
That `&& msg.author.id != bot.user.id` bit is crucial. Before I added that, any time I pasted a URL into the channel the bot would reply... and then it would see its own message and reply over and over again in an infinite loop!

Thankfully since I was running on Glitch I saw what happened and quickly commented out the `bot.createMessage()` line to stop the loop.

