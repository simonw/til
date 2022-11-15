# HTML datalist

A [Datasette feature suggestion](https://github.com/simonw/datasette/issues/1890) concerning autocomplete against a list of known values inspired me to learn how to use the HTML `<datalist>` element ([see MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/datalist)).

It's really easy to use! It allows you to attach a list of suggested values to any input text box, and browsers will then suggest those while the user is typing - while also allowing them to type something entirely custom.

Here's a basic example:

```html
<input type="text" list="party" name="political_party">

<datalist id="party">
<option value="Anti-Administration">
<option value="Pro-Administration">
<option value="Republican">
<option value="Federalist">
<option value="Democratic Republican">
<option value="Pro-administration">
<option value="Anti-administration">
<option value="Unknown">
<option value="Adams">
<option value="Jackson">
<option value="Jackson Republican">
<option value="Crawford Republican">
<option value="Whig">
<option value="Jacksonian Republican">
<option value="Jacksonian">
<option value="Anti-Jacksonian">
<option value="Adams Democrat">
<option value="Nullifier">
<option value="Anti Mason">
<option value="Anti Masonic">
<option value="Anti Jacksonian">
<option value="Democrat">
<option value="Anti Jackson">
<option value="Union Democrat">
<option value="Conservative">
<option value="Ind. Democrat">
<option value="Independent">
<option value="Law and Order">
<option value="American">
<option value="Liberty">
<option value="Free Soil">
<option value="Ind. Republican-Democrat">
<option value="Ind. Whig">
<option value="Unionist">
<option value="States Rights">
<option value="Anti-Lecompton Democrat">
<option value="Constitutional Unionist">
<option value="Independent Democrat">
<option value="Unconditional Unionist">
<option value="Conservative Republican">
<option value="Ind. Republican">
<option value="Liberal Republican">
<option value="National Greenbacker">
<option value="Readjuster Democrat">
<option value="Readjuster">
<option value="Union">
<option value="Union Labor">
<option value="Populist">
<option value="Silver Republican">
<option value="Free Silver">
<option value="Silver">
<option value="Democratic and Union Labor">
<option value="Progressive Republican">
<option value="Progressive">
<option value="Prohibitionist">
<option value="Socialist">
<option value="Farmer-Labor">
<option value="American Labor">
<option value="Nonpartisan">
<option value="Coalitionist">
<option value="Popular Democrat">
<option value="Liberal">
<option value="New Progressive">
<option value="Republican-Conservative">
<option value="Democrat-Liberal">
<option value="AL">
<option value="Libertarian">
</datalist>
```
And here's what that looks like in Firefox:

![Animation showing autocomplete against that list](https://user-images.githubusercontent.com/9599/201845041-e6df06c1-ea93-4410-8696-cdf904cfc61c.gif)

## Creating them in JavaScript

You can also create these in JavaScript using the DOM, for example:

```javascript
var parties = [
  "Anti-Administration",
  "Pro-Administration",
  "Republican",
  "Federalist",
  "Democratic Republican",
  "Pro-administration",
  "Anti-administration",
  "Unknown",
  "Adams",
  "Jackson"
];
var datalist = document.createElement("datalist");
datalist.id = "parties";
parties.forEach(function (party) {
    var option = document.createElement("option");
    option.value = party;
    datalist.appendChild(option);
});
document.body.appendChild(datalist);
```
Then use `input.setAttribute('id', 'parties')` on any input elemnt you want to use that new `datalist`.
