# Compiling to WASM with llvm on macOS

[howto-wasm-minimal](https://github.com/ern0/howto-wasm-minimal) by Zalka Ernő ([my fork here](https://github.com/simonw/howto-wasm-minimal)) is a neat demo of a minimal WASM module. It uses C++ to define functions for simple image manipulation including blurring an image, compiles it to WASM using llvm/clang++, then uses JavaScript to run those functions against an image loaded into a `<canvas>` element.

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
#wasm-objdump -x inc.wasm
```

## Bonus: Web Assembly Binary Toolkit

The last commented-out line of that script caught my attention:

    wasm-objdump -x inc.wasm

I searched, and `wasm-objdump` is part of the tools provided by the [WebAssembly Binary Toolkit ](https://github.com/WebAssembly/wabt).

You can install that with Homebrew by running `brew install wabt`.

Then this worked:

```
% wasm-objdump -x inc.wasm

inc.wasm:	file format wasm 0x1

Section Details:

Type[4]:
 - type[0] () -> nil
 - type[1] (i32) -> i32
 - type[2] (i32, i32) -> nil
 - type[3] (i32, i32, i32) -> nil
Import[1]:
 - memory[0] pages: initial=2 <- env.memory
Function[7]:
 - func[0] sig=0 <__wasm_call_ctors>
 - func[1] sig=1 <inc>
 - func[2] sig=0 <incmem>
 - func[3] sig=2 <gray>
 - func[4] sig=2 <swaprg>
 - func[5] sig=3 <swap_red>
 - func[6] sig=2 <blur>
Global[7]:
 - global[0] i32 mutable=1 <__stack_pointer> - init i32=66560
 - global[1] i32 mutable=0 <__dso_handle> - init i32=1024
 - global[2] i32 mutable=0 <__data_end> - init i32=1024
 - global[3] i32 mutable=0 <__global_base> - init i32=1024
 - global[4] i32 mutable=0 <__heap_base> - init i32=66560
 - global[5] i32 mutable=0 <__memory_base> - init i32=0
 - global[6] i32 mutable=0 <__table_base> - init i32=1
Export[13]:
 - func[0] <__wasm_call_ctors> -> "__wasm_call_ctors"
 - func[1] <inc> -> "inc"
 - func[2] <incmem> -> "incmem"
 - func[3] <gray> -> "gray"
 - func[4] <swaprg> -> "swaprg"
 - func[5] <swap_red> -> "swap_red"
 - func[6] <blur> -> "blur"
 - global[1] -> "__dso_handle"
 - global[2] -> "__data_end"
 - global[3] -> "__global_base"
 - global[4] -> "__heap_base"
 - global[5] -> "__memory_base"
 - global[6] -> "__table_base"
Code[7]:
 - func[0] size=2 <__wasm_call_ctors>
 - func[1] size=7 <inc>
 - func[2] size=69 <incmem>
 - func[3] size=101 <gray>
 - func[4] size=215 <swaprg>
 - func[5] size=1332 <swap_red>
 - func[6] size=615 <blur>
Custom:
 - name: "name"
 - func[0] <__wasm_call_ctors>
 - func[1] <inc>
 - func[2] <incmem>
 - func[3] <gray>
 - func[4] <swaprg>
 - func[5] <swap_red>
 - func[6] <blur>
 - global[0] <__stack_pointer>
Custom:
 - name: "producers"
```
