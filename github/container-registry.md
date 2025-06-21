# Publishing a Docker container for Microsoft Edit to the GitHub Container Registry

Microsoft recently [released Edit](https://devblogs.microsoft.com/commandline/edit-is-now-open-source/), a new terminal text editor written in Rust. It's pretty nice - it's reminiscent of `nano` but with a retro MS DOS feel.

I wanted to run it on my Apple Silicon Mac. Microsoft don't (yet) provide compiled builds for that platform, but they do have [a release](https://github.com/microsoft/edit/releases/tag/v1.2.0) for `aarch64-linux-gnu`. I figured I'd run that in o Docker container (I have [Docker for Desktop](https://www.docker.com/products/docker-desktop/) installed) to try it out.

One thing lead to another and I ended up creating and shipping a new Docker image to GitHub's Container Registry. This means anyone with an Apple Silicon Mac and Docker can try out `edit` against the files in their current directory by running this command:

```bash
docker run --platform linux/arm64 -it --rm -v $(pwd):/workspace ghcr.io/simonw/alpine-edit
```
Hit `Ctrl+Q` or use your mouse to acces `File -> Exit` to exit the editor and terminate the container.

<img width="679" alt="Screenshot of the Edit text editor showing the File menu" src="https://github.com/user-attachments/assets/1c61a41e-4e84-4983-a7cf-1341c4206bf5" />

I did almost _all_ of my figuring out for this project in [this 25 minute Claude Conversation](https://claude.ai/share/5f0e6547-a3e9-4252-98d0-56f3141c3694). This post is the edited highlights of what I learned.

## Running it first as a one-liner

I started by figuring out a shell one-liner for running the binary. This took a few tries - it turned out Microsoft's compiled binary needed `glibc` and my first choice of base image, `alpine`, used `musl` instead.

I got it working using an Ubuntu base image like this:
```bash
docker run --platform linux/arm64 -it --rm \
  -v $(pwd):/workspace \
  -w /workspace ubuntu:latest sh -c "
    apt update && \
    apt install -y zstd curl && \
    curl -L https://github.com/microsoft/edit/releases/download/v1.2.0/edit-1.2.0-aarch64-linux-gnu.tar.zst -o edit.tar.zst && \
    zstd -d edit.tar.zst && \
    tar -xf edit.tar && \
    chmod +x edit && \
    exec bash"
```
Running this command drops you into Bash in the container - running `./edit` then opens the editor.

I managed to get Alpine working too by having it install the `gcompat` package:

```bash
docker run --platform linux/arm64 -it --rm \
  -v $(pwd):/workspace \
  -w /workspace alpine:latest sh -c "
    apk add --no-cache zstd curl gcompat && \
    curl -L https://github.com/microsoft/edit/releases/download/v1.2.0/edit-1.2.0-aarch64-linux-gnu.tar.zst -o edit.tar.zst && \
    zstd -d edit.tar.zst && \
    tar -xf edit.tar && \
    chmod +x edit && \
    exec sh"
```
Both  of these examples take a little while to start as they download a bunch of extra packages every time. I decided to build a reusable image instead.

## A multi-stage Docker build

I decided to use Alpine with the `gcompat` package as it's smaller than using Ubuntu. I told Claude to use a multi-stage build because I didn't want the `zstd` and `curl` binaries in the final image, just the `edit` binary itself.

Here's what we got to:

```dockerfile
# Build stage - download and extract the binary
FROM alpine:latest AS builder

# Install tools needed for download/extraction
RUN apk add --no-cache zstd curl

# Download and extract the edit binary
RUN curl -L https://github.com/microsoft/edit/releases/download/v1.2.0/edit-1.2.0-aarch64-linux-gnu.tar.zst -o /tmp/edit.tar.zst \
    && zstd -d /tmp/edit.tar.zst \
    && tar -xf /tmp/edit.tar -C /tmp/ \
    && chmod +x /tmp/edit

# Final runtime stage - minimal image
FROM alpine:latest

# Install only runtime dependencies
RUN apk add --no-cache \
    gcompat \
    libgcc \
    && rm -rf /var/cache/apk/*

# Copy the binary from build stage
COPY --from=builder /tmp/edit /usr/local/bin/edit

# Set working directory
WORKDIR /workspace

# Set the edit binary as the entrypoint
ENTRYPOINT ["/usr/local/bin/edit"]

# Default to current directory if no args provided
CMD ["."]
```
This has the added bonus that it uses `/usr/local/bin/edit` as the entrypoint, which means just starting the container will drop you directly into the editor.

I built it like this:

```bash
docker build --platform linux/arm64 -t alpine-edit .
```
And then tested it with this command:

```bash
docker run --platform linux/arm64 -it --rm -v $(pwd):/workspace alpine-edit
```

## Publishing to the GitHub Container Registry

GitHub offer a [free container registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) that can be used to distribute Docker images. I've never tried that before, so this felt like a good opportunity to learn how to use it.

First I needed a GitHub Personal Access Token (PAT) with the right permissions to publish to the registry.

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) - [this page here](https://github.com/settings/tokens/new)
2. Create a new token with these scopes:
   - `write:packages`
   - `read:packages`

I logged into the GitHub Container Registry using this command:

```bash
docker login ghcr.io -u simonw --password-stdin
```
I pasted in the token, then hit enter (and nothing happened), then hit `Ctrl+D` to finish the login. That seemed to work.

I built the image again with a tag for the GitHub Container Registry:

```bash
docker build --platform linux/arm64 -t ghcr.io/simonw/alpine-edit:latest .
```
Then pushed it to the registry with this command:

```bash
docker push ghcr.io/simonw/alpine-edit:latest
```
The published package become available at [github.com/users/simonw/packages/container/package/alpine-edit](https://github.com/users/simonw/packages/container/package/alpine-edit) - that page defaulted to private but I clicked on "Package settings" and toggled the visibility to "Public".

Final step: I created an accompanying repository at [github.com/simonw/alpine-edit](https://github.com/simonw/alpine-edit) with the `Dockerfile` and a `README.md` explaining how to use it, then used the "Connect Repository" button on the package page to link the two together.
