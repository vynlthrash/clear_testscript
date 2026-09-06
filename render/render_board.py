#!/usr/bin/env python3
"""Render the shared playmat (two faction zones + Breach Track) for TTS."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHEET_DIR = ROOT / "assets" / "sheets"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H = 2600, 1700

BANDS = [
    (0, 2, "STABLE", "#2f6f4f"),
    (3, 4, "UNSTABLE", "#8a8a2f"),
    (5, 6, "DANGER", "#a8631f"),
    (7, 9, "CRITICAL", "#a8331f"),
    (10, 10, "CATASTROPHIC", "#3a0d0d"),
]

def band_segments():
    segs = []
    for lo, hi, label, color in BANDS:
        segs.append({"lo": lo, "hi": hi, "label": label, "color": color})
    return segs

def track_html():
    total_cells = 11  # 0..10
    cell_w = 100.0 / total_cells
    cells = ""
    for lo, hi, label, color in BANDS:
        span = hi - lo + 1
        cells += (
            f'<div class="band" style="left:{lo*cell_w:.3f}%;width:{span*cell_w:.3f}%;background:{color};">'
            f'<span>{label}</span></div>'
        )
    ticks = ""
    for n in range(11):
        left = n * cell_w + cell_w / 2
        ticks += f'<div class="tick" style="left:{left:.3f}%;">{n}</div>'
    return cells, ticks

def html():
    cells, ticks = track_html()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:{W}px; height:{H}px; font-family:'Liberation Sans','DejaVu Sans',sans-serif; }}
.mat {{ width:{W}px; height:{H}px; position:relative; background:#0e0e10; }}
.zone {{ position:absolute; left:0; right:0; height:44%; display:flex; flex-direction:column; }}
.authority {{ top:0; background:linear-gradient(180deg,#1c3a5e 0%, #14283f 100%); }}
.ruin {{ bottom:0; background:linear-gradient(0deg,#3a0d0d 0%, #240707 100%); }}
.zone-header {{ display:flex; justify-content:space-between; align-items:baseline; padding: 34px 60px 0 60px; }}
.zone-title {{ color:#fff; font-size:64px; font-weight:900; letter-spacing:6px; }}
.zone-tag {{ color:#ffffffaa; font-size:24px; font-weight:700; letter-spacing:4px; }}
.lanes {{ flex:1; display:flex; gap:40px; padding: 30px 60px 40px 60px; }}
.lane {{ flex:1; border:3px dashed #ffffff33; border-radius:18px; display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding-top:14px; }}
.lane .lbl {{ color:#ffffff66; font-size:20px; letter-spacing:3px; font-weight:700; }}
.slots {{ flex:1; width:100%; display:flex; gap:16px; align-items:center; justify-content:center; }}
.slot {{ width:150px; height:210px; border:2px solid #ffffff2a; border-radius:12px; }}
.deckzone {{ width:220px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:14px; }}
.deckslot {{ width:150px; height:210px; border:3px solid #ffffff44; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#ffffff55; font-size:18px; font-weight:800; letter-spacing:2px; }}
.track {{ position:absolute; top:50%; left:6%; right:6%; height:12%; transform:translateY(-50%); background:#000; border-radius:20px; border:6px solid #d8d0c4; box-shadow:0 0 0 6px #000, 0 10px 30px rgba(0,0,0,.6); overflow:visible; }}
.track-inner {{ position:relative; width:100%; height:100%; border-radius:14px; overflow:hidden; }}
.band {{ position:absolute; top:0; bottom:0; display:flex; align-items:center; justify-content:center; border-right:3px solid #00000055; }}
.band span {{ color:#fff; font-size:20px; font-weight:800; letter-spacing:2px; text-shadow:0 1px 3px #000; }}
.tick {{ position:absolute; top:-38px; transform:translateX(-50%); color:#f1e7d8; font-size:26px; font-weight:800; }}
.track-title {{ position:absolute; left:50%; top:-72px; transform:translateX(-50%); color:#f1e7d8; font-size:30px; font-weight:900; letter-spacing:8px; }}
</style></head><body>
<div class="mat">
  <div class="zone authority">
    <div class="zone-header"><div class="zone-title">AUTHORITY</div><div class="zone-tag">SECURE &nbsp;&middot;&nbsp; CONTAIN &nbsp;&middot;&nbsp; PRESERVE</div></div>
    <div class="lanes">
      <div class="deckzone">
        <div class="deckslot">DECK</div>
        <div class="deckslot" style="opacity:.6;">DISCARD</div>
      </div>
      <div class="lane"><div class="lbl">FACILITIES</div><div class="slots"><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div></div></div>
      <div class="lane"><div class="lbl">PERSONNEL</div><div class="slots"><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div></div></div>
    </div>
  </div>

  <div class="track">
    <div class="track-title">BREACH TRACK</div>
    <div class="track-inner">{cells}</div>
    {ticks}
  </div>

  <div class="zone ruin">
    <div class="lanes">
      <div class="lane"><div class="lbl">PERSONNEL / ANOMALIES</div><div class="slots"><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div></div></div>
      <div class="lane"><div class="lbl">FACILITIES</div><div class="slots"><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div><div class="slot"></div></div></div>
      <div class="deckzone">
        <div class="deckslot">DECK</div>
        <div class="deckslot" style="opacity:.6;">DISCARD</div>
      </div>
    </div>
    <div class="zone-header" style="align-items:flex-end;"><div class="zone-title">RUIN</div><div class="zone-tag">RELEASE &nbsp;&middot;&nbsp; EXPLOIT &nbsp;&middot;&nbsp; TRANSCEND</div></div>
  </div>
</div>
</body></html>"""

def main():
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": W, "height": H})
        page.set_content(html())
        page.locator(".mat").screenshot(path=str(SHEET_DIR / "playmat.png"))
        browser.close()
    print("wrote assets/sheets/playmat.png")

if __name__ == "__main__":
    main()
