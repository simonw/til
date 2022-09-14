# Browse files (including SQLite databases) on your iPhone with ifuse

I spotted an intriguing note in the release notes for [osxphotos 0.51.7](https://github.com/RhetTbull/osxphotos/releases/tag/v0.51.7):

> Added ability to read Photos.sqlite from iPhone

This lead me to [osxphotos issue #745](https://github.com/RhetTbull/osxphotos/issues/745) which lead me to [How to access iPhone files with a disk mount](https://reincubate.com/support/how-to/mount-iphone-files/) which lead me to [ifuse](https://github.com/libimobiledevice/ifuse) and [ homebrew-fuse
](https://github.com/gromgit/homebrew-fuse).

Here's what worked for me.

1. Connect the iPhone to a Mac using a USB-C to Lightning cable
2. Find the serial number of your iPhone, by running `system_profiler SPUSBDataType -detailLevel mini | grep -e iPhone -e Serial` and looking for the first number. It will look something like `00008110001631C105BA801E`.
3. Add a hyphen to that serial number after the 8th character: `00008110-001631C105BA801E` - you will need this later
4. `brew install macfuse`
5. `brew install gromgit/fuse/ifuse-mac`
6. A tricky bit: this has installed an unsigned binary, which macOS really doesn't want to execute. So...
7. `mkdir /tmp/iPhone`
8. `ifuse ~/iPhone --udid 00008110-001631C105BA801E` - using the serial number you figured out earlier
9. This should fail with an error complaining about the unsigned binary
10. Open System Preferences -> Security & Privacy and allow that binary to run. You may then need to restart your computer.
11. After the reboot, `mkdir /tmp/iPhone` again.
12. Now try `ifuse ~/iPhone --udid 00008110-001631C105BA801E` again - this time it should work

If everything goes right, you can run `open /tmp/iPhone` to open a Finder window showing at least some of the contents of your phone. You can also `cd /tmp/iPhone` to start poking around from the terminal.

## Finding SQLite databases

The easiest way to find SQLite databases to explore is to run:

    find /tmp/iPhone | grep 'wal'

This searches for files with names like `downloads.28.sqlitedb-wal` - which indicate a SQLite database that has been opened in WAL mode.

On my iPhone I get these:
```
/tmp/iPhone/Downloads/downloads.28.sqlitedb-wal
/tmp/iPhone/Books/MetadataStore/BookMetadataStore.sqlite-wal
/tmp/iPhone/Books/Sync/Database/OutstandingAssets_4.sqlite-wal
/tmp/iPhone/Radio/Radio.db-wal
/tmp/iPhone/iTunes_Control/iTunes/MediaLibrary.sqlitedb-wal
/tmp/iPhone/MediaAnalysis/mediaanalysis.db-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSBusinessCategoryCache.Nature.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSContactCache.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/musiccache.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSLocationCache.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSPublicEventCache.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/PhotosGraph/construction-photosgraph.kgdb-wal
/tmp/iPhone/PhotoData/Caches/GraphService/PhotosGraph/photosgraph-tmp.kgdb-wal
/tmp/iPhone/PhotoData/Caches/GraphService/PhotosGraph/photosgraph.kgdb-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSBusinessCategoryCache.POI.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSBusinessCategoryCache.ROI.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/PGCurationCache.sqlite.sqlite-wal
/tmp/iPhone/PhotoData/Caches/GraphService/CLSBusinessCategoryCache.AOI.sqlite-wal
/tmp/iPhone/PhotoData/Caches/search/psi.sqlite-wal
/tmp/iPhone/PhotoData/CPL/storage/store.cloudphotodb-wal
/tmp/iPhone/PhotoData/Photos.sqlite-wal
```
You can then open them in Datasette by specifying the filename without the `-wal` extension. For example:

    datasette /tmp/iPhone/Radio/Radio.db
