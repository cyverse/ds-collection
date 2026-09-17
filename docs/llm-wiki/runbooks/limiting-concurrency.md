---
type: Runbook
title: Limiting Concurrent Connections per User
description: A worked HAProxy example that caps each iRODS user's total concurrent connections across direct iRODS and WebDAV access, by extracting the client identity from the iRODS startup packet and the HTTP Basic auth header into a shared stick table.
resource: /docs/limiting-concurrency.md
tags: [haproxy, concurrency, irods, webdav, stick-table, proxy]
timestamp: 2026-09-17T00:00:00Z
---

This is an example of limiting each user's total number of connections to
several services with HAProxy — here, iRODS and a WebDAV service in front of
iRODS. It is illustrative configuration, not something a playbook in this
collection deploys. For the proxy the collection does deploy, see
[HAProxy Proxy](/components/haproxy-proxy.md).

The original doc notes that CyVerse does not currently limit concurrent
connections per user, but plans to; it currently limits concurrent
connections per IP address, and only for iRODS.

## Example setup

- One HAProxy server, `data.example.org`, proxies for one iRODS catalog
  service provider and one WebDAV server, limiting each client to `5`
  connections in total.
- The provider (`10.0.0.1`) hosts no storage resources, allows `200`
  concurrent connections, uses zone port `1247/tcp` and reconnection ports
  `20000-20199/tcp`, and serves zone `tempZone`, possibly federated.
- WebDAV (`10.0.1.1`) is Apache with davrods, listening for plain HTTP on
  `80/tcp`; the proxy terminates TLS with `/etc/ssl/private/example.org.pem`.

## Unlimited starting point

Each service gets a combined `listen` block. Each backend is capped at `100`
connections. Because WebDAV itself connects to iRODS, capping WebDAV at 100
leaves at least 100 of the provider's 200 connections for direct iRODS
connections.

```haproxy
listen irods
   mode    tcp
   bind    :1247,:20000-20199
   server  csp 10.0.0.1 maxconn 100

listen webdav
   mode    http
   bind    :443 ssl crt /etc/ssl/private/example.org.pem
   server  dav 10.0.1.1 port 80 maxconn 100
```

## Shared tracking

A client identity is `<account>#<zone>`. Account and zone names are each at
most 250 characters in the ICAT schema, so an identity is at most 501
characters. The stick table therefore uses string keys of length `600`, and
since at most 100 iRODS and 100 WebDAV connections exist at once, it
allocates `300` entries. It sits in its own backend so both services can share
it. An ACL rejects a client whose tracked connection count exceeds `5`, using
the `sc1` counter.

```haproxy
backend concurrency_st
   stick-table  type string len 600 size 300 store conn_cur
```

```haproxy
acl  too-many-conn sc1_conn_cur gt 5
```

## iRODS: identity from the startup packet

An iRODS connection begins with a four-byte length, a `MsgHeader_PI` XML
element, and a `StartupPack_PI` element whose `clientUser` and
`clientRcatZone` children hold the account and authentication zone. The proxy:

1. Waits up to `5s` for request content (`tcp-request inspect-delay`), so it
   never waits indefinitely for lost data.
2. Captures the user and zone by skipping the first four bytes
   (`req.payload(4,0)`) and trimming the text around each element with
   `regsub`, limiting each capture to 250 characters. Captures land in
   `capture.req.hdr(0)` and `capture.req.hdr(1)` in order.
3. Builds `sess.id` as `user#zone`, tracks it in `concurrency_st` with `sc1`,
   and rejects the connection when `too-many-conn` holds.

```haproxy
listen irods
   mode                       tcp
   bind                       :1247,:20000-20199
   server                     irods 10.0.0.1 maxconn 100
   acl                        too-many-conn sc1_conn_cur gt 5
   tcp-request inspect-delay  5s
   tcp-request content        capture req.payload(4,0),regsub([\s\S]*<StartupPack_PI\s*>[\s\S]*<clientUser\s*>,),regsub(</clientUser\s*>[\s\S]*,) len 250
   tcp-request content        capture req.payload(4,0),regsub([\s\S]*<StartupPack_PI\s*>[\s\S]*<clientRcatZone\s*>,),regsub(</clientRcatZone\s*>[\s\S]*,) len 250
   tcp-request content        set-var(sess.user) capture.req.hdr(0)
   tcp-request content        set-var(sess.zone) capture.req.hdr(1)
   tcp-request content        set-var(sess.id) var(sess.user),concat(\#,sess.zone,)
   tcp-request content        track-sc1 var(sess.id) table concurrency_st
   tcp-request content        reject if too-many-conn
```

## WebDAV: identity from Basic auth

davrods uses HTTP Basic authentication and only serves the local zone, so the
zone is assumed to be `tempZone`. The `Authorization` value is
`Basic <base64 of user:password>`; with a 250-character user name and a
password under 250 characters, the header value is at most 674 characters,
so it is captured with length `700`. The proxy strips `Basic `, decodes base64,
removes `:<password>`, appends `#tempZone`, and tracks and rejects as for
iRODS.

```haproxy
listen webdav
   mode                    http
   bind                    :443 ssl crt /etc/ssl/private/example.org.pem
   server                  dav 10.0.1.1 port 80 maxconn 100
   acl                     too-many-conn sc1_conn_cur gt 5
   capture request header  Authorization len 700
   http-request            set-var(sess.name) capture.req.hdr(0),regsub(^Basic\ ,),b64dec,regsub(:.*$,)
   http-request            set-var(sess.id) var(sess.name),concat(\#tempZone,,)
   http-request            track-sc1 var(sess.id) table concurrency_st
   http-request            reject if too-many-conn
```

## Complete configuration

The original doc ends with a full `haproxy.cfg` that adds `global` settings
(daemon, chroot `/var/lib/haproxy`, `maxconn 400`, logging to
`127.0.0.1 local0`) and `defaults` (`maxconn 200`, `option tcplog`) around the
`concurrency_st` backend and the two `listen` blocks above. Its version
differs from the step-by-step blocks in two ways: the WebDAV `listen` uses the
certificate `/etc/ssl/private/cyverse.rocks.pem`, and it builds `sess.id` in a
single step with `regsub(:.*$,\#tempZone)` instead of the separate `sess.name`
variable and `concat`. See `docs/limiting-concurrency.md` for the full file.

# Citations

[1] `docs/limiting-concurrency.md` — the original worked example and complete `haproxy.cfg`.
