# Taskmaster — party scoreboard

A single-page scoreboard for a nine-task, five-team Taskmaster night. Open
`index.html` in any browser and put it on the biggest screen in the house.

## Running it

Double-click `index.html`. That's it — no server, no build, no network. The
page is entirely self-contained, fonts included, so it works offline and from
a USB stick.

## On the TV

The board is laid out for a 1920×1080 screen: at that size the whole thing —
masthead, standings and all nine tasks — fits the screen exactly, with nothing
to scroll. Press **Full screen** to lose the browser chrome.

Sizes are in viewport-height units rather than pixels, so the same layout holds
on any 16:9 display, 1080p or 4K. Windows narrower than 1100px or shorter than
620px fall back to a taller scrolling layout, which is what you get on a phone
or a small laptop window.

## Using it during the party

- **Award points** — click any square and pick a number, or focus a square and
  type the score. Backspace clears it. Arrow keys move around the grid.
  Five points to the team the Taskmaster likes best, down to one for the team
  he likes least, and zero for disqualification.
- **The finale is out of 15**, not 5, because the relay is anyone's game. Its
  picker runs 0–15, and typing works by combining digits pressed in quick
  succession, so `1` then `5` gives 15. Any other task refuses anything above
  its own maximum.
- **Edit anything** — the title, the initials on the wax seal, team names and
  player lists are all click-to-edit.
- **The golden head** sits with whoever is leading and moves the moment that
  changes. The cards re-sort themselves as scores land.
- **Champion** is stamped on the leader only once all nine tasks are judged.
- **Reset scores** clears the grid but keeps names. It asks twice: the first
  press arms the button, the second clears. Clicking elsewhere, pressing
  Escape, or waiting five seconds cancels. It deliberately avoids a browser
  confirm dialog, which a sandboxed page suppresses.

Everything saves to the browser's local storage as you go, so a refresh or an
accidentally closed tab won't lose the night. Scores live in that one browser
on that one machine — this is a scoreboard, not a synced app, so run it from a
single laptop.

## The tasks

1. Longest Line
2. Coolest Phone Photo
3. Recreate Phone Photo
4. Treasure Hunt
5. Hit Song
6. Museum Piece — prize task
7. Painting
8. Commercial
9. Relay — finale

## Changing the tasks or teams

Both are declared at the top of the script in `src/index.template.html` as
`TASKS` and `TEAMS`. Add or remove entries and the grid, cards and totals all
follow — nothing else is hard-coded to nine or five. Give a task a `max` to
change what it is scored out of, as the relay does; leave it off for 5.

Note that team names typed into the page are saved and will override the
defaults on that browser; use **Reset scores** or clear the site's local
storage if you change `TEAMS` and want the new names to show.

## Building

`index.html` is generated and committed, so you only need this if you edit the
template:

```
python3 build.py
```

That inlines the fonts from `fonts/` and the frame from `assets/` into
`src/index.template.html` as data URIs and writes `index.html`, plus
`dist/artifact.html` (the same page as a bare fragment, for hosts that supply
their own document skeleton). Everything is embedded rather than linked
because a page served under a strict content-security policy can't fetch from
another host, and a silent fallback would lose the look the design rests on.

## The gilt frame

Each team card is framed by `assets/frame.png`, applied as a CSS
`border-image`. Nine-slicing it means the mitred corners stay carved at their
drawn size while the beading tiles along whatever width the card ends up, so
one square source wraps a card of any proportion.

The frame is generated, not photographed:

```
python3 tools/make_frame.py     # writes assets/frame.svg
```

Each side of each moulding band is drawn as its own mitred trapezoid so it can
be lit separately — the top rail brightest, the bottom in shadow — which is
what reads as carved rather than printed. Rasterise the SVG to
`assets/frame.png` at 320×320 with any renderer; the `border-image-slice` in
the stylesheet (74) is the frame's thickness in that raster, so it must be
updated together with the raster size.

To use a different frame, drop your own square PNG at `assets/frame.png`, set
the slice to its border thickness in pixels, and rebuild.

## Fonts

- **Veteran Typewriter** — the wordmark and all running text. Supplied by the
  repository owner; check its own licence before redistributing. It ships in
  one weight, so bold is the browser's synthetic bold.
- **Bevan** — display slab, kept for the team names, the scores and the grid
  numerals, where the heavier slab reads better at a glance. SIL Open Font
  License 1.1, redistributed here under its terms.
