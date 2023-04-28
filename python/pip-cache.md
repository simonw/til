# The location of the pip cache directory

`pip` uses a cache to avoid downloading packages again:

```
% pip install lxml  
Collecting lxml
  Using cached lxml-4.9.2-cp311-cp311-macosx_13_0_arm64.whl
Installing collected packages: lxml
Successfully installed lxml-4.9.2
```
The `pip cache dir` command can be used to find the location of that cache on your system:
```
% pip cache dir
/Users/simon/Library/Caches/pip
```
Wheels are cached in `pip/wheels` - in a nested set of folders based on a hash, for example:
```
wheels/fb/5b/f7/0a27880b4a007daeff53a196d01901627f640392b7e76e76e5/lxml-4.9.2-cp311-cp311-macosx_13_0_arm64.whl
```
I found this pattern worked for deleting files from the cache:
```
cd $(pip cache dir)
find wheels | grep lxml | xargs rm
```
