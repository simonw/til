# Relinquishing control in Python asyncio

`asyncio` in Python is a form of co-operative multitasking, where everything runs in a single thread but asynchronous tasks can yield to other tasks to allow them to execute.

Normally you do this with `await` - but I'm thinking through a problem at the moment which could involve long-running asyncio functions. To avoid blocking the event loop, I'd like them to periodically yield to see if there are any other tasks that need to spend some time with the CPU.

This doesn't seem to be covered in the Python `asyncio` documentation, but after some digging I came across this issue in the old `python/asyncio` repo: [Question: How to relinquishing control to the event loop in Python 3.5](https://github.com/python/asyncio/issues/284)

It turns out the supported, optimized idiom is this one:

```python
await asyncio.sleep(0)
```
