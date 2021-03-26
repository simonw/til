# How to call pip programatically from Python

I needed this for the `datasette install` and `datasette uninstall` commands, see [issue #925](https://github.com/simonw/datasette/issues/925).

My initial attempt at this resulted in weird testing errors ([#928](https://github.com/simonw/datasette/issues/928)) - while investigating them I stumbled across [this comment](https://github.com/pypa/pip/blob/e060970d51c5946beac8447eb95585d83019582d/src/pip/_internal/cli/main.py#L23-L47) in the `pip` source code:

```
# Do not import and use main() directly! Using it directly is actively
# discouraged by pip's maintainers. The name, location and behavior of
# this function is subject to change, so calling it directly is not
# portable across different pip versions.

# In addition, running pip in-process is unsupported and unsafe. This is
# elaborated in detail at
# https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program.
# That document also provides suggestions that should work for nearly
# all users that are considering importing and using main() directly.

# However, we know that certain users will still want to invoke pip
# in-process. If you understand and accept the implications of using pip
# in an unsupported manner, the best approach is to use runpy to avoid
# depending on the exact location of this entry point.

# The following example shows how to use runpy to invoke pip in that
# case:
#
#     sys.argv = ["pip", your, args, here]
#     runpy.run_module("pip", run_name="__main__")
#
# Note that this will exit the process after running, unlike a direct
# call to main. As it is not safe to do any processing after calling
# main, this should not be an issue in practice.
```
So I did that! Here's the working version of my `datasette install` command:
```python
 @cli.command() 
 @click.argument("packages", nargs=-1, required=True) 
 def install(packages): 
     "Install Python packages - e.g. Datasette plugins - into the same environment as Datasette" 
     sys.argv = ["pip", "install"] + list(packages) 
     run_module("pip", run_name="__main__") 
```
And here's how I wrote [a unit test](https://github.com/simonw/datasette/blob/afdeda8216d4d3027f87583ccdbef17ad85022ef/tests/test_cli.py#L114-L124) for it:
```python
@mock.patch("datasette.cli.run_module")
def test_install(run_module):
    runner = CliRunner()
    runner.invoke(cli, ["install", "datasette-mock-plugin", "datasette-mock-plugin2"])
    run_module.assert_called_once_with("pip", run_name="__main__")
    assert sys.argv == [
        "pip",
        "install",
        "datasette-mock-plugin",
        "datasette-mock-plugin2",
    ]
```
