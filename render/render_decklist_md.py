#!/usr/bin/env python3
"""Generate a human-readable Markdown decklist from data/cards.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "cards.json"
OUT = ROOT / "docs" / "DECKLISTS.md"

def fmt_card(c):
    cost = c["cost"] if c["cost"] is not None else "—"
    pd = f"{c['power']}/{c['durability']}" if c.get("power") is not None else "—"
    name = c["name"] + (" *(Unique)*" if c.get("unique") else "")
    return f"| {c['qty']} | {name} | {cost} | {c['typeLine']} | {pd} | {c['text']} |"

def main():
    data = json.loads(DATA.read_text())
    lines = [f"# {data['game']} — {data['subtitle']}\n"]
    for deck in data["decks"]:
        lines.append(f"## DECK — {deck['name']}")
        lines.append(f"*{deck['tagline']}*\n")
        total = 0
        for section in deck["sections"]:
            qty_sum = sum(c["qty"] for c in section["cards"])
            total += qty_sum
            lines.append(f"### {section['name']} — {qty_sum}\n")
            lines.append("| Qty | Card | Cost | Type / Threat | P/D | Rules Text |")
            lines.append("|---|---|---|---|---|---|")
            for c in section["cards"]:
                lines.append(fmt_card(c))
            lines.append("")
        lines.append(f"**DECK TOTAL: {total} CARDS**\n")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
