# Compiling to WASM with llvm on macOS

https://github.com/ern0/howto-wasm-minimal ([my fork here](https://github.com/simonw/howto-wasm-minimal)) is a neat demo of a minimal WASM module. It uses C++ to define functions for simple image manipulation including blurring an image, compiles it to WASM using llvm/clang++, then uses JavaScript to run those functions against an image loaded into a `<canvas>` element.

I decided to try compiling it myself:

```
cd /tmp
git clone https://github.com/ern0/howto-wasm-minimal
cd howto-wasm-minimal
./build.sh
```
This gave me the following error:
```
error: unable to create target: 'No available targets are compatible with triple "wasm32"'
```
Searching for the error lead me to [this comment](https://github.com/WebAssembly/wasi-sdk/issues/172#issuecomment-772399153):

> You need to install `llvm` from `Homebrew`. Xcode's `clang` doesn't have support for WebAssembly.

So I installed `llvm` from Homebrew:

```
% brew install llvm
...
To use the bundled libc++ please add the following LDFLAGS:
  LDFLAGS="-L/usr/local/opt/llvm/lib -Wl,-rpath,/usr/local/opt/llvm/lib"

llvm is keg-only, which means it was not symlinked into /usr/local,
because macOS already provides this software and installing another version in
parallel can cause all kinds of trouble.

If you need to have llvm first in your PATH, run:
  echo 'export PATH="/usr/local/opt/llvm/bin:$PATH"' >> ~/.zshrc

For compilers to find llvm you may need to set:
  export LDFLAGS="-L/usr/local/opt/llvm/lib"
  export CPPFLAGS="-I/usr/local/opt/llvm/include"
...
```
I've quoted the relevant output. I'm not ready to permanently replace the system ``llvm`` with the one from Homebrew, so I ran the build script like this instead:
```
% PATH="/usr/local/opt/llvm/bin:$PATH" ./build.sh 
0000000 00 61 73 6d 01 00 00 00 01 14 04 60 00 00 60 01
```
That created a `inc.wasm` file in my current folder.

I tried opening `index.html` in Firefox and got the following error:

> Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at file:///private/tmp/howto-wasm-minimal/inc.wasm. (Reason: CORS request not http).

So I ran a localhost web server instead using this Python one-liner:
```
% python3 -m http.server 8004
Serving HTTP on :: port 8004 (http://[::]:8004/) ...
```
This worked! http://localhost:8004/ displayed the working demo:

<img width="655" alt="A blurry picture of a car" src="https://user-images.githubusercontent.com/9599/160464900-c4c964ac-b825-4a49-b381-e17da3543187.png">

For reference, here's that `build.sh` script in full:

```bash
#!/bin/bash
set -e

clang++ \
	--target=wasm32 \
	-nostdlib \
	-O3 \
	-Wl,--no-entry \
	-Wl,--export-all \
	-Wl,--lto-O3 \
	-Wl,--allow-undefined \
	-Wl,--import-memory \
	-o inc.wasm \
	inc.cpp

hexdump inc.wasm | head -n 1
```
