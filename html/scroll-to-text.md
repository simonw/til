# Scroll to text fragments

I ran a Google search this morning for `s3-credentials simon willison` and when I clicked on the top result it jumped me to a highlighted snippet of text on the page, despite that page not having relevant anchor links.

![A Google search for s3-credentials simon willison - the top result is a featured snippet containing some highlighted text. Next to that is a screenshot of the linked page - those text snippets are still highlighted there.](https://github.com/simonw/til/assets/9599/5ad6d8ec-cc9d-479a-8ef0-7cbe4ad83260)


I decided to figure out how that worked.

The Google search result linked to the following URL:

`https://simonwillison.net/2021/Nov/3/s3-credentials/#:~:text=s3%2Dcredentials%20is%20a%20Python,my%20click%2Dapp%20cookicutter%20template.&text=The%20main%20command%20is%20s3,the%20above%20sequence%20of%20steps.&text=The%20command%20shows%20each%20step,access%20key%20and%20secret%20key.`

The magic is in that `#:~:` section of the URL fragment. In this case it has three `text=` parameters, each of which is a URL encoded string. Decoded, those are:

- `text=s3-credentials is a Python,my click-app cookicutter template.`
- `&text=The main command is s3,the above sequence of steps.`
- `&text=The command shows each step,access key and secret key.`

This is a relatively new web standard called **URL Fragment Text Directives**, also sometimes referred to as **URL Scroll-To-Text Fragment**.

Here's the spec: [URL Fragment Text Directives](https://wicg.github.io/scroll-to-text-fragment/) - categorized as a "Draft Community Group Report". It's published by the W3C's [Web Incubator Community Group (WICG)](https://wicg.io/).

It's currently supported by Chrome and Safari. Safari added support last year - here's [their launch announcement](https://webkit.org/blog/13399/webkit-features-in-safari-16-1/#scroll-to-text-fragment) from Oct 24, 2022.

It's not available in Firefox yet, but they've publicly committed to adding support:

- [Mozilla Specification Positions: positive for Text Fragments](https://mozilla.github.io/standards-positions/#scroll-to-text-fragment)
- [mozilla/standards-positions: Scroll To Text Fragment](https://github.com/mozilla/standards-positions/issues/194) has a more detailed discussion.

There's a bunch more to it than just `text=` - see [the syntax guide](https://wicg.github.io/scroll-to-text-fragment/#syntax) for more details. The full grammar looks like this:

```
#:~:text=[prefix-,]start[,end][,-suffix]
```
The square bracket parts are optional, and provide additional context to clarify the match.

Note that commas that should be literally matched in the text are encoded as `%2C`, avoiding clashes with the above syntax.

To highlight a sentence that starts "Datasette is" and ends "accompanying API" you would use this:

```
#:~:text=Datasette%20is,accompanying%20API
```
- https://datasette.io/#:~:text=Datasette%20is,accompanying%20API

The `prefix-` bit specifies a prefix that should not be highlighted but does need to be present for the match to happen - same with `-suffix`.

So you can match "is a tool" but only if it follows the text "Datasette" using:

```
#:~:text=Datasette-,is%20a%20tool
```
- https://datasette.io/#:~:text=Datasette-,is%20a%20tool

