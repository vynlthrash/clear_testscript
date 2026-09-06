#!/usr/bin/env python3
"""Render CONTAINMENT card faces, backs, and TTS sheet images.

Usage: python3 render/render_cards.py
Outputs individual card PNGs to assets/cards/<deck>/, card backs and
sheet composites to assets/sheets/, and a manifest describing sheet
layout (used later by tts/build_save.py) to data/sheet_manifest.json.
"""
import json
import re
import os
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cards.json"
CARD_DIR = ROOT / "assets" / "cards"
SHEET_DIR = ROOT / "assets" / "sheets"
CARD_W, CARD_H = 500, 700
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

ICONS = {
    "Personnel": '<circle cx="100" cy="70" r="30"/><path d="M40 170 Q100 100 160 170 L160 190 L40 190 Z"/>',
    "Facilities": '<rect x="45" y="90" width="110" height="90" /><polygon points="40,90 100,40 160,90"/><rect x="85" y="130" width="30" height="50" fill="#0000" stroke-width="6" class="cut"/>',
    "Equipment": '<rect x="85" y="30" width="30" height="140" rx="8" transform="rotate(45 100 100)"/><circle cx="60" cy="60" r="26" fill="none" stroke-width="14"/>',
    "Protocols": '<rect x="55" y="35" width="90" height="130" rx="6"/><rect x="70" y="55" width="60" height="8" class="cut"/><rect x="70" y="80" width="60" height="8" class="cut"/><rect x="70" y="105" width="40" height="8" class="cut"/>',
    "Anomalies": '<polygon points="100,25 118,70 165,72 128,102 142,150 100,122 58,150 72,102 35,72 82,70"/><circle cx="100" cy="92" r="14" fill="#0000" class="cut" stroke-width="6"/>',
}

CSS = """
@font-face { font-family: 'Body'; src: local('Liberation Sans'); }
* { box-sizing: border-box; margin:0; padding:0; }
html,body { width:%(w)dpx; height:%(h)dpx; overflow:hidden; }
.card {
  width:%(w)dpx; height:%(h)dpx; position:relative;
  font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
  background: %(paper)s;
  border: 14px solid %(primary)s;
  border-radius: 26px;
  overflow: hidden;
  display:flex; flex-direction:column;
}
.header {
  display:flex; align-items:flex-start; justify-content:space-between;
  padding: 14px 16px 4px 18px; background: %(primary)s; color: #fff;
}
.name { font-size: 30px; font-weight:700; line-height:1.05; max-width: 370px; letter-spacing: -0.3px; text-shadow: 0 1px 2px rgba(0,0,0,.4);}
.cost {
  flex: 0 0 auto; width:56px; height:56px; border-radius:50%%;
  background: radial-gradient(circle at 35%% 30%%, #fff8, %(accent)s 60%%, #0006 100%%);
  border: 3px solid #fff; color:#fff; font-size:28px; font-weight:800;
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 2px 6px rgba(0,0,0,.5);
  margin-left: 10px;
}
.subheader {
  display:flex; align-items:center; justify-content:space-between;
  padding: 8px 18px; background: %(accent)s; color:#1a1a1a;
  font-style: italic; font-size:19px; font-weight:600;
}
.unique-mark { color:#fff; margin-right:6px; font-style:normal; font-weight:900;}
.threat-pill {
  font-style:normal; font-weight:800; font-size:15px; background:#1a1a1a; color:#fff;
  padding:3px 10px; border-radius:12px; letter-spacing: 0.5px;
}
.art {
  position:relative; height: 250px; flex: 0 0 auto;
  background: linear-gradient(135deg, %(primary)s 0%%, %(accent)s 100%%);
  display:flex; align-items:center; justify-content:center;
  overflow:hidden;
}
.art .bgring { position:absolute; width:420px; height:420px; border-radius:50%%; border: 2px solid rgba(255,255,255,.15); }
.art .bgring.b2 { width:320px; height:320px; }
.art svg.icon { width:190px; height:190px; opacity:0.92; }
.art svg.icon path, .art svg.icon rect, .art svg.icon circle, .art svg.icon polygon { fill: rgba(255,255,255,0.85); stroke: rgba(255,255,255,0.85); }
.art svg.icon .cut { fill: transparent !important; stroke: rgba(0,0,0,0.28) !important; }
.section-tag {
  position:absolute; top:10px; left:14px; color:#fff9; font-size:13px; font-weight:700;
  text-transform:uppercase; letter-spacing:2px;
}
.text-box {
  flex: 1 1 auto; padding: 16px 20px; display:flex; align-items:center;
  background: %(paper)s;
}
.text-box p {
  font-family: 'Liberation Serif', 'DejaVu Serif', serif;
  font-size: 21px; line-height:1.32; color:#1c1c1c;
}
.footer {
  display:flex; align-items:center; justify-content:space-between;
  padding: 8px 18px 12px 18px; background: %(primary)s;
}
.deckmark { color: #fff9; font-size:13px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;}
.pd {
  display:flex; align-items:center; gap:6px; background:#0000;
}
.pd .box {
  min-width:38px; text-align:center; padding:4px 9px; border-radius:8px;
  font-weight:800; font-size:21px; color:#fff; border: 2px solid #fff8;
}
.pd .pow { background: #b23a2f; }
.pd .dur { background: #1c3a5e; }
.back {
  width:%(w)dpx; height:%(h)dpx; display:flex; align-items:center; justify-content:center;
  background: radial-gradient(circle at 50%% 40%%, %(accent)s 0%%, %(primary)s 70%%);
  border: 14px solid %(primary)s; border-radius: 26px; box-sizing:border-box;
  font-family:'Liberation Sans',sans-serif;
}
.back .ring { position:absolute; border-radius:50%%; border: 3px solid rgba(255,255,255,.18); }
.back-wordmark { color:#fff; font-size:46px; font-weight:900; letter-spacing:4px; text-shadow:0 2px 8px rgba(0,0,0,.5); z-index:2;}
.back-sub { position:absolute; bottom:60px; color:#fff9; font-size:18px; letter-spacing:3px; font-weight:700;}
"""

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def cost_html(cost):
    if cost is None:
        return ""
    return f'<div class="cost">{cost}</div>'

