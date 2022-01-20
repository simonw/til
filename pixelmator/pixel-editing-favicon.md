# Pixel editing a favicon with Pixelmator

I wanted to [add a favicon](https://github.com/simonw/datasette/issues/1603) to Datasette, using a PNG image served from `/favicon.ico` as suggested in [this article by Adam Johnson](https://adamj.eu/tech/2022/01/18/how-to-add-a-favicon-to-your-django-site/).

Initially I created a 128x128 icon image (using Figma and exporting as PNG) and allowed the browsers to resize it down to 32x32 - but I wasn't satisfied with the result:

![Screenshot showing my resized icon in Firefox, Chrome and Safari](https://user-images.githubusercontent.com/9599/150405946-46d4aadc-deda-47f7-a562-0db5232af36c.png)

I decided to use [Pixelmator](https://www.pixelmator.com/pro/) on my Mac (since I already have a paid license) to hand-edit the icon at 32x32 to see if I could get better results.

Pixelmator's default interface doesn't include a tool for setting individual pixels - even at 1px size the default brushes affect nearby pixels too.

Thanks to [Enabling a Pixel Brush in Pixelmator to Draw Pixel Art on Mac](https://osxdaily.com/2016/11/17/enable-pixel-brush-pixelmator-mac/) on OSXDaily I found the preference pane (in Preferences -> Tools -> Paintig) that lets you drag a pixel editing tool onto the tool palette.

With that added, I could bump up the zoom level on a brand new 32x32 image and start editing pixels.

I used the `I` keyboard shortcut to switch to the eyedropper to select colours, and the `P` keyboard shortcut to switch back to the pixel tool to edit the pixels.

I couldn't figure out how to delete individual pixels (in order to achieve a transparent PNG background) so I used the eraser tool to fuzzy-erase areas, then redrew the pixels by hand with the pixel tool.

![Screenshot of the Pixelmator interface](https://user-images.githubusercontent.com/9599/150406510-b563af5b-21e0-48b2-b73f-bbf4031f3050.png)

I exported the finished image as a PNG, then used https://squoosh.app/ to shrink it down to just 208 bytes.

![Screenshot of the Squoosh interface - I used effort=3 and colors=8](https://user-images.githubusercontent.com/9599/150406568-4081e9aa-2161-4f6c-bc97-5e99780d6ea0.png)

The end result, comparing the browser-resized icon to my hand-edited one:

![The one I let the browser resize has some fuzzy edges. The hand-edited one does not.](https://user-images.githubusercontent.com/9599/150407521-a7b0c823-d9f3-4c31-b927-6ac9d93e9d85.png)
