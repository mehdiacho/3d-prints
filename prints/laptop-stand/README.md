# Vertical laptop stand

A pair of printed holders that stand an Alienware m15 R7 on edge — on the desk, or hooked over
the desk's side edge so the laptop hangs beside it.

**Status: drawing only.** Nothing is modelled and nothing is printed. This print is in the repo
because the drawing is the part that matters at this stage, and because it is the clearest
example of what a blueprint looks like *before* anything has been measured: three arrangements
drawn to scale, a holder cross-section with every size marked PROP., and nine values still
TBD. See [`blueprint.html`](blueprint.html).

## What it is for

The laptop has no lid. Standing it on edge frees the desk and keeps the rear vent clear, but the
charger brace ([`../charger-brace`](../charger-brace)) stands 52.3 mm out of the rear face and
has to go somewhere. Each of the three options is really a different answer to that.

| Option | Edge in the holders | Height standing | Sideways push at the top that tips it |
|---|---|---|---|
| A — front edge down | The palm rest | 279 mm | about 7 N (0.7 kg), leans 28° first |
| B — side edge down | The side away from the charger | 362 mm | about 5 N (0.5 kg), leans 22° first |
| C — rear edge down | The rear edge, lifted 70 mm clear | — | the charger and the vent are at the bottom |

Those forces follow from an **assumed** 2.5 kg, marked IND. on the drawing, since the published
figure is for a machine that still has its lid.

## The holder

Two identical pieces, each 60 mm along the edge, set 50 mm in from each end — two short holders
rather than one long one, because the bed is 220 mm. In cross-section each is a slot with a foot
on one side and a pair of jaws on the other:

- slot 18.4 mm wide (the measured edge plus 1 mm of felt each side) and 45 mm deep,
- 6 mm walls, floor, jaws and foot,
- jaws 60 mm long with a 60 mm foot opposite, 150.4 mm across the base in all,
- the jaws push onto the desk's side edge, which needs 90.4 mm of clear room beside the desk.

A 20 N knock at the top of the laptop puts about 8 MPa in a slot wall, against roughly 40 for
printed PETG along its layers. Hooked on the desk, the lower jaw carries about 6 N. Neither is
close to the limit; tipping over is the failure mode, not breaking.

## What has to be measured before this gets modelled

Nine values, all on the drawing, all red:

**The laptop** — `SC` thickness at the front edge (this sets the slot width), `SD` thickness at
the side edge, `SA` front edge to the bottom row of keys, `SB` far side edge to the nearest key,
`SE` height of the front foot, `SF` front edge back to that foot.

**The desk** — `DA` top thickness at the edge, `DB` clear depth underneath from the edge (the
lower jaw needs 60 mm), `DD` open room beside the desk (the holder and laptop need about 90 mm).

Views 3 and 8 are drawn to a 25 mm desk top as a placeholder. Two photographs settle the shape:
side on, and from underneath.

## Licence

Drawings: CC BY-SA 4.0. See [LICENSE-models.md](../../LICENSE-models.md).
