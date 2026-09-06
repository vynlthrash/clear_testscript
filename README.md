# CONTAINMENT — Tabletop Simulator Mockup

A working Tabletop Simulator prototype for **CONTAINMENT**, an Authority vs.
Ruin card game (two 60-card starter decks, a shared 0–10 Breach Track,
Suppression / Containment / Release, and Research as a secondary resource).

Source rulebook: `docs/source/CONTAINMENT_Authority_Ruin_Starter_Decks_v0.1.docx`.
Human-readable decklists: `docs/DECKLISTS.md`.

## What's here

```
data/cards.json          Structured card data for both decks (source of truth)
data/sheet_manifest.json Generated: maps each card to its sheet grid index
render/                  Scripts that turn cards.json into images
  render_cards.py        Renders all 56 unique card faces + 2 card backs (Playwright)
  build_sheets.py        Composites card faces into TTS sprite sheets
  render_board.py        Renders the shared playmat / Breach Track board
  render_decklist_md.py  Regenerates docs/DECKLISTS.md from cards.json
assets/cards/<deck>/      Individual card face PNGs
assets/sheets/            Sheet images, card backs, and playmat (what TTS actually loads)
tts/build_save.py         Assembles the full Tabletop Simulator save JSON
tts/CONTAINMENT_Mockup.json   The generated TTS save (needs image URLs — see below)
docs/TTS_SETUP.md         How to get this loaded and running in Tabletop Simulator
```

## Quick start

1. Read `docs/TTS_SETUP.md` — you need to host (or locally path) 5 image
   files and patch their URLs into `tts/CONTAINMENT_Mockup.json` before TTS
   can load them.
2. Drop the patched `CONTAINMENT_Mockup.json` into your TTS Saves folder and
   load it.

## Regenerating everything from scratch

```bash
pip install playwright pillow && python3 -c "from playwright.sync_api import sync_playwright"  # browser is pre-fetched at /opt/pw-browsers in this environment
python3 render/render_cards.py
python3 render/build_sheets.py
python3 render/render_board.py
python3 render/render_decklist_md.py
python3 tts/build_save.py
```

Edit `data/cards.json` first if you're adjusting costs/text/quantities after
playtesting — everything downstream regenerates from it.

## Design notes

- Card art is a clean, readable placeholder style (flat color panels + a
  simple category icon: person / building / wrench / document), not final
  illustration — meant for playtesting layout, wording, and pacing, not
  final presentation.
- Authority deck = 27 unique cards across Personnel/Facilities/Equipment/
  Protocols; Ruin deck = 29 unique cards across Personnel/Anomalies/
  Facilities/Protocols. Both decks total exactly 60 cards including
  duplicates, matching the rulebook's Core Rules Reference.
- The playmat encodes the shared Breach Track bands (0–2 Stable, 3–4
  Unstable, 5–6 Danger, 7–9 Critical, 10 Catastrophic) directly from the
  rulebook.
