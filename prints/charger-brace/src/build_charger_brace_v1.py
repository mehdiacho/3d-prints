"""
Laptop charger brace, v1 - two halves that clamp the barrel plug of an Alienware m15 R7 charger and clip over
the laptop's rear bar. Built from blueprint sheet 01 (laptop and plug, measured) and sheet 02 (the brace, proposed).

Coordinates (mm), as on the blueprint:
  u = sideways from the plug's centre line, + towards the HDMI port
  y = up from the laptop's underside
  z = out of the laptop along the plug, 0 = the TOP edge of the rear face
The blueprint's (u, y, z) is a left-handed set, so the model is built with X = -u. Do not remove that minus sign:
without it the part comes out mirrored and the plate lands over the vent.

Letters are the blueprint's measurements. Needs: pip install trimesh manifold3d shapely numpy
"""
import sys, numpy as np, trimesh
from math import cos, pi, sqrt
from manifold3d import Manifold, CrossSection

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
SEG = 96

# ---------------- measured (sheet 01) ----------------
A = 7.5        # metal sleeve diameter
B = 12.67      # sleeve length
C = 11.2       # body diameter
D = 11.3       # bump diameter (widest part of the body)
L = 2.5        # bump length
E = 23.5       # body length including the bump
F = 10.3       # light ring diameter
G = 2.0        # light ring length
H = 4.25       # torn gap
I = 10.0       # strain relief, thick end
AF = 7.95      # strain relief, thin end
J = 14.2       # strain relief length
K = 6.0        # cable diameter
P = 23.0       # laptop thickness at the rear
R = 10.59      # underside to the centre of the jack
N = 3.0        # sleeve left showing when the plug is home
W = 17.4       # jack centre to screw centre
Z = 18.4       # rear bar depth: top of the rear face to the ridge
AL = 5.0       # rear face slope: bottom edge beyond the top edge
AM = 14.0      # ridge to the lowest line of the trough
AN = 10.0      # depth of the trough at its lowest

# ---------------- proposed (sheet 02) ----------------
BA = 2.8                 # spacer plate thickness at the jack
BB = 11.3                # bore that grips the plug body
BC = 16.4                # outside diameter of the shell
BD = 52.3                # how far the brace stands out of the rear face
BK = 6.6                 # cable bore at the mouth
PLATE_VENT, PLATE_HDMI = 7.25, 26.25     # BE 33.5: plate width each side of the centre line
ARM_HDMI = 16.25                         # BG 23.5 = PLATE_VENT + ARM_HDMI
PLATE_FOOT = 4.0                         # BF 19: the plate runs from here up to the top of the rear bar
BI = 5.0                 # hook reach past the ridge
BN = 7.8                 # hole for the metal sleeve
SCREW_HOLE = 4.4         # clearance over the screw beside the jack (screw head not measured)
TIE_Z = (12.0, 39.0)     # where the two cable-tie grooves start
TIE_W, TIE_D = 3.0, 1.0
LIP_R = 6.6              # outside radius at the end of the mouth
# ---------------- fit allowances for v1 ----------------
SPLIT_GAP = 0.3          # left between the halves so the ties can pull them onto the body
BUMP_R = D / 2 + 0.2     # relief so the bump is not pinched
RING_R = F / 2 + 0.2     # pocket over the light ring and the tear
RELIEF_CLR = 0.15        # around the strain relief
PIN_D = 2.0              # hole for a 1.75 filament pin that stops the halves sliding

JY, THK = R, P
FJ = AL * (1 - JY / THK)                 # where the sloping rear face is, at jack height
ZP = FJ + BA                             # outer face of the spacer plate
ZB0 = FJ + N                             # front face of the plug body
ZR0 = ZB0 + E                            # body ends, light ring starts
ZR1 = ZR0 + G
ZS0 = ZR1 + H                            # strain relief starts
ZS1 = ZS0 + J
ZEND = FJ + BD
ROUT = BC / 2
zf = lambda y: AL * (1 - y / THK)        # the sloping rear face
drop = lambda s: AN * (1 - cos(pi * min(1, max(0, s) / AM))) / 2    # ASSUMED trough curve (sheet 01, V4)
trough = lambda z: THK - drop(-Z - z)
ZT = -Z - BI                             # where the hook lip lands


def ccw(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]

def yz_prism(pts_zy, x0, x1):
    """prism from a (z, y) polygon, spanning x0..x1"""
    cs = CrossSection([ccw([(-z, y) for z, y in pts_zy])])
    return Manifold.extrude(cs, x1 - x0).rotate([0, 90, 0]).translate([x0, 0, 0])

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def zcyl(x, y, z0, z1, r):
    return Manifold.cylinder(z1 - z0, r, r, SEG).translate([x, y, z0])

