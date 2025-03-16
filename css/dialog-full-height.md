# Styling an HTML dialog modal to take the full height of the viewport

I've been experimenting with the HTML [dialog element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog) recently, for example in my [Prompts.js](https://simonwillison.net/2024/Dec/7/prompts-js/) JavaScript library.

Today I [got Claude](https://claude.ai/share/2f8efd4e-96eb-4364-9e4d-b6f558d2f9ca) to build me an experiment to use it for a side panel that would slide in from the right hand side of the screen, looking like this:

![The background of a page is dulled. A side panel reaches 80% across the page showing item details - but there's an annoying grey gap below it.](https://static.simonwillison.net/static/2025/dialog-gap.jpg)

But what's with that gap at the bottom? I want the side panel to take up the full height of the screen.

The CSS looked good to me:

```css
dialog {
    position: fixed;
    margin: 0;
    padding: 0;
    border: none;
    width: 80%;
    height: 100vh;
    top: 0;
    right: 0;
    left: auto;
    background-color: white;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    transform: translateX(100%);
    transition: transform 0.1s cubic-bezier(0.2, 0, 0.38, 0.9);
}
```
Where was that gap coming from?

Firefox DevTools didn't answer my question, so I tried poking at Claude, then ChatGPT, and by the time I was [screen sharing with Gemini 2.0 Flash](https://aistudio.google.com/live) and arguing out loud with it about the CSS [Natalie](https://bsky.app/profile/natbat.bsky.social) overheard and took pity on me and stepped in to help.

Her suspicion was that this had something to do with the `<dialog>` element. I got Claude 3.7 Sonnet to [rewrite the code to use a div](https://claude.ai/share/973af807-aaf9-49f4-b624-7b31d72ae563) instead of a dialog and the mysterious gap vanished, which was a strong hint that she was right.

I was using Firefox. Natalie pointed out that Chrome DevTools display default browser styles for elements, so we switched to that and...

![Some thing in the Chrome DevTools. An arrow points to a line from the user agent stylesheet which applies max-height: calc(100% - 6px - 2em) to dialog:-internal-dialog-in-top-layer](https://static.simonwillison.net/static/2025/dialog-gap-chrome.jpg)

Chrome was applying these default styles, including one for `max-height`:

```css
dialog:-internal-dialog-in-top-layer {
    position: fixed;
    inset-block-start: 0px;
    inset-block-end: 0px;
    max-width: calc(100% - 2em - 6px);
    max-height: calc(100% - 2em - 6px);
    user-select: text;
    visibility: visible;
    overflow: auto;
}
```
The mysterious gap was entirely explained by that `max-height: calc(100% - 2em - 6px);` rule.

Adding `max-height: none` to my CSS (or `max-height: 100vh`) fixed the bug!

![Same screen as before but this time the sidebar panel stretches from the top to the bottom of the viewport with no gap.](https://static.simonwillison.net/static/2025/dalog-gap-fixed.jpg)

You can [try that out here](https://tools.simonwillison.net/side-panel-dialog).

## Spelunking through the HTML specification

I was curious if this was expected behavior, so I dug around a bit and found it in the [HTML specification here](https://html.spec.whatwg.org/multipage/rendering.html#flow-content-3): 

> ### 15.3.3 Flow content
> ```css
> ...
>
> dialog:modal {
>   position: fixed;
>   overflow: auto;
>   inset-block: 0;
>   max-width: calc(100% - 6px - 2em);
>   max-height: calc(100% - 6px - 2em);
> }
> ```

The spec lives in GitHub in a 7MB source file which is too large to view through the GitHub web interface, so I ran this:

```bash
cd /tmp
git clone git@github.com:whatwg/html
cd html
git blame source | rg 'max-height:' -C 30
```
It took a while to run:
```
Blaming lines:  53% (79074/148234)
```
Which revealed the relevant commit:

```
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136481) dialog:modal {
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136482)   position: fixed;
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136483)   overflow: auto;
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136484)   inset-block: 0;
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136485)   max-width: calc(100% - 6px - 2em);
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136486)   max-height: calc(100% - 6px - 2em);
075834570 (Tim Nguyen 2023-06-06 21:45:41 -0700 136487) }
```

[075834570](https://github.com/whatwg/html/commit/075834570) moved that text but didn't introduce it, so I ran the same thing against the [parent tree](https://github.com/whatwg/html/tree/af3ff8382c74f7dc9a98dcdd49a24d96bfc75f26):

```bash
git checkout af3ff8382c74f7dc9a98dcdd49a24d96bfc75f26
git blame source | rg '100% - 6px' -C 30
```
And found this:
```
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124234)   <ul>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124235)    <li><span>'position'</span> property to 'fixed'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124236)    <li><span>'overflow'</span> property to 'auto'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124237)    <li><span>'inset-block-start'</span> property to '0'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124238)    <li><span>'inset-block-end'</span> property to '0'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124239)    <li><span>'max-width'</span> property to 'calc(100% - 6px - 2em)'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124240)    <li><span>'max-height'</span> property to 'calc(100% - 6px - 2em)'</li>
979af1532 (Ian Kilpatrick 2020-11-03 10:26:48 -0800 124241)   </ul>
```
Here's [979af1532](https://github.com/whatwg/html/commit/979af1532) with the commit message:

> Change modal `<dialog>`s to be positioned via CSS
>
> Fixes [w3c/csswg-drafts#4645](https://github.com/w3c/csswg-drafts/issues/4645). Fixes [#5178](https://github.com/whatwg/html/issues/5178).

That commit landed in November 2020, and those linked issue threads have all sorts of details about how this change came about.

I also found out today that the HTML [Living Standard](https://html.spec.whatwg.org/multipage/) is very much a living standard - the [whatwg/html](https://github.com/whatwg/html/commits/main) repo has had 12,318 commits, the most recent of which was less than 24 hours ago.
## Update: Firefox can show browser styles

Thanks to [uallo on Hacker News](https://news.ycombinator.com/item?id=43378225#43378963) I learned Firefox _can_ show browser styles in the inspector, but the option is turned off by default:

![Screenshot of Firefox DevTools - click the dot-dot-dot menu, then Settings, then in the Inspector section click Show Browser Styles](https://static.simonwillison.net/static/2025/firefox-show-browser-styles.jpg)

I imagine it is off by default because it adds quite a lot of information:

![DevTools now shows a lot of CSS for the dialog and dialog:modal, displayed as coming from user_agent html.css](https://static.simonwillison.net/static/2025/firefox-user-agent-styles.jpg)

And thanks to _that_ I found [html.css](https://searchfox.org/mozilla-central/source/layout/style/res/html.css) in the Firefox source code repository, which lists all of the default styles used in thet browser.

Here's the [full commit history](https://github.com/mozilla/gecko-dev/commits/HEAD/layout/style/res/html.css) for that `html.css` stylesheet on the official GitHub mirror.

## Update 2: Some backstory on those default user styles

Chromium engineer Ian Kilpatrick dropped a [fascinating comment](https://news.ycombinator.com/item?id=43378225#43380129) on Hacker News explaining the backstory for the `max-height` default rule:

> There's quite a bit of history here, but the abbreviated version is that the dialog element was originally added as a replacement for window.alert(), and there were a libraries polyfilling dialog and being surprisingly widely used.
>
> The mechanism which dialog was originally positioned was relatively complex, and slightly hacky (magic values for the insets).
>
> Changing the behaviour basically meant that we had to add "overflow:auto", and some form of "max-height"/"max-width" to ensure that the content within the dialog was actually reachable.
>
> The better solution to this was to add "max-height:stretch", "max-width:stretch". You can see [the discussion for this here](https://github.com/whatwg/html/pull/5936#discussion_r513642207).
>
> The problem is that no browser had (and still has) shipped the "stretch" keyword. (Blink [likely will "soon"](https://groups.google.com/a/chromium.org/g/blink-dev/c/SiZ2nDt3B9E/m/kP_rKOaDAgAJ?pli=1))
>
> However this was pushed back against as this had to go in a specification - and nobody implemented it ("-webit-fill-available" would have been an acceptable substitute in Blink but other browsers didn't have this working the same yet).
>
> Hence the calc() variant. (Primarily because of "box-sizing:content-box" being the default, and pre-existing border/padding styles on dialog that we didn't want to touch). [...]
