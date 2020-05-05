# Use setup.py to install platform-specific dependencies

For [photos-to-sqlite](https://github.com/dogsheep/photos-to-sqlite) I needed to install `osxphotos` as a dependency, but only if the platform is macOS - it's not available for Linux.

Here's the magic incantation to do that:

```python
setup(
    name="photos-to-sqlite",
    ...
    install_requires=[
        "sqlite-utils>=2.7",
        "boto3>=1.12.41",
        "osxphotos>=0.28.13 ; sys_platform=='darwin'",
    ]
)
```
So ` ; sys_platform=='darwin'` in the install requires line.

More details: https://www.python.org/dev/peps/pep-0508/#environment-markers and https://hynek.me/articles/conditional-python-dependencies/
