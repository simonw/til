# Installing flash-attn without compiling it

If you ever run into instructions that tell you to do this:
```bash
pip install flash-attn --no-build-isolation
```
**Do not try to do this**. It is a trap. For some reason attempting to install this runs a compilation process which can take _multiple hours_. I tried to run this in Google Colab on an A100 machine that I was paying for and burned through $2 worth of "compute units" and an hour and a half of waiting before I gave up.

Thankfully [I learned](https://twitter.com/Sampson4242/status/1849666226299281443) that there's an alternative: the Flash Attention team provide pre-built wheels for their project exclusively through GitHub releases. They're not uploaded to PyPI, possibly because they're 180MB each or maybe because PyPI can't automatically pick the correct torch version?

Whatever the reason, you can find them attached to the most recent release on https://github.com/Dao-AILab/flash-attention/releases

But which one should you use out of the 83 files listed there?

Google Colab has a "ask Gemini" feature so I tried "Give me as many clues as possible as to what flash attention wheel filename would work on this system" and it suggested I look for a `cp310` one (for Python 3.10) on `linux_x86_64` (Colab runs on Linux).

In browsing through the list of 83 options I thought `flash_attn-2.6.3+cu123torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl` might be the right one (shrug?). So I tried this:
```
!wget https://github.com/Dao-AILab/flash-attention/releases/download/v2.6.3/flash_attn-2.6.3+cu123torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
!pip install --no-dependencies --upgrade flash_attn-2.6.3+cu123torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
```
This _seemed_ to work (and installed in just a couple of seconds):
```python
import flash_attn
flash_attn.__version__
```
```
2.6.3
```
But the thing I was trying to run ([deepseek-ai/Janus](https://github.com/deepseek-ai/Janus)) failed with an error:

> `NameError: name '_flash_supports_window_size' is not defined`

At this point I gave up. It's possible I picked the wrong wheel, but there may have been something else wrong.

