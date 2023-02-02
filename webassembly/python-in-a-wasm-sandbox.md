# Run Python code in a WebAssembly sandbox

I've been trying to figure this out for ages. Tim Bart responded to [my call for help on Hacker News](https://news.ycombinator.com/item?id=34598024) with [this extremely useful code example](https://gist.github.com/pims/711549577759ad1341f1a90860f1f3a5) showing how to run Python code in WebAssembly inside Python, using [wasmtime-py](https://github.com/bytecodealliance/wasmtime-py) and the new Python WASM build [released by VMware Wasm Labs](https://wasmlabs.dev/articles/python-wasm32-wasi/).

First step is to download the VMWare build:

```
cd /tmp
mkdir wasm
cd wasm
wget https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/python%2F3.11.1%2B20230118-f23f3f3/python-aio-3.11.1.zip
unzip python-aio-3.11.1.zip
```
Create a virtual environment and install `wasmtime`:
```
python3 -m venv venv
source venv/bin/activate
pip install wasmtime
```

Here's my version of Tim's code, slightly modified to provide a `run_python_code()` function:

```python
from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig
import os
import tempfile


class Result:
    def __init__(self, result, mem_size, data_len, consumed):
        self.result = result
        self.mem_size = mem_size
        self.data_len = data_len
        self.consumed = consumed

    def __str__(self):
        return f"""\
result:

{self.result}

mem size pages of 64kb: {self.mem_size}
data length: {self.data_len}
fuel consumed: {self.consumed}
"""


def run_python_code(code, fuel=400_000_000):
    engine_cfg = Config()
    engine_cfg.consume_fuel = True
    engine_cfg.cache = True

    linker = Linker(Engine(engine_cfg))
    linker.define_wasi()

    python_module = Module.from_file(linker.engine, "bin/python-3.11.1.wasm")

    config = WasiConfig()

    config.argv = ("python", "-c", code)
    config.preopen_dir(".", "/")

    with tempfile.TemporaryDirectory() as chroot:
        out_log = os.path.join(chroot, "out.log")
        err_log = os.path.join(chroot, "err.log")
        config.stdout_file = out_log
        config.stderr_file = err_log

        store = Store(linker.engine)

        # Limits how many instructions can be executed:
        store.add_fuel(fuel)
        store.set_wasi(config)
        instance = linker.instantiate(store, python_module)

        # _start is the default wasi main function
        start = instance.exports(store)["_start"]

        mem = instance.exports(store)["memory"]

        try:
            start(store)
        except Exception as e:
            print(e)
            raise

        with open(out_log) as f:
            result = f.read()

        return Result(
            result, mem.size(store), mem.data_len(store), store.fuel_consumed()
        )


if __name__ == "__main__":
    for code in (
        "print('hello world')",
        "for i in range(10000): print('hello world')",
        "print('hello world')",
        "for i in range(100000): print('hello world')",
    ):
        try:
            print(code)
            print("====")
            print(run_python_code(code))
        except Exception as e:
            print(e)
```
Running this produces the following output (truncated), which illustrates what happens to things that run out of "fuel" (which I set to default to 400,000,000 units):
```
wasmtime % pipenv run python demo.py 
print('hello world')
====
result:

hello world


mem size pages of 64kb: 160
data length: 10485760
fuel consumed: 230790953

for i in range(10000): print('hello world')
====
error while executing at wasm backtrace:
    0: 0xb02e6 - <unknown>!<wasm function 1505>
    1: 0xb2967 - <unknown>!<wasm function 1536>
    2: 0x1b9221 - <unknown>!<wasm function 3563>
    3: 0x1ae61a - <unknown>!<wasm function 3558>
    4: 0x49be2a - <unknown>!<wasm function 10123>
note: using the `WASMTIME_BACKTRACE_DETAILS=1` environment variable may show more debugging information

Caused by:
    wasm trap: all fuel consumed by WebAssembly
error while executing at wasm backtrace:
    0: 0xb02e6 - <unknown>!<wasm function 1505>
    1: 0xb2967 - <unknown>!<wasm function 1536>
    2: 0x1b9221 - <unknown>!<wasm function 3563>
    3: 0x1ae61a - <unknown>!<wasm function 3558>
    4: 0x49be2a - <unknown>!<wasm function 10123>
note: using the `WASMTIME_BACKTRACE_DETAILS=1` environment variable may show more debugging information

Caused by:
    wasm trap: all fuel consumed by WebAssembly
print('hello world')
====
result:

hello world


mem size pages of 64kb: 160
data length: 10485760
fuel consumed: 230794521

for i in range(100000): print('hello world')
====
error while executing at wasm backtrace:
    0: 0x7d7f - <unknown>!<wasm function 72>
...
   17: 0x1c52e9 - <unknown>!<wasm function 3618>
   18: 0x49b7c9 - <unknown>!<wasm function 10123>
note: using the `WASMTIME_BACKTRACE_DETAILS=1` environment variable may show more debugging information

Caused by:
    wasm trap: all fuel consumed by WebAssembly
error while executing at wasm backtrace:
    0: 0x7d7f - <unknown>!<wasm function 72>
...
   16: 0x1c53c2 - <unknown>!<wasm function 3619>
   17: 0x1c52e9 - <unknown>!<wasm function 3618>
   18: 0x49b7c9 - <unknown>!<wasm function 10123>
note: using the `WASMTIME_BACKTRACE_DETAILS=1` environment variable may show more debugging information

Caused by:
    wasm trap: all fuel consumed by WebAssembly
```
