# Recursively fetching metadata for all files in a Google Drive folder

For [google-drive-to-sqlite](https://github.com/simonw/google-drive-to-sqlite) I wanted a mechanism to recursively return metadata on every file in a specified Goole Drive folder.

## Fetching files in a single folder

To fetch files in a single folder with the ID `FOLDER_ID` you need to use this API:

    https://www.googleapis.com/drive/v3/files?q=...

The `q=` parameter needs to be fed the following [special search query](https://developers.google.com/drive/api/v3/search-files):

    "FOLDER_ID" in parents

So the URL for a folder with ID `1E6Zg2X2bjjtPzVfX8YqdXZDCoB3AVA7i` ends up looking like this:

    https://www.googleapis.com/drive/v3/files?q=%221E6Zg2X2bjjtPzVfX8YqdXZDCoB3AVA7i%22%20in%20parents

You need to accompany that with a `Authorization: Bearer YOUR_ACCESS_TOKEN` header - see [Google OAuth for CLI applications](https://til.simonwillison.net/googlecloud/google-oauth-cli-application) for more on that.

## Fetching specific fields

The metadata representation you get back by default is pretty thin.

You can add `&fields=*` to the URL to get back the full JSON representation - but this can actually be a little bit too much data, mainly because it includes a list of every user who has permissions relating to every file.

You can specify individual fields, but it's not instantly obvious how to do so. The syntax turns out to look like this:

    nextPageToken, files(id, kind, name)

Each token corresonds to a key, The `files(id, kind, name)` bit selects the fields you want from items in the `files` array.

The full list of file keys I've been using are:

```json
[
    "kind",
    "id",
    "name",
    "mimeType",
    "starred",
    "trashed",
    "explicitlyTrashed",
    "parents",
    "spaces",
    "version",
    "webViewLink",
    "iconLink",
    "hasThumbnail",
    "thumbnailVersion",
    "viewedByMe",
    "createdTime",
    "modifiedTime",
    "modifiedByMe",
    "owners",
    "lastModifyingUser",
    "shared",
    "ownedByMe",
    "viewersCanCopyContent",
    "copyRequiresWriterPermission",
    "writersCanShare",
    "folderColorRgb",
    "quotaBytesUsed",
    "isAppAuthorized",
    "linkShareMetadata",
]
```

## Recursively fetching from sub-folders

This will get you the files and folders within a folder... but you have to do extra work if you want to recursively fetch files from every sub-folder.

A sub-folder in the response from that API looks like this:

```json
{
    "kind": "drive#file",
    "id": "1ixwEcEUmZ5-RZY2AQrwG-s1rvOF9LtqX",
    "name": "My sub-folder",
    "mimeType": "application/vnd.google-apps.folder"
}
```
So fetching everything involves fetching the contents of a folder, then filtering out anything with a `mimeType` of `application/vnd.google-apps.folder`, extracting the `id` and recursively fetching the contents of that folder too.

You also need to handle pagination, in case a folder contains more than 100 items. That's done using the `nextPageToken` key in the response JSON, which you can then pass as `?pageToken=` to the API to retrieve the next page.

Note that while the Google Drive API implies that a file can live in more than one folder - `parents` is an array of IDs - Google Drive [simplified their model in September 2020](https://cloud.google.com/blog/products/g-suite/simplifying-google-drives-folder-structure-and-sharing-models) such that a file can only be in a single folder.

## Code

Here's [the code I used](https://github.com/simonw/google-drive-to-sqlite/blob/0.1a0/google_drive_to_sqlite/utils.py) to implement recursive fetching of folder contents:

```python
def paginate_files(access_token, *, q=None, fields=None):
    pageToken = None
    files_url = "https://www.googleapis.com/drive/v3/files"
    params = {}
    if fields is not None:
        params["fields"] = "nextPageToken, files({})".format(",".join(fields))
    if q is not None:
        params["q"] = q
    while True:
        if pageToken is not None:
            params["pageToken"] = pageToken
        else:
            params.pop("pageToken", None)
        data = httpx.get(
            files_url,
            params=params,
            headers={"Authorization": "Bearer {}".format(access_token)},
            timeout=30.0,
        ).json()
        if "error" in data:
            raise Exception(data)
        yield from data["files"]
        pageToken = data.get("nextPageToken", None)
        if pageToken is None:
            break


def files_in_folder_recursive(access_token, folder_id, fields):
    for file in paginate_files(
        access_token, q='"{}" in parents'.format(folder_id), fields=fields
    ):
        yield file
        if file["mimeType"] == "application/vnd.google-apps.folder":
            yield from files_in_folder_recursive(access_token, file["id"], fields)
```
