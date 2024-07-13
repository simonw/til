# Trying out free-threaded Python on macOS

Inspired by [py-free-threading.github.io](https://py-free-threading.github.io/) I decided to try out a beta of Python 3.13 with the new free-threaded mode enabled, which removes the GIL.

## Installation

I chose to use the macOS installer to get a pre-built binary. I downloaded and ran the macOS installer from [www.python.org/downloads/release/python-3130b3/](https://www.python.org/downloads/release/python-3130b3/), and then when I got to this screen:

![Installation dialog with a Customize button at the bottom](https://github.com/user-attachments/assets/7e57d8f1-6a4b-4551-babd-127317dff5cd)

I selected the "Customize" option and checked this additional box:

![Customize screen - I have checked the Free-threaded Python (experimental) option](https://github.com/user-attachments/assets/5aa8d4dd-5c70-493e-a183-2f0799079830)

Once it had finished installing I didn't run the script to add it to my path (I didn't want to intefere with my many other Python versions).

This gave me two new Python binaries - one with free-threading enabled and one without:

- `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13`
- `/Library/Frameworks/PythonT.framework/Versions/3.13/bin/python3.13t`

Note the `PythonT.framework` in the second path.

It also seemed to setup the following aliases in `/usr/local/bin`:

- `/usr/local/bin/python3.13`
- `/usr/local/bin/python3.13t`

These are symlinks:
```bash
ls -lah /usr/local/bin | grep python3.13
```
```
lrwxr-xr-x   1 root  wheel    73B Jul 12 16:26 python3.13 -> ../../../Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
lrwxr-xr-x   1 root  wheel    80B Jul 12 16:26 python3.13-config -> ../../../Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13-config
lrwxr-xr-x   1 root  wheel    81B Jul 12 16:26 python3.13-intel64 -> ../../../Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13-intel64
lrwxr-xr-x   1 root  wheel    75B Jul 12 16:26 python3.13t -> ../../../Library/Frameworks/PythonT.framework/Versions/3.13/bin/python3.13t
lrwxr-xr-x   1 root  wheel    82B Jul 12 16:26 python3.13t-config -> ../../../Library/Frameworks/PythonT.framework/Versions/3.13/bin/python3.13t-config
```

Starting those Python processes shows which one has free-threading in the interpreter header:
```
% /usr/local/bin/python3.13
Python 3.13.0b3 (v3.13.0b3:7b413952e8, Jun 27 2024, 09:57:31) [Clang 15.0.0 (clang-1500.3.9.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
% /usr/local/bin/python3.13t
Python 3.13.0b3 experimental free-threading build (v3.13.0b3:7b413952e8, Jun 27 2024, 10:04:51) [Clang 15.0.0 (clang-1500.3.9.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

## Testing it out

I asked Claude 3.5 Sonnet to write me [a quick test script](https://gist.github.com/simonw/21b1e208b81f10731798f11da0af775d), then iterated on and simplified the result myself until I got to this:

```python
import argparse
import time
from concurrent.futures import ThreadPoolExecutor


def cpu_bound_task(n):
    """A CPU-bound task that computes the sum of squares up to n."""
    return sum(i * i for i in range(n))


def main():
    parser = argparse.ArgumentParser(description="Run a CPU-bound task with threads")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks")
    parser.add_argument(
        "--size", type=int, default=5000000, help="Task size (n for sum of squares)"
    )
    args = parser.parse_args()

    print(f"Running {args.tasks} tasks of size {args.size} with {args.threads} threads")

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        list(executor.map(cpu_bound_task, [args.tasks] * args.size))
    end_time = time.time()
    duration = end_time - start_time

    print(f"Time with threads: {duration:.2f} seconds")


if __name__ == "__main__":
    main()
```
I saved this as `gildemo.py` and tried running it with the new Python binaries the one with free-threading enabled and the one without.

**IMPORTANT: This code has a bug, explained below.

Here's what I saw in Activity Monitor while running the scripts:

No free-threading (with the GIL) - reported 99% CPU usage:

![Activity Monitor window showing a Python process using 99.2% CPU with 5 threads. Terminal visible above running a script: "Running 10 tasks of size 10000000 with 4 threads"](https://github.com/user-attachments/assets/686e2dcd-daff-4cfe-ba1e-c4aa38b0a10a)

Free-threading (no GIL) - reported 258.8% CPU usage:

![Activity Monitor window showing a PythonT process using 258.8% CPU with 5 threads. Terminal visible above running a script: "Running 10 tasks of size 10000000 with 4 threads".](https://github.com/user-attachments/assets/e7b8d291-a8a1-4e98-a73f-880403e14e8c)

And here are some results from running the script (invalid due to the bug described below).

First with the GIL in place:
```
% python3.13 gildemo.py --size 1000000 
Running 10 tasks of size 1000000 with 4 threads
Time with threads: 17.14 seconds
```
And then without the GIL:
```
% python3.13t gildemo.py --size 1000000 
Running 10 tasks of size 1000000 with 4 threads
Time with threads: 8.19 seconds
```
## Fixing an embarrassing bug

Bartek Ogryczak [spotted a bug](https://twitter.com/var_tec/status/1811928300840976662) in the code above:

> I was wondering with only 2x improvement with 4 threads, and seems like the the code is off:
>
> `map(cpu_bound_task, [args.tasks] * args.size)`
>
> ought to be
>
> `map(cpu_bound_task, [args.size] * args.tasks)`

I had to think a bit about this. The `executor.map()` method takes two arguments - the function to be run in the thread, and a list of arguments where each argument will be passed to a separate invocation of that function.

`tasks` is the number of times to run the function in the test. `size` controls the complexity of that function (the sum of squares up to that number).

Running `[x] * 5` produces `[x, x, x, x, x]` - the list duplicated by that constant.

So Bartek is right! Consider this invocation:

```bash
python3.13t gildemo.py --size 10000000 --threads 4 --tasks 10
```
That should run `sum(i * i for i in range(10000000))` 10 times in four different threads. But, thanks to the bug in the code, it actually runs `sum(i * i for i in range(10))` 10000000 times in four threads!

The original mistake here came from Claude, but I'm responsible for it - I broke the cardinal rule of LLM-assisted programming, which is to closely review every line of code it produces.

After applying Bartek's fix I get these results with free-threading (no GIL):
```
% python3.13t gildemo.py --size 10000000 --threads 4
Running 10 tasks of size 10000000 with 4 threads
Time with threads: 1.38 seconds
% python3.13t gildemo.py --size 10000000 --threads 8
Running 10 tasks of size 10000000 with 8 threads
Time with threads: 1.10 seconds
% python3.13t gildemo.py --size 10000000 --threads 12
Running 10 tasks of size 10000000 with 12 threads
Time with threads: 1.00 seconds
```
And these results with the GIL in place:
```
% python3.13 gildemo.py --size 10000000 --threads 4 
Running 10 tasks of size 10000000 with 4 threads
Time with threads: 4.01 seconds
% python3.13 gildemo.py --size 10000000 --threads 8
Running 10 tasks of size 10000000 with 8 threads
Time with threads: 4.03 seconds
% python3.13 gildemo.py --size 10000000 --threads 12 
Running 10 tasks of size 10000000 with 12 threads
Time with threads: 3.92 seconds
```
