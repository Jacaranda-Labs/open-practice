#!/usr/bin/env python3
"""Put the brand's face on the accounts that have a profile API.

Bluesky and Mastodon both accept an avatar, a header and a bio; Discord's webhook has no profile at
all, Nostr has none, and Pinterest's is edited in the app. Running this twice is harmless — it
overwrites the same fields with the same bytes.

    python3 tools/brand_profiles.py [--dry]

Reads OP_BSKY_ID / OP_BSKY_PASS / OP_MASTODON_INSTANCE / OP_MASTODON_TOKEN, and the art from
../open-practice-brand if it is present (falls back to the deployed copies on the site).
"""
import argparse
import json
import os
import sys
import urllib.request
import uuid

SITE = os.environ.get("OP_SITE_URL", "https://open-practice.open-practice.workers.dev").rstrip("/")
KIT = os.environ.get("OP_KIT", os.path.expanduser("~/open-practice-brand"))
BIO = ("Free, practical AI learning. 6 build paths, 86 guided activities, 39 free tools.\n\n"
       "Make something real, then explain where it stops working.\n\n"
       "Independent · non-degree · non-accredited.\n" + SITE)


def art(kit_path: str, fallback: str) -> bytes:
    """Prefer the kit on disk; fall back to the deployed copy on the site."""
    path = os.path.join(KIT, kit_path)
    if os.path.exists(path):
        return open(path, "rb").read()
    req = urllib.request.Request(fallback, headers={"User-Agent": "OpenPracticeDesk/1.0"})
    with urllib.request.urlopen(req, timeout=30) as f:
        return f.read()


def _http(url, data=None, headers=None, method=None):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            return f.status, json.load(f)
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body[:200]


def bluesky(dry: bool) -> str:
    ident, pw = os.environ.get("OP_BSKY_ID"), os.environ.get("OP_BSKY_PASS")
    if not (ident and pw):
        return "skip: OP_BSKY_ID / OP_BSKY_PASS not set"
    st, sess = _http("https://bsky.social/xrpc/com.atproto.server.createSession",
                     json.dumps({"identifier": ident, "password": pw}).encode(),
                     {"Content-Type": "application/json"})
    if st != 200:
        return f"FAIL login {st}"
    auth = {"Authorization": f"Bearer {sess['accessJwt']}"}

    def blob(name, url):
        st, b = _http("https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                      art(name, url), {**auth, "Content-Type": "image/png"})
        return b.get("blob") if st == 200 else None

    if dry:
        return "would set displayName, description, avatar and banner"
    avatar = blob("icons/icon-512.png", f"{SITE}/brand/icon-512.png")
    banner = blob("banners/x-header-1500x500.png", f"{SITE}/brand/x-header-1500x500.png")
    rec = {"$type": "app.bsky.actor.profile", "displayName": "Open Practice", "description": BIO}
    if avatar:
        rec["avatar"] = avatar
    if banner:
        rec["banner"] = banner
    st, b = _http("https://bsky.social/xrpc/com.atproto.repo.putRecord",
                  json.dumps({"repo": sess["did"], "collection": "app.bsky.actor.profile",
                              "rkey": "self", "record": rec}).encode(),
                  {**auth, "Content-Type": "application/json"})
    return "profile set" if st == 200 else f"FAIL putRecord {st}: {str(b)[:120]}"


def mastodon(dry: bool) -> str:
    inst = (os.environ.get("OP_MASTODON_INSTANCE") or "").replace("https://", "").strip("/")
    tok = os.environ.get("OP_MASTODON_TOKEN")
    if not (inst and tok):
        return "skip: OP_MASTODON_INSTANCE / OP_MASTODON_TOKEN not set"
    if dry:
        return "would set display_name, note, avatar and header"
    b = "----op" + uuid.uuid4().hex
    parts = []
    for k, v in {"display_name": "Open Practice", "note": BIO, "bot": "false"}.items():
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for field, kit_path, name in (("avatar", "icons/icon-512.png", "avatar.png"),
                                  ("header", "banners/x-header-1500x500.png", "header.png")):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{field}"; filename="{name}"\r\n'
                     f'Content-Type: image/png\r\n\r\n'.encode()
                     + art(kit_path, f"{SITE}/brand/" + kit_path.split("/")[-1]) + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    st, d = _http(f"https://{inst}/api/v1/accounts/update_credentials", b"".join(parts),
                  {"Authorization": f"Bearer {tok}",
                   "Content-Type": f"multipart/form-data; boundary={b}"}, "PATCH")
    return "profile set" if st == 200 else f"FAIL {st}: {str(d)[:120]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    bad = 0
    for name, fn in (("bluesky", bluesky), ("mastodon", mastodon)):
        out = fn(a.dry)
        print(f"  {name:<9} {out}")
        bad += out.startswith("FAIL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
