# Google OAuth for a CLI application

I had to figure out how to do the OAuth flow while building my [google-drive-to-sqlite](https://github.com/simonw/google-drive-to-sqlite) CLI application - [issue here](https://github.com/simonw/google-drive-to-sqlite/issues/2).

For CLI apps, the flow is that you show the user a URL, they click on it, sign into their Google account, grant your application permission and the Google website then shows them a code. They copy and paste that code back into your application and you can exchange it for an `access_token` and a `refresh_token`. The `access_token` will work for an hour, but you can store the `refresh_token` and use it to obtain a new `access_token` any time you like.

## Setting up the OAuth app

In the Google Cloud console you need to navigate to "APIs and Services", "Credentials", "Create Credentials" and select "OAuth client ID". You need to create a client ID for application type "Desktop app".

![Screenshot of the Google Cloud API key interface](https://raw.githubusercontent.com/simonw/til/main/googlecloud/google-oauth-cli-application-oauth-client-id.png)

Completing this form will give you a `google_client_id` and a `google_client_secret`. Even though it's called a secret it's safe to distribute this in your application and include it in your code in a public GitHub repository. The [Google documentation](https://developers.google.com/identity/protocols/oauth2#installed) says:

> The process results in a client ID and, in some cases, a client secret, which you embed in the source code of your application. (In this context, the client secret is obviously not treated as a secret.)

## Providing an authentication link

The link the user clicks on should look like this (broken into multiple lines for readability):

    https://accounts.google.com/o/oauth2/v2/auth
      ?access_type=offline
      &client_id=YOUR_CLIENT_ID_HERE
      &redirect_uri=urn:ietf:wg:oauth:2.0:oob
      &response_type=code
      &scope=https://www.googleapis.com/auth/drive.readonly

In this case I am using a `scope` of `https://www.googleapis.com/auth/drive.readonly` because I want to access files in the user's Google Drive - you'll need to hunt around in the documentation to figure out which scope you need.

Here's a live demo link for my `google-drive-to-sqlite` application:

https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&client_id=148933860554-98i3hter1bsn24sa6fcq1tcrhcrujrnl.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly

Once the user completes that flow, they will be given a code to copy and paste. When they give you that code you can exchange it for tokens using this API (illustrated with Python):

```python
copied_code = '4/1A...'

import httpx
response = httpx.post("https://www.googleapis.com/oauth2/v4/token", data={
    "code": copied_code,
    "client_id": google_client_id,
    "client_secret": google_client_secret,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "authorization_code",
})
tokens = response.json()
```
The `tokens` variable is now a Python dictionary with `access_token` and `refresh_token` keys.

## Making authenticated calls

You can use the `access_key` straight away for calls like this one:

```python
response = httpx.get("https://www.googleapis.com/drive/v3/files", headers={
    "Authorization": "Bearer {}".format(access_key)
})
print(response.json())
```

## Exchanging a refresh_token for an access_token

Here's my code for exchanging the `refresh_token` for a new `access_token`:

```python
data = httpx.post(
    "https://www.googleapis.com/oauth2/v4/token",
    data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
    },
).json()
if "error" in data:
    raise click.ClickException(str(data))
return data["access_token"]
```
## The rest of my code

Most of my code that handles this can be found in the [cli.py module](https://github.com/simonw/google-drive-to-sqlite/blob/9377505af30366d57adafd1aa7846a2a6f4e990a/google_drive_to_sqlite/cli.py) in `google-drive-to-sqlite`.
