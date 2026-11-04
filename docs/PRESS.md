# Open Practice press

One practice activity a day, posted on Open Practice's own accounts, every post carrying a card drawn by the shared
media engine (the same engine as DeskOS and Tapstall), in the Open Practice brand.

- **Code:** `scripts/press/press.py` (compose, rails, run), `mediakit.py` + `brand.json` + `logo.png` + `fonts/` (the
  engine), `make_cards.py` (pre-renders `apps/web/public/brand/press/<activity>-{wide,square,pin}.png`), `oauth1.py`
  (Tumblr signing and one-time authorisation), `test_press.py`.
- **Schedule:** `.github/workflows/press.yml`, daily 13:35 UTC, ~1 billable minute. Kill switch: repo variable `OP_PRESS=off`.
- **Choice:** by date, all 50 activities in order, then round again. Links carry `?src=<rail>`, counted by the growth API.
- **Cadence:** Bluesky, Mastodon, Nostr, Discord daily; Facebook and Tumblr Mon-Fri; Pinterest Mon/Wed/Fri; Blogger Tue/Thu/Sat.
- **Guard:** today's posts are kept in the Actions cache (`.press-state`), so a re-run never posts twice (`force` overrides).
- **Images:** wide (Bluesky, Discord, Blogger), square (Mastodon, Nostr, Facebook, Tumblr), pin (Pinterest). A missing
  card is drawn on the spot and the activity's own cover is used as the public URL: no post goes out without an image.
- **New or edited activities:** `python3 scripts/press/make_cards.py`, commit, deploy.

## Accounts (GitHub secrets / variables on king-kunta-cpu/open-practice)

| rail | secrets | variables |
|---|---|---|
| Bluesky | `OP_BSKY_ID`, `OP_BSKY_PASS` (app password) | |
| Mastodon | `OP_MASTODON_TOKEN` (scope write:statuses write:media) | `OP_MASTODON_INSTANCE` (default mastodon.social) |
| Nostr | `OP_NOSTR_NSEC` | |
| Discord | `OP_DISCORD_WEBHOOK` | |
| Facebook / Pinterest | `OP_BUFFER_KEY` (Buffer API key, channels connected in Buffer) | `OP_PINBOARD` (board id) |
| Tumblr | `OP_TUMBLR_CONSUMER_KEY`, `OP_TUMBLR_CONSUMER_SECRET`, `OP_TUMBLR_TOKEN`, `OP_TUMBLR_TOKEN_SECRET` | `OP_TUMBLR_BLOG` |
| Blogger | `OP_BLOGGER_EMAIL` (post-by-email address), `OP_SMTP_USER`, `OP_SMTP_PASS` (Gmail app password) | |

A rail with no secret shows "waiting for account" in the run summary and sends nothing.
