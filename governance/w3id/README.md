# w3id.org registration for TOP

TOP's canonical namespace is `https://w3id.org/top/` (see
[RFC-0001](../rfcs/proposed/0001-namespace-migration-w3id.md)). `w3id.org` is a
community-run permanent-identifier redirector (the W3C Permanent Identifier Community
Group); it holds no content and simply redirects to wherever TOP is hosted.

## Why the config lives here

`top/.htaccess` is the redirect rule that makes `w3id.org/top/**` resolve. The upstream
copy lives in `perma-id/w3id.org`, but the **source of truth is here**, version-controlled
with the ontology it serves.

## To register (one-time) or update

1. Set `the-ontology-project.org` in [`top/.htaccess`](top/.htaccess) to the live hosting domain.
2. Copy it to `top/.htaccess` in a pull request against
   [`perma-id/w3id.org`](https://github.com/perma-id/w3id.org). Their CONTRIBUTING asks
   for a short description and a maintainer contact.
3. Once merged, `https://w3id.org/top/...` resolves to the host. Verify with:
   `curl -sIL -H 'Accept: text/turtle' https://w3id.org/top/core/v1`.

## Order of operations (from RFC-0001)

Register w3id **and** stand up `the-ontology-project.org` **before** rewriting the ontology's IRIs —
never rewrite first, or resolution breaks in the gap.
