#!/usr/bin/env python3
"""OAuth 1.0a (HMAC-SHA1) for the Tumblr rail, stdlib only, plus the one-time authorisation helper.

  python3 press/oauth1.py tumblr-start  <state-file>          prints the link to open while logged in as the blog owner
  python3 press/oauth1.py tumblr-finish <state-file> <url>    paste the address you were sent back to; prints the tokens

Needs OP_TUMBLR_CONSUMER_KEY / OP_TUMBLR_CONSUMER_SECRET in the environment. The state file holds the
temporary request-token secret: keep it outside the repo. The printed access token and secret become the GitHub
secrets OP_TUMBLR_TOKEN / OP_TUMBLR_TOKEN_SECRET; they do not expire until the app is revoked on Tumblr.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TUMBLR = "https://www.tumblr.com/oauth"
# Set the app's "Default callback URL" (tumblr.com/oauth/apps) to https://open-practice.zlnew.workers.dev/: the
# Worker keeps the verifier in D1 settings (tumblr_oauth_return), so nobody has to copy an address by hand.
# No oauth_callback: Tumblr only allows the callback registered on the app, and sends the user back there with
# ?oauth_token=...&oauth_verifier=... in the address. The page itself may not load; the address is all we need.


def q(s) -> str:
    return urllib.parse.quote(str(s), safe="~-._")


def signature(method: str, url: str, params: dict, consumer_secret: str, token_secret: str = "") -> str:
    base = "&".join([method.upper(), q(url), q("&".join(f"{q(k)}={q(v)}" for k, v in sorted((str(k), str(v)) for k, v in params.items())))])
    key = f"{q(consumer_secret)}&{q(token_secret)}"
    return base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()


def auth_header(method: str, url: str, form: dict, ck: str, cs: str, token: str = "", ts: str = "", extra: dict | None = None,
                nonce: str | None = None, timestamp: str | None = None) -> str:
    oa = {"oauth_consumer_key": ck, "oauth_nonce": nonce or secrets.token_hex(16), "oauth_signature_method": "HMAC-SHA1",
          "oauth_timestamp": timestamp or str(int(time.time())), "oauth_version": "1.0", **(extra or {})}
    if token:
        oa["oauth_token"] = token
    oa["oauth_signature"] = signature(method, url, {**form, **oa}, cs, ts)
    return "OAuth " + ", ".join(f'{q(k)}="{q(v)}"' for k, v in sorted(oa.items()))


def _post(url: str, header: str, form: dict | None = None) -> str:
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form or {}).encode(), method="POST",
                                 headers={"Authorization": header, "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Open Practice-press/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def tumblr_start(state_file: str) -> str:
    ck, cs = os.environ["OP_TUMBLR_CONSUMER_KEY"], os.environ["OP_TUMBLR_CONSUMER_SECRET"]
    url = f"{TUMBLR}/request_token"
    # ask for our callback explicitly (Tumblr fixes the return address when the token is made); an app whose default
    # callback is elsewhere refuses it, and then the app default is used
    cb = os.environ.get("OP_TUMBLR_CALLBACK", "https://open-practice.zlnew.workers.dev/")
    try:
        body = dict(urllib.parse.parse_qsl(_post(url, auth_header("POST", url, {}, ck, cs, extra={"oauth_callback": cb}))))
    except urllib.error.HTTPError as e:
        if e.code != 400:
            raise
        body = dict(urllib.parse.parse_qsl(_post(url, auth_header("POST", url, {}, ck, cs))))
    with open(state_file, "w") as f:
        json.dump({"token": body["oauth_token"], "secret": body["oauth_token_secret"], "at": int(time.time())}, f)
    os.chmod(state_file, 0o600)
    return f"{TUMBLR}/authorize?oauth_token={q(body['oauth_token'])}"


def tumblr_finish(state_file: str, returned: str) -> dict:
    ck, cs = os.environ["OP_TUMBLR_CONSUMER_KEY"], os.environ["OP_TUMBLR_CONSUMER_SECRET"]
    st = json.load(open(state_file))
    qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(returned.strip()).query or returned.strip()))
    if qs.get("oauth_token") and qs["oauth_token"] != st["token"]:
        raise SystemExit("that link belongs to an older authorisation; run tumblr-start again")
    url = f"{TUMBLR}/access_token"
    body = dict(urllib.parse.parse_qsl(_post(url, auth_header("POST", url, {}, ck, cs, st["token"], st["secret"], extra={"oauth_verifier": qs["oauth_verifier"]}))))
    return {"OP_TUMBLR_TOKEN": body["oauth_token"], "OP_TUMBLR_TOKEN_SECRET": body["oauth_token_secret"]}


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "tumblr-start":
        print(tumblr_start(sys.argv[2]))
    elif len(sys.argv) >= 4 and sys.argv[1] == "tumblr-finish":
        print(json.dumps(tumblr_finish(sys.argv[2], sys.argv[3])))
    else:
        print(__doc__)
        sys.exit(2)
