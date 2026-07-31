# Taskmaster — party scoreboard

A single-page scoreboard for a nine-task, five-team Taskmaster night. Open
`index.html` in any browser and put it on the biggest screen in the house.

## Running it

Double-click `index.html`. That's it — no server, no build, no network. The
page is entirely self-contained, fonts included, so it works offline and from
a USB stick.

## Using it during the party

- **Award points** — click any square and pick a number, or focus a square and
  type `0`–`5`. Backspace clears it. Arrow keys move around the grid.
  Five points to the team the Taskmaster likes best, down to one for the team
  he likes least, and zero for disqualification.
- **Edit anything** — the title, the Taskmaster and assistant names, team
  names, player lists and each task's wording are all click-to-edit.
- **The golden head** sits with whoever is leading and moves the moment that
  changes. The cards re-sort themselves as scores land.
- **Champion** is stamped on the leader only once all nine tasks are judged.
- **Reset scores** clears the grid but keeps names and player lists.

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

Each ships with default wording written to be read aloud. Edit it on the page
to suit your house; edits persist.

## Changing the tasks or teams

Both are declared at the top of the script in `src/index.template.html` as
`TASKS` and `TEAMS`. Add or remove entries and the grid, cards, pips and
totals all follow — nothing else is hard-coded to nine or five.

Note that team names typed into the page are saved and will override the
defaults on that browser; use **Reset scores** or clear the site's local
storage if you change `TEAMS` and want the new names to show.

## Building

`index.html` is generated and committed, so you only need this if you edit the
template:

```
python3 build.py
```

That inlines the fonts from `fonts/` into `src/index.template.html` as data
URIs and writes `index.html`, plus `dist/artifact.html` (the same page as a
bare fragment, for hosts that supply their own document skeleton). Fonts are
embedded rather than linked because a page served under a strict
content-security policy can't fetch a font CDN, and the fallback would lose
the wordmark the design rests on.

## Fonts

- **Bevan** — display slab, for the wordmark, team names and scores
- **Courier Prime** — typewriter, for task wording and labels

Both are licensed under the SIL Open Font License 1.1 and are redistributed
here under its terms.
