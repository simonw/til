# How to get credentials for a new Twitter bot

I wanted to build a Twitter bot that would tweet Covid sewage graphs from [this page](https://covid19.sccgov.org/dashboard-wastewater) every day.

To do that, I needed the following four credentials for a new [@covidsewage](https://twitter.com/covidsewage) Twitter account.

- consumer key (for a new Twitter application)
- consumer secret
- access token key (for my specific Twitter account)
- access token secret

## Applying for a Developer account

I created my new Twitter account, then applied to set that up as a Twitter Developer on https://developer.twitter.com/

When I filled in the form there I said I wanted to create a bot. I think this is one of the things that triggers a manual review flow.

I filled out the application form and submitted it.

I then got an email requesting further details - I replied to that email with pretty much a copy of the data I had entered in the application form early on.

A few days later my application was approved.

## Configuring the app

Since the goal here is to get credentials that can be used to write to the account (in order to Tweet), the application needs to be configured to support that.

It turns out you need to turn on "OAuth 1.0a" in order to generate a read-write token for the account (thanks Igor Brigadir for [the tip](https://twitter.com/IgorBrigadir/status/1515766922742272004)).

The following settings worked for me:

<img width="475" alt="Screenshot showing settings - I set it to read-write permissions with OAuth 1.0 and filled out the website and callback URI fields" src="https://user-images.githubusercontent.com/9599/163735286-d5e64f63-6d70-4a41-9a6f-975e1e918c1c.png">

Since callback URI and website URI were required (even though I'm not going to be using them) I set them to the Twitter profile page, which seemed to work.

## Generating the credentials

Having configured the app, the "Keys and tokens" page for that application gave me the option to generate an access token and secret for the account:

<img width="475" alt="Screenshot indicating the revoke / regenerate token button" src="https://user-images.githubusercontent.com/9599/163735341-44fae6ca-5c16-4798-a15b-53112750b54e.png">

## Building the bot

Having generated the four credentials I needed, I built the rest of the bot using GitHub Actions, see https://github.com/simonw/covidsewage-bot
