# Blueprint first

Every print in this repository starts the same way: with a measurement blueprint of the
real object the part has to fit, drawn and agreed before any CAD is written. No model,
no STL, until the blueprint's numbers are filled in.

This is not a style preference. The first key fob body was built from photographs and
estimates and did not fit. It only came right once there was a labelled drawing — a
drawing makes it obvious what still needs measuring and exactly where each number
belongs. Everything below is what that turned into after a few prints.

## What counts as a blueprint here

One interactive page per print, holding a numbered set of sheets. Sheet 01, sheet 02,
and so on, switched by tabs. A static printable sheet is an optional extra, never the
deliverable.

A sheet has:

- Ink linework on paper, a sheet numeral and title, a revision and a status.
- Views laid out as a grid of cards. A closed card shows the linework alone, cropped to
  what matters; opening one rolls it out and shows every tag, note and caption.
- A measurement schedule. Clicking a row highlights that measurement's points and edges,
  draws its dimension line and opens the right view — switching sheets if it lives on
  another one. Clicking a point or an edge shows which measurements use it.
- Keyed notes, and a title block that prints.
- A light sheet and a dark sheet.
- A 2D / 3D switch. 3D stays greyed out until the part is actually modelled.

## Unknowns stay visible

This is the part that does the real work. Every value that is not a confirmed caliper
reading is marked, in red, as one of:

| Mark | Means |
|---|---|
| `TBD` | Nobody has measured it yet |
| `(IND.)` | Indicative — read off a photo or a tape, not trusted |
| `(PROP.)` | Proposed — a size chosen for the design, not measured off anything |
| `DERIVED` | Worked out from other measurements |

A schedule filter lists everything still open on the sheet. The point is that a drawing
with twelve red rows is *honest* and useful, and a drawing where a plausible number has
quietly replaced a missing one is neither. Guessed dimensions are how the first fob body
came out wrong.

## Measurements get cross-checked

Numbers that ought to add up are checked against each other before anything is modelled.
On the key head, `J` + the tab width + `K` had to match the overall width `B`. On the
silicone tray, 2 rim + 8 cells + 7 dividers came to 343.5 against a measured length of
340 — the silicone gives, so the cells were drawn at their measured sizes centred in the
measured outline, and the discrepancy was written down rather than averaged away.

## Handedness — the mistake worth knowing about

Measurement axes get chosen because they are easy to measure: from an edge, from a face,
down from a tip. That very often makes them **left-handed**, and a model built straight
from left-handed axes comes out **mirrored**.

The Mazda body v3 was modelled this way and came out back to front, with its tab and
blade pockets on the wrong face. Nothing about it looked wrong on screen. It cost three
printed fit tests to find out.

So, as a rule:

- State in the title block which way x, y and z run and where zero is.
- Before building, check that x × y = z. If it comes to −z, mirror **one** axis exactly
  once in the model, and say so in the script.
- Before publishing or printing, render the model from a named face and compare it with
  the 2D view of that face. The features have to be on the same side.

Every build script in this repo carries that mirror and a comment saying why.
`build_ice_rack_v2.py` mirrors Y; `build_mazda_body_v4.py` mirrors Z; the charger brace
uses X = −u.

## Fit tests before full parts

Wherever a part mates with something, print only the mating end first, in tight,
standard and loose variants, marked so they can be told apart after printing — the key
fob uses a different number of grooves on each.

And a part that has to close around something with a hook or a lip gets **split and glued
around it**, rather than forced over it. Both the charger brace and the fob body v4 are
two halves that close on a split plane. Forcing a hook through a closed socket is how you
break a part you have waited a week to collect.

## The order

1. Photographs from every side, plus any existing model of a similar part.
2. A first blueprint with every point and edge tagged and every value `TBD`.
3. A correction pass — orientation, missing features, asymmetries — **before** measuring.
   Fix the drawing first, or the measurements go to the wrong places.
4. Caliper readings, reported by letter. Anything not already on the sheet gets described
   by the points it sits between and added as a new letter.
5. Cross-check the numbers against each other.
6. Only then model it, with the parameters named after the blueprint's letters, and check
   the handedness.
7. Add the part to the page: its 2D views and proposed sizes, its model behind the switch.
8. Fit test the mating end.
9. Keep the drawing current. New measurements and new design options go onto the page, not
   into a conversation.

## Worked examples in this repo

- [`prints/key-fob/blueprint.html`](prints/key-fob/blueprint.html) — two sheets: the key
  head measured, and the body in two glued halves with its 3D model.
- [`prints/ice-tray-rack/blueprint.html`](prints/ice-tray-rack/blueprint.html) — five
  sheets, three competing fill designs, a question still open on the drawing.
- [`prints/charger-brace/blueprint.html`](prints/charger-brace/blueprint.html) — the card
  grid's first outing, with the part itself on its
  [own sheet](prints/charger-brace/part-sheet.html).
- [`prints/laptop-stand/blueprint.html`](prints/laptop-stand/blueprint.html) — a drawing
  at the stage before any measuring: three options drawn, nine values `TBD`.

The pages here are published read-only. In the working copies the schedule has a
measurement entry box; it is switched off by `const PUBLIC = true` near the top of each
page's script, because the store it saves to does not exist outside the working copy.
