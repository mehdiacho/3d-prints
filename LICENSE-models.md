# Licence for the models, drawings and renders

Everything in this repository that is **not code** — the STL and GLB files, the
blueprint pages and their drawings, the renders, photographs and the written
descriptions — is licensed under

**[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)**

Copyright © 2026 Mehdi Acho.

## In short

You may print these parts, modify them, and use them commercially, provided you:

- **give credit** — name Mehdi Acho and link back to this repository, and
- **share alike** — if you publish a modified model or drawing, license it under
  CC BY-SA 4.0 as well.

The full legal text is at
<https://creativecommons.org/licenses/by-sa/4.0/legalcode>.

## What counts as code

The build scripts under each print's `src/`, and the page code inside the blueprint
HTML, are **MIT** — see [LICENSE](LICENSE). You can lift a script into a closed project
without the share-alike obligation. The geometry it generates is still CC BY-SA.

## No warranty

These are hobby parts, and most of them have not been printed, let alone tested under
load. Printed plastic fails in ways that depend on your printer, your filament, your
slicer settings and how you use the part. Figures in the READMEs for how much force a
part holds are calculated, not measured, and are marked as such. Nothing here is
supplied with any warranty or any fitness for a particular purpose. Check anything that
has to hold something up or carry mains-connected hardware before you trust it.

## Third-party geometry

**`prints/key-fob/`** — the outer cross-section of the flip-key body was taken from a
downloaded TPU fob cover of unrecorded origin. The derivation is thin: one planar
section of that model, reduced to its convex hull, inset 1.5 mm, then rescaled to the
31.90 × 15.80 mm measured here, so what survives is corner curvature on a rounded
rectangle. Every other dimension of the part is an original caliper reading, recorded on
[that print's blueprint](prints/key-fob/blueprint.html).

No licence for the source model could be found. If you are its author, open an issue and
the geometry will be removed or credited as you prefer. The dependency can also be cut
outright by generating the profile from the measured width, thickness and corner radii —
see the note in [`prints/key-fob/README.md`](prints/key-fob/README.md).

Nothing else in this repository derives from anyone else's model.
