# Geocoding from Python on macOS using pyobjc-framework-CoreLocation

Rhet Turnbull [shared](https://twitter.com/RhetTurnbull/status/1883559820541956605) this [short script](https://gist.github.com/RhetTbull/db70c113efd03029c6ff619f4699ce34) for looking up the named timezone for a given location from Python on macOS using `objc` and the `CoreLocation` framework. It uses the `objc` package and [pyobjc-framework-CoreLocation](https://pypi.org/project/pyobjc-framework-CoreLocation/).

This piqued my interest, so I [conversed with Claude](https://gist.github.com/simonw/fed886265bc32af81efa8e7973fea621) about other things I could do with that same framework. Here's the script we came up with, for geocoding an address passed to it using Core Location's `CLGeocoder.geocodeAddressString()` method:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyobjc-core",
#     "pyobjc-framework-CoreLocation",
#     "click"
# ]
# ///
"""Basic geocoding using CoreLocation on macOS."""

import click
import objc
from CoreLocation import CLGeocoder
from Foundation import NSRunLoop, NSDate

def forward_geocode(address: str) -> list[dict]:
    with objc.autorelease_pool():
        geocoder = CLGeocoder.alloc().init()
        results = {"placemarks": [], "error": None}
        completed = False
        
        def completion(placemarks, error):
            nonlocal completed
            if error:
                results["error"] = error.localizedDescription()
            elif placemarks:
                results["placemarks"] = placemarks
            completed = True
            
        geocoder.geocodeAddressString_completionHandler_(address, completion)
        
        while not completed:
            NSRunLoop.currentRunLoop().runMode_beforeDate_(
                "NSDefaultRunLoopMode",
                NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )
        
        if results["error"]:
            raise Exception(f"Geocoding error: {results['error']}")
            
        return [{
            "latitude": pm.location().coordinate().latitude,
            "longitude": pm.location().coordinate().longitude,
            "name": pm.name(),
            "locality": pm.locality(),
            "country": pm.country()
        } for pm in results["placemarks"]]

@click.command()
@click.argument('address')
def main(address):
    try:
        locations = forward_geocode(address)
        for loc in locations:
            click.echo("\nLocation found:")
            for key, value in loc.items():
                if value:
                    click.echo(f"{key}: {value}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()
```
This can be run using `uv run` like this:

```bash
uv run geocode.py '500 Grove St, San Francisco, CA'
```
Example output:
```
Location found:
latitude: 37.777717
longitude: -122.42504
name: 500 Grove St
locality: San Francisco
country: United States 
```
I tried this without a network connection and it failed, demonstrating that Core Location uses some form of network-based API to geocode addresses.

There are a few new-to-me tricks in this script.

`with objc.autorelease_pool()` is a neat [memory management pattern](https://pyobjc.readthedocs.io/en/latest/api/module-objc.html#objc.autorelease_pool) provided by PyObjC for establishing an autorelease memory pool for the duration of a Python `with` block. Everything allocated by Objective C should be automatically cleaned up at the end of that block.

The `geocodeAddressString` method takes a completion handler. In this code we're setting that to a Python function that communicates state using shared variables:

```python
results = {"placemarks": [], "error": None}
completed = False

def completion(placemarks, error):
    nonlocal completed
    if error:
        results["error"] = error.localizedDescription()
    elif placemarks:
        results["placemarks"] = placemarks
    completed = True
```
We start that running like so:
```python
geocoder = CLGeocoder.alloc().init()
geocoder.geocodeAddressString_completionHandler_(address, completion)
```
Then the clever bit:
```python
while not completed:
    NSRunLoop.currentRunLoop().runMode_beforeDate_(
        "NSDefaultRunLoopMode",
        NSDate.dateWithTimeIntervalSinceNow_(0.1)
    )
```
Where did this code come from? It turns out Claude lifted that from the Rhet Turnbull script I fed into it earlier. Here's [that code with Rhet's comments](https://gist.github.com/RhetTbull/db70c113efd03029c6ff619f4699ce34#file-tzname-py-L54-L66):

```python
WAIT_FOR_COMPLETION = 0.01  # wait time for async completion in seconds
# ...

# reverseGeocodeLocation_completionHandler_ is async so run the event loop until completion
# I usually use threading.Event for this type of thing in pyobjc but the the thread blocked forever
waiting = 0
while not completed:
    NSRunLoop.currentRunLoop().runMode_beforeDate_(
        "NSDefaultRunLoopMode",
        NSDate.dateWithTimeIntervalSinceNow_(WAIT_FOR_COMPLETION),
    )
    waiting += WAIT_FOR_COMPLETION
    if waiting >= COMPLETION_TIMEOUT:
        raise TimeoutError(
            f"Timeout waiting for completion of reverseGeocodeLocation_completionHandler_: {waiting} seconds"
        )
```
Is this the best pattern for  my own, simpler script? I don't know for sure, but it works. Approach with caution!

Since my script has inline script dependencies and I've [published it to a Gist](https://gist.github.com/simonw/178ea93ac035293744bde97270d6a7a0) you can run it directly with `uv run` without first installing anything else like this:

```bash
uv run https://gist.githubusercontent.com/simonw/178ea93ac035293744bde97270d6a7a0/raw/88c817e4103034579ec7523d8591bf60aa11fa67/geocode.py \
  '500 Grove St, San Francisco, CA'
```
