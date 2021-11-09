# Using Tesseract.js to OCR every image on a page

Pasting this code into a DevTools console should load [Tesseract.js](https://github.com/naptha/tesseract.js) from a CDN, loop through every image loaded by that page (every PNG, GIF, JPG or JPEG), run OCR on them and output the result to the DevTools console.
                                                                     
There's one major catch: the images need to be served in a context that allows JavaScript to read their content - either from the same domain, or from a separate domain with a permissive CORS policy.
                                                                     
Very few sites do this! It worked on www.google.com for me, where it successfully OCRs the Google logo as containing the text "Google".
                                                                     
```javascript
var s = document.createElement("script")
s.src = "https://unpkg.com/tesseract.js@v2.1.0/dist/tesseract.min.js";
document.head.appendChild(s);
s.onload = (async () => {
  const imageUrls = performance.getEntries().map(f => f.name).filter(
    n => n.includes('.jpg') || n.includes('.gif') || n.includes('.png')  || n.includes('.jpeg')
  );
  const worker = Tesseract.createWorker();
  await worker.load();
  await worker.loadLanguage('eng');
  await worker.initialize('eng');
  for (const url of imageUrls) {
    console.log(url);
    var { data: { text } } = await worker.recognize(url);
    console.log(text);
  }
});
```
