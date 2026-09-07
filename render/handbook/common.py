"""Shared CSS/HTML chrome for the CONTAINMENT physical-game handbook pages."""

PAGE_W, PAGE_H = 1700, 2200

ACCENTS = {
    "neutral": {"accent": "#c98a2b", "accent_dim": "#5a4118"},
    "authority": {"accent": "#5fa8d3", "accent_dim": "#1c3a5e"},
    "ruin": {"accent": "#d3604f", "accent_dim": "#5a1c14"},
}

BASE_CSS = """
* { box-sizing: border-box; margin:0; padding:0; }
html, body { width:%(w)dpx; height:%(h)dpx; background:#0b0b0d; overflow:hidden;
  font-family:'DejaVu Sans','Liberation Sans',sans-serif; color:#e9e6df; }
.page { position:relative; width:%(w)dpx; height:%(h)dpx; background:
  radial-gradient(ellipse at 50%% -10%%, #17171a 0%%, #0b0b0d 55%%); }

.noise { position:absolute; inset:0; opacity:.05; background-image:
  repeating-linear-gradient(0deg, #fff 0 1px, transparent 1px 3px); pointer-events:none; }

.frame { position:absolute; left:56px; right:56px; top:120px; bottom:110px; }
.bracket { position:absolute; width:46px; height:46px; border-color:%(accent)s; opacity:.85; }
.bracket.tl { top:0; left:0; border-top:4px solid; border-left:4px solid; }
.bracket.tr { top:0; right:0; border-top:4px solid; border-right:4px solid; }
.bracket.bl { bottom:0; left:0; border-bottom:4px solid; border-left:4px solid; }
.bracket.br { bottom:0; right:0; border-bottom:4px solid; border-right:4px solid; }

.topbar { position:absolute; top:0; left:56px; right:56px; height:74px;
  display:flex; align-items:center; justify-content:space-between;
  border-bottom:2px solid #2a2a2e; font-family:'DejaVu Sans Mono',monospace;
  font-size:15px; letter-spacing:2px; color:#8a877e; text-transform:uppercase; }
.topbar .doc { color:%(accent)s; font-weight:bold; }

.botbar { position:absolute; bottom:0; left:56px; right:56px; height:64px;
  display:flex; align-items:center; justify-content:space-between;
  border-top:2px solid #2a2a2e; font-family:'DejaVu Sans Mono',monospace;
  font-size:13px; letter-spacing:2px; color:#6f6c64; text-transform:uppercase; }
.barcode { display:flex; align-items:flex-end; gap:3px; height:28px; }
.barcode div { width:3px; background:#6f6c64; }

.sectag { display:inline-flex; align-items:center; gap:14px; margin-bottom:18px; }
.sectag .num { font-family:'DejaVu Sans Mono',monospace; font-size:22px; font-weight:bold;
  color:#0b0b0d; background:%(accent)s; padding:6px 14px; border-radius:2px; letter-spacing:1px; }
.sectag .lbl { font-size:15px; letter-spacing:6px; color:%(accent)s; font-weight:bold;
  text-transform:uppercase; }

h1.title { font-size:56px; font-weight:900; letter-spacing:1px; color:#f4f1ea;
  text-transform:uppercase; margin-bottom:8px; line-height:1.05; }
p.lede { font-size:19px; line-height:1.55; color:#c9c6bd; max-width:1050px; margin-bottom:22px;
  overflow-wrap:break-word; word-break:break-word; }
p.body { font-size:16.5px; line-height:1.62; color:#c9c6bd; margin-bottom:16px; max-width:1050px;
  overflow-wrap:break-word; word-break:break-word; }
.panel { background:#141416; border:1px solid #2a2a2e; border-radius:6px; padding:22px 26px;
  margin-bottom:18px; }
.panel.note { border-color:%(accent)s55; background:%(accent)s14; }
.panel .kicker { font-size:12px; letter-spacing:3px; color:%(accent)s; font-weight:bold;
  text-transform:uppercase; margin-bottom:8px; }
.panel p { font-size:15px; line-height:1.55; color:#d6d3ca; overflow-wrap:break-word; word-break:break-word; }

table.ref { width:100%%; border-collapse:collapse; margin-bottom:20px; }
table.ref th { text-align:left; font-size:12.5px; letter-spacing:2px; text-transform:uppercase;
  color:#0b0b0d; background:%(accent)s; padding:10px 14px; }
table.ref td { font-size:15px; color:#d6d3ca; padding:10px 14px; border-bottom:1px solid #232326;
  overflow-wrap:break-word; word-break:break-word; }
table.ref tr:nth-child(even) td { background:#141416; }

.crest { width:64px; height:64px; }
.crest polygon, .crest circle, .crest path { stroke:%(accent)s; fill:none; stroke-width:2.5; }
"""

def crest_svg(accent, size=64):
    return f"""<svg class="crest" style="width:{size}px;height:{size}px" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="46" style="stroke:{accent}"/>
      <circle cx="50" cy="50" r="38" style="stroke:{accent};opacity:.5"/>
      <polygon points="50,28 72,66 28,66" style="stroke:{accent}"/>
    </svg>"""

def barcode_html(n=28, seed=7):
    import random
    r = random.Random(seed)
    bars = "".join(f'<div style="height:{r.randint(10,28)}px"></div>' for _ in range(n))
    return f'<div class="barcode">{bars}</div>'

def page_css(theme="neutral"):
    colors = ACCENTS[theme]
    return BASE_CSS % {"w": PAGE_W, "h": PAGE_H, "accent": colors["accent"]}

def shell(body_html, theme="neutral", doc_code="PCD-RB-001", page_no="", running_title="CONTAINMENT FIELD MANUAL"):
    colors = ACCENTS[theme]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{page_css(theme)}</style></head>
<body><div class="page">
  <div class="noise"></div>
  <div class="topbar"><span>{running_title}</span><span class="doc">{doc_code}</span></div>
  <div class="frame">
    <div class="bracket tl"></div><div class="bracket tr"></div>
    <div class="bracket bl"></div><div class="bracket br"></div>
  </div>
  <div style="position:absolute; left:112px; right:112px; top:170px; bottom:160px; overflow:hidden;">
    {body_html}
  </div>
  <div class="botbar">{barcode_html()}<span>PROTOTYPE // NOT FOR DISTRIBUTION</span><span>{page_no}</span></div>
</div></body></html>"""

def sectag(num, label, theme="neutral"):
    return f'<div class="sectag"><span class="num">{num}</span><span class="lbl">{label}</span></div>'
