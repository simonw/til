# Pointing a custom subdomain at Read the Docs

I host the documentation for Datasette on [Read the Docs](https://readthedocs.org/). Until today it lived at https://datasette.readthedocs.io/ but today I moved it to a custom subdomain, https://docs.datasette.io/

Most of this is handled by the https://readthedocs.org/dashboard/datasette/domains/ interface, but there were a couple of extra details.

## CNAME record

First, I needed to add a `CNAME` record for `docs.datasette.io` pointing to `readthedocs.org.`

It's good to do that in advance of adding the domain to Read the Docs, because when you add the domain they instantly start redirecting traffic from the old `datasette.readthedocs.io` domain to the new custom `docs.datasette.io` domain - even if that domain hasn't finished updating DNS and issuing certificates yet!

When I first tried this I got the following error in the *Read the Docs* interface:

>  SSL certificate status: pending_issuance: caa_error: docs.datasette.io

It turns out this was because my DNS hosting provider, Vercel, had added a `CAA` record to the root `datasette.io` domain restricting which certificate authorities could issue certificates. It was locked down to `letsencrypt.org`, but for the Read the Docs certificate mechanism to work I needed to add two more CAA records.

With the help of Read the Docs support I added these:

- `CAA` for `datasette.io`: `0 issue "comodoca.com"`
- `CAA` for `datasette.io`: `0 issue "digicert.com"`

I confirmed that they were working using `dig CAA +short datasette.io`:

```
~ % dig CAA +short datasette.io
0 issue "letsencrypt.org"
0 issue "digicert.com"
0 issue "comodoca.com"
```

Having done this, I added the domain in the Read the Docs interface once more and this time it worked!
