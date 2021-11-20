# Assigning a custom subdomain to a Fly app

I deployed an app to [Fly](https://fly.io/) and decided to point a custom subdomain to it.

My fly app is https://datasette-apache-proxy-demo.fly.dev/

I wanted the URL to be https://datasette-apache-proxy-demo.datasette.io/ (see [issue #1524](https://github.com/simonw/datasette/issues/1524)).

Relevant documentation: [SSL for Custom Domains](https://fly.io/docs/app-guides/custom-domains-with-fly/).

## Assign a CNAME

First step was to add a CNAME to my `datasette.io` domain.

I pointed `CNAME` of `datasette-apache-proxy-demo.datasette.io` at `datasette-apache-proxy-demo.fly.dev.` using Vercel DNS:

<img width="586" alt="image" src="https://user-images.githubusercontent.com/9599/142740008-942f180b-bedb-4a44-b6ef-1b0e7fd32416.png">

## Issuing a certificate

Fly started serving from `http://datasette-apache-proxy-demo.datasette.io/` as soon as the DNS change propagated. To get `https://` to work I had to run this:

```
% flyctl certs create datasette-apache-proxy-demo.datasette.io 
Your certificate for datasette-apache-proxy-demo.datasette.io is being issued. Status is Awaiting certificates.
```
I could then run this command periodically to see if it had been issued, which happened about 53 seconds later:
```
apache-proxy % flyctl certs show datasette-apache-proxy-demo.datasette.io
The certificate for datasette-apache-proxy-demo.datasette.io has been issued.

Hostname                  = datasette-apache-proxy-demo.datasette.io

DNS Provider              = constellix

Certificate Authority     = Let's Encrypt

Issued                    = ecdsa,rsa

Added to App              = 53 seconds ago

Source                    = fly
```
