# Getting Mastodon running on a custom domain

This TIL is mainly a rehash of these two articles by Jacob and Andrew:

- [Setting up a personal Fediverse ID / Mastodon instance](https://jacobian.org/til/my-mastodon-instance/) - Jacob Kaplan-Moss
- [The Fediverse, And Custom Domains](https://aeracode.org/2022/11/01/fediverse-custom-domains/)

I decided if I was going to get into Mastodon I wanted it on a domain that I controlled.

Here's my [research issue](https://github.com/simonw/simonwillisonblog/issues/290) where I first figured this all out.

## masto.host

Both Andrew and Jacob chose [masto.host](https://masto.host/) as a managed host for their instances. Mastodon is open source and runs on Ruby, PostgreSQL and Redis, but managing those is enough of a hassle that I'd much rather have someone else do it for me.

Since Andrew and Jacob had done the due diligence on this already I just went with the one they are using.

I see this as a pleasantly low-risk vendor, because since I'm pointing my own domain at it I can move elsewhere pretty easily if I need to.

My impressions of it so far have been excellent - especially the speed of their customer support (see later note).

## Pay for an account, then set up a CNAME

I paid for a subscription, then added the following configuration to my Cloudflare DNS:

![CNAME of fedi pointed to vip.masto.host, Proxy states of DNS only](https://user-images.githubusercontent.com/9599/199629095-2704cd43-1046-4bff-8460-f756d2510f97.png)

`masto.host` provided detailed instructions for this, including making sure to turn off the Cloudflare caching proxy.

This started working within less than a minute - and https://fedi.simonwillison.net/ was live.

## Creating an account, promoting it to admin

Once my instance was live I used the default account creation flow to create myself an account.

I then used the https://my.masto.host/hosting interface to find the "Change User Role" option and used that to upgrade my new user account to administrator status.

Having done that I gained access to the https://fedi.simonwillison.net/admin/settings/edit interface, where I blocked anyone else from creating an account and changed the site theme to "Mastodon (Light)" (which I like better).

<img width="1100" alt="Screenshot of the Mastodon site settings panel" src="https://user-images.githubusercontent.com/9599/199629280-4add2ded-752f-4d7c-b9b8-91bda4a81811.png">

Frustratingly these settings require an email address, which is shown publicly on a page on the site. I used iCloud in Mobile Safari on my phone to create a disposable email address to use here.

## Getting a vanity address

I wanted `@simon@simonwillison.net` as my ID, but it started out as `@simon@fedi.simonwillison.net`.

To do this, you need to set up some `/.well-known/...` URLs on your core domain.

I exactly copied [how Andrew did this](https://aeracode.org/2022/11/01/fediverse-custom-domains/). Here's [my commit to my Django blog]().

There's one last step here: as explained in [Mastodon usernames different from the domain used for installation](https://masto.host/mastodon-usernames-different-from-the-domain-used-for-installation/) you need to update the `LOCAL_DOMAIN` and `WEB_DOMAIN` settings. These aren't currently available for `masto.host` customers to change, but you can email their support team about it.

I emailed them and they fixed it for me six minutes later! And now `@simon@simonwillison.net` both works and is displayed on https://fedi.simonwillison.net/@simon

## Finding people to follow

I started by following `@jacob@jacobian.org` and `@andrew@aeracode.org`. Then I looked at who they were following. Then I tweeted about my new account and started following-back people who followed me.
