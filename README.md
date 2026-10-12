# 3d-prints

Parts I have designed for things I own, and the measurement drawings they came from.

Every print here starts with a blueprint — an interactive drawing of the real object the part
has to fit, with every caliper reading on it and every unknown marked in red — and nothing gets
modelled until that drawing's numbers are filled in. The drawings are as much the point as the
models. [METHOD.md](METHOD.md) explains why, and what it cost to learn.

| Print | What it is | Status | Drawings |
|---|---|---|---|
| **[Laptop charger brace](prints/charger-brace)** | Clamps a barrel plug and hooks over the laptop's rear bar, so a knock on the cable loads the bar and not the jack | Modelled as v1, ready for a test print | [blueprint](prints/charger-brace/blueprint.html) · [part sheet](prints/charger-brace/part-sheet.html) |
| **[Mazda flip key body](prints/key-fob)** | A printed replacement shell for a 2007 Atenza flip key, in two halves glued around the original metal head | v4 modelled, not yet printed | [blueprint](prints/key-fob/blueprint.html) |
| **[Freezer ice tray rack](prints/ice-tray-rack)** | Four stacking bays that hold ice trays in a chest freezer and let you fill them where they stand | Modelled as v3, not printed | [blueprint](prints/ice-tray-rack/blueprint.html) · [fill simulation](prints/ice-tray-rack/simulation.html) |
| **[Vertical laptop stand](prints/laptop-stand)** | Two holders that stand a lidless laptop on edge, on the desk or hooked over its edge | Drawing only — nine values still TBD | [blueprint](prints/laptop-stand/blueprint.html) |

Nothing in this repository has been printed yet. Statuses are honest: "modelled" means the
geometry exists and the booleans are clean, not that anyone has held the part.

## How a print folder is laid out

```
prints/<slug>/
  README.md          what it is, what it weighs, what to buy, what is still open
  blueprint.html     the measurement drawing: sheets, schedule, 2D/3D switch
  meta.json          order on the portfolio, and which render and model lead
  models/            STLs in mm, Z up — parts/, reference/ and assemblies/ where it helps
  web/               GLBs for 3D views on the web, each kept under 2 MB
  renders/           images, and printable sheets as PDF and PNG
  plates/            sliced print plates, where there are any
  src/               the build scripts the models come from
```

The HTML pages are standalone: open one from disk and it works. They are published read-only —
in the working copies the measurement schedule has an entry box for typing caliper readings
into, switched off here by `const PUBLIC = true` near the top of each page's script, because the
store it saves to does not exist outside the working copy.

Some 3D views on the drawings show **3D VIEW UNAVAILABLE**. That is the designed fallback, not
a bug: the models those particular views want are not in the repository, for reasons given in
each print's README. The 2D sheets are complete.

## For the portfolio

[`prints.json`](prints.json) is the contract between this repository and
[mehdiacho.tech](https://mehdiacho.tech): the site fetches it at load, so a push here shows up
there without a redeploy.

```
https://raw.githubusercontent.com/mehdiacho/3d-prints/main/prints.json
```

It is written by [`tools/build_web.py`](tools/build_web.py), which takes each print's title,
description and status from its README, finds its pages, models and lead render, and stamps the
last commit that touched its folder.

```bash
python tools/build_web.py --check    # validate, write nothing
python tools/build_web.py            # validate, then write prints.json
python tools/build_web.py --fix      # also decimate any web GLB over 2 MB (needs trimesh)
```

It also refuses to write if a file is near GitHub's size limits or if anything published is
tracked by git-lfs — raw.githubusercontent and jsDelivr serve the LFS pointer text, not the
file, so an LFS'd model is a silently broken model on the web. Plain git only here; the largest
file is about 7 MB.

jsDelivr is faster and also works, but caches a branch for hours:

```
https://cdn.jsdelivr.net/gh/mehdiacho/3d-prints@main/prints.json
https://purge.jsdelivr.net/gh/mehdiacho/3d-prints@main/prints.json
```

## Rebuilding the models

Each print's README has its own command. They all want the same handful of packages:

```bash
pip install manifold3d trimesh numpy shapely scipy
```

The scripts carry the blueprint's measurement letters in their variable names, so a dimension
on a drawing traces to the line of code that uses it. Every one of them mirrors exactly one
axis on export, with a comment saying why — see the handedness section of
[METHOD.md](METHOD.md), which is the mistake that cost the most.

## Licence

- **Code** — the build scripts and the page code: [MIT](LICENSE).
- **Models, drawings, renders and descriptions**:
  [CC BY-SA 4.0](LICENSE-models.md) — credit and share alike.

One exception, stated in full in [LICENSE-models.md](LICENSE-models.md) and in
[that print's README](prints/key-fob/README.md): the key fob body's outer cross-section derives
from a downloaded model whose licence could not be found. That model is not published here, and
the derivation can be removed outright.

No warranty. Most of these have never been printed, and the figures for how much force a part
holds are calculated, not measured, and are marked as such. Check anything that has to hold
something up before you trust it.
