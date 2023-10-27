# A simple two column CSS grid

For my blog entry today [Now add a walrus: Prompt engineering in DALL-E 3](https://simonwillison.net/2023/Oct/26/add-a-walrus/) I wanted to display little grids of 2x2 images along with their captions.

I decided to use CSS grids for this.

I started [with GPT-4](https://chat.openai.com/share/388dad10-1e0f-45a6-ae4d-4aab9db62f3e). My prompt:

> HTML and CSS to display a grid of four images, each with a paragraph caption below the image - use figcaption 
>
> The 2x2 grid should be as wide the page, the columns should be 50%, the images should be full width available to them

It gave me this HTML, which I mostly stuck with:

```html
<div class="grid-container">
    <figure>
        <img src="image1.jpg" alt="Image 1">
        <figcaption>Caption for Image 1</figcaption>
    </figure>
    <figure>
        <img src="image2.jpg" alt="Image 2">
        <figcaption>Caption for Image 2</figcaption>
    </figure>
    <figure>
        <img src="image3.jpg" alt="Image 3">
        <figcaption>Caption for Image 3</figcaption>
    </figure>
    <figure>
        <img src="image4.jpg" alt="Image 4">
        <figcaption>Caption for Image 4</figcaption>
    </figure>
</div>
```
And this CSS:
```css
.grid-container {
    display: grid;
    grid-template-columns: 50% 50%; /* Two columns, each 50% */
    grid-template-rows: auto auto; /* Two rows */
    gap: 10px; /* Adjust the gap between grid items if needed */
    width: 100%; /* Full width of the page */
}
figure {
    margin: 0; /* Remove default margin */
}
img {
    width: 100%; /* Full width of the column */
    height: auto; /* Maintain aspect ratio */
}
figcaption {
    text-align: center; /* Center the caption */
    padding-top: 5px; /* Space between image and caption */
}
```
After some iteration I ended up with the following.

```css
.grid-container {
    display: grid;
    grid-template-columns: 50% 50%;
    gap: 10px;
}
figure {
    margin: 0;
}
figcaption {
    padding-top: 10px
}
img {
    width: 100%;
}
```
It turned out `width: 100%` and `grid-template-rows: auto auto;` were both unnecessary - they represented the default settings. I chose not to style the caption.

The `margin: 0` on `<figure>` was needed because without it browsers default to an ugly ~40px margin.

The key styles here are on that wrapping `<div>`.

`display: grid` switches that element into CSS grid mode. Every direct descendant of that element becomes a grid item.

`grid-template-columns: 50% 50%` sets the grid to have two columns, each 50% of the width of the container.

**Update:** Michael Nolan [points out](https://mastodon.me.uk/@mikenolan/111305738775991125) that a neater way to achieve the same thing is to use `grid-template-columns: 1fr 1fr;` - this has the same effect as `50% 50%` (two equally sized columns) but is a better pattern for when you start moving to other divisions, since `1fr 1fr 1fr` is a much nicer way to specify three columns than `33.33% 33.33% 33.33%`.

`gap: 10px` is a shortcut that sets both the horizontal and vertical gap between the grid items to 10px.

I decided to match the top padding of the `<figcaption>` to the gap between the grid items.

... and that's everything! The result is a grid which lays out the items in the order they appear in the HTML, wrapping to a new row every two items.

Here's that HTML again, this time with some real images and captions:
```html
<div class="grid-container">
    <figure>
        <img loading="lazy" style="width: 100%" src="https://static.simonwillison.net/static/2023/dalle-3/pelican-1-1.png" alt="Pelican 1">
        <figcaption>Photo of a refined pelican wearing a shiny gold monocle, perched on a railing with the Monaco Grand Prix F1 race in the background. The race cars blur past on the circuit, while yachts are anchored in the nearby harbor.</figcaption>
    </figure>
    <figure>
        <img loading="lazy" style="width: 100%" src="https://static.simonwillison.net/static/2023/dalle-3/pelican-1-2.png" alt="Pelican 2">
        <figcaption>Illustration of a sophisticated pelican donning a crystal clear monocle, observing the Monaco F1 race with keen interest. The race track is filled with speeding F1 cars, and the Mediterranean Sea sparkles in the distance with luxurious yachts.</figcaption>
    </figure>
    <figure>
        <img loading="lazy" style="width: 100%" src="https://static.simonwillison.net/static/2023/dalle-3/pelican-1-3.png" alt="Pelican 3">
        <figcaption>Watercolor painting of a posh pelican, its feathers groomed to perfection, equipped with a delicate monocle. It stands tall with the iconic Monaco F1 race happening behind it, cars racing at breakneck speeds and the shimmering sea beyond.</figcaption>
    </figure>
    <figure>
        <img loading="lazy" style="width: 100%" src="https://static.simonwillison.net/static/2023/dalle-3/pelican-1-4.png" alt="Pelican 4">
        <figcaption>Vector image of an elegant pelican with a classy monocle, standing gracefully against the backdrop of the Monaco Grand Prix. The F1 cars create a colorful streak as they race, and lavish yachts float in the nearby waters.</figcaption>
    </figure>
</div>
```
And this is what it looks like rendered:

![A 2x2 grid of images of pelicans, each with a caption](https://github.com/simonw/til/assets/9599/3d1d7179-0f2d-4aa8-bcdf-b267cded3272)

## Grid debugging tools

Firefox, Chrome and Safari all have very similar CSS grid debugging tools. Here's what those look like in Firefox:

![Those pelicans again, this time with the Firefox debug toolbar open. The grid lines are visible along with number labels against the rows and columns.](https://github.com/simonw/til/assets/9599/6b5ca1d9-b207-4967-a805-8242d95c5279)

Each grid on the page can be highlighted as an overlay - in this case I have four grids (one for each cluster of photos) and each of those gets assigned a different color.

The numbers represent the grid lines. My simple layout doesn't use these, but they can be used to specify regions of the grid in more complex layouts.

