# Wildcard DNS and SSL on Fly

[Fly](https://fly.io/) makes it surprisingly easy to configure wildcard DNS, such that `anything.your-new-domain.dev` is served by a single Fly application (which can include multiple instances in multiple regions with global load-balancing).

Their documentation is at [SSL for Custom Domains](https://fly.io/docs/app-guides/custom-domains-with-fly). Here's how I set it up.

## Register the domain

I'm using `your-new-domain.dev` in this example, which is not a domain I have registered. `.dev` is interesting here because it requires SSL (or TLS if you want to be pedantic about it).

## Create an application with an IPv4 and IPv6 IP address

First, create an application:

    fly apps create --name your-wildcard-dns-app

Then create both an IPv4 and an IPv6 address for the application:
```
fly ips allocate-v4 -a your-wildcard-dns-app
TYPE ADDRESS      REGION CREATED AT 
v4   37.16.10.138 global 7s ago     

fly ips allocate-v6 -a your-wildcard-dns-app
TYPE ADDRESS             REGION CREATED AT 
v6   2a09:8280:1::1:3e99 global 4s ago     
```
The IPv4 address is so you can serve traffic.

The IPv6 address is needed as part of Fly's scheme to protect against subdomain takeover - see [How CDNs Generate Certificates: A Note About a Related Problem](https://fly.io/blog/how-cdns-generate-certificates/#a-note-about-a-related-problem) for details.

## Configuring DNS

Now setup the following DNS records:
```
your-new-domain.dev   A: 37.16.10.138
your-new-domain.dev   AAAA: 2a09:8280:1::1:3e99
*.your-new-domain.dev CNAME: your-wildcard-dns-app.fly.dev.
```

That `CNAME` record does the real magic here.

## Issue the certificate

You can ask Fly to issue the certificate (which uses LetsEncrypt under the hood) by running this:
```
fly certs create "*.your-new-domain.dev" \
  -a your-wildcard-dns-app
```

## Verifying the certificate

There's one last step: you need ta add an additional DNS record to verify the certificate.

Instructions for doing this can be found at:

    https://fly.io/apps/your-wildcard-dns-app/certificates

Click to view your unverified certificate and you should get a set of information that includes the extra DNS entry you need to add.

It will look something like this:

    _acme-challenge.your-new-domain.dev CNAME your-new-domain.dev.6g0mj.flydns.net.

Add that DNS record, then click the "Check again" button on the certificate screen and your certificate should be verified shortly afterwards.

## Deploy an app

With the certificate in place, you can deploy a Fly app (using regular Fly or the new [Fly Machines](https://fly.io/blog/fly-machines/)). Traffic to any subdomain of your domain, with or without `https://`, will be served by your new application.
