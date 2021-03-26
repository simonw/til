# Finding the largest SQLite files on a Mac

This runs using Spotlight so it's really fast:

    mdfind "kMDItemDisplayName == *.sqlite" -0 | xargs -0 stat "-f%z %N" | sort -nr | head -n 20

I have a lot of files in my Dropbox so I excluded those like this:

```
~ % mdfind "kMDItemDisplayName == *.sqlite" -0 | xargs -0 stat "-f%z %N" | sort -nr | grep -v Dropbox | head -n 20
852422656 /Users/simon/Pictures/Photos Library.photoslibrary/database/Photos.sqlite
301924352 /Users/simon/Library/Reminders/Container_v1/Stores/Data-A8BA15F3-C80E-43B3-9E21-F7D1CD42AB6A.sqlite
51343360 /Users/simon/Pictures/Photos Library.photoslibrary/database/search/psi.sqlite
47349760 /Users/simon/Library/Application Support/Firefox/Profiles/ljj897b8.default-release/webappsstore.sqlite
47185920 /Users/simon/Library/Application Support/Firefox/Profiles/ljj897b8.default-release/places.sqlite
33779712 /Users/simon/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite
```
Figured out via [this comment](https://news.ycombinator.com/item?id=24179518) by why_only_15 on Hacker News.
