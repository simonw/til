# Histogram with tooltips in Observable Plot

Given an array of datetime objects, I wanted to plot a histogram. But I wanted to automatically pick a bucket size for that histogram that resulted in something interesting, no matter what range of time the individual points covered.

I figured out that [d3](https://d3js.org/) has a mechanism for this: `d3.bin().thresholds()` ([docs here](https://github.com/d3/d3-array#bin-thresholds)). This defaults to using [Sturges' formula](https://en.wikipedia.org/wiki/Histogram#Sturges'_formula) but has various other options.

This [d3 Histogram](https://observablehq.com/@d3/histogram) notebook helped me figure this out:

![Animation showing what happens when I pass different values to the .thresholds() method](https://user-images.githubusercontent.com/9599/130336516-608f8d37-70e3-4506-8b16-f8ef00f9ec85.gif)

## Implementing this in Observable Plot

The higher level [Observable Plot](https://observablehq.com/@observablehq/plot) library provides binning. Here's the recipe I figured out for generating a histogram with that, in my [Histogram of my tweets over time](https://observablehq.com/@simonw/my-tweets-over-time) notebook:

```javascript
Plot.plot({
  y: {
    grid: true
  },
  marks: [Plot.rectY(tweets, Plot.binX({ y: "count" }, { x: "created_at" }))]
})
```

<img width="669" alt="My histogram of tweets" src="https://user-images.githubusercontent.com/9599/130336556-6f91a1e5-8efe-448d-83f3-a9748cb11aac.png">

It turns out that while d3 uses Sturges' formula Observable Plot instead uses Scott's rule:

> D3 chose Sturges’ formula because it was the popular choice (at the time) but Observable Plot defaults to Scott’s rule, with a max of 200 bins, which tends to perform better. Related: <a href="https://robjhyndman.com/papers/sturges.pdf">https://robjhyndman.com/papers/sturges.pdf</a></p>
> 
> [Mike Bostock](https://twitter.com/mbostock/status/1429281697854464002) - @mbostock

## Adding tooltips

I wanted to add tooltips to the above chart. This was the hardest part to figure out - it turns out that second argument to `.binX()` can take a `title` option, which can be a function that accepts a `bin` array of items and returns a title.

This is what I ended up using:

```javascript
Plot.plot({
  y: {
    grid: true
  },
  marks: [
    Plot.rectY(
      tweets,
      Plot.binX(
        { y: "count" },
        {
          x: "created_at",
          title: bin => {
            let sorted = [...Array.from(bin).map(t => t.created_at)].sort();
            let min = sorted[0];
            let max = sorted.slice(-1)[0];
            let count = sorted.length;
            return `${sorted.length} item${
              sorted.length == 0 ? '' : 's'
            }\nFrom: ${min}\nTo: ${max}`;
          }
        }
      )
    )
  ]
})
```
- `[...bin.map(t => t.created_at)].sort()` is a recipe for creating a sorted copy of an array of values
- `max = sorted.slice(-1)[0]` gets the last item in that array

Then I compose and return the string.

<img width="664" alt="Screnshoot showing the generated tooltip" src="https://user-images.githubusercontent.com/9599/130336609-c2ad97ff-93f3-49b2-a420-edb9ff558ae6.png">

Here's [my Twitter thread](https://twitter.com/simonw/status/1429194217482424324) where I figured this out.
