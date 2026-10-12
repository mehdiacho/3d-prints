"""
Mazda flip key (2007 Atenza) - replacement remote BODY, v4: two halves glued together around the head's tab.

What changed from v3 (after the v3 fit tests, 9 Oct 2026):
  1. v3 came out MIRRORED. The measurement coordinates below (x, y, z) are a left-handed set, and v3 used them
     as right-handed model axes, so the blade slot ended up on the wrong side and nothing lined up. v4 builds in
     the same coordinates and then mirrors z once (the same fix as the charger brace's X = -u). Do not remove it.
  2. The button panels are on the LOGO face, the same face as the V notch for the logo-face skirt and the face
     the tab and folded blade sit closest to. v3 had them on the rivet face.
  3. The body is split on a plane parallel to the faces (y = SPLIT_Y), through the tab socket, the hook catch and
     the blade slot, so the hook never has to be forced into a closed socket:
       - RIVET half (y < SPLIT_Y): lay the head in it, logo face up, blade folded. The tab, hook, base and blade
         all drop into pockets that are open on the split face.
       - LOGO half (y > SPLIT_Y): lay it on top and glue. Everything under the logo-face skirt's V is left open
         in this half, so it closes straight down over the skirt.
     Two 2.0 holes take 1.75 filament pins to line the halves up.

Coordinates (mm), as on the measurement blueprint:
  x = across the width, 0 = blade-side edge          y = thickness, 0 = rivet face, 15.8 = logo face
  z = along the key, 0 = dome tip of the head, increasing towards the keyring end
Needs: pip install trimesh manifold3d shapely numpy   (and the TPU cover STL for the profile shape)
"""
import sys, numpy as np, trimesh
from shapely.geometry import MultiPoint, Polygon
from shapely.geometry.polygon import orient
from manifold3d import Manifold, CrossSection

COVER_STL = sys.argv[1] if len(sys.argv) > 1 else "Mazda_5_Fob_Cover.stl"   # only used for the curved cross-section
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

# ---------------- measured (blueprint letters) ----------------
W, TH = 31.90, 15.80          # B, C
E = 23.34                     # dome tip -> bottom corners
D = 21.34                     # dome tip -> rivet-face rim centre (V points up)
S = 29.10                     # dome tip -> logo-face rim centre (V points down, the skirt)
AB = 24.34                    # dome tip -> flat bottom face
AF = 1.44                     # bottom face set in from the outer faces
TAB_X, TAB_W = 15.30, 7.04    # J, H
HOOK = 1.80                   # I - H
TAB_Y, TAB_T = 7.95, 5.50     # M, L
TAB_LEN = 14.60               # F
BLADE_W = 10.00               # P (blade flush with the blade side, O = 0)
GAP_Y0, GAP_Y1 = 7.53, 11.13  # blade gap (T = 3.60)
TIP = E + 39.12               # N: folded blade tip from the dome tip

# ---------------- design ----------------
SPLIT_Y = 10.2                # glue plane: rivet half below, logo half above
SKIRT_CLR = 0.2               # room under the logo-face skirt's V
BLADE_CLR = 0.6
END = TIP + 3.0
END_ROUND = 1.5
RING = dict(x=26.5, z=END - 5.5, d=4.5)
PANEL_DEPTH = 0.8
PINS = [(12.0, 33.0), (26.0, 34.0)]   # (x, z) of the two filament pins
PIN_D, PIN_LEN = 2.0, 3.0              # hole diameter, depth into each half
FIT_TEST_Z = AB + TAB_LEN + 2.5        # fit test = everything from the joint to here

VARIANTS = {  # name: (tab clearance per side, extra room at the rivet-face lip, marking grooves)
    "A_tight": (0.15, 0.00, 1),
    "B_standard": (0.25, 0.00, 2),
    "C_loose": (0.35, 0.15, 3),
}

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def xz_prism(pts_xz, y0, y1):
    """prism from an (x, z) polygon, spanning y0..y1"""
    cs = CrossSection([list(orient(Polygon(pts_xz), 1.0).exterior.coords)[:-1]])
    m = Manifold.extrude(cs, y1 - y0).rotate([90, 0, 0])
    return m.translate([0, y1, 0])

