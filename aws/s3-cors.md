# Adding a CORS policy to an S3 bucket

Amazon S3 buckets that are configured to work as public websites can support CORS, allowing assets such as JavaScript modules to be loaded by JavaScript running on other domains.

This configuration happens at the bucket level - it's not something that can be applied to individual items.

[Here's their documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enabling-cors-examples.html). As with so many AWS things it involves hand-crafting a JSON document: the documentation for that format, with useful examples, [is here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ManageCorsUsing.html).

## Using s3-credentials

My [s3-credentials tool](https://s3-credentials.readthedocs.io/) now has a command for setting a CORS policy:

```
s3-credentials set-cors-policy my-cors-bucket \
  --allowed-method GET \
  --allowed-origin https://simonwillison.net/
```
Here's the [full documentation for that command](https://s3-credentials.readthedocs.io/en/stable/other-commands.html#set-cors-policy-and-get-cors-policy).

## Using the S3 web console

I originally opted to use the S3 web console option - find the bucket in the console interface, click the "Security" tab and you can paste in a JSON configuration.

The configuration I tried first was this one:

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "https://simonwillison.net/"
        ],
        "ExposeHeaders": []
    }
]
```
This should enable CORS access for GET requests from code running on my https://simonwillison.net/ site.

The `AllowedOrigins` key is interesting: it works by inspecting the `Origin` header on the incoming request, and returning CORS headers based on if that origin matches one of the values in the list.

I used `curl -i ... -H "Origin: value"` to confirm that this worked:

```
~ % curl -i 'http://static.simonwillison.net.s3-website-us-west-1.amazonaws.com/static/2022/photoswipe/photoswipe-lightbox.esm.js' \
  -H "Origin: https://simonwillison.net" | head -n 20
-x-amz-request-id: 4YY7ZBCVJ167XCR9
 Date: Tue, 04 Jan 2022 21:02:44 GMT
-Access-Control-Allow-Origin: *
-Access-Control-Allow-Methods: GET
:Vary: Origin, Access-Control-Request-Headers, Access-Control-Request-Method
-Last-Modified: Tue, 04 Jan 2022 20:10:26 GMT
-ETag: "8e26fa2b966ca8bac30678cdd6af765c"
:Content-Type: text/javascript
-Server: AmazonS3

~ % curl -i 'http://static.simonwillison.net.s3-website-us-west-1.amazonaws.com/static/2022/photoswipe/photoswipe-lightbox.esm.js' | head -n 20
x-amz-request-id: MPD20P9P3X45BR1Q
Date: Tue, 04 Jan 2022 21:02:48 GMT
Last-Modified: Tue, 04 Jan 2022 20:10:26 GMT
ETag: "8e26fa2b966ca8bac30678cdd6af765c"
Content-Type: text/javascript
Server: AmazonS3
```

With the `Origin` header on the request it returns the `Access-Control-Allow-Origin` headers. Without it does not.

I'm running my S3 bucket behind a Cloudflare cache. As you can see above, S3 returns a `Vary: Origin` header so caches know that they should respect that header when returning cached content.

But... while Cloudflare [added support for Vary](https://blog.cloudflare.com/vary-for-images-serve-the-correct-images-to-the-correct-browsers/) in September 2021 they only support it for images, not for other file formats! So sadly I don't think you can use CORS for JavaScript modules in this way if you are using Cloudflare.

I also tried using `"AllowedOrigins": ["*"]` in my S3 configuration, but I found that if you make a request without an `Origin` header S3 still doesn't return `Access-Control-Allow-Origin` - so under a cache that does not support Vary you run the risk of caching an asset without those headers.

## CORS policy to allow PUT using signed credentials

A useful feature of S3 is that you can generate [signed credentials](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) that allow JavaScript running in a browser to upload files to a pre-determined key in a bucket.

After much frustration, here's the CORS policy that's needed to enable this:

```json
[
    {
        "AllowedHeaders": [
            "content-type"
        ],
        "AllowedMethods": [
            "PUT"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "content-type",
            "etag"
        ]
    }
]
```
I used this command to set that policy:
```bash
s3-credentials set-cors-policy -m PUT -o '*' name-of-bucket -e content-type -e etag -h content-type
```
