# Downloading archived Git repositories from archive.softwareheritage.org

Last February I [blogged about](https://simonwillison.net/2025/Feb/7/sqlite-s3vfs/) a neat script called `sqlite-s3vfs` which was released as MIT licensed open source by the UK government's Department for Business and Trade.

I went looking for it today and found that the [github.com/uktrade/sqlite-s3vfs](https://github.com/uktrade/sqlite-s3vfs) repository is now a 404.

Since this is taxpayer-funded software and was released MIT I felt a moral obligation to try and restore the repository!

My restored copy can be found at [github.com/simonw/sqlite-s3vfs](https://github.com/simonw/sqlite-s3vfs). Here's how I made it.

Claude suggested trying the [Software Heritage archive](https://archive.softwareheritage.org/) and sure enough a search for `https://github.com/uktrade/sqlite-s3vfs` on their site resolved to [this archived page](https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://github.com/uktrade/sqlite-s3vfs), which appeared to have a full copy of the repo.

Downloading a snapshot of the most recent state was easy enough, but I wanted the full Git history. I stumbled across [this Hacker News comment](https://news.ycombinator.com/item?id=37516523#37517378) which helped me figure out the right way to do this.

Software Heritage have all sorts of different IDs. The ID that worked for me was something they call a "snapshot ID". I found this in their "Permalinks" sidebar under the "snapshot" tag:

![Screenshot of Software Heritage archive page for https://github.com/uktrade/sqlite-s3vfs showing visit type: git, dated 12 April 2025, 15:35:23 UTC. Navigation tabs include Code, Branches (38), Releases (0), and Visits. Branch: HEAD is selected with commit 8e0f4b6. A red "Permalinks" sidebar is expanded showing instructions: "To reference or cite the objects present in the Software Heritage archive, permalinks based on SoftWare Hash IDentifiers (SWHIDs) must be used. Select below a type of object currently browsed in order to display its associated SWHID and permalink." Three options shown: directory, revision, and snapshot (selected). The SWHID displayed is "swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf;origin=https://github.com/uktrade/sqlite-s3vfs" with a checked "Add contextual information" checkbox and buttons for "Copy identifier" and "Copy permalink".](https://github.com/user-attachments/assets/8fa16a43-d52e-4fc7-8d94-0a291e7bd04b)

It started `swh:1:snp:` - the ID for this repository was:

    swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf

You can then make an API call to request a Git bundle for that snapshot:

```bash
curl -XPOST 'https://archive.softwareheritage.org/api/1/vault/git-bare/swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf/'
```
This returned JSON that looks like this:

```json
{
  "fetch_url": "https://archive.softwareheritage.org/api/1/vault/git-bare/swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf/raw/",
  "progress_message": null,
  "id": 417949633,
  "status": "done",
  "swhid": "swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf"
}
```
That `fetch_url` is what you need to download the Git bundle as a `.tar.gz` file. It redirects to blob storage so you need to use `-L` with `curl`:

```bash
curl -L -o bundle.tar.gz 'https://archive.softwareheritage.org/api/1/vault/git-bare/swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf/raw/'
```
Then decompress it:
```bash
tar -xzvf bundle.tar.gz
```
The result starts like this:
```
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/HEAD
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/branches/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/config
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/description
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/hooks/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/info/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/info/exclude
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/info/refs
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/info/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/info/packs
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/pack/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/pack/pack-9946e5e52f40fd1df3352da074f9ac059e87ca9d.idx
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/objects/pack/pack-9946e5e52f40fd1df3352da074f9ac059e87ca9d.pack
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/github_actions/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/github_actions/dot-github/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/github_actions/dot-github/workflows/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/github_actions/dot-github/workflows/actions/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/dependabot/github_actions/dot-github/workflows/actions/download-artifact-4.1.7
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/heads/main
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/pull/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/pull/11/
x swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git/refs/pull/11/head
...
```
That `swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git` is a bare Git repository. You can clone it into a usable working copy like this:

```bash
git clone swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git sqlite-s3vfs
```
I created an empty repo on GitHub and ran these commands to push everything up:

```bash
cd sqlite-s3vfs
git remote set-url origin git@github.com:simonw/sqlite-s3vfs.git
git push --all origin
git push --tags origin
```
I had to use `set-url` because the original origin was that `/tmp/swh:1:snp:1930ecd7bcc8c8666c721c4def3944c98d650abf.git` local path.

## Building an HTML tool to make this easier in the future

It turns out all of the relevant APIs are unauthenticated and support CORS headers, so I had Claude Code build me a page for automating part of this process in the future:

https://tools.simonwillison.net/software-heritage-repo

Here's that tool with the old GitHub repo URL pre-filled, just click the button:

https://tools.simonwillison.net/software-heritage-repo#https%3A%2F%2Fgithub.com%2Fuktrade%2Fsqlite-s3vfs

And here's [the Claude Code transcript](https://gistpreview.github.io/?3a76a868095c989d159c226b7622b092/index.html) I used to build this.
