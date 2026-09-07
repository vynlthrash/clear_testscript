#!/usr/bin/env python3
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PAGE_W, PAGE_H, shell, sectag, crest_svg, barcode_html, ACCENTS

from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "_handbook_pages"
OUT_PDF = ROOT / "docs" / "CONTAINMENT_Handbook.pdf"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def page_cover():
    accent = ACCENTS["neutral"]["accent"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:{PAGE_W}px; height:{PAGE_H}px; background:#0b0b0d; font-family:'DejaVu Sans',sans-serif; overflow:hidden; }}
.page {{ position:relative; width:{PAGE_W}px; height:{PAGE_H}px;
  background: radial-gradient(ellipse at 50% 30%, #1c1c1f 0%, #0b0b0d 60%); }}
.frame {{ position:absolute; left:70px; right:70px; top:70px; bottom:70px; border:2px solid #2a2a2e; }}
.bracket {{ position:absolute; width:64px; height:64px; border-color:{accent}; }}
.bracket.tl {{ top:-2px; left:-2px; border-top:5px solid; border-left:5px solid; }}
.bracket.tr {{ top:-2px; right:-2px; border-top:5px solid; border-right:5px solid; }}
.bracket.bl {{ bottom:-2px; left:-2px; border-bottom:5px solid; border-left:5px solid; }}
.bracket.br {{ bottom:-2px; right:-2px; border-bottom:5px solid; border-right:5px solid; }}
.stamp {{ position:absolute; top:150px; left:50%; transform:translateX(-50%);
  font-family:'DejaVu Sans Mono',monospace; font-size:16px; letter-spacing:6px; color:{accent};
  border:2px solid {accent}; padding:8px 22px; text-transform:uppercase; }}
.crestwrap {{ position:absolute; top:330px; left:50%; transform:translateX(-50%); }}
h1.big {{ position:absolute; top:640px; left:50%; transform:translateX(-50%);
  font-size:130px; font-weight:900; letter-spacing:4px; color:#f4f1ea; text-transform:uppercase;
  text-align:center; width:100%; text-shadow:0 4px 30px rgba(0,0,0,.6); }}
.sub {{ position:absolute; top:800px; left:50%; transform:translateX(-50%);
  font-size:30px; letter-spacing:10px; color:{accent}; text-transform:uppercase; font-weight:bold; }}
.factions {{ position:absolute; top:900px; left:50%; transform:translateX(-50%);
  display:flex; gap:60px; font-family:'DejaVu Sans Mono',monospace; font-size:15px;
  letter-spacing:3px; color:#8a877e; }}
.factions .a {{ color:#5fa8d3; }} .factions .r {{ color:#d3604f; }}
.footer {{ position:absolute; bottom:110px; left:0; right:0; text-align:center; }}
.footer .tag {{ font-size:14px; letter-spacing:4px; color:#6f6c64; margin-bottom:10px; text-transform:uppercase;}}
.footer .bc {{ display:flex; justify-content:center; gap:3px; }}
.footer .bc div {{ width:3px; background:#6f6c64; }}
</style></head><body><div class="page">
  <div class="frame"><div class="bracket tl"></div><div class="bracket tr"></div>
    <div class="bracket bl"></div><div class="bracket br"></div></div>
  <div class="stamp">Restricted &middot; PCD Field Manual</div>
  <div class="crestwrap">{crest_svg(accent, size=180)}</div>
  <h1 class="big">Containment</h1>
  <div class="sub">Authority vs. Ruin</div>
  <div class="factions">
    <span class="a">SECURE // CONTAIN // PRESERVE</span>
    <span>&middot;</span>
    <span class="r">RELEASE // EXPLOIT // TRANSCEND</span>
  </div>
  <div class="footer">
    <div class="tag">Doc PCD&#8209;RB&#8209;001 &nbsp;&bull;&nbsp; Rev v0.1 &nbsp;&bull;&nbsp; Design Prototype</div>
    <div class="bc">{"".join(f'<div style="height:{h}px"></div>' for h in [22,10,26,14,8,22,18,10,26,14,22,8,18,26,10,22])}</div>
  </div>
</div></body></html>"""


def page_orientation():
    accent = ACCENTS["neutral"]["accent"]
    body = f"""
    {sectag("01", "Orientation")}
    <h1 class="title">What Is Containment</h1>
    <p class="lede">A two-deck head-to-head card game about a shared crisis neither player can fully
    control. <b>Authority</b> builds infrastructure, studies what it captures, and tries to keep the
    lid on. <b>Ruin</b> wants the lid off.</p>

    <p class="body">Authority wants to build infrastructure, Suppress threats, convert dangerous
    Anomalies into Contained value, and prevent the shared Breach Track from reaching catastrophe.
    Ruin wants to make containment unreliable, sacrifice expendable Personnel, raise Breach
    deliberately, and Release the very Anomalies Authority worked to secure.</p>

    <p class="body">Both sides share one Breach Track. Every escalation is a resource both players
    are spending from the same account &mdash; which is what makes the game a fight over a shared
    clock, not two separate solitaire piles.</p>

    <div style="display:flex; gap:24px; margin-top:28px;">
      <div class="panel" style="flex:1;">
        <div class="kicker" style="color:#5fa8d3;">Authority</div>
        <p>Control / midrange. Wins by stabilizing the board and out-lasting Ruin's escalation.</p>
      </div>
      <div class="panel" style="flex:1;">
        <div class="kicker" style="color:#d3604f;">Ruin</div>
        <p>Aggressive risk/release. Wins by pushing Breach into windows only it can exploit.</p>
      </div>
    </div>

    <div class="panel note" style="margin-top:10px;">
      <div class="kicker">At a Glance</div>
      <p>2 players &nbsp;&bull;&nbsp; 60-card starter decks (15-card competitive side deck) &nbsp;&bull;&nbsp;
      20 starting Stability &nbsp;&bull;&nbsp; 7-card opening hand, 7-card max hand size &nbsp;&bull;&nbsp;
      shared Breach Track, 0&ndash;10</p>
    </div>
    """
    return shell(body, theme="neutral", page_no="02")


PHASES = [
    ("Refresh", "Ready your Exhausted Personnel and Facilities."),
    ("Breach", "Resolve any effects tied to the current Breach band, including a Catastrophic Breach at 10."),
    ("Draw", "Draw a card."),
    ("Main", "Deploy Personnel, Facilities, Equipment; play Protocols/Responses."),
    ("Combat", "Attack with Ready Personnel/Anomalies."),
    ("Second Main", "Play anything left in hand you can still afford."),
    ("End", "Discard down to your maximum hand size of 7 if needed."),
]
PHASES_HTML = "".join(
    f'''<div style="flex:1; min-width:180px; background:#141416; border:1px solid #2a2a2e;
        border-radius:6px; padding:14px 16px;">
        <div style="color:#c98a2b; font-weight:bold; font-size:14px; letter-spacing:2px;
          text-transform:uppercase; margin-bottom:6px;">{i+1}. {name}</div>
        <div style="font-size:13.5px; color:#a9a69d; line-height:1.4;">{desc}</div></div>'''
    for i, (name, desc) in enumerate(PHASES)
)


def page_setup():
    body = f"""
    {sectag("02", "Setup & Turn Order")}
    <h1 class="title">Objective &amp; Setup</h1>

    <div class="panel note">
      <div class="kicker">Design Note</div>
      <p>The v0.1 design draft doesn't yet codify an exact loss condition. The strongest candidate,
      based on how Stability is spent and restored throughout the card pool, is: <b>a player is
      defeated when their Stability reaches 0.</b> Treat this as a working assumption to confirm
      during playtesting, not settled rules text.</p>
    </div>

    <p class="body" style="margin-top:10px;"><b>Before the first turn:</b></p>
    <table class="ref">
      <tr><th style="width:60px;">#</th><th>Step</th></tr>
      <tr><td>1</td><td>Each player shuffles their 60-card deck.</td></tr>
      <tr><td>2</td><td>Set both players' Stability to 20.</td></tr>
      <tr><td>3</td><td>Set the shared Breach Track to 0.</td></tr>
      <tr><td>4</td><td>Each player draws a 7-card opening hand.</td></tr>
      <tr><td>5</td><td>Decide who takes the first turn.</td></tr>
    </table>

    <p class="body" style="margin-top:22px;"><b>Every turn moves through the same seven phases:</b></p>
    <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:8px;">
      {PHASES_HTML}
    </div>
    """
    return shell(body, theme="neutral", page_no="03")


def page_breach():
    bands = [
        ("0", "2", "STABLE", "#2f6f4f"),
        ("3", "4", "UNSTABLE", "#8a8a2f"),
        ("5", "6", "DANGER", "#a8631f"),
        ("7", "9", "CRITICAL", "#a8331f"),
        ("10", "10", "CATASTROPHIC", "#5a1414"),
    ]
    total_cells = 11
    cell_pct = 100.0 / total_cells
    segs = ""
    for lo, hi, label, color in bands:
        span = (int(hi) - int(lo) + 1) * cell_pct
        left = int(lo) * cell_pct
        segs += (f'<div style="position:absolute; left:{left:.3f}%; width:{span:.3f}%; top:0; bottom:0;'
                 f' background:{color}; display:flex; align-items:center; justify-content:center;'
                 f' border-right:2px solid #0b0b0d;">'
                 f'<span style="color:#fff; font-weight:bold; font-size:14px; letter-spacing:2px;">{label}</span></div>')
    ticks = "".join(
        f'<div style="position:absolute; left:{(n*cell_pct+cell_pct/2):.3f}%; transform:translateX(-50%);'
        f' top:-34px; color:#c9c6bd; font-size:16px; font-weight:bold;">{n}</div>'
        for n in range(11)
    )
    body = f"""
    {sectag("03", "The Breach Track")}
    <h1 class="title">A Clock Both Players Wind</h1>
    <p class="lede">One shared 0&ndash;10 track. Both decks have ways to push it up or pull it back &mdash;
    what happens at each band changes who benefits from the current state of the board.</p>

    <div style="position:relative; height:90px; margin:80px 0 30px 0; border-radius:8px;
      border:3px solid #d8d0c4; overflow:hidden; box-shadow:0 10px 26px rgba(0,0,0,.5);">
      {segs}{ticks}
    </div>

    <div class="panel note">
      <div class="kicker">At Breach 10 &mdash; Catastrophic Breach</div>
      <p>Each player loses 2 Stability. All Contained Anomalies are Released. Each player Exhausts
      one Ready Facility. Breach then resets to 5.</p>
    </div>

    <p class="body" style="margin-top:18px;">Several cards key their abilities directly to these bands.
    A <b>Danger</b>&#8209;labeled ability triggers while Breach is 5 or higher; a <b>Critical</b>&#8209;labeled
    ability triggers in the Critical band (Breach 7&ndash;9). Read a card's keyworded ability header
    against this track to know when it's live.</p>
    """
    return shell(body, theme="neutral", page_no="04")


GLOSSARY = [
    ("Exhaust", "Tap a card to pay an activated ability's cost, or force a target into that same "
                "tapped-down state so it can't act. Written both as a cost (“Exhaust: …”) "
                "and as an effect (“Exhaust target Anomaly”)."),
    ("Ready", "The reverse of Exhaust — a card returns to an untapped, usable state and can "
              "attack, block, or activate again."),
    ("Suppress N / Suppressed", "Apply N Suppression to an Anomaly, marking progress toward safely "
                                 "Containing it. Several Anomalies change behavior once Suppressed."),
    ("Contain / Contained", "Move an Anomaly out of active play and into your control at a "
                             "Containment Facility, usually gated by a Suppression threshold (e.g. "
                             "“Contain — 3, while Suppressed”)."),
    ("Release / Released", "The reverse of Contain — a Contained Anomaly re-enters play as an "
                            "active threat, often raising Breach when it happens."),
    ("Threat N", "A rating on Anomalies (2–5) used as a targeting restriction by other cards, "
                 "e.g. “Exhaust target Anomaly with Threat 2 or less.”"),
    ("Capacity N", "How many Anomalies a Containment Facility can hold Contained at once."),
    ("Stabilize N", "Restore N Stability to yourself."),
    ("Sacrifice", "Remove a card you control from play, usually as a cost, to trigger an effect."),
    ("Rapid Deployment", "This card can attack the turn it's deployed, ignoring the usual "
                          "summoning-sickness delay."),
    ("Guard", "While this card is Ready, Contained Anomalies you control can't be Released by an "
              "opponent's effects."),
    ("Overwhelm", "Appears on the largest Anomalies (Hollow Mass, THE THING BELOW). Wording alone "
                  "doesn't fully specify the mechanic — treat as excess-damage-carries-over "
                  "until formalized."),
    ("Clearance", "A card-specific status (currently only on Black-Level Access Card) rather than a "
                  "general keyword with its own independent rules."),
    ("Research", "A persistent secondary resource that accumulates across turns and is spent by "
                 "specific card effects."),
    ("Energy (typed)", "The per-turn resource Facilities generate. Some is typed (Authority, "
                        "Analysis, Ruin) — matching type likely matters for what it can pay for."),
    ("Danger / Critical", "Ability headers keyed to the Breach Track: Danger triggers at Breach 5+, "
                           "Critical triggers in the Critical band (Breach 7–9)."),
    ("Catastrophe", "An ability header tied to the aftermath of a Catastrophic Breach (Breach "
                     "hitting 10), seen on THE THING BELOW."),
]

def page_glossary():
    rows = "".join(
        f'<tr><td style="width:230px; font-weight:bold; color:#f4f1ea;">{term}</td><td>{defn}</td></tr>'
        for term, defn in GLOSSARY
    )
    body = f"""
    {sectag("04", "Glossary")}
    <h1 class="title">Keywords &amp; Glossary</h1>
    <div class="panel note">
      <div class="kicker">Working Definitions</div>
      <p>Derived from how these terms are actually used across both starter decks &mdash; not
      verbatim rules text from the design doc, which doesn't yet define them independently.
      Confirm and formalize wording during playtesting.</p>
    </div>
    <table class="ref" style="margin-top:6px;">
      <tr><th>Term</th><th>Working definition</th></tr>
      {rows}
    </table>
    """
    return shell(body, theme="neutral", page_no="05")


ANATOMY_ITEMS = [
    ("Name", "The card's unique title."),
    ("Cost", "Energy required to deploy or play it. Facilities show — (no cost)."),
    ("Type line", "Category and subtype — e.g. Personnel — Security. “Unique” "
                   "means only one copy of that exact card can be in play per player."),
    ("Category icon", "Quick visual read on card type: Personnel, Facility, Equipment, Protocol, or Anomaly."),
    ("Rules text", "What the card actually does, written in plain language plus keywords "
                    "from the glossary."),
    ("Power / Durability", "Attack strength / damage it can take before being destroyed. "
                            "Facilities and Protocols don't have this."),
]
ANATOMY_HTML = "".join(
    f'''<div style="display:flex; gap:14px; align-items:flex-start;">
      <div style="min-width:34px; height:34px; border-radius:50%; background:{ACCENTS["neutral"]["accent"]};
        color:#0b0b0d; font-weight:bold; display:flex; align-items:center; justify-content:center;
        font-size:16px;">{i+1}</div>
      <div><div style="font-weight:bold; color:#f4f1ea; font-size:16px; margin-bottom:2px;">{label}</div>
      <div style="font-size:14.5px; color:#a9a69d; line-height:1.4;">{desc}</div></div></div>'''
    for i, (label, desc) in enumerate(ANATOMY_ITEMS)
)


def page_anatomy():
    card_img = ROOT / "assets" / "cards" / "authority" / "site-security-officer.png"
    card_b64 = base64.b64encode(card_img.read_bytes()).decode("ascii")
    body = f"""
    {sectag("05", "Card Anatomy")}
    <h1 class="title">Reading a Card</h1>
    <div style="display:flex; gap:60px; align-items:flex-start; margin-top:10px;">
      <div style="position:relative; flex:0 0 auto;">
        <img src="data:image/png;base64,{card_b64}" style="width:420px; border-radius:18px; box-shadow:0 20px 50px rgba(0,0,0,.6);" />
      </div>
      <div style="flex:1; display:flex; flex-direction:column; gap:22px; padding-top:6px;">
        {ANATOMY_HTML}
      </div>
    </div>
    <p class="body" style="margin-top:26px;">Anomaly cards additionally show a <b>Threat rating</b> in
    place of a subtype (e.g. “Anomaly &mdash; Threat 3”) — the number other cards check
    when they target “Threat N or less.”</p>
    """
    return shell(body, theme="neutral", page_no="06")


def faction_page(theme, num, name, tagline, playstyle, composition, signature, total):
    accent = ACCENTS[theme]["accent"]
    comp_rows = "".join(f"<tr><td>{cat}</td><td>{count}</td></tr>" for cat, count in composition)
    sig_rows = "".join(
        f'''<div class="panel" style="flex:1; min-width:260px;">
        <div class="kicker" style="color:{accent};">{card}</div><p>{why}</p></div>'''
        for card, why in signature
    )
    body = f"""
    {sectag(num, "Faction Dossier")}
    <h1 class="title" style="color:{accent};">{name}</h1>
    <p class="lede">{tagline}</p>
    <p class="body">{playstyle}</p>

    <div style="display:flex; gap:36px; margin-top:20px;">
      <table class="ref" style="flex:0 0 380px;">
        <tr><th>Category</th><th>Count</th></tr>
        {comp_rows}
        <tr><td style="font-weight:bold; color:#f4f1ea;">Total</td>
            <td style="font-weight:bold; color:#f4f1ea;">{total}</td></tr>
      </table>
      <div style="flex:1;">
        <div class="kicker" style="color:{accent}; font-size:13px; letter-spacing:3px;
          text-transform:uppercase; margin-bottom:10px;">Signature Cards</div>
        <div style="display:flex; flex-wrap:wrap; gap:14px;">{sig_rows}</div>
      </div>
    </div>
    """
    return shell(body, theme=theme, page_no="07" if theme == "authority" else "08")


def page_quickref():
    accent = ACCENTS["neutral"]["accent"]
    body = f"""
    <div style="text-align:center; margin-top:40px;">{crest_svg(accent, size=90)}</div>
    <h1 class="title" style="text-align:center; margin-top:20px;">Quick Reference</h1>

    <table class="ref" style="margin-top:26px;">
      <tr><th>Rule</th><th>Standard</th></tr>
      <tr><td>Deck size</td><td>60+ cards (starters are exactly 60)</td></tr>
      <tr><td>Copy limit</td><td>Max 4 copies per card name, except Basic Facilities</td></tr>
      <tr><td>Starting state</td><td>20 Stability &middot; 7-card opening hand &middot; Breach 0 &middot; max hand size 7</td></tr>
      <tr><td>Turn order</td><td>Refresh &rarr; Breach &rarr; Draw &rarr; Main &rarr; Combat &rarr; Second Main &rarr; End</td></tr>
      <tr><td>Breach bands</td><td>0&ndash;2 Stable &middot; 3&ndash;4 Unstable &middot; 5&ndash;6 Danger &middot; 7&ndash;9 Critical &middot; 10 Catastrophic</td></tr>
      <tr><td>Catastrophic Breach</td><td>Each player −2 Stability, Contained Anomalies Released, each Exhausts one Ready Facility, Breach resets to 5</td></tr>
      <tr><td>Competitive side deck</td><td>15 cards</td></tr>
    </table>

    <div class="panel note" style="margin-top:30px;">
      <p style="text-align:center;">This is a design prototype. Costs, wording, and quantities are
      subject to playtesting. See DECKLISTS.md for the full card-by-card lists.</p>
    </div>
    """
    return shell(body, theme="neutral", page_no="09")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = [
        ("01_cover", page_cover()),
        ("02_orientation", page_orientation()),
        ("03_setup", page_setup()),
        ("04_breach", page_breach()),
        ("05_glossary", page_glossary()),
        ("06_anatomy", page_anatomy()),
        ("07_authority", faction_page(
            "authority", "06", "Authority", "SECURE. CONTAIN. PRESERVE.",
            "Control / midrange. Establish Personnel and Facilities, Suppress and Contain "
            "Anomalies, generate Research, and keep the shared Breach Track under control.",
            [("Personnel", 20), ("Facilities", 15), ("Equipment", 7), ("Protocols", 18)],
            [
                ("Director Evelyn Voss", "Anthem effect plus a card-draw engine off Stabilizing."),
                ("Chief Containment Officer Hale", "Guard locks down your Contained Anomalies while Ready."),
                ("Containment Team Alpha-9", "Big body that both Suppresses on entry and rewards Containing."),
                ("SITE-WIDE LOCKDOWN", "A board-wide reset button when Breach is spiraling."),
            ], 60)),
        ("08_ruin", faction_page(
            "ruin", "07", "Ruin", "RELEASE. EXPLOIT. TRANSCEND.",
            "Aggressive risk/release. Sacrifice Personnel, escalate Breach, exploit Anomalies, "
            "sabotage containment, and turn Catastrophic Breaches into offensive windows.",
            [("Personnel", 16), ("Anomalies", 15), ("Facilities", 13), ("Protocols", 16)],
            [
                ("The Unnamed Witness", "A modal payoff that can Release, draw, or push Breach on entry."),
                ("Subject ZERO", "Locked behind Breach 7+, then punishes Authority for Containing anything."),
                ("THE THING BELOW", "Gets cheaper as Breach climbs and comes back swinging after Catastrophe."),
                ("LET THEM OUT", "Forces Catastrophic Breach on your terms, then rewards you for it."),
            ], 60)),
        ("09_quickref", page_quickref()),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": PAGE_W, "height": PAGE_H})
        images = []
        for name, html in pages:
            page.set_content(html)
            page.wait_for_timeout(50)
            out_path = OUT_DIR / f"{name}.png"
            page.screenshot(path=str(out_path))
            images.append(out_path)
            print(f"rendered {out_path.name}")
        browser.close()

    imgs = [Image.open(p).convert("RGB") for p in images]
    imgs[0].save(OUT_PDF, save_all=True, append_images=imgs[1:], resolution=200.0)
    print(f"wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
