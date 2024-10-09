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

## Developer mode

After publishing this I got [this tip from Homebrew team member @yossarian](https://infosec.exchange/@yossarian/113278362201612512):

> you’re getting attestations by default probably because you have developer mode enabled; those kind of rate limiting issues are why it isn’t in GA yet

I must have turned developer mode on years ago and forgot about it! Here's [the documentation](https://docs.brew.sh/Manpage#developer-subcommand) - to check the mode run:

```bash
brew developer
```
I got this:
```
Developer mode is enabled.
```
To turn it off:
```bash
brew developer off
```
Then confirm:
```bash
brew developer
```
```
Developer mode is disabled.
```
I believe the challenges I had in this TIL can be explained by developer mode.

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
