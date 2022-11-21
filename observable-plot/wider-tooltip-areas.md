# Wider tooltip areas for Observable Plot

In [this Observable notebook](https://observablehq.com/@simonw/mastodon-users-and-statuses-over-time) I'm plotting a line on a chart, but I want to provide tooltips showing the exact value at any point on the line.

Observable Plot (on desktop at least) can do that using the `title` mark property. But... if a line is only 1 pixel wide actually triggering a tooltip requires pin-point accuracy.

I figured out a workaround: render the same line twice - once with a tooltip and a very wide line length set to a low opacity, and then again as a solid thin black line.

Here's what that looks like in JavaScript code for a cell:

```javascript
Plot.plot({
  marks: [
    // This mark exists just for the tooltip - hence why it is wider and almost invisible
    Plot.line(points, {
      x: "date",
      y: "users",
      // Function to generate the text shown on the tooltip:
      title: (d) => d.date.toLocaleString() + " - " + d.users.toLocaleString(),
      strokeWidth: 12,
      opacity: 0.01
    }),
    // This mark displays with the default stroke of a single pixel wide black line
    Plot.line(points, {
      x: "date",
      y: "users"
    })
  ],
})
```
The final effect looks like this:

<img width="657" alt="CleanShot 2022-11-21 at 13 55 17@2x" src="https://user-images.githubusercontent.com/9599/203165945-936b527b-6222-4f72-af56-9f072243ecd5.png">
