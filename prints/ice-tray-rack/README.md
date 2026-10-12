# Freezer ice tray rack

A stack of printed bays that hold rigid ice trays in a chest freezer and let you fill them
where they stand, instead of carrying full trays across the kitchen.

**Status: modelled as v3, not printed and not fit-tested.** The trays it holds were
measured with calipers; every dimension of the rack itself is a proposal. The build does check
every pair of parts for collisions and reports zero — see
[`models/report.json`](models/report.json) — but a clean boolean is not a fit test.

## What it is

The tray is 2 × 6 rigid plastic, twelve cells, 210 × 102 × 34.5 mm, measured and drawn on
[the blueprint](blueprint.html) before anything was modelled.

One bay holds one tray, hanging it on the four fins along its long sides. Bays stack four high
on printed pegs: each peg threads into the tube below and snaps into the one above, in tubes
that run **outside** the bay walls. The tubes have room for a 5 mm magnet later if the thread
turns out not to be enough. Under the bottom bay, four adaptors snap into those same tubes and
take four screw-in levelling feet.

Four high, the stack is 237 mm tall and 133 mm wide across the tubes, 281 mm tall with the
splitter on top.

## How it fills — still an open question

Filling is question **FILL** on the drawing, and the models cover all three answers. There is
a working [fill simulation](simulation.html) for comparing them: pour a volume, tilt the
freezer, and see which cells spill over their walls.

| Option | How it fills | Water per tray | Cubes |
|---|---|---|---|
| At the tap | Pull a bay out, fill it, slide it back | 300 ml | Snap apart cleanly |
| Splitter | One pour into a trough, four tubes, one per tray | 300 ml each | Snap apart cleanly |
| Cascade | Pour into the top tray, it spills into a pan, then the next | 400 ml each | Joined at the top |

300 ml brings every cell to 1 mm under the walls between them, which is the fill that twists
apart cleanly. The cascade has to run at 400 ml, because a tray only spills over its own lip
when it is full to the brim — so those cubes come out joined. That is the trade, and it is why
the choice is still open.

## Parts

Black PETG throughout. Grams are solid PETG at 1.27 g/cm³, an upper bound: a sliced part comes
out lighter.

| File | What it is | Grams | For a 4-high stack |
|---|---|---|---|
| [`models/parts/bay.stl`](models/parts/bay.stl) | One tray bay, 200 × 133 × 54 | 38.7 | 4 |
| [`models/parts/peg.stl`](models/parts/peg.stl) | Threads into the tube below, snaps into the one above | 0.7 | 12, +2 for the splitter |
| [`models/parts/foot-adaptor.stl`](models/parts/foot-adaptor.stl) | Snaps into the bottom bay's tubes, takes a foot | 4.0 | 4 |
| [`models/parts/foot.stl`](models/parts/foot.stl) | Printed screw foot, no hardware | 3.9 | 4 |
| [`models/parts/spout.stl`](models/parts/spout.stl) | Push-in spout through a bay's side wall | 1.6 | 4, splitter only |
| [`models/parts/splitter-trough.stl`](models/parts/splitter-trough.stl) | One pour, four equal shares | 74.3 | 1, splitter only |
| [`models/parts/plug.stl`](models/parts/plug.stl) | Blanks off a splitter hole for a bay not in use | 0.6 | 0–3 |
| [`models/parts/catch-pan.stl`](models/parts/catch-pan.stl) | Cascade: catches the spill, drains to the next tray | 37.1 | 3, cascade only |

Four bays, twelve pegs, the adaptors and the feet come to about 190 g. Add the splitter
(76 g with its spouts) **or** the cascade pans (111 g), not both.

[`plates/`](plates) has the six plates these come on, sliced for a 220 × 220 bed, as `.3mf`
with a preview `.png` each, and [`plates/plates.json`](plates/plates.json) listing what is on
each one and what it weighs. One bay goes on every plate, because a bay is what fills the bed.

**Reference geometry, not for printing** — [`models/reference/`](models/reference):
`plastic-tray.stl` is the bought tray, so you can check clearances yourself.
`silicone-tray.stl` is a second tray that was measured and then shelved (sheet 04).
`bay-for-simulation.stl` is a coarser bay the fill simulation uses.

**Assemblies, not for printing** — [`models/assemblies/`](models/assemblies) holds the whole
stack in each of the three fill arrangements. They are for looking at, and their threads are
drawn coarse.

## What you have to buy

- **8 mm inside-diameter silicone or PVC tube** — splitter option only, about 1.5 m.
- **5 × 3 mm neodymium disc magnets** — optional, four per joint, only if the printed thread
  does not hold. None found in Botswana; South African suppliers stock them.

## Print settings

Black PETG, 0.16 mm layers, 4 walls, 40 % infill or more, no supports, 100 % scale. PETG rather
than PLA because PLA goes brittle at freezer temperatures.

The side-wall windows have 45° tops so they bridge without support. The pegs are printed
threads, so they want a slow first few layers and no ironing.

FDM prints are not food-safe in any strict sense — water sits in the layer lines. Water only
touches the trough, the tubes and the spouts; wash them.

## Rebuilding the models

Every STL and GLB here is generated. Nothing was pushed around by hand.

```bash
pip install manifold3d trimesh numpy shapely scipy
python src/build_ice_rack_v3.py out
```

It writes one STL per part in millimetres with Z up for slicing, one GLB per model in metres
with Y up for the web, and a JSON report of masses, stack heights and every collision check.

The script carries the blueprint's letters in its variable names, so a dimension on the drawing
can be traced to the line that uses it. It mirrors Y once on export: the blueprint's axes are
left-handed, and a different print in this repo came out mirrored for exactly that reason.

## What is still open

- **FILL** — tap, splitter or cascade. Nothing gets printed until this is answered.
- **PQ** — whether the tray's length and width were taken across the top or the chin.
- Freezer inside sizes are placeholders (at least 300 × 500 × 500 deep), marked IND.
- Nothing is fit-tested. The peg thread in particular is a printed M-ish thread at 2 mm pitch
  and has never been turned.
- **The drawing is one revision behind the models.** Sheet 01 — the tray, which is the only
  part of this that was measured — is current. The rack sheets (02, 03 and 05) still draw the
  v2 arrangement: a 52 mm bay with the tray standing on floor rails, corner posts carrying
  bosses and 5 mm magnet pockets, and a separate levelling base under the stack. v3 is what is
  in `models/`: in v2 those corner posts ran through the tray's own lip corners and collided
  with it, so v3 moved them outside the walls, hung the tray on its four side fins instead,
  grew the bay to 54 mm, and replaced the base with the pegs and screw-in foot adaptors
  described above. Redrawing those three sheets is the next job on this print. Until then the
  3D views on them show "3D VIEW UNAVAILABLE" rather than showing you geometry the text around
  it no longer describes.
- A levelling shim: the simulation showed that if the spout end sits low, the back cells freeze
  over their walls. The stack wants its back a touch higher.

## Licence

Models, drawings and renders: CC BY-SA 4.0. The build script: MIT. See
[LICENSE](../../LICENSE) and [LICENSE-models.md](../../LICENSE-models.md).
