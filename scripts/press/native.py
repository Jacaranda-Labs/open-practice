"""Press v3 composer: one story, written natively for each platform, then checked by a findability gate.

Canonical copy: scratch/press/native.py (JS port native.js). Copied verbatim into each press; do not edit a copy alone.
See playbook/PRESS-V3.md for the rules. Pure: no network, no clock, no randomness.

    posts = compose_all(story)          # {"bsky": {...}, "mastodon": {...}, ...}
    problems = gate("bsky", posts["bsky"], story)   # [] when the post is fit to publish
"""
from __future__ import annotations

import html as _html
import re

E = _html.escape
RAILS = ("bsky", "mastodon", "tumblr", "pinterest", "blogger", "facebook", "linkedin", "nostr", "discord")
BANNED = [r"\bthe best\b", r"\bbest[- ]in[- ]class\b", r"#1\b", r"\bnumber one\b", r"world[- ]class", r"revolutionar", r"game[- ]chang", r"\bguarantee",
          r"most are free to start", r"\bhobby\b", r"\bx\.com\b", r"twitter\.com",
          r"in today'?s fast[- ]paced", r"\bunlock\b", r"\bsupercharge"]
MASTODON_URL = 23


def clean(t: str) -> str:
    t = re.sub(r"\s*\u2014\s*", ", ", str(t or ""))      # em dashes read as machine copy; a comma reads as a person
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def fit(text: str, limit: int) -> str:
    """Cut at a sentence end if that keeps half the room, else at a word, with an ellipsis."""
    text = clean(text)
    if len(text) <= limit:
        return text
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s)", text[: limit + 1])]
    if ends and ends[-1] >= limit // 2:
        return text[: ends[-1]].strip()
    cut = text[: limit - 1]
    cut = cut[: cut.rfind(" ")] if " " in cut[limit // 2:] else cut
    return cut.rstrip(" ,.;:") + "\u2026"


def camel(tag: str) -> str:
    """'public procurement' / 'public-procurement' -> 'PublicProcurement'; keeps existing CamelCase."""
    parts = re.split(r"[^A-Za-z0-9]+", str(tag))
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def words(tag: str) -> str:
    """'PublicProcurement' -> 'public procurement' (Tumblr and Pinterest want readable phrases)."""
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(tag))
    return re.sub(r"[^a-z0-9 ]+", " ", t.lower()).strip()


def slug(t: str, n: int = 60) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(t).lower())).strip("-")[:n].strip("-")


def tags(story: dict, n: int) -> list[str]:
    out = []
    for h in story.get("hashtags") or []:
        c = camel(h)
        if c and c.lower() not in [x.lower() for x in out]:
            out.append(c)
    return out[:n]


def hl(ts: list[str]) -> str:
    return " ".join("#" + t for t in ts)


def hook(s: dict, rail: str) -> str:
    """A platform may get its own opening line (LinkedIn first person, Facebook warmer); else the shared hook."""
    return clean((s.get("hooks") or {}).get(rail) or s["hook"])


def lede(s: dict) -> str:
    """Short-form body under the hook (social posts); the standalone summary stays for cards, pins and blogs."""
    return clean(s.get("lede") or s["summary"])


def _pack(lines: list[str], limit: int) -> list[str]:
    """Pack lines into as few posts as fit `limit` each (Bluesky replies)."""
    posts, cur = [], ""
    for ln in lines:
        ln = fit(ln, limit)
        nxt = (cur + "\n" + ln) if cur else ln
        if len(nxt) <= limit:
            cur = nxt
        else:
            posts.append(cur)
            cur = ln
    return posts + ([cur] if cur else [])


def mlen(text: str) -> int:
    """Mastodon length: every URL counts as 23 characters."""
    return len(re.sub(r"https?://\S+", "x" * MASTODON_URL, text))


# ---------------------------------------------------------------- composers
def c_bsky(s: dict) -> dict:
    t2 = tags(s, 2)
    tail = ("\n\n" + hl(t2)) if t2 else ""
    head = hook(s, "bsky")
    room = 300 - len(tail)
    body = fit(head + "\n\n" + lede(s), room)
    if body.endswith("\u2026"):
        body = fit(head, room)
    pts = [("\u2022 " + clean(p)) for p in s.get("points") or []]
    replies = _pack(pts, 300)[:1]
    last = fit(clean(s.get("takeaway", "")), 300 - len(s["url"]) - 2) + "\n\n" + s["url"]
    replies.append(last.strip())
    return {"text": body + tail, "replies": replies[:2], "tags": [words(x).replace(" ", "")[:64] for x in tags(s, 10)[2:10]][:8],
            "card": {"title": fit(s["title"], 300), "description": fit(s["summary"], 280)}, "alt": clean(s.get("alt", "")), "langs": ["en"]}


