# Verifying your GitHub profile on Mastodon

Mastodon has a really neat way of implementing verification, using the [rel=me microformat](https://microformats.org/wiki/rel-me).

You can edit your Mastodon profile and add up to four links to it. Mine [looks like this](https://fedi.simonwillison.net/@simon) at the moment:

<img width="565" alt="My Mastodon profile has four links: BLOG: simonwillison.net, GitHub: simonw.github.io, Twitter: twitter.com/simonw and TIL: til.simonwilliso.net. All but the Twitter one show a green checkmark and a green background, to indicate they are verified." src="https://user-images.githubusercontent.com/9599/202297154-a2b00a62-beaa-44a5-9114-5fed2fb9b6fc.png">

The verification checkmark can be had by embedding a link BACK to your Mastodon profile on another site.

My https://simonwillison.net/ and https://til.simonwillison.net/ page headers include the following HTML:

    <link href="https://fedi.simonwillison.net/@simon" rel="me">

Getting a verified link to GitHub is a tiny bit trickier. GitHub _does_ support `rel=me` - but only on two of the links in your profile:

<img width="335" alt="The edit profile form on GitHub, with a number of different form fields" src="https://user-images.githubusercontent.com/9599/202298033-fd78a7c0-1c83-4b37-b708-ef65038c1443.png">

The only two fields here that will have `rel=me` applied to them when GitHub serves the final page are the link field (which I have set to my personal blog at https://simonwillison.net/ and, weirdly, the location field (which I have set to Half Moon Bay, CA).

So the easiest way to verify your GitHub profile is to point one of those to your Mastodon page, which in my case is https://fedi.simonwillison.net/@simon

But... I didn't want to sacrifice either of those fields!

The first thing I tried was editing my profile to point to Mastodon, then editing my Mastodon profile to trigger a verification job, then editing my GitHub profile back again.

This looked like it worked, at least for my own personal Mastodon server. But it turns out other people visiting my profile wouldn't see the verified checkmark, because each Mastodon server runs its own verification checks - and their server was checking after I had reverted the change I had made.

Angus Hollands [suggested a neat fix](https://twitter.com/agoose77/status/1592875047152410624): use a GitHub Pages domain instead.

GitHub reserves `https://your-username.github.io/` as a URL that you can create your own static GitHub Pages site on.

The way you do this is to create a repository called `github.com/your-username/your-username.github.io` - any HTML you put in that repo will be served from your personal domain.

Angus pointed out that since GitHub restrict who can publish there, proving ownership of `simonw.github.io` is equivalent to proving ownership of `github.com/simonw`.

So I did that instead! I set up https://simonw.github.io/ to be a page that served the `rel=me` link AND redirected to my https://github.com/simonw profile.

Here's [the HTML](https://github.com/simonw/simonw.github.com/blob/main/index.html) I used to make that happen:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Redirecting to github.com/simonw/</title>
    <meta http-equiv="refresh" content="0; URL=https://github.com/simonw">
    <link href="https://github.com/simonw" rel="me">
    <link href="https://simonwillison.net/" rel="me">
    <link href="https://fedi.simonwillison.net/@simon" rel="me">
  </head>
  <body style="margin: 0; padding: 0">
    <a
      href="https://github.com/simonw"
      style="
        display: block;
        height: 100vh;
        width: 100vw;
        margin: 0;
        padding: 0;
        color: white;
      "
    >
      github.com/simonw
    </a>
  </body>
</html>
```
The key pieces here are that `<link href="https://fedi.simonwillison.net/@simon" rel="me">` element to verify my Mastodon profile, and the `<meta http-equiv="refresh" content="0; URL=https://github.com/simonw">` to implement the redirect.

GitHub Pages doesn't allow you to use real server-side redirects, so this `<meta>` tag is the next best thing.

It's completely unneccessary, but I decided to make the page itself a huge clickable link element which would redirect to the right place, using `height: 100vh` and `width: 100vw` to fill the page and setting the text to be white on a white background to keep it invisible for the split second before the redirect happens.
