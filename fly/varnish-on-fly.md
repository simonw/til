# Running Varnish on Fly

The goal: run [Varnish](https://varnish-cache.org/) in a [Fly](https://fly.io/) container as a caching proxy in front of another Fly application.

I ended up switching to Cloudflare for running a Varnish-style cache in front of my Fly application (purely to reduce the number of moving parts I needed to maintain), but I'm publishing my notes on how I got Varnish working here in case I need them in the future.

## The Dockerfile

Fly apps run Docker containers. Here's the minimal `Dockerfile` that worked for me:
```dockerfile
FROM varnish

COPY default.vcl /etc/varnish/

USER varnish

ENTRYPOINT [ \
    "varnishd", "-F", \
    "-f", "/etc/varnish/default.vcl", \
    "-a", "http=:8000,HTTP", \
    "-s", "malloc,256M", \
    "-T", "none" \
]
```

## default.vcl

The `default.vcl` file is the Varnish configuration file. Here's the one I used:
```vcl
vcl 4.1;

backend default {
  .host = "my-underlying-app.fly.dev";
  .port = "80";
}

sub vcl_recv {
    unset req.http.x-cache;
}

sub vcl_hit {
    set req.http.x-cache = "hit";
}

sub vcl_miss {
    set req.http.x-cache = "miss";
}

sub vcl_pass {
    set req.http.x-cache = "pass";
}

sub vcl_pipe {
    set req.http.x-cache = "pipe uncacheable";
}

sub vcl_synth {
    set req.http.x-cache = "synth synth";
    set resp.http.x-cache = req.http.x-cache;
}

sub vcl_deliver {
    if (obj.uncacheable) {
        set req.http.x-cache = req.http.x-cache + " uncacheable" ;
    } else {
        set req.http.x-cache = req.http.x-cache + " cached" ;
    }
    set resp.http.x-cache = req.http.x-cache;
}
```
## fly.toml

The Fly configuration file for the application:
```toml
app = "my-varnish-app"
primary_region = "lax"
kill_signal = "SIGINT"
kill_timeout = "5s"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    interval = 10000
    timeout = 2000
    grace_period = "10s"
```
I'm using `internal_port = 8000` here because I ran Varnish using `-a "http=:8000,HTTP"` in the `ENTRYPOINT` in the `Dockerfile`.

## Deploying the application

With all of the above files in a folder, the deploy command looks like this:

```bash
flyctl deploy
```

The result ends up running at `https://my-varnish-app.fly.dev/`, and will serve pages from the underlying app - only caching them if those pages include a `cache-control: s-maxage=15` header or similar.

## Further reading

I pieced this together mainly with help from the information in [this 4 year old forum thread](https://community.fly.io/t/running-varnish-on-fly/82), plus searching around for more recent Varnish configuration examples.
