# Pausing traffic and retrying in Caddy

A pattern I really like for zero-downtime deploys is the ability to "pause" HTTP traffic at the load balancer, such that incoming requests from browsers appear to take a few extra seconds to return, but under the hood they've actually been held in a queue while a backend server is swapped out or upgraded in some way.

I first heard about this pattern [from Braintree](https://simonwillison.net/2011/Jun/30/braintree/), and a [conversation on Twitter](https://twitter.com/simonw/status/1463652411365494791) today brought up a few more examples, including [this NGINX Lua config](https://github.com/basecamp/intermission) from Basecamp.

[Caddy](https://caddyserver.com/) creator Matt Holt [pointed me](https://twitter.com/mholt6/status/1463656086360051714) to [lb_try_duration and lb_try_interval](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#lb_try_duration) in Caddy, which can hold requests for up to a specific number of seconds, retrying the backend to see if it has become available again.

I decided to try this out. This was my first time using Caddy and I'm really impressed with both the design of the software and the quality of the [getting started documentation](https://caddyserver.com/docs/getting-started).

## The Caddyfile

You can configure Caddy in a bunch of different ways - the two main options are using JSON via the Caddy API or using their own custom Caddyfile format.

Here's the `Caddyfile` I created:

```
{
    auto_https off
}
:80 {
    reverse_proxy localhost:8003 {
        lb_try_duration 30s
        lb_try_interval 1s
    }
}
```
Caddy defaults to `https`, even on `localhost`, which is very cool but not what I wanted for this demo - hence the first block.

The next block listens on port 80 and proxies to `localhost:8003` - with a 30s duration during which incoming requests will "pause" if the backend is not available, and a polling interval of 1s.

## Running Caddy

I started Caddy in the same directory as my `Caddyfile` using:

    caddy run

Then I hit `http://localhost/` in my browser. The browser hung, waiting for the response.

Then I started [Datasette](https://datasette.io/) on port 8003 like this:

    datasette -p 8003

And about a second later my browser returned a response showing the Datasette homepage!

Quitting and restarting Datasette while executing new requests confirmed that traffic was being paused while the backend was unavailable.

## Trying to reconfigure the proxy

My second experiment didn't work, sadly. I wanted to see if I could reconfigure the backend to use `localhost:8004` instead, and then reload Caddy such that paused traffic would resume against the new backend.

I edited the `Caddyfile` to use port `8004` and ran this to hot-reload the configuration:

    caddy reload

New requests did indeed get served from the new backend, but sadly requests that I had already started (and were paused awaiting the backend) did not automatically get served from the new backend - I had to hit refresh in my browser instead.

I [filed a Caddy issue](https://github.com/caddyserver/caddy/issues/4442) about this.