def ycyl(x, z, y0, y1, r):
    return Manifold.cylinder(y1 - y0, r, r, 48).rotate([-90, 0, 0]).translate([x, y0, z])

# ---- cross-section: the real fob outline (from the cover), scaled to W x TH, y from the rivet face ----
cover = trimesh.load(COVER_STL)
sec = cover.section(plane_origin=[0, 0, -45], plane_normal=[0, 0, 1])
pts = np.vstack([e[:, :2] for e in sec.discrete])
prof = MultiPoint(pts).convex_hull.buffer(-1.5, join_style=1)
c = np.array(orient(prof, 1.0).exterior.coords)[:-1]
minx, miny, maxx, maxy = prof.bounds
c = np.c_[(c[:, 0] - minx) * W / (maxx - minx), (maxy - c[:, 1]) * TH / (maxy - miny)]
PROFILE = Polygon(c)

def section(inset):
    p = orient(PROFILE.buffer(-inset, join_style=1), 1.0)
    return np.array(p.exterior.coords)[:-1]

def extrude_xy(poly, z0, z1):
    return Manifold.extrude(CrossSection([list(orient(poly, 1.0).exterior.coords)[:-1]]), z1 - z0).translate([0, 0, z0])

# ---- solid body: profile slices lofted, rounded at the keyring end ----
def solid():
    z0 = D - 0.5
    zs = list(np.arange(z0, END - END_ROUND, 2.0)) + list(np.linspace(END - END_ROUND, END, 7))
    parts, prev = [], None
    for z in zs:
        d = z - (END - END_ROUND)
        inset = END_ROUND - np.sqrt(max(END_ROUND ** 2 - d ** 2, 0)) if d > 0 else 0
        cur = [[x, y, z] for x, y in section(min(inset, 7.0))]
        if prev is not None:
            parts.append(Manifold.hull_points(prev + cur))
        prev = cur
    b = parts[0]
    for p in parts[1:]:
        b = b + p
    return b
SOLID = solid()

zr = lambda x: E - (E - D) * (1 - abs(x - W / 2) / (W / 2))      # rivet-face rim: up to D in the middle
zl = lambda x: E + (S - E) * (1 - abs(x - W / 2) / (W / 2))      # logo-face rim: down to S in the middle
XS = np.linspace(-1, W + 1, 41)

# OEM button layout, now on the LOGO face. Each panel is (x, fraction 0..1 down its own height) scaled to its z band.
SX = W / 34.0
PANELS = [
    ([(7.5, 0), (26.5, 0), (26.5, .76), (17, 1), (7.5, .76)], (30.6, 38.4)),     # nearest the joint
    ([(7.5, .23), (17, 0), (26.5, .23), (26.5, 1), (7.5, 1)], (39.9, 47.4)),
    ([(7, .19), (17, 0), (27, .19), (27, .81), (17, 1), (7, .81)], (48.9, 56.6)),  # nearest the keyring
]