def c_mastodon(s: dict) -> dict:
    ts = tags(s, 5)
    tail = "\n\n" + hl(ts) if ts else ""
    link = "\n\n" + s["url"]
    pts = [("\u2022 " + fit(p, 120)) for p in (s.get("points") or [])[:3]]
    for k in (3, 2, 1, 0):
        body = hook(s, "mastodon") + "\n\n" + lede(s) + ("\n\n" + "\n".join(pts[:k]) if k else "")
        if s.get("takeaway") and k >= 2:
            body += "\n\n" + clean(s["takeaway"])
        if mlen(body + link + tail) <= 500:
            break
    else:
        body = fit(hook(s, "mastodon") + "\n\n" + lede(s), 500 - MASTODON_URL - len(tail) - 4)
    return {"text": body + link + tail, "alt": clean(s.get("alt", "")), "language": "en"}


def c_tumblr(s: dict) -> dict:
    topics = [words(t) for t in (s.get("topics") or [])] + [words(h) for h in (s.get("hashtags") or [])]
    seen, tg = set(), []
    for t in topics:
        if t and t not in seen and len(t) <= 139:
            seen.add(t)
            tg.append(t)
    pts = "".join(f"<li>{E(clean(p))}</li>" for p in s.get("points") or [])
    body = (f"<p>{E(hook(s, 'tumblr'))}</p><p>{E(lede(s))}</p>" + (f"<ul>{pts}</ul>" if pts else "")
            + (f"<p><b>Try this:</b> {E(clean(s['takeaway']))}</p>" if s.get("takeaway") else "")
            + f'<p><a href="{E(s["url"], quote=True)}">{E(s.get("link_text") or s["title"])}</a></p>')
    return {"title": fit(s["title"], 100), "html": body, "tags": tg[:30], "slug": slug(s.get("keyphrase") or s["title"]),
            "alt": clean(s.get("alt", ""))}


def c_pinterest(s: dict) -> dict:
    title = fit(s.get("pin_title") or s["title"], 100)
    desc = clean(s["summary"])
    for p in (s.get("points") or [])[:2]:
        if len(desc) + len(p) + 2 < 420:
            desc += " " + clean(p).rstrip(".") + "."
    if s.get("takeaway") and len(desc) + len(s["takeaway"]) + 1 <= 500:
        desc += " " + clean(s["takeaway"])
    desc = re.sub(r"(?<!\w)#(\w)", r"\1", desc)
    return {"title": title, "description": fit(desc, 500), "alt": fit(s.get("alt", ""), 500), "link": s["url"]}


def c_blogger(s: dict) -> dict:
    if s.get("long_html"):
        html = s["long_html"]
    else:
        pts = "".join(f"<li>{E(clean(p))}</li>" for p in s.get("points") or [])
        faq = "".join(f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in s.get("faq") or [])
        html = (f"<p><b>{E(clean(s['summary']))}</b></p><p>{E(hook(s, 'blogger'))}</p>"
                + (f"<h2>{E(s.get('points_title') or 'What to know')}</h2><ul>{pts}</ul>" if pts else "")
                + (f"<h2>What to do today</h2><p>{E(clean(s['takeaway']))}</p>" if s.get("takeaway") else "")
                + (f"<h2>Frequently asked questions</h2>{faq}" if faq else "")
                + f'<p><a href="{E(s["url"], quote=True)}">{E(s.get("link_text") or s["title"])}</a></p>')
    return {"title": fit(s.get("blog_title") or s["title"], 100), "html": html, "alt": clean(s.get("alt", ""))}


def c_facebook(s: dict) -> dict:
    ts = tags(s, 2)
    pts = "\n".join("\u2713 " + clean(p) for p in (s.get("points") or [])[:4])
    text = (fit(hook(s, "facebook"), 125) + "\n\n" + lede(s) + ("\n\n" + pts if pts else "")
            + ("\n\n" + clean(s["question"]) if s.get("question") else "") + "\n\n" + s["url"] + ("\n\n" + hl(ts) if ts else ""))
    return {"text": text, "alt": clean(s.get("alt", ""))}


def c_linkedin(s: dict) -> dict:
    ts = tags(s, 5)
    pts = "\n".join(f"{i + 1}. {clean(p)}" for i, p in enumerate((s.get("points") or [])[:5]))
    text = (fit(hook(s, "linkedin"), 150) + "\n\n" + clean(s["summary"]) + ("\n\n" + pts if pts else "")
            + ("\n\n" + clean(s["takeaway"]) if s.get("takeaway") else "")
            + ("\n\n" + clean(s["question"]) if s.get("question") else "") + "\n\n" + s["url"] + ("\n\n" + hl(ts) if ts else ""))
    return {"text": fit(text, 3000), "alt": clean(s.get("alt", ""))}


def c_nostr(s: dict) -> dict:
    ts = tags(s, 5)
    pts = "\n".join("- " + clean(p) for p in (s.get("points") or [])[:5])
    text = hook(s, "nostr") + "\n\n" + lede(s) + ("\n\n" + pts if pts else "") + "\n\n" + s["url"] + ("\n\n" + hl(ts) if ts else "")
    return {"text": text, "t": [t.lower() for t in ts]}


