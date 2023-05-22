# hexdump and hexdump -C

While exploring null bytes in [this issue](https://github.com/simonw/ttok/issues/3) I learned that the `hexdump` command on macOS (and presumably other Unix systems) has a confusing default output.

Consider the following:
```
$ echo -n 'abc\0' | hexdump
0000000 6261 0063                              
0000004
```
Compared to:
```
$ echo -n 'a' | hexdump    
0000000 0061                                   
0000001
```
I'm using `echo -n` here to avoid adding an extra newline, which encodes as `0a`.

My shell hell is `zsh` - `bash` requires different treatment, see below.

How come `abc\0` starts with 6261 where `a` starts with `0061`?

It turns out `hexdump` default format is 16-bit words in little-endian format, which is really confusing.

## hexdump -C

Using the `-C` option fixes this:
```
$ echo -n 'a' | hexdump -C
00000000  61                                                |a|
00000001
$ echo -n 'abc\0' | hexdump -C
00000000  61 62 63 00                                       |abc.|
00000004
```
`C` here stands for "canonical".

In addition to causing `hexdump` to output byte by byte, it also includes an ASCII representation on the right hand side.

## Null bytes in Bash

Karl Pettersson [pointed out](https://twitter.com/KarlPettersso10/status/1660721994793377792) that these examples won't work on Bash.

I ran `bash` on my Mac and found the following:

```
bash-3.2$ echo -n 'abc\0' | hexdump -C
00000000  61 62 63 5c 30                                    |abc\0|
00000005
bash-3.2$ echo -n $'abc\0' | hexdump -C
00000000  61 62 63                                          |abc|
00000003
bash-3.2$ printf 'abc\0' | hexdump -C
00000000  61 62 63 00                                       |abc.|
00000004
bash-3.2$ printf $'abc\0' | hexdump -C
00000000  61 62 63                                          |abc|
00000003
```
So it looks like using `printf 'abc\0'` is the best recipe for Bash on macOS. I'm not sure if Bash on other platforms differs.
