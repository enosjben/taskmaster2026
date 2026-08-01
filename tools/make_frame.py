#!/usr/bin/env python3
"""Generate the gilt picture frame used around each team's score.

Writes assets/frame.svg — a square, mitred, five-band moulding meant to be
consumed as a CSS border-image. Square because border-image slices a fixed
number of pixels off each edge, so a square source wraps a card of any
proportion without the corners distorting.

Each side of every band is drawn as its own mitred trapezoid so it can be lit
separately: light from the top-left means the top rail is brightest and the
bottom rail darkest, which is what reads as carved rather than printed.
"""

import pathlib

S = 600                      # source square
BANDS = [0, 22, 46, 104, 128, 138]   # ring boundaries, outer -> inner
SIDES = ("top", "right", "bottom", "left")

# Gold ramp, light -> dark.
GOLD = ["#FBF0CC", "#F3DFA2", "#E3C377", "#C9A24E", "#A07C33", "#6E5320", "#43310F"]

# How strongly each side is lit. Top catches the light, bottom is in shadow.
LIGHT = {"top": 0.00, "left": 0.85, "right": 1.85, "bottom": 2.50}

# Per band: (index into GOLD for the near edge, for the far edge)
BAND_RAMP = [(2, 5), (0, 3), (1, 4), (0, 2), (4, 6)]


def shade(idx: float) -> str:
    """Sample the gold ramp at a fractional index."""
    i = max(0.0, min(len(GOLD) - 1.0, idx))
    lo, hi = int(i), min(int(i) + 1, len(GOLD) - 1)
    t = i - lo
    a, b = GOLD[lo].lstrip("#"), GOLD[hi].lstrip("#")
    out = []
    for c in range(3):
        va = int(a[c * 2:c * 2 + 2], 16)
        vb = int(b[c * 2:c * 2 + 2], 16)
        out.append(round(va + (vb - va) * t))
    return "#%02X%02X%02X" % tuple(out)


def trapezoid(outer: float, inner: float, side: str) -> str:
    """One mitred rail: the band between two ring offsets, on one side."""
    o, i = outer, inner
    pts = {
        "top":    [(o, o), (S - o, o), (S - i, i), (i, i)],
        "bottom": [(o, S - o), (S - o, S - o), (S - i, S - i), (i, S - i)],
        "left":   [(o, o), (o, S - o), (i, S - i), (i, i)],
        "right":  [(S - o, o), (S - o, S - o), (S - i, S - i), (S - i, i)],
    }[side]
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def gradient_dir(side: str) -> tuple:
    """Gradient runs across the rail, from the outer edge to the inner edge."""
    return {
        "top":    (0, 0, 0, 1),
        "bottom": (0, 1, 0, 0),
        "left":   (0, 0, 1, 0),
        "right":  (1, 0, 0, 0),
    }[side]


