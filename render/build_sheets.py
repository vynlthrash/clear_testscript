#!/usr/bin/env python3
"""Composite individual card faces into TTS-ready sprite sheets.

TTS CustomDeck cards are addressed by a grid index (row-major,
left-to-right / top-to-bottom, 0-based) into a single sheet image.
This script lays out each deck's unique cards into the smallest
10-wide grid that fits them, padding unused cells with a blank tile,
and writes data/sheet_manifest.json with the width/height/index for
each card slug so tts/build_save.py can reference them.
"""
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CARD_DIR = ROOT / "assets" / "cards"
SHEET_DIR = ROOT / "assets" / "sheets"
MANIFEST_PATH = ROOT / "data" / "sheet_manifest.json"
CARD_W, CARD_H = 500, 700
MAX_COLS = 10

def build_sheet(deck_id, order):
    n = len(order)
    cols = min(MAX_COLS, n)
    rows = math.ceil(n / cols)
    sheet = Image.new("RGBA", (cols * CARD_W, rows * CARD_H), (0, 0, 0, 0))

    for idx, entry in enumerate(order):
        r, c = divmod(idx, cols)
        img_path = CARD_DIR / deck_id / f"{entry['slug']}.png"
        im = Image.open(img_path).convert("RGBA")
        sheet.paste(im, (c * CARD_W, r * CARD_H))
        entry["index"] = idx

    out_path = SHEET_DIR / f"{deck_id}-sheet.png"
    sheet.convert("RGB").save(out_path)
    print(f"wrote {out_path} ({cols}x{rows}, {n} cards, {n} used / {cols*rows} slots)")
    return {"cols": cols, "rows": rows, "count": n, "file": str(out_path.relative_to(ROOT))}

def main():
    manifest = json.loads(MANIFEST_PATH.read_text())
    for deck_id, deck in manifest["decks"].items():
        grid = build_sheet(deck_id, deck["order"])
        deck["grid"] = grid
        deck["back_file"] = str((SHEET_DIR / f"{deck_id}-back.png").relative_to(ROOT))
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
    print("updated data/sheet_manifest.json")

if __name__ == "__main__":
    main()
