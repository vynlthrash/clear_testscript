#!/usr/bin/env python3
"""Renders the CONTAINMENT comprehensive rulebook (physical/print game),
v1.0 — a completed ruleset built on top of the v0.1 design draft's
explicit rules (deck size, copy limit, starting state, Breach bands,
turn order) plus a full set of firm rulings for everything the draft
left unstated (win condition, zones, combat, Suppress/Contain/Release,
keyword mechanics), modeled loosely on Magic: The Gathering per the
designer's direction. Grounded against every card's printed text in
data/cards.json so no ruling here contradicts an actual card.
"""
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
NEUTRAL = ACCENTS["neutral"]["accent"]


def flow_row(items, color=NEUTRAL, numbered=True):
    return "".join(
        f'''<div style="flex:1; min-width:180px; max-width:100%; background:#141416; border:1px solid #2a2a2e;
            border-radius:6px; padding:14px 16px; overflow-wrap:break-word; word-break:break-word;">
            <div style="color:{color}; font-weight:bold; font-size:14px; letter-spacing:2px;
              text-transform:uppercase; margin-bottom:6px;">{(str(i + 1) + '. ') if numbered else ''}{name}</div>
            <div style="font-size:13.5px; color:#a9a69d; line-height:1.4;">{desc}</div></div>'''
        for i, (name, desc) in enumerate(items)
    )


def numbered_list(items, color=NEUTRAL):
    return "".join(
        f'''<div style="display:flex; gap:14px; align-items:flex-start; margin-bottom:18px;">
          <div style="min-width:34px; height:34px; border-radius:50%; background:{color};
            color:#0b0b0d; font-weight:bold; display:flex; align-items:center; justify-content:center;
            font-size:16px; flex:0 0 auto;">{i + 1}</div>
          <div style="overflow-wrap:break-word; word-break:break-word;">
          <div style="font-weight:bold; color:#f4f1ea; font-size:16px; margin-bottom:2px;">{label}</div>
          <div style="font-size:14.5px; color:#a9a69d; line-height:1.45;">{desc}</div></div></div>'''
        for i, (label, desc) in enumerate(items)
    )


# ---------------------------------------------------------------- cover
def page_cover():
    accent = NEUTRAL
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
.crestwrap {{ position:absolute; top:300px; left:50%; transform:translateX(-50%); }}
h1.big {{ position:absolute; top:610px; left:50%; transform:translateX(-50%);
  font-size:130px; font-weight:900; letter-spacing:4px; color:#f4f1ea; text-transform:uppercase;
  text-align:center; width:100%; text-shadow:0 4px 30px rgba(0,0,0,.6); }}
.sub {{ position:absolute; top:770px; left:50%; transform:translateX(-50%);
  font-size:30px; letter-spacing:10px; color:{accent}; text-transform:uppercase; font-weight:bold; }}
