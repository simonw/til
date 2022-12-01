# Workaround for google-github-actions/setup-gcloud errors

I used the [google-github-actions/setup-gcloud](https://github.com/google-github-actions/setup-gcloud) action in all of my GitHub Actions workflows that deploy applications to Cloud Run.

The pattern I used to use looked like this:

```yaml
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Set up Cloud Run
      uses: google-github-actions/setup-gcloud@v0
      with:
        version: '275.0.0'
        service_account_email: ${{ secrets.GCP_SA_EMAIL }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    - name: Deploy to Cloud Run
      run: |-
        gcloud config set run/region us-central1
        gcloud config set project datasette-222320
        datasette publish cloudrun content.db --service my-service
```
At some point around the 30th November 2022 this pattern started to fail with errors that looked like this:
```
Error: google-github-actions/setup-gcloud failed with: failed to execute command `gcloud --quiet auth activate-service-account *** --key-file -`: /opt/hostedtoolcache/gcloud/275.0.0/x64/lib/googlecloudsdk/core/console/console_io.py:544: SyntaxWarning: "is" with a literal. Did you mean "=="?
  if answer is None or (answer is '' and default is not None):
ERROR: gcloud failed to load: module 'collections' has no attribute 'MutableMapping'
    gcloud_main = _import_gcloud_main()
    import googlecloudsdk.gcloud_main
    from googlecloudsdk.api_lib.iamcredentials import util as iamcred_util
    from googlecloudsdk.api_lib.util import exceptions
    from googlecloudsdk.core.resource import resource_printer
    from googlecloudsdk.core.resource import config_printer
    from googlecloudsdk.core.resource import resource_printer_base
    from googlecloudsdk.core.resource import resource_projector
    from google.protobuf import json_format as protobuf_encoding
    from google.protobuf import symbol_database
    from google.protobuf import message_factory
    from google.protobuf import reflection
    from google.protobuf.internal import python_message as message_impl
    from google.protobuf.internal import containers
    MutableMapping = collections.MutableMapping

This usually indicates corruption in your gcloud installation or problems with your Python interpreter.

Please verify that the following is the path to a working Python 2.7 executable:
    /opt/hostedtoolcache/Python/3.10.8/x64/bin/python

If it is not, please set the CLOUDSDK_PYTHON environment variable to point to a working Python 2.7 executable.

If you are still experiencing problems, please reinstall the Cloud SDK using the instructions here:
    https://cloud.google.com/sdk/
```
After some frustrating trial-and-error, I found that a workaround which is currently effective for some reason (on 1st December 2022) is to downgrade the Python version to 3.9 and increase the `version` field to `318.0.0`.

## Maybe upgrade to google-github-actions/setup-gcloud@v1 ?

In  writing this up I noticed that I'm still using `v0` of the action, but `v1` is now available.

It looks like `v1` works with Python 3.11! And doesn't need that `version: '275.0.0'` bit either.

This may be a good solution for you.

It doesn't work for me yet though. I tried upgrading that instead, but got this error when running my `datasette publish cloudrun` script:

```
Updated property [run/region].
Updated property [core/project].
ERROR: (gcloud.builds.submit) You do not currently have an active account selected.
Please run:

  $ gcloud auth login

to obtain new credentials.
```
So I'm sticking with `v0` until I have time to figure that problem out too.

## My related issues

- https://github.com/simonw/datasette/issues/1923
- https://github.com/simonw/datasette.io/issues/127
