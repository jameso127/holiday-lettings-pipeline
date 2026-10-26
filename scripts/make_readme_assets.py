"""Generate the README illustrations (SVGs) in docs/assets/.

Usage:
    uv run python scripts/make_readme_assets.py

Numbers come from the verified dbt build. Re-run this after they change.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"  # STATIC=1 skips animation, for previewing the final frame
OUT = ROOT / "docs" / "assets"

# Coastal theme: deep teal, sea green, sand and coral. Chart colours (SKY, SEA, CORAL) are CVD-validated.
DEEP, SEA, SEA_DARK, SKY = "#0b3c49", "#00897b", "#00695c", "#45b3d6"
SAND, SAND_2, SAND_3, DUNE = "#fbf6ee", "#f4ebdc", "#e6d5b8", "#c9ad7f"
CORAL, GOLD, INK, GREY = "#e2582c", "#f2b134", "#1f2a2e", "#5b6b70"
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'Cascadia Code', Consolas, 'SFMono-Regular', Menlo, monospace"

STYLE = f"""
  .t {{ font-family: {FONT}; fill: {DEEP}; }}
  .h {{ font-family: {FONT}; font-weight: 800; fill: {DEEP}; }}
  .m {{ font-family: {MONO}; fill: {INK}; }}
  .cap {{ font-family: {FONT}; font-weight: 700; letter-spacing: 1.5px; }}
"""


def svg(name, w, h, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">\n'
        f"<style>{STYLE}</style>\n{body}\n</svg>\n",
        encoding="utf-8",
    )
    print("wrote", (OUT / name).relative_to(ROOT))


def card(x, y, w, h, fill="#ffffff", stroke=SAND_3, r=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def text(x, y, s, size=18, cls="t", anchor="start", weight=400, fill=None):
    style = f' style="fill:{fill}"' if fill else ""
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{style}>{s}</text>'


def appear(delay):
    """Fade and slide in after `delay` seconds, then stay.

    The animation starts at 0s and holds hidden until `delay`, so viewers that ignore SVG animation
    still show the element instead of leaving it invisible.
    """
    if STATIC:
        return ""
    dur = delay + 0.6
    k = delay / dur
    return (
        f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{dur}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 12;0 12;0 0" '
        f'keyTimes="0;{k:.3f};1" dur="{dur}s" fill="freeze"/>'
    )


def arrow(x1, y1, x2, y2, colour=DUNE):
    """Arrow with a dashed line that flows towards the head."""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2 - 10}" y2="{y2}" stroke="{colour}" stroke-width="3" stroke-dasharray="8 6">'
        f'<animate attributeName="stroke-dashoffset" from="28" to="0" dur="1s" repeatCount="indefinite"/></line>'
        f'<path d="M {x2 - 12} {y2 - 7} L {x2} {y2} L {x2 - 12} {y2 + 7} Z" fill="{colour}"/>'
    )


# ----------------------------------------------------------------------------------------- hero
def hero():
    chips = [
        (800, 80, "' Guest 43 '", "Guest 43"),
        (830, 140, "COMPLETED", "completed"),
        (800, 200, "14/12/2023", "2023-12-14"),
        (830, 260, "$5225.00", "5225.00"),
    ]
    chip_svg = ""
    for i, (x, y, before, after) in enumerate(chips):
        chip_svg += f"""
  <g>
    <rect x="{x}" y="{y - 26}" width="340" height="40" rx="20" fill="{SAND}" opacity="0.97"/>
    {text(x + 20, y, before, 17, "m", fill=CORAL)}
    {text(x + 180, y, "→", 20, anchor="middle", weight=700, fill=GREY)}
    {text(x + 202, y, after, 17, "m", weight=700, fill=SEA_DARK)}
    {appear(0.4 + 0.5 * i)}
  </g>"""
    body = f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{DEEP}"/><stop offset="1" stop-color="{SEA_DARK}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="320" rx="28" fill="url(#bg)"/>
  <circle cx="1140" cy="30" r="130" fill="{SEA}" opacity="0.35"/>
  <circle cx="60" cy="340" r="150" fill="{SEA}" opacity="0.25"/>
  {text(64, 92, "TAKE-HOME TASK · DATA ENGINEERING", 16, "cap", fill=SAND_3)}
  {text(64, 156, "Holiday lettings bookings", 54, "h", fill="#ffffff")}
  {text(64, 204, "From messy legacy exports to a clean dataset", 23, fill=SAND_2)}
  {text(64, 236, "and a per-property summary, with dbt on DuckDB.", 23, fill=SAND_2)}
  <rect x="64" y="262" width="96" height="6" rx="3" fill="{GOLD}"/>
  {chip_svg}"""
    svg("hero.svg", 1200, 320, body)