.factions {{ position:absolute; top:870px; left:50%; transform:translateX(-50%);
  display:flex; gap:60px; font-family:'DejaVu Sans Mono',monospace; font-size:15px;
  letter-spacing:3px; color:#8a877e; }}
.factions .a {{ color:#5fa8d3; }} .factions .r {{ color:#d3604f; }}
.subtitle2 {{ position:absolute; top:960px; left:50%; transform:translateX(-50%);
  font-size:17px; letter-spacing:3px; color:#6f6c64; text-transform:uppercase; }}
.footer {{ position:absolute; bottom:110px; left:0; right:0; text-align:center; }}
.footer .tag {{ font-size:14px; letter-spacing:4px; color:#6f6c64; margin-bottom:10px; text-transform:uppercase;}}
.footer .bc {{ display:flex; justify-content:center; gap:3px; }}
.footer .bc div {{ width:3px; background:#6f6c64; }}
</style></head><body><div class="page">
  <div class="frame"><div class="bracket tl"></div><div class="bracket tr"></div>
    <div class="bracket bl"></div><div class="bracket br"></div></div>
  <div class="stamp">Restricted &middot; PCD Field Manual</div>
  <div class="crestwrap">{crest_svg(accent, size=170)}</div>
  <h1 class="big">Containment</h1>
  <div class="sub">Authority vs. Ruin</div>
  <div class="factions">
    <span class="a">SECURE // CONTAIN // PRESERVE</span>
    <span>&middot;</span>
    <span class="r">RELEASE // EXPLOIT // TRANSCEND</span>
  </div>
  <div class="subtitle2">Comprehensive Rules</div>
  <div class="footer">
    <div class="tag">Doc PCD&#8209;RB&#8209;002 &nbsp;&bull;&nbsp; Rev v1.0 &nbsp;&bull;&nbsp; Design Prototype</div>
    <div class="bc">{"".join(f'<div style="height:{h}px"></div>' for h in [22,10,26,14,8,22,18,10,26,14,22,8,18,26,10,22])}</div>
  </div>
</div></body></html>"""


DOC = dict(doc_code="PCD-RB-002", running_title="CONTAINMENT COMPREHENSIVE RULES")


# ---------------------------------------------------------------- 01 orientation
def page_orientation():
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

    <p class="body" style="margin-top:18px;">If you've played Magic: the Gathering, most of the
    scaffolding here will feel familiar &mdash; Stability is your life total, Energy is your mana,
    Facilities are your lands, Personnel and Anomalies are your creatures. The Breach Track,
    Suppression, and Containment are new systems layered on top of that scaffolding, and they're
    what actually makes Containment its own game.</p>
    """
    return shell(body, theme="neutral", page_no="02", **DOC)


# ---------------------------------------------------------------- 02 golden rules
def page_golden_rules():
    golden = [
        ("A card's printed text always wins.", "If anything in this rulebook conflicts with the "
         "exact wording on a card, the card is right and this book is wrong. This book exists to "
         "cover what cards don't spell out, not to override what they do."),
        ("“You” means that card's controller.", "On any card, “you” and “your” refer to "
         "whoever controls that card at the time — not necessarily whoever owns it (a Contained "
         "or Released Anomaly can change controller over the course of a game)."),
        ("Effects happen in the order they're written.", "Read a card's rules text left to right, "
         "top to bottom, resolving each instruction before moving to the next."),
        ("You can't do the impossible.", "If a cost or instruction can't be fully paid or performed "
         "(not enough Energy, no legal target, no Facility with open Capacity), that action simply "
         "can't be taken — nothing happens instead."),
    ]
    body = f"""
    {sectag("02", "Golden Rules")}
    <h1 class="title">Golden Rules &amp; Objective</h1>

    {numbered_list(golden)}

    <div class="panel note" style="margin-top:6px;">
      <div class="kicker">Objective</div>
      <p style="font-size:16px;"><b>You lose the game immediately if your Stability is reduced to
      0 or lower, or if you're required to draw a card while your deck is empty.</b> You win when
      your opponent loses. There is no other win condition — Containment is not a race to a
      separate finish line, it's a fight over how long you can keep standing.</p>
    </div>
    """
    return shell(body, theme="neutral", page_no="03", **DOC)


# ---------------------------------------------------------------- 03 zones & resources
def page_zones():
    zones = [
        ("Deck", "Your shuffled 60 cards. Face-down, unseen by either player except by card effect."),
        ("Hand", "Cards you've drawn but not yet played. Hidden from your opponent. Maximum 7 at your End Phase."),
        ("Battlefield", "The shared play area. Personnel, Anomalies, Facilities, and Equipment you "
                         "control sit here, face up, visible to both players."),
        ("Contained", "A sub-zone at a specific Containment Facility. Anomalies moved here by a "
                       "Contain effect leave the battlefield as active threats but stay in play, "
                       "under their containing player's control, counting against that Facility's Capacity."),
        ("Discard Pile", "Face-up. Destroyed or sacrificed cards, and Protocols/Responses after they "
                          "resolve, go here. Public information either player can look through."),
        ("Breach Track", "Shared — neither player owns it. A single counter from 0 to 10 tracking "
                          "the crisis both decks are pushing on."),
    ]
    zone_rows = "".join(f"<tr><td style='width:200px; font-weight:bold; color:#f4f1ea;'>{n}</td><td>{d}</td></tr>" for n, d in zones)

    body = f"""
    {sectag("03", "Zones &amp; Resources")}
    <h1 class="title">Where Everything Lives</h1>

    <table class="ref">
      <tr><th>Zone</th><th>What's there</th></tr>
      {zone_rows}
    </table>

    <p class="body" style="margin-top:20px;"><b>Three numbers you're always tracking:</b></p>
    <div style="display:flex; gap:20px;">
      <div class="panel" style="flex:1;">
        <div class="kicker">Stability</div>
        <p>Your life total. Starts at 20. No hard cap — Stabilize effects can push it above 20
        unless a card says otherwise. Hits 0 or below, you lose.</p>
      </div>
      <div class="panel" style="flex:1;">
        <div class="kicker">Energy</div>
        <p>Generated by Exhausting Facilities. Some is typed (Authority, Analysis, Ruin) — only
        spend typed Energy on costs that accept that type or generic costs. Unspent Energy empties
        at your End Phase; it does not carry into your next turn.</p>
      </div>
      <div class="panel" style="flex:1;">
        <div class="kicker">Research</div>
        <p>A persistent resource. Unlike Energy, it never empties on its own — it only goes down
        when a card spends it.</p>
      </div>
    </div>

    <p class="body" style="margin-top:20px;"><b>Card types, at sorcery or response speed:</b></p>
    <table class="ref">
      <tr><th>Type</th><th>Behavior</th></tr>
      <tr><td>Personnel / Anomaly</td><td>Stays on the battlefield. Has Power/Durability, can attack and block.</td></tr>
      <tr><td>Facility</td><td>Stays on the battlefield. Generates Energy when Exhausted. At most one deployed per turn.</td></tr>
      <tr><td>Equipment</td><td>Stays on the battlefield, attached to one Personnel you control (never an Anomaly — every
      printed Equipment specifically says “Assigned Personnel”). If that Personnel leaves play, the Equipment
      stays on the battlefield unattached until you pay its cost again to reassign it.</td></tr>
      <tr><td>Protocol / Directive</td><td>Protocols resolve once and go to the discard pile, like a sorcery.
      Directives stay in play as an ongoing effect once resolved, like an enchantment.</td></tr>
      <tr><td>Response</td><td>Resolves once and goes to the discard pile — but can be played almost any
      time, including during combat or your opponent's turn, not just your Main phase.</td></tr>
    </table>
    """
    return shell(body, theme="neutral", page_no="04", **DOC)


# ---------------------------------------------------------------- 04 setup
def page_setup():
    body = f"""
    {sectag("04", "Setup")}
    <h1 class="title">Before The First Turn</h1>
    <table class="ref">
      <tr><th style="width:60px;">#</th><th>Step</th></tr>
      <tr><td>1</td><td>Each player shuffles their 60-card deck.</td></tr>
      <tr><td>2</td><td>Set both players' Stability to 20.</td></tr>
      <tr><td>3</td><td>Set the shared Breach Track to 0.</td></tr>
      <tr><td>4</td><td>Each player draws a 7-card opening hand.</td></tr>
      <tr><td>5</td><td>Decide who takes the first turn (die roll, coin flip, whatever you like).</td></tr>
    </table>

    <div class="panel note" style="margin-top:16px;">
      <div class="kicker">Deckbuilding Reminder</div>
      <p>60+ cards per deck. Maximum 4 copies of any card with the same name, except Basic
      Facilities, which are unlimited. A 15-card competitive side deck is used for game two and
      three of a match, swapped in between games exactly like a sideboard.</p>
    </div>
    """
    return shell(body, theme="neutral", page_no="05", **DOC)


# ---------------------------------------------------------------- 05 turn structure
PHASES = [
    ("Refresh", "Ready every Exhausted Personnel, Facility, and Equipment you control. This "
                "happens automatically — no player may respond to it."),
    ("Breach", "Check the current Breach Track band and resolve any “at your Breach Phase” "
               "abilities. If Breach is at 10, resolve a Catastrophic Breach right now (see The "
               "Breach Track)."),
    ("Draw", "Draw one card."),
    ("Main", "Play at sorcery speed: deploy up to one Facility, deploy any Personnel, Anomalies, "
             "or Equipment you can afford, and play Protocols or Directives."),
    ("Combat", "Declare attackers, then your opponent declares blockers, then damage is dealt "
               "(see Combat)."),
    ("Second Main", "Identical rules to Main — anything left in hand you can still afford."),
    ("End", "If you have more than 7 cards in hand, discard down to 7."),
]

def page_turns():
    body = f"""
    {sectag("05", "Turn Structure")}
    <h1 class="title">Seven Phases, Every Turn</h1>
    <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:6px;">
      {flow_row(PHASES)}
    </div>

    <div class="panel note" style="margin-top:22px;">
      <div class="kicker">Sorcery Speed vs. Response Speed</div>
      <p>Protocols and Directives can only be played during your own Main or Second Main phase,
      and only when nothing else is currently happening. Responses are the exception — true to
      their name, they can be played almost any time: during combat, during your opponent's turn,
      or reacting to another card as it happens.</p>
    </div>

    <p class="body" style="margin-top:16px;">A Personnel, Anomaly, or Facility can't attack or use
    an Exhaust-cost ability the turn it's deployed unless it has <b>Rapid Deployment</b> — it needs
    to have been under your control since the start of your most recent turn first.</p>
    """
    return shell(body, theme="neutral", page_no="06", **DOC)


# ---------------------------------------------------------------- 06 combat
def page_combat():
    steps = [
        ("Declare Attackers", "You choose any number of your Ready Personnel/Anomalies that "
                               "aren't affected by summoning restrictions and Exhaust them to attack. "
                               "Attacks target your opponent by default."),
        ("Declare Blockers", "Your opponent assigns any number of their Ready Personnel/Anomalies "
                              "to block individual attackers. Blocking doesn't Exhaust the blocker. "
                              "An attacker can be blocked by more than one card."),
        ("Damage", "Each attacker and everything blocking it deal damage equal to their Power to "
                    "each other, simultaneously. A card that's taken damage equal to or greater than "
                    "its Durability this turn is destroyed and goes to its owner's discard pile."),
        ("Unblocked Damage", "An attacker with no blockers deals its Power directly to the "
                              "defending player's Stability."),
    ]
    body = f"""
    {sectag("06", "Combat")}
    <h1 class="title">Attacking &amp; Blocking</h1>
    {numbered_list(steps)}

    <div style="display:flex; gap:24px; margin-top:8px;">
      <div class="panel" style="flex:1;">
        <div class="kicker">Overwhelm</div>
        <p>If a card with Overwhelm is blocked, its controller assigns just enough damage to
        destroy the blocker(s) first, then sends any leftover damage through to the defending
        player's Stability.</p>
      </div>
      <div class="panel" style="flex:1;">
        <div class="kicker">Rapid Deployment</div>
        <p>Lets a card attack (or use an Exhaust-cost ability) the same turn it's deployed,
        skipping the usual wait.</p>
      </div>
    </div>
    """
    return shell(body, theme="neutral", page_no="07", **DOC)


# ---------------------------------------------------------------- 07 breach track
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
    {sectag("07", "The Breach Track")}
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
    A <b>Danger</b>&#8209;labeled ability is live while Breach is 5 or higher; a <b>Critical</b>&#8209;labeled
    ability is live in the Critical band specifically (Breach 7&ndash;9); a <b>Catastrophe</b>&#8209;labeled
    ability triggers right after a Catastrophic Breach finishes resolving.</p>
    """
    return shell(body, theme="neutral", page_no="08", **DOC)


# ---------------------------------------------------------------- 08 suppression/contain/release
def page_containment():
    cycle = [
        ("Deploy", "Ruin plays an Anomaly onto the battlefield. It attacks and blocks like any Personnel."),
        ("Suppress", "Authority applies Suppression counters to it. Once it has 1+, it's “Suppressed.” "
                      "Suppression counters stay on it until removed by name — they don't clear on their own."),
        ("Contain", "While Suppressed, Authority pays the Anomaly's printed Contain cost at a Containment "
                     "Facility with open Capacity, moving it to the Contained zone under Authority's control."),
        ("Release", "A Release effect returns it to the battlefield as an active threat, under the control "
                     "of whoever originally cast it — usually spiking Breach as the cost of letting it out."),
    ]
    body = f"""
    {sectag("08", "Suppression &amp; Containment")}
    <h1 class="title">The Core Loop</h1>
    <p class="lede">This is Containment's signature system — everything else in the game exists to
    push this cycle one way or the other.</p>

    <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:16px;">
      {flow_row(cycle, numbered=False)}
    </div>

    <table class="ref" style="margin-top:24px;">
      <tr><th style="width:170px;">Rule</th><th>Detail</th></tr>
      <tr><td>Who can Suppress</td><td>Either player can target any Anomaly with a Suppress effect,
      but in practice it's almost always Authority weakening an opponent's Anomaly.</td></tr>
      <tr><td>Containing requires</td><td>The Anomaly must be Suppressed, and you need a Containment
      Facility you control with Capacity still open. Pay the cost printed on the Anomaly (e.g.
      “Contain — 3”) in Energy.</td></tr>
      <tr><td>While Contained</td><td>The Anomaly isn't on the battlefield — it can't attack, block,
      or be targeted by battlefield-only effects. It counts against its Facility's Capacity.</td></tr>
      <tr><td>Releasing</td><td>Returns the Anomaly to the battlefield under its original caster's
      control. Any “Released —” ability on the Anomaly triggers now, unless the Facility it was
      Contained at disables Released abilities (Standard Containment Cell C-14).</td></tr>
      <tr><td>Guard</td><td>A card with Guard stops <i>opponents</i> from Releasing Contained
      Anomalies you control while it's Ready. It doesn't stop you from Releasing your own.</td></tr>
    </table>
    """
    return shell(body, theme="neutral", page_no="09", **DOC)


# ---------------------------------------------------------------- 09 glossary
GLOSSARY = [
    ("Exhaust", "Tap a card to pay an activated ability's cost, or force a target into that same "
                "tapped-down state so it can't act. Written both as a cost (“Exhaust: …”) "
                "and as an effect (“Exhaust target Anomaly”)."),
    ("Ready", "The reverse of Exhaust — a card returns to an untapped, usable state and can "
              "attack, block, or activate again."),
    ("Suppress N / Suppressed", "Apply N Suppression counters to an Anomaly. 1 or more counters "
                                 "makes it “Suppressed.” See Suppression &amp; Containment."),
    ("Contain / Contained", "Move a Suppressed Anomaly into your control at a Containment "
                             "Facility, paying its printed Contain cost. See Suppression &amp; Containment."),
    ("Release / Released", "Return a Contained Anomaly to the battlefield under its original "
                            "caster's control. See Suppression &amp; Containment."),
    ("Threat N", "A fixed rating on Anomalies (2–5) used as a targeting restriction by other "
                 "cards, e.g. “Exhaust target Anomaly with Threat 2 or less.”"),
    ("Capacity N", "How many Anomalies a Containment Facility can hold Contained at once."),
    ("Stabilize N", "Restore N Stability to yourself. Same effect as “restore N Stability” — "
                     "different cards use either wording."),
    ("Sacrifice", "Remove a card you control from play, usually as a cost, to trigger an effect."),
    ("Rapid Deployment", "This card can attack, or use an Exhaust-cost ability, the turn it's "
                          "deployed — it skips the usual one-turn wait."),
    ("Guard", "While this card is Ready, Contained Anomalies you control can't be Released by an "
              "opponent's effects."),
    ("Overwhelm", "If blocked, assign just enough damage to destroy the blocker(s), then send any "
                  "leftover damage through to the defending player."),
    ("Clearance", "A named status a specific card grants (currently only Black-Level Access Card) "
                  "— its effect is written out on the card that grants it, not defined separately here."),
    ("Research", "A persistent secondary resource. Unlike Energy, it never empties on its own."),
    ("Energy (typed)", "The per-turn resource Facilities generate. Some is typed (Authority, "
                        "Analysis, Ruin); spend typed Energy only on costs that accept that type or "
                        "generic costs. Empties at your End Phase."),
    ("Danger / Critical", "Ability headers keyed to the Breach Track: Danger is live at Breach 5+, "
                           "Critical is live in the Critical band (Breach 7–9)."),
    ("Catastrophe", "An ability header that triggers right after a Catastrophic Breach (Breach "
                     "hitting 10) finishes resolving."),
]

def page_glossary():
    rows = "".join(
        f'<tr><td style="width:230px; font-weight:bold; color:#f4f1ea;">{term}</td><td>{defn}</td></tr>'
        for term, defn in GLOSSARY
    )
    body = f"""
    {sectag("09", "Glossary")}
    <h1 class="title">Keywords &amp; Glossary</h1>
    <p class="body">Every term below is grounded in how it's actually used across both starter
    decks. Suppress, Contain, and Release get their own dedicated section — this list gives the
    short version and cross-references it.</p>
    <table class="ref" style="margin-top:6px;">
      <tr><th>Term</th><th>Definition</th></tr>
      {rows}
    </table>
    """
    return shell(body, theme="neutral", page_no="10", **DOC)


# ---------------------------------------------------------------- 10 card anatomy
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
      <div style="min-width:34px; height:34px; border-radius:50%; background:{NEUTRAL};
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
    {sectag("10", "Card Anatomy")}
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
    return shell(body, theme="neutral", page_no="11", **DOC)


# ---------------------------------------------------------------- faction dossiers
def faction_page(theme, num, page_no, name, tagline, playstyle, composition, signature, total):
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
    return shell(body, theme=theme, page_no=page_no, **DOC)


# ---------------------------------------------------------------- quick reference
def page_quickref():
    accent = NEUTRAL
    body = f"""
    <div style="text-align:center; margin-top:30px;">{crest_svg(accent, size=80)}</div>
    <h1 class="title" style="text-align:center; margin-top:16px;">Quick Reference</h1>

    <table class="ref" style="margin-top:20px;">
      <tr><th>Rule</th><th>Standard</th></tr>
      <tr><td>Deck size</td><td>60+ cards (starters are exactly 60); max 4 copies per name except Basic Facilities</td></tr>
      <tr><td>Starting state</td><td>20 Stability &middot; 7-card opening hand &middot; Breach 0 &middot; max hand size 7</td></tr>
      <tr><td>Losing</td><td>Stability reaches 0 or below, or you must draw from an empty deck</td></tr>
      <tr><td>Turn order</td><td>Refresh &rarr; Breach &rarr; Draw &rarr; Main &rarr; Combat &rarr; Second Main &rarr; End</td></tr>
      <tr><td>Breach bands</td><td>0&ndash;2 Stable &middot; 3&ndash;4 Unstable &middot; 5&ndash;6 Danger &middot; 7&ndash;9 Critical &middot; 10 Catastrophic</td></tr>
      <tr><td>Catastrophic Breach</td><td>Each player &minus;2 Stability, Contained Anomalies Released, each Exhausts one Ready Facility, Breach resets to 5</td></tr>
      <tr><td>Suppress &rarr; Contain &rarr; Release</td><td>Weaken an Anomaly, pay its Contain cost at an open Containment Facility, or let it back out later</td></tr>
      <tr><td>Facility limit</td><td>One deployed per turn</td></tr>
      <tr><td>Energy</td><td>Empties at your End Phase — Research does not</td></tr>
      <tr><td>Competitive side deck</td><td>15 cards</td></tr>
    </table>

    <div class="panel note" style="margin-top:26px;">
      <p style="text-align:center;">This is a design prototype. Costs, wording, and quantities are
      subject to playtesting. See DECKLISTS.md for the full card-by-card lists.</p>
    </div>
    """
    return shell(body, theme="neutral", page_no="12", **DOC)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = [
        ("00_cover", page_cover()),
        ("01_orientation", page_orientation()),
        ("02_golden_rules", page_golden_rules()),
        ("03_zones", page_zones()),
        ("04_setup", page_setup()),
        ("05_turns", page_turns()),
        ("06_combat", page_combat()),
        ("07_breach", page_breach()),
        ("08_containment", page_containment()),
        ("09_glossary", page_glossary()),
        ("10_anatomy", page_anatomy()),
        ("11_authority", faction_page(
            "authority", "11", "13", "Authority", "SECURE. CONTAIN. PRESERVE.",
            "Control / midrange. Establish Personnel and Facilities, Suppress and Contain "
            "Anomalies, generate Research, and keep the shared Breach Track under control.",
            [("Personnel", 20), ("Facilities", 15), ("Equipment", 7), ("Protocols", 18)],
            [
                ("Director Evelyn Voss", "Anthem effect plus a card-draw engine off Stabilizing."),
                ("Chief Containment Officer Hale", "Guard locks down your Contained Anomalies while Ready."),
                ("Containment Team Alpha-9", "Big body that both Suppresses on entry and rewards Containing."),
                ("SITE-WIDE LOCKDOWN", "A board-wide reset button when Breach is spiraling."),
            ], 60)),
        ("12_ruin", faction_page(
            "ruin", "12", "14", "Ruin", "RELEASE. EXPLOIT. TRANSCEND.",
            "Aggressive risk/release. Sacrifice Personnel, escalate Breach, exploit Anomalies, "
            "sabotage containment, and turn Catastrophic Breaches into offensive windows.",
            [("Personnel", 16), ("Anomalies", 15), ("Facilities", 13), ("Protocols", 16)],
            [
                ("The Unnamed Witness", "A modal payoff that can Release, draw, or push Breach on entry."),
                ("Subject ZERO", "Locked behind Breach 7+, then punishes Authority for Containing anything."),
                ("THE THING BELOW", "Gets cheaper as Breach climbs and comes back swinging after Catastrophe."),
                ("LET THEM OUT", "Forces Catastrophic Breach on your terms, then rewards you for it."),
            ], 60)),
        ("13_quickref", page_quickref()),
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