def threat_html(threat):
    if not threat:
        return ""
    return f'<div class="threat-pill">THREAT {threat}</div>'

def pd_html(power, durability):
    if power is None and durability is None:
        return '<div class="pd"></div>'
    return (
        '<div class="pd">'
        f'<div class="box pow">{power}</div>'
        f'<div class="box dur">{durability}</div>'
        "</div>"
    )

def card_html(deck, section_name, card):
    colors = deck["colors"]
    css = CSS % {"w": CARD_W, "h": CARD_H, **colors}
    icon = ICONS.get(section_name, ICONS["Protocols"])
    unique_mark = '<span class="unique-mark">&#9733;</span>' if card.get("unique") else ""
    type_line = card["typeLine"]
    threat = card.get("threat")
    power = card.get("power")
    durability = card.get("durability")
    cost = card.get("cost")
    text = card["text"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body><div class="card">
  <div class="header">
    <div class="name">{card['name']}</div>
    {cost_html(cost)}
  </div>
  <div class="subheader">
    <div>{unique_mark}{type_line}</div>
    {threat_html(threat)}
  </div>
  <div class="art">
    <div class="section-tag">{section_name}</div>
    <div class="bgring"></div><div class="bgring b2"></div>
    <svg class="icon" viewBox="0 0 200 200">{icon}</svg>
  </div>
  <div class="text-box"><p>{text}</p></div>
  <div class="footer">
    <div class="deckmark">{deck['name']}</div>
    {pd_html(power, durability)}
  </div>
</div></body></html>"""

def back_html(deck):
    colors = deck["colors"]
    css = CSS % {"w": CARD_W, "h": CARD_H, **colors}
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body><div class="back" style="position:relative;">
  <div class="ring" style="width:420px;height:420px;"></div>
  <div class="ring" style="width:320px;height:320px;"></div>
  <div class="back-wordmark">CONTAINMENT</div>
  <div class="back-sub">{deck['name']}</div>
</div></body></html>"""

def main():
    data = json.loads(DATA.read_text())
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    SHEET_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {"decks": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": CARD_W, "height": CARD_H})

        for deck in data["decks"]:
            deck_id = deck["id"]
            out_dir = CARD_DIR / deck_id
            out_dir.mkdir(parents=True, exist_ok=True)
            order = []  # slug order defines sheet grid index

            for section in deck["sections"]:
                for card in section["cards"]:
                    slug = slugify(card["name"])
                    html = card_html(deck, section["name"], card)
                    page.set_content(html)
                    page.locator(".card").screenshot(path=str(out_dir / f"{slug}.png"))
                    order.append({
                        "slug": slug,
                        "name": card["name"],
                        "qty": card["qty"],
                        "section": section["name"],
                    })
                    print(f"rendered {deck_id}/{slug}.png")

            # back
            page.set_content(back_html(deck))
            page.locator(".back").screenshot(path=str(SHEET_DIR / f"{deck_id}-back.png"))

            manifest["decks"][deck_id] = {"name": deck["name"], "order": order}

        browser.close()

    (ROOT / "data" / "sheet_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Wrote data/sheet_manifest.json")

if __name__ == "__main__":
    main()
