# Interpreting photo orientation and locations in EXIF data

I upgraded my [Niche Museums](https://www.niche-museums.com/) site to use [PhotoSwipe](https://photoswipe.com/) for its photo galleries today. Here's [my issue](https://github.com/simonw/museums/issues/37).

This lead me down a bit of a rabbit hole of photo EXIF data.

The two problems I ended up solving:

- Given photo EXIF data, what is the width and height of the image (taking photo orientation into account)?
- Also given EXIF data, how can I determine the latitude and longitude of the photo?

## Figuring out the width and height

The PhotoSwipe gallery code needs to have the width and heights of the images embedded in custom `data-` attributes like this:

```html
<a
  data-pswp-height="3024"
  data-pswp-width="4032"
  href="https://niche-museums.imgix.net/pioneer-history-19.jpeg?w=1200&auto=compress" 
  class="gallery-photo">
  <img
    src="https://niche-museums.imgix.net/pioneer-history-19.jpeg?w=400&blur=200&px=16&auto=format">
</a>
```
My database was only storing the URL to those images, not their widths and heights. In order to generate the correct HTML I needed that extra information.

Niche Museums hosts photos in an S3 bucket behind [Imgix](https://imgix.com/), which means I can resize the photos on demand using the `?w=` and `?h=` query parameters.

It also means I can get back JSON for the EXIF data of the images by appending `?fm=json`.

https://niche-museums.imgix.net/pioneer-history-18.jpeg?fm=json

There's a lot of information in there, but the most important bits for solving this problem are:
```json
{
  "Orientation": 3,
  "PixelWidth": 4032,
  "PixelHeight": 3024
}
```
For my first attempt, I assumed that `PixelWidth` and `PixelHeight` represented the width and height of the image, respectively.

This almost worked... except for some photos which were displayed in portrait mode, for which the two values appeared to be swapped.

The answer turned out to be in the `Orientation` parameter. GPT-4 helped me understand the following:

> The values you mentioned (1, 3, 6, and 8) represent the most common orientations:
>
> - 1: Normal (0° rotation)
> - 3: Upside-down (180° rotation)
> - 6: Rotated 90° counterclockwise (270° clockwise)
> - 8: Rotated 90° clockwise (270° counterclockwise)

So I need to flip the width and height values if the orientation is 6 or 8.

I ended up doing that using this SQL query:

```sql
select
    'https://niche-museums.imgix.net/' || filename as url,
    case
        when Orientation in (6, 8) then PixelHeight
        else PixelWidth
    end as width,
    case
        when Orientation in (6, 8) then PixelWidth
        else PixelHeight
    end as height
from raw_photos;
```
## That raw_photos table

I skipped a step here: how did I load the data into that `raw_photos` table in the first place?

First I wrote [a Python script](https://github.com/simonw/museums/blob/6577b0c4b25e025de1176d2017d61742616ddf8e/fetch_photo_metadata.py) to retrieve the JSON metadata for every photo. This dumped them into [a photos-metadata/ directory](https://github.com/simonw/museums/tree/main/photos-metadata), each one with a name like `IMG_0859.jpeg.json`.

That script now [runs in GitHub Actions](https://github.com/simonw/museums/blob/6577b0c4b25e025de1176d2017d61742616ddf8e/.github/workflows/push.yml#L35-L46) to catch metadata for newly added photos - a form of [Git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/).

Next, I wrote [a sqlite-utils Python script](https://github.com/simonw/museums/blob/6577b0c4b25e025de1176d2017d61742616ddf8e/load_photo_metadata.py) to load all of those JSON files into my SQLite database. That script also creates a `photos` view that implements the above `case` SQL logic.

I initially wrote this as a shell script, but it was a LOT slower than doing it in Python:
```bash
for json_file in photos-metadata/*.json; do
  sqlite-utils insert browse.db raw_photos \
    --pk=filename \
    --replace \
    --alter \
    --silent \
    --convert "def convert(row):
      row['filename'] = '$(basename $json_file .json)'
      return row
    " \
    $json_file
done
```
## The latitude/longitude problem

Having loaded the JSON data into my SQLite table, some of my rows now had a `GPS` column value that looked like this:

```json
{
    "HPositioningError": 26.4704,
    "Longitude": 118.301,
    "Latitude": 34.1191,
    "Speed": 0.919278,
    "SpeedRef": "K",
    "ImgDirection": 167.075,
    "LatitudeRef": "N",
    "AltitudeRef": 0,
    "ImgDirectionRef": "T",
    "LongitudeRef": "W",
    "Altitude": 341.598,
    "DestBearingRef": "T",
    "DestBearing": 167.075
}
```
I tried plotting that on a map using [datasette-cluster-map](https://datasette.io/plugins/datasette-cluster-map) and the following query:

```sql
select
  json_object(
    'image', 'https://niche-museums.imgix.net/' || filename || '?w=600',
    'title', filename
  ) as popup,
  json_extract(GPS, '$.Latitude') as latitude,
  json_extract(GPS, '$.Longitude') as longitude
from
  raw_photos
where json_extract(GPS, '$.Latitude') is not null
```
Here's [the map](https://www.niche-museums.com/browse?sql=select%0D%0A++json_object%28%0D%0A++++%27image%27%2C+%27https%3A%2F%2Fniche-museums.imgix.net%2F%27+%7C%7C+filename+%7C%7C+%27%3Fw%3D600%27%2C%0D%0A++++%27title%27%2C+filename%0D%0A++%29+as+popup%2C%0D%0A++json_extract%28GPS%2C+%27%24.Latitude%27%29+as+latitude%2C%0D%0A++json_extract%28GPS%2C+%27%24.Longitude%27%29+as+longitude%0D%0Afrom%0D%0A++raw_photos%0D%0Awhere+json_extract%28GPS%2C+%27%24.Latitude%27%29+is+not+null&_hide_sql=1) that produced:

<img width="1130" alt="A map with a bunch of labels, but they are scattered mainly across Asia and the Middle East" src="https://user-images.githubusercontent.com/9599/233794576-f4906c1e-cf22-416d-a210-9ba388ea9e6a.png">

I haven't been to most of those countries, so those locations are showing in the wrong place!

I said to GPT-4:
> ```json
> {
>     "HPositioningError": 128,
>     "Longitude": 122.449,
>     "Latitude": 37.7422,
>     "Speed": 0,
>     "SpeedRef": "K",
>     "ImgDirectionRef": "T",
>     "ImgDirection": 320.522,
>     "LongitudeRef": "W",
>     "LatitudeRef": "N",
>     "AltitudeRef": 0,
>     "DateStamp": "2018:02:20",
>     "Altitude": 167,
>     "TimeStamp": "22:44:21",
>     "DestBearingRef": "T",
>     "DestBearing": 320.522
> }
> ```
> How do I turn that into a latitude/longitude with correct - or +

It replied:

> To convert the given JSON data into a proper latitude/longitude format with correct positive or negative signs, you'll need to account for the LatitudeRef and LongitudeRef values. If the LatitudeRef is "S" (South), the latitude should be negative. If the LongitudeRef is "W" (West), the longitude should be negative.

I pasted in my SQL query and said "Rewrite this SQL query to apply those rules" - and it gave me the following:

```sql
select
  json_object(
    'image', 'https://niche-museums.imgix.net/' || filename || '?w=600',
    'title', filename
  ) as popup,
  case
    when json_extract(GPS, '$.LatitudeRef') = 'S'
      then -1 * json_extract(GPS, '$.Latitude')
    else json_extract(GPS, '$.Latitude')
  end as latitude,
  case
    when json_extract(GPS, '$.LongitudeRef') = 'W'
      then -1 * json_extract(GPS, '$.Longitude')
    else json_extract(GPS, '$.Longitude')
  end as longitude
from
  raw_photos
where json_extract(GPS, '$.Latitude') is not null
```
[Try that here](https://www.niche-museums.com/browse?sql=select%0D%0A++json_object%28%0D%0A++++%27image%27%2C+%27https%3A%2F%2Fniche-museums.imgix.net%2F%27+%7C%7C+filename+%7C%7C+%27%3Fw%3D600%27%2C%0D%0A++++%27title%27%2C+filename%0D%0A++%29+as+popup%2C%0D%0A++case%0D%0A++++when+json_extract%28GPS%2C+%27%24.LatitudeRef%27%29+%3D+%27S%27%0D%0A++++++then+-1+%2A+json_extract%28GPS%2C+%27%24.Latitude%27%29%0D%0A++++else+json_extract%28GPS%2C+%27%24.Latitude%27%29%0D%0A++end+as+latitude%2C%0D%0A++case%0D%0A++++when+json_extract%28GPS%2C+%27%24.LongitudeRef%27%29+%3D+%27W%27%0D%0A++++++then+-1+%2A+json_extract%28GPS%2C+%27%24.Longitude%27%29%0D%0A++++else+json_extract%28GPS%2C+%27%24.Longitude%27%29%0D%0A++end+as+longitude%0D%0Afrom%0D%0A++raw_photos%0D%0Awhere+json_extract%28GPS%2C+%27%24.Latitude%27%29+is+not+null&_hide_sql=1) - it gave me the map I was looking for.

<img width="1123" alt="Now the markers are mainly in the US and Europe, with a few in Madagascar and one with an open popup showing a photo of Recoleta-Cemetery in Argentina." src="https://user-images.githubusercontent.com/9599/233794606-288d324a-afdc-4111-a1f0-ff530bb48671.png">
