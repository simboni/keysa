# KeYSA — Kenya Youths Support Association

The website for keysa.org, served as static files.

## Read this first: these are build outputs, not source

This repository holds the **compiled** site — `index.html`, route folders and
a `_next/` bundle produced by a Next.js static export. There is no
`package.json`, no `src/`, and no `next.config`.

That has one consequence worth understanding before anyone is asked to change
anything: **the content here cannot practically be edited**. The text lives
inside minified HTML and hashed JavaScript chunks. A typo in a programme
description is not a one-line fix; it is an archaeology exercise.

So the first job on this site is not hosting, it is **finding the source
project** — whatever had the `src/` directory and the content files. Until it
turns up, this repo is a snapshot that can be served and nothing more.

## What the site is

Nine routes: about, contact, donate, get-involved, news, programs, projects,
team, plus the home page and a 404.

**Nothing on it stores data.** Every form composes a `mailto:` to
`info@keysa.org` and hands off to the visitor's mail client — the donate and
get-involved pages prefill a message body. There is no database, no form
service, no API. Moving this site moves everything it has.

**No dependency on Netlify.** It was deployed there, but the only trace is the
`_headers` file, which Netlify reads and other servers ignore. Nothing calls a
Netlify function or posts to Netlify Forms, so leaving is a clean break.

## Hosting

Static files behind the shared `edge-caddy` on the Contabo box. See
`deploy/contabo/keysa/` in **simboni/peter-misiati** for the kit.

`www.keysa.org` is canonical: the build writes `https://www.keysa.org` into
its Open Graph, Twitter and JSON-LD metadata, so the apex redirects to www
rather than the other way round. Serving the apex as canonical would leave
every social preview pointing at a URL that redirects.

The security and caching rules in `_headers` do not apply outside Netlify and
have been translated into the Caddy site file: frame-deny, nosniff, a referrer
policy, a permissions policy, and a one-year immutable cache on
`/_next/static/*`. Change them in both places or they drift.
