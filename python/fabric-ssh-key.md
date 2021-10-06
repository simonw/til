# Using Fabric with an SSH public key

Inspired by [this tweet](https://twitter.com/driscollis/status/1445772718507376646) by Mike Driscoll I decided to try using Fabric to run commands over SSH from a Python script, using a public key for authentication.

This worked:

```python
from fabric import Connection

c = Connection(
    host="my-server.simonwillison.net",
    user="root",
    connect_kwargs={
        "key_filename": "/path/to/id_rsa.pub",
    },
)
output = c.run("pwd && ls -lah")
# This outputs to the console but also lets me retrieve the result like so:
string_output = output.stdout
```

Mike's Tweet recipe looks like this:
```python
with Connection(f"{username}@{host}:{port}", connect_kwargs={"password: "pw"}) as conn:
    output = conn.run("docker images")
    print(output.stdout)
```
