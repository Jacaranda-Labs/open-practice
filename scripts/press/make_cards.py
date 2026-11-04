#!/usr/bin/env python3
"""Pre-render every activity's press cards (wide, square, pin) into apps/web/public/brand/press/, so each post has a
public image URL. Re-run after adding or editing activities, then deploy:  python3 scripts/press/make_cards.py
Not part of build:assets on purpose: PNG bytes can differ across Pillow versions, and the check job diffs that output."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mediakit  # noqa: E402
import press  # noqa: E402
from PIL import Image  # noqa: E402
import io  # noqa: E402


def small(png: bytes) -> bytes:
    """Flat-colour cards compress far better as a 128-colour palette; text stays crisp."""
    im = Image.open(io.BytesIO(png)).convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = io.BytesIO()
    im.save(out, "PNG", optimize=True)
    return out.getvalue()


def main() -> int:
    press.CARDS.mkdir(parents=True, exist_ok=True)
    total = 0
    for a in press.activities():
        for shape in ("wide", "square", "pin"):
            b = small(mediakit.render("stat", shape, press.card_data(a)))
            press.card_path(a, shape).write_bytes(b)
            total += len(b)
    print(f"{len(press.activities())} activities, {total // 1024} KB in {press.CARDS.relative_to(press.ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
