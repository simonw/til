# Using nginx to proxy to a Unix domain socket

I figured this out while adding `--uds` support to Datasette in [#1388](https://github.com/simonw/datasette/issues/1388). Save the following in `nginx.conf`:

```nginx
daemon off;
events {
  worker_connections  1024;
}
http {
  server {
    listen 8092;
    location / {
      proxy_pass http://datasette;
      proxy_set_header Host $host;
    }
  }
  upstream datasette {
    server unix:/tmp/datasette.sock;
  }
}
```
Start `nginx` against that configuration file - this works without root provided you listen on a high port:

    nginx -c $PWD/nginx.conf

(The `$PWD` seems necessary to avoid `nginx` looking in its default directory.)

Start something listening on the `/tmp/datasette.sock` path - with the latest Datasette you can do this:

    datasette --uds /tmp/datasette.sock

Now hits to `http://localhost:8092/` will proxy through to Datasette.