def build(clr, slack, marks):
    lip = AF - slack
    b = SOLID
    # ---- joint with the head ----
    b = b - box(-2, W + 2, lip, TH + 2, 0, E)                                                     # cut to the corner level
    b = b - xz_prism([(x, zr(np.clip(x, 0, W))) for x in XS] + [(W + 1, 0), (-1, 0)], -2, lip)   # rivet-face lip up to D
    b = b - extrude_xy(PROFILE.buffer(-lip, join_style=1), 0, AB)                                # recess for the bottom face
    # everything under the logo-face skirt's V is open in the logo half, so that half closes straight over it
    b = b - xz_prism([(x, zl(np.clip(x, 0, W)) + SKIRT_CLR + slack) for x in XS] + [(W + 1, 0), (-1, 0)], SPLIT_Y - 0.001, TH + 2)
    # ---- folded blade slot: open on the blade side and at the top ----
    b = b - box(-2, BLADE_W + BLADE_CLR, GAP_Y0, GAP_Y1, 0, TIP + 0.8)
    # ---- tab socket with the hook catch; both open on the split face ----
    tx0, tx1 = TAB_X - clr, TAB_X + TAB_W + clr
    ty0, ty1 = TAB_Y - clr, TAB_Y + TAB_T + clr
    depth = AB + TAB_LEN + 0.6
    b = b - box(tx0, tx1, ty0, ty1, 0, depth)
    b = b - box(tx0 - HOOK - clr, tx0 + 0.01, ty0, ty1, depth - 1.4 - 2 * clr, depth)
    # ---- keyring hole ----
    b = b - ycyl(RING["x"], RING["z"], -5, TH + 5, RING["d"] / 2)
    # ---- button panels, PANEL_DEPTH under the curved logo face ----
    skin = extrude_xy(PROFILE.buffer(1.0, join_style=1), 0, END + 1) - extrude_xy(PROFILE.buffer(-PANEL_DEPTH, join_style=1), -1, END + 2)   # outer side well clear of the face: no coincident faces
    for poly, (za, zb) in PANELS:
        b = b - (skin ^ xz_prism([(x * SX, za + f * (zb - za)) for x, f in poly], TH / 2, TH + 2))
    # ---- filament pins across the split ----
    for x, z in PINS:
        b = b - ycyl(x, z, SPLIT_Y - PIN_LEN, SPLIT_Y + PIN_LEN, PIN_D / 2)
    # ---- marking grooves on the tab-side edge (1 = tight, 2 = standard, 3 = loose), on both halves ----
    for i in range(marks):
        b = b - box(W - 0.6, W + 2, -1, TH + 1, 34 + 1.6 * i, 34.8 + 1.6 * i)
    return b

def halves(m):
    big = 500
    rivet = m ^ box(-big, big, -big, SPLIT_Y, -big, big)
    logo = m ^ box(-big, big, SPLIT_Y, big, -big, big)
    return rivet, logo

def fix_handedness(m):
    """The measurement axes are left-handed: mirror z once so the part is not built back to front."""
    return m.mirror([0, 0, 1])

def to_mesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts)

def standing(m):
    """Stand a half on its keyring end (or the fit test on its cut face), joint up. Mirroring is already done; this only translates."""
    t = to_mesh(m)
    parts = [p for p in t.split(only_watertight=False) if abs(p.volume) > 1.0]   # drop zero-volume slivers left by a cut
    t = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    t.apply_translation(-np.array([t.bounds[0, 0], t.bounds[0, 1], t.bounds[0, 2]]))
    return t

def export_set(m, stem):
    r, l = halves(fix_handedness(m))
    tr, tl = standing(r), standing(l)
    tr.export(f"{OUT}/{stem}_rivet_half.stl"); tl.export(f"{OUT}/{stem}_logo_half.stl")
    tl2 = tl.copy(); tl2.apply_translation([0, tr.extents[1] + 6, 0])
    trimesh.util.concatenate([tr, tl2]).export(f"{OUT}/{stem}_both_halves.stl")
    for n, t in (("rivet half", tr), ("logo half", tl)):
        print(f"{stem} {n}: watertight={t.is_watertight} bodies={len(t.split(only_watertight=False))} "
              f"size={t.extents.round(2)} vol={t.volume / 1000:.2f} cm3 PETG~{t.volume / 1000 * 1.27:.1f} g")
    return fix_handedness(m)

if __name__ == "__main__":
    for name, (clr, slack, marks) in VARIANTS.items():
        whole = build(clr, slack, marks)
        export_set(whole, f"mazda_flipkey_body_v4_{name}")
        export_set(whole ^ box(-5, 40, -5, 25, 0, FIT_TEST_Z), f"mazda_flipkey_fit_test_v4_{name}")
        if name == "B_standard":   # one-piece reference model for the blueprint's 3D view (mirroring fixed, not split)
            to_mesh(fix_handedness(whole)).export(f"{OUT}/mazda_flipkey_body_v4_reference_whole.stl")
