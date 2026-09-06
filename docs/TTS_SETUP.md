# Loading the CONTAINMENT mockup into Tabletop Simulator

This repo builds a full Tabletop Simulator save (`tts/CONTAINMENT_Mockup.json`)
containing both 60-card starter decks (Authority, Ruin), a shared playmat with
the Breach Track, and counters for Stability / Research / Breach.

TTS loads card and board art from a URL (or a local file path, for solo
testing on your own machine). The generated save file has 5 placeholder
strings where those URLs go. You must fill them in before loading.

## 1. The 5 images to host

All in `assets/sheets/`:

| Placeholder in `CONTAINMENT_Mockup.json` | File |
|---|---|
| `REPLACE_ME_AUTHORITY_SHEET_URL` | `authority-sheet.png` |
| `REPLACE_ME_AUTHORITY_BACK_URL` | `authority-back.png` |
| `REPLACE_ME_RUIN_SHEET_URL` | `ruin-sheet.png` |
| `REPLACE_ME_RUIN_BACK_URL` | `ruin-back.png` |
| `REPLACE_ME_PLAYMAT_URL` | `playmat.png` |

## 2. Option A — host them (works for multiplayer / sharing)

1. Upload the 5 files to an image host that gives a direct `.png` link.
   [imgur.com/upload](https://imgur.com/upload) works with no account —
   after uploading, right-click each image and "Copy image address" (the
   link must end in `.png`, not point to an imgur *page*).
2. Open `tts/CONTAINMENT_Mockup.json` in a text editor and replace each
   `REPLACE_ME_*` token with the matching URL (find-and-replace, keep the
   quotes around it).
3. Save the file.

## 2. Option B — local file paths (solo testing only, single machine)

Replace each placeholder with an absolute path to the file on your machine,
prefixed with `file:///`, e.g.:

- Windows: `file:///C:/Users/you/clear_testscript/assets/sheets/authority-sheet.png`
- Mac/Linux: `file:///Users/you/clear_testscript/assets/sheets/authority-sheet.png`

This will NOT work for other players in multiplayer — they don't have the
file. Use Option A to share the mockup.

## 3. Load it in Tabletop Simulator

Copy `CONTAINMENT_Mockup.json` into your TTS saves folder:

- Windows: `Documents\My Games\Tabletop Simulator\Saves\`
- Mac: `~/Library/Tabletop Simulator/Saves/`
- Linux: `~/.local/share/Tabletop Simulator/Saves/`

Launch Tabletop Simulator → **Games → Load** → select
"CONTAINMENT - Authority vs Ruin Mockup".

## 4. What's on the table

- **Authority deck** (60 cards, blue back) near one edge, face down.
- **Ruin deck** (60 cards, red back) near the opposite edge, face down.
- **Playmat** with two faction zones and the shared 0–10 Breach Track
  painted down the middle (Stable / Unstable / Danger / Critical /
  Catastrophic bands).
- **5 counters**: Authority Stability (starts at 20), Ruin Stability
  (starts at 20), Authority Research, Ruin Research, and a shared Breach
  counter — right-click → or use the +/- on each to track state as you play.
- **A rules notecard** with the turn order and Breach bands for quick
  reference (double-click it to read).

Everything is freely draggable — if the decks or counters don't line up with
the playmat exactly the way you'd like, just move them; TTS doesn't need
them to be pixel-perfect.

## 5. Regenerating after edits

If you change card text/costs/quantities in `data/cards.json` (e.g. after
playtesting), rebuild everything:

```bash
python3 render/render_cards.py   # re-renders all 56 unique card faces + backs
python3 render/build_sheets.py   # re-composites the two sheet images
python3 render/render_board.py   # re-renders the playmat (only needed if you change render_board.py)
python3 tts/build_save.py        # rebuilds CONTAINMENT_Mockup.json (placeholders reset each time)
```

You'll need to re-upload the changed sheet image(s) and patch the URL(s)
again after regenerating.
