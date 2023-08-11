# Catching up with the Cosmopolitan ecosystem

I caught up with some of the latest developments in the ecosystem around Justine Tunney's [cosmopolitan](https://github.com/jart/cosmopolitan) and Actually Portable Executable (APE) projects this week. They are _absolutely fascinating_.

An [Actually Portable Executable](https://justine.lol/ape.html) is a wildly clever hack. It's a single binary file which can run as an executable on multiple platforms - on x86-64 Linux, macOS, Windows and various BSDs, and for ARM-64 on Linux and macOS too (macOS ARM-64 is a recent addition).

Some posts that help explain how this works:

- [αcτµαlly pδrταblε εxεcµταblε](https://justine.lol/ape.html) from August 24th 2020 explains the initial hack
- [APE Loader](https://justine.lol/apeloader/) from June 11th, 2022 explains some of the more recent internals

Pretty much anything written in standard C can be turned into one of these things, using the [cosmocc compiler](https://github.com/jart/cosmopolitan/tree/master#getting-started) something like this:

```bash
./configure CC=cosmocc
make
make install

cosmocc -o executable.com hello.c
```
Then run `./executable.com` on any of the above platforms to run the program!

There are a whole bunch of components to this.

[Cosmopolitan](https://github.com/jart/cosmopolitan) is probably the most important. It describes itself as a "build-once run-anywhere C library" - it includes both the `cosmocc` compiler and implements a [bewildering array](https://justine.lol/cosmopolitan/functions.html) of system call wrappers to get everything to work cross-platform.

## Trying out redbean

[redbean](https://redbean.dev/) is one of the most interesting applications built on top of Cosmopolitan. It's a "single-file distributable web server" - you download `redbean-2.2.com` and run it to start a server (on any of the supported operating systems), but it also acts as a zip file - so you can load your own files into that archive for it to serve, or provide it with Lua code that it can execute as well. And it bundles SQLite. It's really cool!

To use it on macOS you have to dance around the security settings a little bit. Here's how I got it working:

```bash
# Download the redbean binary
curl -O https://redbean.dev/redbean-2.2.com
# Make it executable
chmod +x redbean-2.2.com
# Try to run it the first time
./redbean-2.2.com
```
This triggers a security warning:

<img width="284" alt="redbean-2.2.com cannot be opened because the developer cannot be verified. macOS cannot verify that this app is free from malware. Firefox downloaded this file today at 4:44 PM. Move to Trash" src="https://github.com/simonw/til/assets/9599/c4004948-6aba-4a3e-b916-d9f39c0627f7">

To work around this, go to System Preferences > Security & Privacy > General and click "Allow Anyway" next to the warning about the redbean binary:

![Screenshot of the Privacy panel - an arrow points to the Allow Anyway button.](https://github.com/simonw/til/assets/9599/50e64eb8-422c-47fe-9731-edd9df7dd089)

Now try `./redbean-2.2.com` again and it should show this:

<img width="285" alt="macOS cannot verify the developer of redbean-2.2.com. Are you sure you want to open it? By opening this app, you will be overriding system security which can expose your computer and personal information to malware that may harm your Mac or compromise your privacy. Firefox downloaded this file today at" src="https://github.com/simonw/til/assets/9599/9b446b99-6f42-4da1-8a5d-bc309cb3b1d4">

Click "Open" and it will run. Then visit http://localhost:8080/ to see it in a browser:

<img width="536" alt="redbean/2.2.0 and a file listing in a browser" src="https://github.com/simonw/til/assets/9599/5738cb24-6e15-435f-a721-4926e0d61edf">

## redbean.systems - an online compiler

One of the latest additions to the ecosystem - in the last couple of months - is [redbean.systems](https://redbean.systems/) - which offers an online compiler that can accept C code and turn it into a downloadable APE executable file.

The homepage includes a Mandelbrot fractal demo. Clicking "build" on that generates an executable:

<img width="995" alt="Actually Portable Executable Demos: Build and share fat binaries for ARM (Linux/MacOS) and AMD (Linux/MacOS/Windows/FreeBSD/NetBSD/OpenBSD) online. Then a textarea with C source code, and some build logs, and a link to download an executable file." src="https://github.com/simonw/til/assets/9599/88b876c8-8bd6-40ca-bd71-1d119ebc7bbf">

Download that, run `chmod 755 ...` on it, then jump through the same security hoops as before... and you can run the command!

## Cosmopolitan Python

There are various versions of Python that have been compiled to Cosmopolitan, too.

[Python is Actually Portable](https://ahgamut.github.io/2021/07/13/ape-python/) from July 2021, updated July 2022 describes efforts to run Python on Cosmopolitan in detail.

[Issue #141: Compiling Python](https://github.com/jart/cosmopolitan/issues/141) is a multi-year, detailed issue thread documenting different attempts at this.

[https://justine.lol/ftrace/python.com](https://justine.lol/ftrace/python.com) is a downloadable executable of Python 3.6 that worked on my Mac:

```
$ ./python.com   
Python 3.6.14+ (Actually Portable Python) [GCC 9.2.0] on cosmo
Type "help", "copyright", "credits" or "license" for more information.
>>: import sys
>>: sys.version
'3.6.14+ (Actually Portable Python) [GCC 9.2.0]'
```

[superconfigure/releases/tag/z0.0.1](https://github.com/ahgamut/superconfigure/releases/tag/z0.0.1) is a release from 9th August 2023 that includes both a `python.com` bundling Python 3.11 and a `datasette.com` that packages my [Datasette](https://datasette.io/) application! Sadly these don't appear to include macOS ARM support so I haven't been able to run them myself yet.

## The --strace option

A fun extra trick you can do: add `--strace` when running an API and it will output the system calls that are made as the executable runs.

Here's the output of that for the Mandelbrot program:

```
./6465048416604704318.com --strace
SYS  90990             96'864 getenv("TERM") → "xterm-256color"
         !!!!!!!!"""""""""""""""""""""""""""##########$$$$%%&(.)(*2%$#######""""""""!!!!!!!!!!!!!!!!!
SYS  90990            111'856 write(1, u"         !!!!!!!!“““““““““““““““““““““““"..., 102) → 102
        !!!!!!!"""""""""""""""""""""""""""###########$$$$%%&'(*0+('&%$$#######""""""""!!!!!!!!!!!!!!!
SYS  90990            113'712 write(1, u"        !!!!!!!“““““““““““““““““““““““““"..., 102) → 102
       !!!!!!""""""""""""""""""""""""""############$$$$$%&(**-:::1('&%$$$#######""""""""!!!!!!!!!!!!!
SYS  90990            115'520 write(1, u"       !!!!!!““““““““““““““““““““““““““#"..., 102) → 102
      !!!!!""""""""""""""""""""""""""############$$$%%%&'(+:::::::02*&%$$$$$######""""""""!!!!!!!!!!!
SYS  90990            117'440 write(1, u"      !!!!!““““““““““““““““““““““““““###"..., 102) → 102
      !!!"""""""""""""""""""""""""############$$%%%%%&&&'(4:::::::8:'&&%%%$$$$$####"""""""""!!!!!!!!!
SYS  90990            119'520 write(1, u"      !!!“““““““““““““““““““““““““######"..., 102) → 102
     !!!""""""""""""""""""""""""##########$$$%&&'2''''(())+7::::::1*)(('&%%%%%'&$###"""""""""!!!!!!!!
SYS  90990            121'776 write(1, u"     !!!““““““““““““““““““““““““########"..., 102) → 102
    !!!"""""""""""""""""""""""#######$$$$$$%%&(-:0/+*,::2::::::::::::5:::('''(.+&%$##"""""""""!!!!!!!
SYS  90990            124'768 write(1, u"    !!!“““““““““““““““““““““““#######$$$"..., 102) → 102
   !!""""""""""""""""""""""#####$$$$$$$$$%%%&&(*3:::7:::::::::::::::::::::,::8:1)%$$##""""""""""!!!!!
SYS  90990            128'192 write(1, u"   !!““““““““““““““““““““““#####$$$$$$$$"..., 102) → 102
   !""""""""""""""""""""####$$$$$$$$$$$%%%%&'()*.8::::::::::::::::::::::::::::56&%$$###""""""""""!!!!
SYS  90990            131'472 write(1, u"   !““““““““““““““““““““####$$$$$$$$$$$%"..., 102) → 102
  !!""""""""""""""""####$%%%$$$$$$$$%%%%%&'):8:5:::::::::::::::::::::::::::::0*(&%%$$##""""""""""!!!!
SYS  90990            134'976 write(1, u"  !!““““““““““““““““####$%%%$$$$$$$$%%%%"..., 102) → 102
  !"""""""""""######$$%%(+'&&&&&&&&&&&&&&''),3:::::::::::::::::::::::::::::::::+(()%$###""""""""""!!!
SYS  90990            138'720 write(1, u"  !“““““““““““######$$%%(+‘&&&&&&&&&&&&&"..., 102) → 102
 !"""""""#########$$$$%%)3*()(()4+(('''''(*9::::::::::::::::::::::::::::::::::::::*%$###"""""""""""!!
SYS  90990            178'160 write(1, u" !“““““““#########$$$$%%)3*()(()4+((‘‘‘‘"..., 102) → 102
 !"""##########$$$$$$%%&'(*/:7.13::/:+*))*-:::::::::::::::::::::::::::::::::::::,(&%$####""""""""""!!
SYS  90990            182'704 write(1, u" !“““##########$$$$$$%%&‘(*/:7.13::/:+*)"..., 102) → 102
 ""##########$$$$$$$%&&&()+0:::::::::::2,,0:::::::::::::::::::::::::::::::::::::::&$$####"""""""""""!
SYS  90990            187'472 write(1, u" ““##########$$$$$$$%&&&()+0:::::::::::2"..., 102) → 102
 "#########$$$$$$$%(''((*0:::::::::::::::1::::::::::::::::::::::::::::::::::::::,'%$$#####""""""""""!
SYS  90990            192'432 write(1, u" “#########$$$$$$$%(‘‘((*0::::::::::::::"..., 102) → 102
 ########$%%%%%%&&'(+.,..5::::::::::::::::::::::::::::::::::::::::::::::::::::::'%%$$#####""""""""""!
SYS  90990            197'376 write(1, u" ########$%%%%%%&&‘(+.,..5::::::::::::::"..., 102) → 102
 $$$%%&&(&&'''''(,*+.:::::::::::::::::::::::::::::::::::::::::::::::::::::::::*'&%$$$#####""""""""""!
SYS  90990            202'592 write(1, u" $$$%%&&(&&‘‘‘‘‘(,*+.:::::::::::::::::::"..., 102) → 102
 $$&%%'):)('))((),,,9::::::::::::::::::::::::::::::::::::::::::::::::::::::::,('&%$$$#####""""""""""!
SYS  90990            207'968 write(1, u" $$&%%‘):)(‘))((),,,9:::::::::::::::::::"..., 102) → 102
 ##$$$##$%%%%%%&&&'(*8181::::::::::::::::::::::::::::::::::::::::::::::::::::::*&%$$$#####""""""""""!
SYS  90990            212'960 write(1, u" ##$$$##$%%%%%%&&&‘(*8181:::::::::::::::"..., 102) → 102
 "#########$$$$%%%&(+(()*.:::::::::::::::4:::::::::::::::::::::::::::::::::::::::&%$$#####""""""""""!
SYS  90990            226'656 write(1, u" “#########$$$$%%%&(+(()*.::::::::::::::"..., 102) → 102
 ""##########$$$$$$$%&&'+*-2::::::::::::..4::::::::::::::::::::::::::::::::::::::/&$$####"""""""""""!
SYS  90990            231'424 write(1, u" ““##########$$$$$$$%&&‘+*-2::::::::::::"..., 102) → 102
 """"##########$$$$$$%&&'(*2::4::::::0.**+-:::::::::::::::::::::::::::::::::::::,(&%$####"""""""""""!
SYS  90990            235'968 write(1, u" ““““##########$$$$$$%&&‘(*2::4::::::0.*"..., 102) → 102
 !"""""##########$$$$%%&'-3.-*)*-:+)8(((()*.:::::::::::::::::::::::::::::::::::::,'%$####""""""""""!!
SYS  90990            240'304 write(1, u" !“““““##########$$$$%%&‘-3.-*)*-:+)8((("..., 102) → 102
  !"""""""""#######$$$%%'4''&&&')('&&&&&''(+/::::::::::::::::::::::::::::::::::-5+-%$###""""""""""!!!
SYS  90990            244'336 write(1, u"  !“““““““““#######$$$%%‘4‘‘&&&‘)(‘&&&&&"..., 102) → 102
  !"""""""""""""""####$%&%%%%%%$$$%%%%%&&&')::::::::::::::::::::::::::::::::::.('&%$$###""""""""""!!!
SYS  90990            247'920 write(1, u"  !“““““““““““““““####$%&%%%%%%$$$%%%%%&"..., 102) → 102
   !"""""""""""""""""""###$$$$$$$$$$$$%%%%%&(-*-1:::::::::::::::::::::::::::::/(&%$$###""""""""""!!!!
SYS  90990            262'448 write(1, u"   !“““““““““““““““““““###$$$$$$$$$$$$%%"..., 102) → 102
   !!"""""""""""""""""""""#####$$$$$$$$$%%%%&'(+::::::::::::::::::::::::::0::::,7%$$##""""""""""!!!!!
SYS  90990            265'840 write(1, u"   !!“““““““““““““““““““““#####$$$$$$$$$"..., 102) → 102
    !!"""""""""""""""""""""""#######$$$$$$%%%&*:::4:+-::::::::::::::::::.)):7)+,(%$##""""""""""!!!!!!
SYS  90990            269'040 write(1, u"    !!“““““““““““““““““““““““#######$$$$"..., 102) → 102
    !!!""""""""""""""""""""""""##########$$$%&:)2/)(((+,*+,/::::::/,+))5(&&&&&'+%$##""""""""""!!!!!!!
SYS  90990            271'536 write(1, u"    !!!““““““““““““““““““““““““#########"..., 102) → 102
     !!!!"""""""""""""""""""""""""###########$$%%%%%&&&''),::::::::8('&&%%%%$$$$###"""""""""!!!!!!!!!
SYS  90990            273'568 write(1, u"     !!!!“““““““““““““““““““““““““######"..., 102) → 102
      !!!!""""""""""""""""""""""""""############$$$%%%%&'(+::::::::-(&%%$$$$$#####"""""""""!!!!!!!!!!
SYS  90990            275'376 write(1, u"      !!!!““““““““““““““““““““““““““####"..., 102) → 102
       !!!!!""""""""""""""""""""""""""############$$$$$%%)+2,/:::,**'%$$$$#######""""""""!!!!!!!!!!!!
SYS  90990            277'024 write(1, u"       !!!!!““““““““““““““““““““““““““##"..., 102) → 102
        !!!!!!"""""""""""""""""""""""""""###########$$$$$%&&'),:,)'&%$$$#######""""""""!!!!!!!!!!!!!!
SYS  90990            278'496 write(1, u"        !!!!!!““““““““““““““““““““““““““"..., 102) → 102
         !!!!!!!!""""""""""""""""""""""""""###########$$$$%&'(.,,-*%%$#######"""""""!!!!!!!!!!!!!!!!!
SYS  90990            279'888 write(1, u"         !!!!!!!!“““““““““““““““““““““““"..., 102) → 102
SYS  90990            280'288 exit(0)
SYS  90990            280'560 __cxa_finalize(&10000001d88, 0)
SYS  90990            281'040 _Exit(0)
```
