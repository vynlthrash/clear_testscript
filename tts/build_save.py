#!/usr/bin/env python3
"""Build the Tabletop Simulator save (.json) for the CONTAINMENT mockup.

Reads data/sheet_manifest.json (produced by render/render_cards.py and
render/build_sheets.py) and assembles a full TTS save file with:
  - Authority deck (60 cards, DeckCustom + CustomDeck sheet reference)
  - Ruin deck (60 cards)
  - Shared playmat (Custom_Board) with the Breach Track
  - Counters: Stability x2, Research x2, Breach x1
  - A rules notecard

Image URLs are left as REPLACE_ME_* placeholders (TTS needs each image
reachable by URL, or a local absolute file path for solo play) -- see
docs/TTS_SETUP.md for how to fill them in.
"""
import json
import random
import string
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "sheet_manifest.json"
OUT_PATH = ROOT / "tts" / "CONTAINMENT_Mockup.json"

_used_guids = set()

def guid():
    while True:
        g = "".join(random.choices(string.hexdigits.lower()[:16], k=6))
        if g not in _used_guids:
            _used_guids.add(g)
            return g

def transform(px=0, py=1, pz=0, rx=0, ry=0, rz=0, sx=1, sy=1, sz=1):
    return {
        "posX": px, "posY": py, "posZ": pz,
        "rotX": rx, "rotY": ry, "rotZ": rz,
        "scaleX": sx, "scaleY": sy, "scaleZ": sz,
    }

def custom_deck_entry(face_url, back_url, cols, rows):
    return {
        "FaceURL": face_url,
        "BackURL": back_url,
        "NumWidth": cols,
        "NumHeight": rows,
        "BackIsHidden": False,
        "UniqueBack": False,
        "Type": 0,
    }

def build_deck_object(deck_key, deck_id, deck_info, face_url, back_url, pos, rot):
    grid = deck_info["grid"]
    cols, rows = grid["cols"], grid["rows"]
    cd = {str(deck_key): custom_deck_entry(face_url, back_url, cols, rows)}

    contained = []
    deck_ids = []
    for entry in deck_info["order"]:
        card_id = deck_key * 100 + entry["index"]
        for _ in range(entry["qty"]):
            contained.append({
                "Name": "Card",
                "Transform": transform(pos[0], 1, pos[2], rot[0], rot[1], rot[2]),
                "Nickname": entry["name"],
                "Description": "",
                "GUID": guid(),
                "CardID": card_id,
                "CustomDeck": cd,
                "SidewaysCard": False,
            })
            deck_ids.append(card_id)

    return {
        "Name": "DeckCustom",
        "Transform": transform(pos[0], pos[1], pos[2], rot[0], rot[1], rot[2]),
        "Nickname": f"{deck_info['name']} Deck",
        "Description": "",
        "GUID": guid(),
        "DeckIDs": deck_ids,
        "CustomDeck": cd,
        "ContainedObjects": contained,
    }

def build_counter(nickname, value, pos):
    return {
        "Name": "Counter",
        "Transform": transform(pos[0], pos[1], pos[2]),
        "Nickname": nickname,
        "Description": "",
        "GUID": guid(),
        "Counter": {"value": value},
    }

def build_board(image_url, pos, scale):
    return {
        "Name": "Custom_Board",
        "Transform": transform(pos[0], pos[1], pos[2], sx=scale[0], sy=1, sz=scale[1]),
        "Nickname": "Playmat - Breach Track",
        "Description": "",
        "GUID": guid(),
        "Locked": True,
        "CustomImage": {
            "ImageURL": image_url,
            "ImageSecondaryURL": "",
            "WidthScale": 0,
        },
    }

def build_notecard(pos):
    text = (
        "CONTAINMENT -- Quick Reference (v0.1 prototype)\n\n"
        "Deck size: 60+ cards (these starters are exactly 60). Max 4 copies of a "
        "card name, except Basic Facilities.\n"
        "Start: 20 Stability, 7-card opening hand, Breach 0, max hand size 7.\n\n"
        "Turn order: Refresh -> Breach -> Draw -> Main -> Combat -> Second Main -> End.\n\n"
        "Breach Track (0-10, shared): 0-2 Stable | 3-4 Unstable | 5-6 Danger | "
        "7-9 Critical | 10 Catastrophic Breach.\n"
        "Catastrophic Breach (at 10): each player loses 2 Stability, all Contained "
        "Anomalies are Released, each player Exhausts one Ready Facility, then "
        "Breach resets to 5.\n\n"
        "Resources: normally deploy one Facility per turn. Facilities generate "
        "Energy. Research is a persistent secondary resource.\n"
        "Signature systems: Breach Track, Suppression, Containment/Release, "
        "Threat ratings, Research.\n\n"
        "Authority (Control/Midrange): Secure. Contain. Preserve.\n"
        "Ruin (Aggressive Risk/Release): Release. Exploit. Transcend.\n\n"
        "Competitive side deck: 15 cards. This is a design prototype -- costs, "
        "wording and quantities are subject to playtesting."
    )
    return {
        "Name": "Notecard",
        "Transform": transform(pos[0], pos[1], pos[2]),
        "Nickname": "CONTAINMENT - Quick Reference",
        "Description": text,
        "GUID": guid(),
    }

def main():
    manifest = json.loads(MANIFEST_PATH.read_text())
    decks = manifest["decks"]

    authority = build_deck_object(
        1, "authority", decks["authority"],
        "REPLACE_ME_AUTHORITY_SHEET_URL", "REPLACE_ME_AUTHORITY_BACK_URL",
        pos=(-11, 1.5, 11), rot=(0, 180, 0),
    )
    ruin = build_deck_object(
        2, "ruin", decks["ruin"],
        "REPLACE_ME_RUIN_SHEET_URL", "REPLACE_ME_RUIN_BACK_URL",
        pos=(11, 1.5, -11), rot=(0, 0, 0),
    )

    board = build_board("REPLACE_ME_PLAYMAT_URL", pos=(0, 1, 0), scale=(38, 24.85))

    counters = [
        build_counter("Authority Stability (start 20)", 20, (-16, 1.5, 6)),
        build_counter("Ruin Stability (start 20)", 20, (16, 1.5, -6)),
        build_counter("Authority Research", 0, (-16, 1.5, 3)),
        build_counter("Ruin Research", 0, (16, 1.5, -3)),
        build_counter("Breach Track", 0, (0, 1.5, 0)),
    ]

    notecard = build_notecard(pos=(0, 3, 16))

    save = {
        "SaveName": "CONTAINMENT - Authority vs Ruin Mockup",
        "GameMode": "",
        "Date": datetime.now(timezone.utc).isoformat(),
        "Table": "Table_Poker",
        "TableURL": "",
        "Sky": "",
        "SkyURL": "",
        "Note": "CONTAINMENT starter-deck mockup. See docs/TTS_SETUP.md before loading.",
        "Rules": "",
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "XmlUI": "",
        "CustomUIAssets": [],
        "LuaScript": "",
        "LuaScriptState": "",
        "ObjectStates": [board, authority, ruin, notecard] + counters,
        "TabStates": {},
        "VersionNumber": "",
    }

    OUT_PATH.write_text(json.dumps(save, indent=2))
    print(f"wrote {OUT_PATH} ({len(json.dumps(save))} bytes)")
    print(f"Authority deck: {len(authority['DeckIDs'])} cards, Ruin deck: {len(ruin['DeckIDs'])} cards")

if __name__ == "__main__":
    main()
