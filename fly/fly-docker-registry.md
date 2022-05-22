# Using the Fly Docker registry

[Fly.io](https://fly.io/) lets you deploy Docker containers that will be compiled as a Firecracker VM and run in locations around the world.

Fly offer [a number of ways](https://fly.io/docs/reference/builders/) to build and deploy apps. For many frameworks you can run `fly launch` and it will detect the framework and configure a container for you. For others you can pass it a `Dockerfile` which will be built and deployed. But you can also push your own images to a Docker registry and deploy them to Fly.

Today I figured out how to use Fly's own registry to deploy an app.

## Tagging images for the Fly registry

Fly's registry is called `registry.fly.io`. To use it, you need to tag your Docker images with a tag that begins with that string.

Every Fly app gets its own registry subdomain. You can create apps in a number of ways, but the easiest is to use the Fly CLI:

    flyctl apps create datasette-demo

Fly app names must be globally unique across all of Fly - you will get an error if the app name is already taken.

You can create an app with a random, freely available name using the `--generate-name` option:

```
~ % flyctl apps create --generate-name
? Select Organization: Simon Willison (personal)
New app created: rough-dew-1296
```

Now that you have an app name, you can tag your Docker image using:

    registry.fly.io/your-app-name:unique-tag-for-your-image

If you are building an image using Docker on your machine, you can run this command in the same directory as your `Dockerfile`:

    docker build -t registry.fly.io/datasette-demo:datasette-demo-v0 .

## Pushing images to the registry

In order to push your image to Fly, you will first need to [authenticate](https://fly.io/docs/flyctl/auth-docker/).

The `flyctl auth docker` command will do this for you:
```
~ % flyctl auth docker
Authentication successful. You can now tag and push images to registry.fly.io/{your-app}
```
This works by hooking into Docker's own authentication mechanism. You can see what it has done by looking at your `~/.docker/config.json` file. Mine looks like this:

```json
{
  "auths": {
    "registry.fly.io": {
      "auth": "... secret token here ..."
    }
  ,
  "experimental": "disabled",
  "stackOrchestrator": "swarm"
}
```
Now you can push your image to the registry like this:

    docker push registry.fly.io/datasette-demo:datasette-demo-v0

## Deploying an image

Now that your image is pushed, you can deploy an instance of it like this:

    flyctl deploy --app datasette-demo \
      --image registry.fly.io/datasette-demo:datasette-demo-v0

A few seconds later your app will be running at:

    https://name-of-your-app.fly.dev/