# ------------------------------------------------------------------------------------- pipeline
def pipeline():
    w, h = 250, 64
    cols = {"raw": 36, "stg": 334, "mart": 632, "out": 916}
    boxes = {
        "raw": ("raw", 168, "holiday_lettings.csv", "200 rows · read as text"),
        "stg": ("stg", 168, "stg_bookings", "view · clean + cast"),
        "clean": ("mart", 108, "bookings_clean", "fill gaps + flag them"),
        "summary": ("mart", 228, "property_summary", "aggregate per property"),
        "out1": ("out", 108, "bookings_clean.parquet", "the clean dataset"),
        "out2": ("out", 228, "property_summary.parquet", "the summary table"),
    }
    styles = {
        "raw": ("#ffffff", SAND_3, DEEP, GREY),
        "stg": (SAND_2, SAND_3, DEEP, GREY),
        "mart": (SEA, SEA, "#ffffff", SAND),
        "out": ("#ffffff", GOLD, DEEP, GREY),
    }
    body = f'<rect width="1200" height="340" rx="24" fill="{SAND}" stroke="{SAND_2}" stroke-width="2"/>'
    for col, label in (("raw", "RAW"), ("stg", "STAGING"), ("mart", "MARTS"), ("out", "OUTPUT")):
        body += text(cols[col] + w / 2, 64, label, 15, "cap", "middle", fill=SEA_DARK)

    def right(k):
        col, y = boxes[k][0], boxes[k][1]
        return cols[col] + w, y + h / 2

    def left(k):
        col, y = boxes[k][0], boxes[k][1]
        return cols[col], y + h / 2

    for a, b in (("raw", "stg"), ("stg", "clean"), ("clean", "out1"), ("summary", "out2")):
        body += arrow(*right(a), *left(b))
    cx = cols["mart"] + w / 2  # property_summary reads bookings_clean
    body += arrow(cx, 108 + h, cx, 228, SEA_DARK)

    for i, (col, y, name, sub) in enumerate(boxes.values()):
        fill, stroke, ink, sub_ink = styles[col]
        x = cols[col]
        body += f"""
  <g>
    {card(x, y, w, h, fill, stroke, 14)}
    {text(x + w / 2, y + 28, name, 17, "m", "middle", 600, ink)}
    {text(x + w / 2, y + 50, sub, 14, anchor="middle", fill=sub_ink)}
    {appear(0.2 * i)}
  </g>"""
    svg("pipeline.svg", 1200, 340, body)


