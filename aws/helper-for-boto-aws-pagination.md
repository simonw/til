# Helper function for pagination using AWS boto3

I noticed that a lot of my boto3 code in [s3-credentials](https://github.com/simonw/s3-credentials) looked like this:

```python
paginator = iam.get_paginator("list_user_policies")
for response in paginator.paginate(UserName=username):
    for policy_name in response["PolicyNames"]:
        print(policy_name)
```
This was enough verbosity that I was hesitating on implementing pagination properly for some method calls.

I came up with this helper function to use instead:

```python
def paginate(service, method, list_key, **kwargs):
    paginator = service.get_paginator(method)
    for response in paginator.paginate(**kwargs):
        yield from response[list_key]
```
Now the above becomes:
```python
for policy_name in paginate(iam, "list_user_policies", "PolicyNames", UserName=username):
    print(policy_name)
```
Here's [the issue](https://github.com/simonw/s3-credentials/issues/63) and the [refactoring commit](https://github.com/simonw/s3-credentials/commit/fc1e06ca3ffa2c73e196cffe741ef4e950204240).
