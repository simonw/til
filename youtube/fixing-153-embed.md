# Error 153 Video player configuration error on YouTube embeds

I recently noticed that almost every YouTube video on [my blog](https://simonwillison.net/) was displaying the same mysterious error message:

<img width="1392" height="806" alt="YouTube embed showing a large error message: Watch video on YouTube. Error 153 Video player configuration error" src="https://github.com/user-attachments/assets/a3e2b87e-afe0-4a93-a180-d9521d074917" />

In all cases the HTML looked something like this:

```html
<iframe style="max-width: 100%" width="560" height="315"
  src="https://www.youtube.com/embed/FgxwCaL6UTA"
  frameborder="0" allow="autoplay; encrypted-media" allowfullscreen="allowfullscreen"> </iframe>
```
It turned out the solution may be to replace `www.youtube.com/embed/` with `www.youtube-nocookie.com/embed/`:

```html
<iframe style="max-width: 100%" width="560" height="315"
  src="https://www.youtube-nocookie.com/embed/FgxwCaL6UTA"
  frameborder="0" allow="autoplay; encrypted-media" allowfullscreen="allowfullscreen"> </iframe>
```
This mostly fixed the problem, [as demonstrated by this page](https://simonwillison.net/2023/May/2/prompt-injection-explained/).

(Weirdly on some refreshes of the page I get the same error. I'm not sure why that is.)