# -------------------------------------------------------------------------------------- filling
def filling():
    """Three real bookings as table rows: each blank cell is shown filled, with the sum that filled it."""
    MINT = "#e3f4f1"
    cols = [("booking", 140), ("check-in", 250), ("check-out", 160), ("nights", 160), ("daily rate", 170),
            ("total", 200)]
    # Each cell: (value, how it was worked out or "", filled from a blank?)
    rows = [
        ("ID-1043", [("2023-03-06", "03-20 − 14 nights", True), ("2023-03-20", "", False),
                     ("14", "3,626 ÷ 259", False), ("259", "", False), ("3,626", "", False)]),
        ("ID-1096", [("2023-05-11", "", False), ("2023-05-24", "", False), ("13", "", False),
                     ("205", "2,665 ÷ 13", True), ("2,665", "", False)]),
        ("ID-1063", [("2023-05-22", "", False), ("2023-05-27", "", False), ("5", "", False),
                     ("357", "", False), ("1,785", "357 × 5", True)]),
    ]
    x0, top, head_h, row_h = 60, 112, 46, 80
    table_w = sum(w for _, w in cols)
    height = top + head_h + row_h * len(rows) + 96

    body = f'<rect width="1200" height="{height}" rx="24" fill="{SAND}"/>'
    # The rule, in one line
    body += text(600, 58, "daily rate  ×  nights  =  total".replace(" ", "&#160;"), 26, "h", "middle", fill=SEA_DARK)
    body += text(600, 88, "holds in every complete row, so a blank cell can be worked out from the others",
                 16, anchor="middle", fill=GREY)

    body += card(x0, top, table_w, head_h + row_h * len(rows), "#ffffff", SAND_3, 14)
    x = x0
    for label, w in cols:
        body += text(x + 20, top + 30, label.upper(), 13, "cap", fill=SEA_DARK)
        x += w
    for i, (booking, cells) in enumerate(rows):
        y = top + head_h + i * row_h
        body += f'<line x1="{x0}" y1="{y}" x2="{x0 + table_w}" y2="{y}" stroke="{SAND_3}" stroke-width="1.5"/>'
        body += text(x0 + 20, y + 44, booking, 18, "m", weight=700, fill=DEEP)
        x = x0 + cols[0][1]
        for (value, how, filled), (_, w) in zip(cells, cols[1:]):
            if filled:
                body += f"""
  <g>
    <rect x="{x + 6}" y="{y + 8}" width="{w - 12}" height="{row_h - 16}" rx="10" fill="{MINT}" stroke="{SEA}" stroke-width="2"/>
    <rect x="{x + w - 92}" y="{y + 14}" width="78" height="20" rx="10" fill="{CORAL}"/>
    {text(x + w - 53, y + 28, "was blank", 11, anchor="middle", weight=700, fill="#ffffff")}
    {text(x + 20, y + 40, value, 19, "m", weight=700, fill=SEA_DARK)}
    {text(x + 20, y + 62, how, 13, "m", fill=SEA_DARK)}
    {appear(0.5 + 0.5 * i)}
  </g>"""
            else:
                body += text(x + 20, y + 44, value, 18, "m", fill=INK)
                if how:
                    body += text(x + 20, y + 64, how, 13, "m", fill=GREY)
            x += w

    foot = top + head_h + row_h * len(rows)
    body += text(600, foot + 42, "Filled this way: 48 check-ins, 23 rates and 15 totals, each flagged as imputed.",
                 16, anchor="middle", weight=600, fill=SEA_DARK)
    body += text(600, foot + 70, "When two of the three are blank, the cell stays NULL: 19 stays, 11 rates and 8 totals.",
                 16, anchor="middle", weight=600, fill=CORAL)
    svg("filling.svg", 1200, height, body)


# ------------------------------------------------------------------------------------- coverage
def coverage():
    """Per column: values recorded in the raw file, values filled, and values still unknown."""
    rows = [("check_in_date", 133, 48, 19), ("daily_rate_usd", 166, 23, 11), ("total_booking_value", 177, 15, 8)]
    x0, bar_w = 270, 880
    body = f'<rect width="1200" height="300" rx="24" fill="#ffffff" stroke="{SAND_2}" stroke-width="2"/>'
    legend = [(x0, "recorded in raw file", SKY), (x0 + 220, "filled (flagged)", SEA),
              (x0 + 400, "still unknown (left NULL)", CORAL)]
    for lx, label, colour in legend:
        body += f'<rect x="{lx}" y="38" width="16" height="16" rx="4" fill="{colour}"/>'
        body += text(lx + 24, 52, label, 15, fill=GREY)
    for i, (col, recorded, filled, unknown) in enumerate(rows):
        y = 92 + i * 66
        body += text(x0 - 20, y + 26, col, 17, "m", "end")
        x = x0
        for value, colour, label_ink in ((recorded, SKY, DEEP), (filled, SEA, "#ffffff"), (unknown, CORAL, "#ffffff")):
            seg = bar_w * value / 200
            body += f"""
  <g>
    <rect x="{x}" y="{y}" width="{seg - 2}" height="38" rx="4" fill="{colour}"/>
    {text(x + seg / 2 - 1, y + 25, value, 15, anchor="middle", weight=700, fill=label_ink)}
    {appear(0.3 * i)}
  </g>"""
            x += seg
    svg("coverage.svg", 1200, 300, body)


if __name__ == "__main__":
    hero()
    pipeline()
    filling()
    coverage()
