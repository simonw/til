# Driving an external display from a Mac laptop

For a friend's wedding I needed to run a Google Photos slideshow on some large televisions.

I had two MacBook Pro laptops. Here's how I got it to work.

Hardware:

- Two MacBook laptops
- Two laptop power supplies (battery only doesn't work)
- Two HDMI cables
- Two HDMI-to-UBC-C dongles

I wanted to leave the laptops closed, tucked away within HDMI cable distance of the TVs.

The power supplies were necessary because macOS won't let you close the lid of a laptop that is connected to an external display and have it stay powered up.

## Settings

It took a few iterations to find the right settings. The key thing was that I needed the laptop and the display to stay on, for several hours, despite the laptop itself being closed.

There are three separate preference panels involved in this.

In "Battery", switch to the "Power Adapter" tab and move "Turn display off after:" to "Never" and check the "Prevent your Mac from automatically sleeping when the display is off" checkbox:

![Screenshot of power adapter settings](https://user-images.githubusercontent.com/9599/189490465-a8b6da6c-1215-452b-9eda-874b4542fcef.png)

In "Desktop & Screen Saver" turn off the option to "Show screensaver after X minutes":

![Screenshot of screensaver settings](https://user-images.githubusercontent.com/9599/189490561-10b3b056-28f5-4b96-b3cb-56c978231bef.png)

In "Security and Privacy", turn off the option to "Require password ... after sleep or screen saver begins":

![Screenshot of security and privacy settings](https://user-images.githubusercontent.com/9599/189490619-cc9fdc4c-b55b-41dd-b7a8-61d14b5e5093.png)

Don't forget to undo these changes when your laptop returns to its regular use!