def c_discord(s: dict) -> dict:
    pts = "\n".join("\u2022 " + clean(p) for p in (s.get("points") or [])[:6])
    return {"text": fit(f"**{clean(s['title'])}**\n{clean(s['summary'])}" + ("\n" + pts if pts else "") + "\n" + s["url"], 1800)}


COMPOSE = {"bsky": c_bsky, "mastodon": c_mastodon, "tumblr": c_tumblr, "pinterest": c_pinterest, "blogger": c_blogger,
           "facebook": c_facebook, "linkedin": c_linkedin, "nostr": c_nostr, "discord": c_discord}


def compose_all(story: dict, rails=RAILS) -> dict:
    need = [k for k in ("url", "title", "summary", "hook") if not story.get(k)]
    if need:
        raise ValueError("story is missing " + ", ".join(need))
    return {r: COMPOSE[r](story) for r in rails}


# ---------------------------------------------------------------- the findability gate
def _keyphrase_in(kp: str, *texts: str) -> bool:
    if not kp:
        return True
    ws = [w for w in re.findall(r"[a-z0-9]+", kp.lower()) if len(w) > 2]
    blob = " ".join(texts).lower()
    return all(w in blob for w in ws)


def _ht(text: str) -> list[str]:
    return re.findall(r"(?<![\w/#])#([A-Za-z][A-Za-z0-9_]*)", text)


def gate(rail: str, p: dict, story: dict) -> list[str]:
    kp, bad = story.get("keyphrase", ""), []
    # marketing claims are checked in what the composer wrote; an article body the business supplied (its own vetted
    # teaching text, where "which works best" is fine) is not re-judged here
    skip = {"html"} if story.get("long_html") else set()
    allt = " ".join(str(v) for k, v in p.items() if isinstance(v, str) and k not in skip) + " " + " ".join(p.get("replies") or [])
    for rx in BANNED:
        if re.search(rx, re.sub(r"https?://\S+", "", allt), re.I):
            bad.append(f"banned phrase /{rx}/")
    if "alt" in p and story.get("alt") is not None:
        if len(p.get("alt") or "") < 30:
            bad.append("alt text missing or under 30 characters")
        elif "#" in p["alt"]:
            bad.append("hashtags in alt text")
    if rail == "bsky":
        for i, t in enumerate([p["text"]] + p.get("replies", [])):
            if len(t) > 300:
                bad.append(f"bluesky post {i} is {len(t)} > 300")
        if len(_ht(p["text"])) > 3:
            bad.append("more than 3 inline hashtags on Bluesky")
        if not _keyphrase_in(kp, p["text"], p["card"]["title"], p["card"]["description"]):
            bad.append("keyphrase not in the Bluesky text or card")
        if len(p.get("tags", [])) > 8:
            bad.append("more than 8 hidden Bluesky tags")
    elif rail == "mastodon":
        if mlen(p["text"]) > 500:
            bad.append(f"mastodon post is {mlen(p['text'])} > 500")
        n = len(_ht(p["text"]))
        if not 3 <= n <= 5:
            bad.append(f"mastodon needs 3-5 hashtags, has {n}")
    elif rail == "tumblr":
        if not _keyphrase_in(kp, p["title"]):
            bad.append("keyphrase not in the Tumblr title")
        if not 5 <= len(p["tags"]) <= 30:
            bad.append(f"tumblr needs 5-30 tags, has {len(p['tags'])}")
        if any(t != t.lower() for t in p["tags"]):
            bad.append("tumblr tags must be lowercase phrases")
    elif rail == "pinterest":
        if len(p["title"]) > 100:
            bad.append("pin title over 100")
        if not _keyphrase_in(kp, p["title"][:60]):
            bad.append("keyphrase not in the first 60 characters of the pin title")
        if len(p["description"]) > 500:
            bad.append("pin description over 500")
        if _ht(p["description"]):
            bad.append("hashtags in the pin description (Pinterest search ignores them)")
        if not p.get("link"):
            bad.append("pin has no link")
    elif rail == "blogger":
        if not _keyphrase_in(kp, p["title"]):
            bad.append("keyphrase not in the blog title")
        if p["html"].count("<h2") < 2:
            bad.append("blog post needs at least 2 H2 sections")
        if "question" not in p["html"].lower() and "<h3" not in p["html"]:
            bad.append("blog post has no FAQ")
    elif rail == "facebook":
        if len(p["text"].split("\n", 1)[0]) > 125:
            bad.append("facebook hook over 125 characters")
        if len(_ht(p["text"])) > 2:
            bad.append("more than 2 hashtags on Facebook")
        if story["url"] not in p["text"]:
            bad.append("facebook post has no link")
    elif rail == "linkedin":
        if len(p["text"].split("\n", 1)[0]) > 150:
            bad.append("linkedin first line over 150 characters")
        n = len(_ht(p["text"]))
        if not 3 <= n <= 5:
            bad.append(f"linkedin needs 3-5 hashtags, has {n}")
        if len(p["text"]) > 3000:
            bad.append("linkedin post over 3000")
    elif rail == "discord":
        if len(p["text"]) > 1800:
            bad.append("discord post over 1800")
    return bad