def build() -> str:
    defs, shapes = [], []

    for b, (outer, inner) in enumerate(zip(BANDS, BANDS[1:])):
        near, far = BAND_RAMP[b]
        for side in SIDES:
            gid = f"g{b}{side}"
            x1, y1, x2, y2 = gradient_dir(side)
            lit = LIGHT[side]
            defs.append(
                f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                f'<stop offset="0" stop-color="{shade(near + lit)}"/>'
                f'<stop offset=".45" stop-color="{shade((near + far) / 2 + lit)}"/>'
                f'<stop offset="1" stop-color="{shade(far + lit)}"/>'
                f"</linearGradient>"
            )
            shapes.append(
                f'<polygon points="{trapezoid(outer, inner, side)}" fill="url(#{gid})"/>'
            )

    # Repeating ornament down the centre of the widest band (index 2).
    orn_out, orn_in = BANDS[2], BANDS[3]
    mid = (orn_out + orn_in) / 2
    half = (orn_in - orn_out) / 2
    beads = []
    step = 46
    start = BANDS[2] + step * 0.5
    n = int((S - 2 * BANDS[2]) // step)
    for k in range(n):
        pos = start + k * step + (S - 2 * BANDS[2] - n * step) / 2
        for side in SIDES:
            if side == "top":
                cx, cy, rx, ry = pos, mid, step * 0.30, half * 0.62
            elif side == "bottom":
                cx, cy, rx, ry = pos, S - mid, step * 0.30, half * 0.62
            elif side == "left":
                cx, cy, rx, ry = mid, pos, half * 0.62, step * 0.30
            else:
                cx, cy, rx, ry = S - mid, pos, half * 0.62, step * 0.30
            beads.append(
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="url(#bead)" opacity=".85"/>'
            )
    defs.append(
        '<radialGradient id="bead" cx=".36" cy=".3" r=".8">'
        f'<stop offset="0" stop-color="{GOLD[0]}"/>'
        f'<stop offset=".5" stop-color="{GOLD[2]}"/>'
        f'<stop offset="1" stop-color="{GOLD[5]}"/>'
        "</radialGradient>"
    )

    # Corner cartouches: a scrolled boss over each mitre.
    corners = []
    c0 = BANDS[0] + 6
    c1 = BANDS[3] - 6
    for sx, sy, ox, oy in ((1, 1, c0, c0), (-1, 1, S - c0, c0),
                           (1, -1, c0, S - c0), (-1, -1, S - c0, S - c0)):
        corners.append(
            f'<g transform="translate({ox},{oy}) scale({sx},{sy})">'
            f'<path d="M0,0 L{c1 - c0},0 Q{(c1 - c0) * .52},{(c1 - c0) * .30} '
            f'{(c1 - c0) * .34},{(c1 - c0) * .56} Q{(c1 - c0) * .22},{(c1 - c0) * .84} '
            f'0,{c1 - c0} Z" fill="url(#corner)"/>'
            f'<circle cx="{(c1 - c0) * .30}" cy="{(c1 - c0) * .30}" r="{(c1 - c0) * .17}" fill="url(#bead)"/>'
            f"</g>"
        )
    defs.append(
        '<linearGradient id="corner" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{GOLD[0]}"/>'
        f'<stop offset=".45" stop-color="{GOLD[2]}"/>'
        f'<stop offset="1" stop-color="{GOLD[4]}"/>'
        "</linearGradient>"
    )

    # Carved relief: noise lit from the same direction, clipped to the frame.
    defs.append(
        '<filter id="carve" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.055" numOctaves="4" seed="9" result="n"/>'
        '<feDiffuseLighting in="n" lighting-color="#F0D999" surfaceScale="2.6" '
        'diffuseConstant="1.15" result="lit">'
        '<feDistantLight azimuth="315" elevation="56"/>'
        "</feDiffuseLighting>"
        '<feComposite in="lit" in2="SourceAlpha" operator="in"/>'
        "</filter>"
    )

    frame_path = (
        f'M0,0 H{S} V{S} H0 Z '
        f'M{BANDS[-1]},{BANDS[-1]} V{S - BANDS[-1]} H{S - BANDS[-1]} V{BANDS[-1]} Z'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
{chr(10).join(defs)}
<clipPath id="frameOnly"><path d="{frame_path}" fill-rule="evenodd"/></clipPath>
</defs>
<g clip-path="url(#frameOnly)">
{chr(10).join(shapes)}
{chr(10).join(beads)}
{chr(10).join(corners)}
<path d="{frame_path}" fill-rule="evenodd" filter="url(#carve)" opacity=".34"
      style="mix-blend-mode:overlay"/>
</g>
<path d="{frame_path}" fill-rule="evenodd" fill="none"/>
<rect x=".5" y=".5" width="{S - 1}" height="{S - 1}" fill="none" stroke="#4A3612" stroke-width="1.6" opacity=".55"/>
<rect x="{BANDS[-1]}" y="{BANDS[-1]}" width="{S - 2 * BANDS[-1]}" height="{S - 2 * BANDS[-1]}"
      fill="none" stroke="#4A3612" stroke-width="2.4" opacity=".5"/>
</svg>
"""


def main() -> None:
    out = pathlib.Path(__file__).parent.parent / "assets" / "frame.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB), slice = {BANDS[-1]}")


if __name__ == "__main__":
    main()
