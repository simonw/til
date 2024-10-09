# Upgrading Homebrew and avoiding the failed to verify attestation error

I managed to get my Homebrew installation back into shape today. The first problem I was having is that it complained that macOS Sequoia was unsupported:

```
Warning: You are using macOS 15.
We do not provide support for this pre-release version.
```

It turns out I was on an older Homebrew version. Sequoia support was added [in Homebrew 4.4.0](https://brew.sh/2024/10/01/homebrew-4.4.0/) released on October 1st 2024.

For some reason `brew upgrade` wasn't fetching that new version. I ended up using this recipe [from StackOverflow](https://apple.stackexchange.com/a/277391):

```bash
cd "$(brew --repo)" && git fetch && git reset --hard origin/master && brew update
```

## Failed to verify attestation

Homebrew added [a feature recently](https://github.com/Homebrew/brew/issues/17019) that checks cryptographical "attestations" on downloaded packages. This is implemented via the GitHub `gh` command.

My first problem was that I got this error:

    unknown command "attestation" for "gh"

The solution ([thanks again, StackOverflow](https://stackoverflow.com/questions/78919643/unknown-command-attestation-for-gh)) was to manually upgrade the `gh` package first to get the new command:
```bash
brew upgrade gh
```

Then I ran `brew upgrade` to upgrade everything... which didn't quite work, because I kept running into warnings like this one:

```
==> Verifying attestation for ca-certificates
Warning: Failed to verify attestation. Retrying in 1...
Warning: Failed to verify attestation. Retrying in 3...
Warning: Failed to verify attestation. Retrying in 9...
Warning: Failed to verify attestation. Retrying in 27...
```
I frequently have rate limiting problems with my GitHub account, so my hunch is that these were causing the command to fail.

The fix was to run this instead, using the `HOMEBREW_NO_VERIFY_ATTESTATIONS` environment variable to disable attestation checking entirely:

```bash
HOMEBREW_NO_VERIFY_ATTESTATIONS=1 brew upgrade
```
