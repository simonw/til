# Quick and dirty mock testing with mock_calls

I needed to write a test that checked for a really complex sequence of mock calls for [s3-credentials#3](https://github.com/simonw/s3-credentials/issues/3).

I ended up using the following trick:

```python
def test_create(mocker):
    boto3 = mocker.patch("boto3.client")
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["create", "pytest-bucket-simonw-1", "-c"])
        assert [str(c) for c in boto3.mock_calls] == [
            "call('s3')",
            "call('iam')",
            "call().head_bucket(Bucket='pytest-bucket-simonw-1')",
            "call().get_user(UserName='s3.read-write.pytest-bucket-simonw-1')",
            'call().put_user_policy(PolicyDocument=\'{"Version": "2012-10-17", "Statement": [{"Sid": "ListObjectsInBucket", "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::pytest-bucket-simonw-1"]}, {"Sid": "AllObjectActions", "Effect": "Allow", "Action": "s3:*Object", "Resource": ["arn:aws:s3:::pytest-bucket-simonw-1/*"]}]}\', PolicyName=\'s3.read-write.pytest-bucket-simonw-1\', UserName=\'s3.read-write.pytest-bucket-simonw-1\')',
            "call().create_access_key(UserName='s3.read-write.pytest-bucket-simonw-1')",
            "call().create_access_key().__getitem__('AccessKey')",
            "call().create_access_key().__getitem__().__str__()",
        ]
```
I used the trick I describe in [How to cheat at unit tests with pytest and Black](https://simonwillison.net/2020/Feb/11/cheating-at-unit-tests-pytest-black/) where I run that comparison against an empty `[]` list, then use `pytest --pdb` to drop into a debugger and copy and paste the output of `[str(c) for c in boto3.mock_calls]` into my test code.

Initially I used a comparison directly against `boto3.mock_calls` - but this threw a surprising error. The calls sequence I baked into my tests looked like this:

```python
from unittest.mock import call

# ...

        assert boto3.mock_calls == [
            call("s3"),
            call("iam"),
            call().head_bucket(Bucket="pytest-bucket-simonw-1"),
            call().get_user(UserName="s3.read-write.pytest-bucket-simonw-1"),
            call().put_user_policy(
                PolicyDocument='{"Version": "2012-10-17", "Statement": [{"Sid": "ListObjectsInBucket", "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::pytest-bucket-simonw-1"]}, {"Sid": "AllObjectActions", "Effect": "Allow", "Action": "s3:*Object", "Resource": ["arn:aws:s3:::pytest-bucket-simonw-1/*"]}]}',
                PolicyName="s3.read-write.pytest-bucket-simonw-1",
                UserName="s3.read-write.pytest-bucket-simonw-1",
            ),
            call().create_access_key(UserName="s3.read-write.pytest-bucket-simonw-1"),
            call().create_access_key().__getitem__("AccessKey"),
            call().create_access_key().__getitem__().__str__(),
        ]
```
But when I ran `pytest` that last one failed:
```
E             -  'call().create_access_key().__getitem__()',
E             ?  -                                        ^
E             +  call().create_access_key().__getitem__().__str__(),
E             ?                                          ^^^^^^^^^^
```
It turns out `__str__()` calls do not play well with the `call()` constructor - see [this StackOverflow question](https://stackoverflow.com/questions/61926147/how-to-represent-unittest-mock-call-str).

My solution was to cast them all to `str()` using a list comprehension, which ended up fixing that problem.

## Gotcha: parameter ordering

There's one major flaw to the `str()` trick I'm using here: the order in which parameters are displayed in the string representation of `call()` may differ between Python versions. I had to undo this trick in one place I was using it ([see here](https://github.com/simonw/s3-credentials/issues/8)) as a result due to the following test failure:

```
E  At index 4 diff:
     "call().get_user_policy(PolicyName='policy-one', UserName='one')"
  != "call().get_user_policy(UserName='one', PolicyName='policy-one')"
```
