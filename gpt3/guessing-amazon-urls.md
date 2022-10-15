# Guessing Amazon image URLs using GitHub Copilot

I was experimenting with the new [Readwise export API](https://readwise.io/api_deets#export) and it gave me back the following JSON:

```json
{
  "user_book_id": 15433610,
  "title": "Screenwriting: The Sequence Approach",
  "author": "Paul Joseph Gulino",
  "readable_title": "Screenwriting",
  "source": "kindle",
  "cover_image_url": "https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL75_.jpg",
  "unique_url": null,
  "book_tags": [],
  "category": "books",
  "readwise_url": "https://readwise.io/bookreview/15433610",
  "source_url": null,
  "asin": "B00F9476Y0",
  "highlights": []
}
```
The image URL `https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL75_.jpg` produced a tiny little image - this one:

<img alt="A tiny picture of a book cover" src="https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL75_.jpg">

I wanted to get back a bigger version of that image. On a hunch, I popped open a VS Code window running GitHub Copilot and typed this:

```
https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL75_.jpg
# That image but bigger:
```
It autocompleted for me:
```
https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL.jpg
```
Which is indeed a larger version of the image!

<img alt="Screenwriting: The Sequence Approach - a much bigger book cover image, with legible text" src="https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL.jpg">

I typed `#` and hit autocomplete again, to see what would happen, and got this:

```
# That image but smaller:
https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL50_.jpg
```

<img alt="An even tinier picture of a book cover" src="https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL50_.jpg">

Another correct guess. GPT-3/Copilot clearly includes training data that has seen these URLs before.

I typed `#` one more time and it autocompleted again to:

```
# That image but with a different format:
https://images-na.ssl-images-amazon.com/images/I/51UMeAAJNRL._SL50_.gif
```
... and this time that URL is a 404. Copilot made this one up!
