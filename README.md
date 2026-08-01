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

That button only works when the page is opened directly. An embedded copy is
refused the Fullscreen API by its host frame, so the button detects that on
load and names your browser's own full-screen key instead — `F11`, or
`Ctrl+Cmd+F` on a Mac. Open `index.html` from disk for the real thing.

Sizes are in viewport-height units rather than pixels, so the same layout holds
on any 16:9 display, 1080p or 4K. Windows narrower than 1100px or shorter than
620px fall back to a taller scrolling layout, which is what you get on a phone
or a small laptop window.

## The home screen

Before anything is scored the board shows the team sheet: five framed squads
with everyone's name, big enough to read across a room. Names and players are
editable there — one player per line — and edits flow straight through to the
scoreboard and the phone.

**Open the scoreboard** moves on when you're ready, and the board opens by
itself the moment the first task is scored, so you can leave the team sheet up
while people arrive. The **Teams** button brings it back at any point, and
**Reset scores** returns to it for a fresh night.

## Using it during the party

- **Award points** — click any square and pick a number, or focus a square and
  type the score. Backspace clears it. Arrow keys move around the grid.
  Five points to the team the Taskmaster likes best, down to one for the team
  he likes least, and zero for disqualification.
- **The finale is open-ended.** The relay shows buttons up to 15, but its
  picker also has a field for any number at all, in case a team runs away with
  it. Typing into a cell works too — digits pressed in quick succession
  combine, so `1` then `5` gives 15 and `2` then `4` gives 24. Every other task
  still refuses anything above five.
- **Task names stay sealed** until a task is being scored. Until then the board
  shows only its number, so nobody watching the TV learns what is coming. Your
  phone always shows every name, because you need them.
- **Team names and player lists are click-to-edit**, on the home screen or on
  the standings cards. The wordmark and the wax seal are fixed, and cannot be
  selected or altered by a passing guest — change them in
  `src/index.template.html` and rebuild.
- **The golden head** sits with whoever is leading and moves the moment that
  changes. The cards re-sort themselves as scores land.
- **Totals sit on wax seals** under each framed team, as they do on the show.
- **Champion** is stamped on the leader only once all nine tasks are judged.
- **Reset scores** clears the grid but keeps names. It asks twice: the first
  press arms the button, the second clears. Clicking elsewhere, pressing
  Escape, or waiting five seconds cancels. It deliberately avoids a browser
  confirm dialog, which a sandboxed page suppresses.

Opened straight from disk, everything saves to that browser's local storage as
you go, so a refresh or a closed tab won't lose the night. To score from your
phone instead, run the server below.

## Scoring from your phone

Run this on the laptop driving the TV:

```
python3 server.py
```

It prints two addresses. Open the first on the laptop (that's the board you
AirPlay or cast), and the second on your phone. Both devices need to be on the
same wifi; nothing leaves your network and no accounts are involved.

On the phone you pick a task, tap a score for each of the five teams, and press
**Submit round**. The whole round lands on the TV at once, rather than
appearing one team at a time as you tap. Submit stays disabled until all five
teams have a score, so a half-finished round can't go up by accident, and after
a successful submit the phone moves itself to the next unjudged task.

A sting plays on the laptop each time a round lands, so the room hears the
scores arrive. Sound is **on by default** — the button reports the current
state rather than what pressing it will do.

Browsers keep audio locked until the page has been interacted with, so press
the button once before guests arrive: the first press only unlocks and plays
the sting, so you can set the volume without accidentally muting. Every press
after that toggles, and the choice is remembered. Only rounds submitted from
the phone make a noise; typing scores on the laptop stays silent.

It works both ways: rename a team or type a score on the laptop and the phone
updates too. A small **Remote linked** marker appears on the board while a
server is attached. If the phone loses wifi it says so rather than silently
dropping scores.

Scores live on the laptop in `party-state.json` and are written on every
change, so restarting the server — or closing the laptop lid — doesn't lose the
night. Delete that file to start a fresh party.

Everything still works with no server at all: opened from disk the board keeps
using local storage exactly as before, and never looks for one.

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

Starting squads live alongside the team names, in `TEAMS` in the page and in
`server.py` — both, since whichever is holding the night seeds the other. Names
and players typed into the page are saved and will override those defaults;
delete `party-state.json` (or clear the site's local storage when running
without the server) if you change them in the source and want the new ones.

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

## The sting

`assets/sting.mp3` is played when a round lands, inlined as a data URI like
everything else. Swap that file and rebuild to change it. It is the one asset
here that isn't original work — keep that in mind before making the repository
public.

## Fonts

- **Veteran Typewriter** — the wordmark and all running text. Supplied by the
  repository owner; check its own licence before redistributing. It ships in
  one weight, so bold is the browser's synthetic bold.
- **Bevan** — display slab, kept for the team names, the scores and the grid
  numerals, where the heavier slab reads better at a glance. SIL Open Font
  License 1.1, redistributed here under its terms.
