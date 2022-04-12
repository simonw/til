# Trick Apple Photos into letting you access your video files

I had an 11GB movie in Apple Photos (sync'd from my iPhone) and I wanted to upload it to YouTube (actually via AirDrop to another laptop first).

The "export" options in Apple Photos provided no visual indicator of what they were doing - as far as I could tell they were broken.

I wanted to deal with the actual file on disk. I figured out how to get access to that like so:

1. Right click on the movie in Apple Photes
2. Select Edit With -> QuickTime Player
3. In QuickTime Player, command-click on the filename in the QuickTime window to get a list of folders
4. Click on the parent folder of the file to get a Finder window

Now you can treat the .MOV like a regular file! Right click and AirDrop and suchlike should work fine.

The command-click menu in QuickTime should look like this:

<img width="368" alt="IMG_7790.mov
In a folder with a big complex UUID name
In a folder called ExternalEditSessions
In a folder called com.apple.Photos
in a folder called private
In a folder called Photos Library.photoslibrary" src="https://user-images.githubusercontent.com/9599/163071235-6ff80bc1-374c-4905-93d6-cd3c5486c6a8.png">

Then when I went to quit the Apple Photos app later it told me I had export jobs in progress, the jobs that I hadn't been able to see in the first place!