def revolve(pts_rz):
    """solid of revolution about the plug's axis from an (r, z) outline"""
    return Manifold.revolve(CrossSection([ccw(list(pts_rz))]), SEG).translate([0, JY, 0])


def brace(arm_t):
    army = THK + arm_t
    under = [(ZT + (-Z - ZT) * i / 8, trough(ZT + (-Z - ZT) * i / 8)) for i in range(9)]     # hook underside, shaped to the trough
    profile = [(zf(PLATE_FOOT), PLATE_FOOT), (ZP, PLATE_FOOT), (ZP, army), (-Z - 1.5, army),
               (ZT - 1.9, trough(ZT) + arm_t + 0.4), (ZT - 1.5, trough(ZT) + 0.6), *under, (0, THK)]
    # X = -u: the HDMI side is negative X
    body = yz_prism(profile, -PLATE_HDMI, PLATE_VENT)
    body -= box(-PLATE_HDMI - 1, -ARM_HDMI, THK, army + 1, ZT - 5, ZP + 1)          # the arm is narrower than the plate
    body -= box(-PLATE_HDMI - 1, -ARM_HDMI, trough(ZT) - 1, THK + .001, ZT - 5, -.001)   # so is the hook (nothing there anyway)
    outer = [(ROUT, ZP - .01), (ROUT, TIE_Z[0]), (ROUT - TIE_D, TIE_Z[0]), (ROUT - TIE_D, TIE_Z[0] + TIE_W), (ROUT, TIE_Z[0] + TIE_W),
             (ROUT, TIE_Z[1]), (ROUT - TIE_D, TIE_Z[1]), (ROUT - TIE_D, TIE_Z[1] + TIE_W), (ROUT, TIE_Z[1] + TIE_W), (ROUT, 44), (LIP_R, ZEND)]
    body += revolve([(0, ZP - .01), *outer, (0, ZEND)])
    # the hollow: sleeve hole, body bore, bump relief, ring-and-tear pocket, strain relief taper, mouth
    bore = [(0, -2), (BN / 2, -2), (BN / 2, ZP), (BB / 2, ZP), (BB / 2, ZR0 - L - .3), (BUMP_R, ZR0 - L - .3), (BUMP_R, ZR0),
            (RING_R, ZR0), (RING_R, ZS0), (I / 2 + RELIEF_CLR, ZS0), (AF / 2 + RELIEF_CLR, ZS1), (BK / 2, ZS1), (BK / 2, ZEND - 4), (5, ZEND + .01), (0, ZEND + .01)]
    body -= revolve(bore)
    body -= zcyl(-W, JY, -2, ZP + 1, SCREW_HOLE / 2)
    for s in (1, -1):                                                              # windows at the light ring
        x0, x1 = sorted((s * 4.5, s * (ROUT + 1)))
        body -= box(x0, x1, JY - 1.7, JY + 1.7, ZR0 - .6, ZR1 + .6)
    body -= Manifold.cylinder(8, PIN_D / 2, PIN_D / 2, 32).rotate([0, 90, 0]).translate([-4, 20.6, 3.0])   # filament pin
    return body


def halves(arm_t):
    b = brace(arm_t)
    big = 200
    vent = b ^ box(SPLIT_GAP / 2, big, -big, big, -big, big)        # X > 0 = vent side
    hdmi = b ^ box(-big, -SPLIT_GAP / 2, -big, big, -big, big)
    return b, vent, hdmi

def to_mesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts)

def on_bed(m, side):
    """lay a half on its split face. A proper rotation, never a mirror."""
    t = to_mesh(m)
    Rm = np.eye(4)
    Rm[:3, :3] = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]] if side == "hdmi" else [[0, 0, -1], [0, 1, 0], [1, 0, 0]]
    t.apply_transform(Rm)
    t.apply_translation(-np.array([t.bounds[0, 0], t.bounds[0, 1], t.bounds[0, 2]]))
    return t


if __name__ == "__main__":
    for arm_t, tag in ((2.4, "arm2.4"), (3.0, "arm3.0")):
        whole, vent, hdmi = halves(arm_t)
        tv, th = on_bed(vent, "vent"), on_bed(hdmi, "hdmi")
        tv.export(f"{OUT}/charger_brace_v1_{tag}_vent_half.stl"); th.export(f"{OUT}/charger_brace_v1_{tag}_hdmi_half.stl")
        both = th.copy(); tv2 = tv.copy(); tv2.apply_translation([0, th.extents[1] + 6, 0])
        plate = trimesh.util.concatenate([both, tv2]); plate.export(f"{OUT}/charger_brace_v1_{tag}_both_halves.stl")
        for n, t in (("vent half", tv), ("hdmi half", th)):
            print(f"{tag} {n}: watertight={t.is_watertight} bodies={len(t.split(only_watertight=False))} size={t.extents.round(2)} vol={t.volume / 1000:.2f} cm3 PETG~{t.volume / 1000 * 1.27:.1f} g")
