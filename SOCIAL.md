# The company accounts

Six rails, one identity: **Open Practice**. Every credential below was verified by reading the
account back, and each rail has already published a post from this repository.

| rail | account | how it posts |
|---|---|---|
| Bluesky | `@open-practice.bsky.social` | app password → `createSession` → `createRecord` |
| Mastodon | `@open_si_practice@mastodon.social` | bearer token → `POST /api/v1/statuses` |
| Nostr | `npub13ststv2dt7h92k6ztad2eq2u2lt9jc5pcs5z24n6369z0ayfuy5qk4h` | secp256k1 + BIP-340 schnorr over websocket |
| Discord | webhook "Captain Hook", channel `1569043887899811942` | webhook, `wait=true` so the message id comes back |
| Pinterest | `pinterest.com/open_si_practice/open-si-practice` | Buffer GraphQL `createPost`, `mode: shareNow` |
| Tumblr | `open-si-practice.tumblr.com` | OAuth 1.0a, `POST /v2/blog/{blog}/post` (singular route, form-encoded) |

## Commands

```bash
python3 tools/social.py armed          # which rails this process can post to
python3 tools/social.py verify         # read back every identity; exits 1 if one is dead
python3 tools/social.py post --text "…" --link https://open-practice.open-practice.workers.dev/
python3 tools/social.py post --rails nostr --text "…" --dry
python3 -m unittest discover -s tools/tests -p "test_social.py"     # 23 tests, no network
```

## Pinterest goes through Buffer

Pinterest has no usable posting API for a normal account, so the pin is published by Buffer, which
holds the channel. One `createPost` mutation against `https://api.buffer.com`, bearer auth.

- IDs on this account: organization `6af0c533ee908366fa79e503`, Pinterest channel
  `6af0c57162b70b94b0c2a2c1`, board `open-si-practice` serviceId `253327616479060842`.
- Every pin carries an image (`brand/card-activities.png`, served from the site — 200, image/png).
  A text-only pin renders as a broken card.
- Read a pin back without a browser: `https://www.pinterest.com/open_si_practice/open-si-practice.rss`.
- The legacy `api.bufferapp.com/1/...` API is dead (401). Bearer against `api.buffer.com` only.
- GraphQL variables must match Buffer's scalar type names (`OrganizationId!`, not `String!`), so IDs
  are inlined as string literals.

## Relays

Measured this session: `relay.damus.io`, `relay.primal.net` and `relay.nostr.net` accept in about a
second. `nos.lol`, `relay.nostr.band` and `nostr.mom` time out. Override with `OP_NOSTR_RELAYS`.

## Tumblr

The app (`B0MJj96…`, secret `PvHfQJM0…`) was authorised for the blog `open-si-practice` (primary, the
only blog on that account). The handshake is three steps and only the middle one needs a human:

```bash
export OP_TUMBLR_CK=… OP_TUMBLR_CS=…
python3 tools/tumblr_connect.py link                  # prints an authorize URL
# sign in as the blog, approve, then paste the callback URL back:
python3 tools/tumblr_connect.py exchange "<callback url>"
```

The request-token secret is written to `~/.op_tumblr_pending.json` (0600) because an OAuth 1.0a
exchange needs both halves and the secret is issued exactly once. It is kept separate from the
Mechanism Audit pending file so the two desks cannot clobber each other.

Text posts carry a `title`: Tumblr themes render it above the body, and the first line is usually
the better title. `/v2/blog/{blog}/post` (singular, form-encoded) returns 201; the plural `/posts`
route is NPF and wants a JSON content array.

**Blog title and description:** `POST /v2/blog/{blog}/settings` returns 400 `Bad Request` for every
payload tried, so the display title is still the slug `open-si-practice`. That is a dashboard edit,
not an API one.

## Not armed, and why
- **Reddit (`u/open_ai_practice`), Quora (`Open_Si_Practice`), Medium (`Open_Si_Practice`)** —
  passwords only; none has a posting API worth using. Copy-paste lanes, copy is in
  `open-practice-social-pack.md`.
- **Facebook, Instagram, Threads, YouTube, TikTok, GBP** — empty cells in the workbook. Connecting any
  of them to the same Buffer account turns it into a one-line addition here, no new code.

## Secrets

Repo secrets (15): `OP_BSKY_ID`, `OP_BSKY_PASS`, `OP_MASTODON_INSTANCE`, `OP_MASTODON_TOKEN`,
`OP_NOSTR_NSEC`, `OP_DISCORD_WEBHOOK`, `OP_BUFFER_TOKEN`, `OP_PINTEREST_BOARD`, `OP_TUMBLR_CK`,
`OP_TUMBLR_CS`, `OP_TUMBLR_TOKEN`, `OP_TUMBLR_TOKEN_SECRET`, `OP_TUMBLR_BLOG`,
`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.

`.github/workflows/social.yml` verifies daily at 06:41 UTC and posts on dispatch.
