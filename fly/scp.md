# How to scp files to and from Fly

I have a Fly instance with a 20GB volume, and I wanted to copy files to and from the instance from my computer using `scp`.

Here's the process that worked for me.

1. Connect to Fly's WireGuard network. Fly have [step by step instructions](https://fly.io/docs/reference/private-networking/#step-by-step) for this - you need to install a WireGuard app (I used the [official WireGuard macOS app](https://www.wireguard.com/install/)) and use the `fly wireguard create` command to configure it.
2. Generate 24 hour limited SSH credentials for your Fly organization: Run `fly ssh issue`, follow the prompt to select your organization and then tell it where to put the credentials. I saved them to `/tmp/fly` since they will only work for 24 hours.
3. Find the IPv6 private address for the instance you want to connect to. My instance is in the `laion-aesthetic` application so I did this by running: `fly ips private -a laion-aesthetic`
4. If the image you used to build the instance doesn't have `scp` installed you'll need to install it. On Ubuntu or Debian machines you can do that by attaching using `fly ssh console -a name-of-app` and then running `apt-get update && install openssh-client -y`. Any time you restart the container you'll have to run this step again, so if you're going to do it often you should instead update the image you are using to include this package.
6. Run the `scp` like this: `scp -i /tmp/fly root@\[fdaa:0:4ef:a7b:ad0:1:9c23:2\]:/data/data.db /tmp` - note how the IPv6 address is enclosed in `\[...\]`.
