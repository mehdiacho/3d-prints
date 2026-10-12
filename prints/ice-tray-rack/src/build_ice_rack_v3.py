"""Ice tray rack v3 — models for the Ice Tray Blueprint (sheets 01 to 05).

v3 (11 Oct, evening; Mehdi): the tray hangs on its four long-side fins (fin seats), not on floor rails; printed pegs
join the bays (threaded into the bay below, snapped into the bay above), in tubes outside the walls, with room for
5 mm magnets later; the catch pan sits under each bay's own tray on its floor ties; levelling feet screw into
adaptors under the bottom bay (no base). Lighter everywhere. v2 had the bay's corner posts running through the
tray's lip corners: fixed by moving the posts outside the walls.

Units mm, Z up, as drawn on the blueprint. Every name below carries the blueprint's letter.
  python3 build_ice_rack_v3.py <out folder>
Writes one STL per part (mm, Z up, for slicing and for Fusion) and one GLB per model shown on the page
(metres, Y up, for the page's 3D view, published as base64 text).

MEASURED (Mehdi, 9 and 11 Oct): the plastic tray and the silicone tray.
PROPOSED (PROP.): the bay, pegs, feet, the splitter, the cascade pan and the silicone base plate. Nothing here is fit-tested.
Handedness: x along the tray from its left end, y across from the far edge towards you, z up.
Seen from above that is x to the right and y down the page, which is left-handed (x × y = -z), so the
model mirrors y once (Y_MIRROR) on export and then matches the plan views.
"""
import math, os, sys
import numpy as np
import manifold3d as mf
import trimesh

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
mf.set_circular_segments(28)
M, CS = mf.Manifold, mf.CrossSection
ROUND = mf.JoinType.Round


# ---------- helpers ----------
def rrect(x0, y0, x1, y1, r=0.0):
    w, h = x1 - x0, y1 - y0
    r = max(0.0, min(r, w / 2 - 0.01, h / 2 - 0.01))
    if r <= 0:
        return CS.square([w, h]).translate([x0, y0])
    return CS.square([w - 2 * r, h - 2 * r]).translate([x0 + r, y0 + r]).offset(r, ROUND)


def slab(cs, z0, z1):
    return M.extrude(cs, z1 - z0).translate([0, 0, z0])


def box(x0, y0, z0, x1, y1, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def frustum(bot, top, z0, z1):
    """hull of two thin slabs: rounded-rect frustum"""
    e = 0.01
    return M.batch_hull([slab(bot, z0, z0 + e), slab(top, z1 - e, z1)])


def union(parts):
    parts = [p for p in parts if p is not None]
    return M.batch_boolean(parts, mf.OpType.Add) if len(parts) > 1 else parts[0]


def to_trimesh(man):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(vertices=v.copy(), faces=f.copy(), process=True)


Y_MIRROR = True   # the blueprint's y runs away from you seen from above with x to the right: mirror once


def fix(tm):
    tm = tm.copy()
    if Y_MIRROR:
        tm.apply_transform(np.diag([1, -1, 1, 1]))   # trimesh flips the winding itself on a reflection
    assert tm.is_winding_consistent and tm.volume > 0, "faces must point out"
    return tm


def save(name, man, glb_parts=None):
    tm = fix(to_trimesh(man))
    tm.export(os.path.join(OUT, name + ".stl"))
    return tm


def glb(name, meshes):
    """metres, Y up: (x, y, z)mm -> (x, z, -y)m"""
    sc = trimesh.Scene()
    T = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float) @ np.diag([0.001, 0.001, 0.001, 1])
    for i, tm in enumerate(meshes):
        t = tm.copy(); t.apply_transform(T)
        sc.add_geometry(t, node_name=f"{name}_{i}")
    path = os.path.join(OUT, name + ".glb")
    sc.export(path)
    return path


report = {}


def note(name, man):
    v = man.volume()
    bb = man.bounding_box()
    report[name] = dict(vol_cm3=round(v / 1000, 1), petg_g=round(v / 1000 * 1.27, 1),
                        size=[round(bb[3] - bb[0], 1), round(bb[4] - bb[1], 1), round(bb[5] - bb[2], 1)])


# =====================================================================
# PLASTIC TRAY — sheet 01, MEASURED (P Q R S T U V AA W AB AC AD AE AF AG Z AH AI AJ AK AL)
# =====================================================================
PL, PWd, PH = 210.0, 102.0, 34.5          # P Q R
LIP, CWp, CHp = 6.5, 28.0, 39.5           # S T U
DVp = (PL - 2 * LIP - 6 * CWp) / 5        # AM 5.8 (DERIVED)
MIDp = PWd - 2 * LIP - 2 * CHp            # AN 10 (DERIVED)
PFL = PH - 33.5                           # floor, from V
IWH = 24.5                                # AA walls between cells, above the floor
WTOP = PFL + IWH                          # 25.5 above the table
RDG, RGAP = 2.0, 3.45                     # W, AB
CHIN, CHT, LIPT = 12.0, 1.2, 1.2          # AC AD AG
FIN, FIN2, FINT, FINX, FINY = 29.5, 27.5, 1.5, 166.0, 62.0   # Z AH AI AK AJ
SUPG = 20.0                               # AL
PTAP = 3.0                                # cell taper: NOT MEASURED (drawn)
WALL = 1.0                                # cell wall: NOT MEASURED (drawn)
px0 = lambda i: LIP + i * (CWp + DVp)
py0 = lambda j: LIP + j * (CHp + MIDp)


def plastic_tray():
    parts = []
    # lip frame and chin skirt
    outer = rrect(0, 0, PL, PWd, 4)
    parts.append(slab(outer - rrect(LIP, LIP, PL - LIP, PWd - LIP, 2), PH - LIPT, PH))
    parts.append(slab(outer - rrect(CHT, CHT, PL - CHT, PWd - CHT, 3), PH - CHIN, PH))
    # basin wall from the walls' tops up to the lip
    parts.append(slab(rrect(LIP - WALL, LIP - WALL, PL - LIP + WALL, PWd - LIP + WALL, 2) - rrect(LIP, LIP, PL - LIP, PWd - LIP, 2), WTOP - 2, PH))
    # cells: tapered outer bodies tiled at the walls' top
    cav = []
    for i in range(6):
        for j in range(2):
            xa = LIP - WALL if i == 0 else px0(i) - DVp / 2
            xb = PL - LIP + WALL if i == 5 else px0(i) + CWp + DVp / 2
            ya = LIP - WALL if j == 0 else py0(j) - MIDp / 2
            yb = PWd - LIP + WALL if j == 1 else py0(j) + CHp + MIDp / 2
            cx0, cx1, cy0, cy1 = px0(i), px0(i) + CWp, py0(j), py0(j) + CHp
            bot_in = rrect(cx0 + PTAP, cy0 + PTAP, cx1 - PTAP, cy1 - PTAP, 3)
            parts.append(frustum(bot_in.offset(WALL, ROUND), rrect(xa, ya, xb, yb, 1), 0, WTOP))
            cav.append(frustum(bot_in, rrect(cx0, cy0, cx1, cy1, 2.5), PFL, WTOP + 0.01))
    # ridges on the walls between cells, stopping short at each end
    for i in range(1, 6):
        x = px0(i) - DVp / 2
        for y0, y1 in [(LIP + RGAP, py0(0) + CHp - RGAP), (py0(1) + RGAP, PWd - LIP - RGAP)]:
            parts.append(box(x - 0.6, y0, WTOP - 0.5, x + 0.6, y1, WTOP + RDG))
    # fins: two per corner cell, stepped bottom: the half joined to the cell reaches Z, the half by the chin AH (flipped 11 Oct)
    fxA, fyA = (PL - FINX) / 2, (PWd - FINY) / 2 - FINT
    ymid = (CHT + LIP) / 2
    for x in (fxA, PL - fxA - FINT):
        for (ya, yb, yc) in [(CHT, ymid, LIP - 0.3), (PWd - CHT, PWd - ymid, PWd - LIP + 0.3)]:
            lo, hi = sorted((ya, yb)); parts.append(box(x, lo, PH - FIN2, x + FINT, hi, PH - LIPT))
            lo, hi = sorted((yb, yc)); parts.append(box(x, lo, PH - FIN, x + FINT, hi, PH - LIPT))
    xmid = (CHT + LIP) / 2
    for y in (fyA, PWd - fyA - FINT):
        for (xa, xb, xc) in [(CHT, xmid, LIP - 0.3), (PL - CHT, PL - xmid, PL - LIP + 0.3)]:
            lo, hi = sorted((xa, xb)); parts.append(box(lo, y, PH - FIN2, hi, y + FINT, PH - LIPT))
            lo, hi = sorted((xb, xc)); parts.append(box(lo, y, PH - FIN, hi, y + FINT, PH - LIPT))
    # supports between the chin and the cells
    for i in range(1, 5):     # mid-cell, full chin height, long sides (not the corner cells)
        x = px0(i) + CWp / 2 - 0.6
        for ya, yb in [(CHT, LIP - 0.3), (PWd - LIP + 0.3, PWd - CHT)]:
            parts.append(box(x, ya, PH - CHIN, x + 1.2, yb, PH - LIPT))
    for i in range(1, 6):     # between cells, half height
        x = px0(i) - DVp / 2 - 0.6
        for ya, yb in [(CHT, LIP - 0.3), (PWd - LIP + 0.3, PWd - CHT)]:
            parts.append(box(x, ya, PH - CHIN / 2, x + 1.2, yb, PH - LIPT))
    for y in (PWd / 2 - SUPG / 2 - 1.2, PWd / 2 + SUPG / 2):   # two at each end, AL apart
        for xa, xb in [(CHT, LIP - 0.3), (PL - LIP + 0.3, PL - CHT)]:
            parts.append(box(xa, y, PH - CHIN, xb, y + 1.2, PH - LIPT))
    body = union(parts)
    # the pool above the walls between cells, and the cells
    pool = slab(rrect(LIP, LIP, PL - LIP, PWd - LIP, 2), WTOP, PH + 1)
    return body - union(cav + [pool])


# =====================================================================
# SILICONE TRAY — sheet 04 (shelved), MEASURED (A B E F G I J K; C D as drawn)
# =====================================================================
SL, SW, CWs, CHs, DV, SH, RT, KD = 340.0, 185.0, 32.0, 37.0, 6.5, 31.5, 5.0, 28.5
FLR = SH - KD
SRX, SRY = (SL - 8 * CWs - 7 * DV) / 2, (SW - 4 * CHs - 3 * DV) / 2
SR, PWL, LIPW, LIPD, CBX, CBY = 24.0, 1.3, 6.0, 1.75, 30.0, 35.0   # L TBD; wall; lip (IND.); cup bottoms H O TBD
sx0 = lambda i: SRX + i * (CWs + DV)
sy0 = lambda j: SRY + j * (CHs + DV)
scx = lambda i: sx0(i) + CWs / 2
scy = lambda j: sy0(j) + CHs / 2


def silicone_tray():
    parts, cav = [], []
    rim = rrect(0, 0, SL, SW, SR)
    parts.append(slab(rim, SH - RT, SH))
    parts.append(slab(rim - rrect(LIPW, LIPW, SL - LIPW, SW - LIPW, max(SR - LIPW, 1)), SH - RT - LIPD, SH))
    for i in range(8):
        for j in range(4):
            top_in = rrect(sx0(i), sy0(j), sx0(i) + CWs, sy0(j) + CHs, 4)
            bot_out = rrect(scx(i) - CBX / 2, scy(j) - CBY / 2, scx(i) + CBX / 2, scy(j) + CBY / 2, 4)
            bot_in = rrect(scx(i) - CBX / 2 + PWL, scy(j) - CBY / 2 + PWL, scx(i) + CBX / 2 - PWL, scy(j) + CBY / 2 - PWL, 3)
            parts.append(frustum(bot_out, top_in.offset(PWL, ROUND), 0, SH - RT + 0.5))
            cav.append(frustum(bot_in, top_in, FLR, SH + 0.5))
    return union(parts) - union(cav)


# the silicone tray's base plate (sheet 04, PROPOSED, parked)
BP = dict(x0=10, x1=SL - 10, t=2.4, rib=2, ribH=6, perH=8, endT=3, endL=120, gapR=0.5, winX=18, winY=22, r=12)
BP["endH"] = SH - RT - BP["gapR"]; BP["split"] = SL / 2
ribX = [SRX - DV / 2 + i * (CWs + DV) for i in range(9)]
ribY = [SRY - DV / 2 + j * (CHs + DV) for j in range(5)]


def silicone_base_plate():
    b = BP
    plate = rrect(b["x0"], 0, b["x1"], SW, b["r"])
    for i in range(8):
        for j in range(4):
            plate = plate - rrect(scx(i) - b["winX"] / 2, scy(j) - b["winY"] / 2, scx(i) + b["winX"] / 2, scy(j) + b["winY"] / 2, 3)
    parts = [slab(plate, 0, b["t"])]
    for j in range(5):
        h = b["perH"] if j in (0, 4) else b["ribH"]
        parts.append(box(ribX[0] - 1, ribY[j] - 1, 0, ribX[8] + 1, ribY[j] + 1, b["t"] + h))
    for i in range(9):
        h = b["perH"] if i in (0, 4, 8) else b["ribH"]
        if i == 4:
            parts.append(box(b["split"] - 2, ribY[0], 0, b["split"] + 2, ribY[4], b["t"] + h))
        else:
            parts.append(box(ribX[i] - 1, ribY[0], 0, ribX[i] + 1, ribY[4], b["t"] + h))
    for x0 in (b["x0"], b["x1"] - b["endT"]):
        parts.append(box(x0, SW / 2 - b["endL"] / 2, 0, x0 + b["endT"], SW / 2 + b["endL"] / 2, b["t"] + b["endH"]))
    return union(parts)




COARSE = False      # True: fewer facets, for the page's viewer and for Fusion's simulation


def thread(r, h, e, pitch, z0=0.0):
    """a printed screw thread, no hardware: a circle set e off-centre, twisted one turn per pitch as it rises.
    The matching hole is the same shape a little bigger; screwing along it sweeps the same shape."""
    seg, per = (16, 12) if COARSE else (48, 40)
    turns = h / pitch
    return M.extrude(CS.circle(r, seg).translate([e, 0]), h, max(2, int(turns * per)), turns * 360.0).translate([0, 0, z0])


def ring_grooves(r, zs, h, seg=40):
    return union([M.cylinder(h, r, r, seg).translate([0, 0, z]) for z in zs])


# =====================================================================
# THE BAY v3 — sheet 02, PROPOSED. One plastic tray per bay; bays stack.
# x along the tray (front x = 0), y across from the left wall's inner... see below, z up from the bay's underside.
# The tray hangs on its four long-side fins, which drop into slotted seats on the inside of the walls.
# =====================================================================
BAY = dict(L=200.0, Win=110.0, t=1.6, H=54.0,
           tie=4.0, tieF=5.0, tieM=3.0, tieB=2.0,            # floor ties: front, middle, back heights (the pan rests on them, falling to the back)
           win=31.0, winZ0=3.0, winZ1=50.0, nwin=5,           # pointed windows in the walls
           tubeOD=11.0, tubeY=-4.5, tubeX=6.0, segB=13.0, segT=14.0, cone=9.0,   # peg tubes outside the walls
           seatW=10.0, seatT=2.0, webH=3.0, slotW=5.0, slotD=2.5, cells=9.0)            # fin seats; the tray's cells stand 9 clear of the bay's underside
BAY["W"] = BAY["Win"] + 2 * BAY["t"]
BAY["Win"] = 110.0
PEG = dict(r=3.3, e=0.6, pitch=2.0, thL=8.0, clr=0.25, sock=6.3, pin=6.1, rib=6.8, ribH=0.8, groove=7.0, grooveH=1.0,
           pinL=11.0, slot=1.2, slotL=9.0, grooves=(3.0, 7.0), bore=5.2)
TRAY_X0 = (BAY["L"] - PL) / 2                     # -5: the tray centred along the bay
TRAY_Y0 = BAY["t"] + (BAY["Win"] - PWd) / 2       # 6
TRAY_Z0 = BAY["cells"]                            # the cells' bottoms
FINX_T = [(PL - FINX) / 2 + FINT / 2, PL - (PL - FINX) / 2 - FINT / 2]   # fin centres along the tray (tray x)
FINX_B = [TRAY_X0 + f for f in FINX_T]            # ... and along the bay
SEAT_TOP = TRAY_Z0 + PH - FIN                     # 14: where the fin's lowest edge (Z) lands
_inner = ((CHT + LIP) / 2 + LIP - 0.3) / 2          # middle of the fin's inner half, across the tray
SEAT_YC = [TRAY_Y0 + _inner, TRAY_Y0 + PWd - _inner]  # the seat plates sit under it
TUBES = [(x, y) for x in (BAY["tubeX"], BAY["L"] - BAY["tubeX"]) for y in (BAY["tubeY"], BAY["W"] - BAY["tubeY"])]
SPORT = dict(x=176.0, hole=8.4, od=8.0, bore=5.0, coll=2.0, collD=14.0, out=12.0, reach=16.0)
SPORT["z"] = TRAY_Z0 + PH + SPORT["od"] / 2 + 1.0  # spout run just above the tray's lip
SPORT["tip"] = TRAY_Z0 + PH + 2.0


SIM = False   # True: plain bores instead of threads and grooves (for Fusion's simulation)


def peg_socket_bottom():
    """cut: the snap socket in the bottom of a tube, with two grooves for the pin's ribs"""
    p = PEG
    if SIM:
        return M.cylinder(p["pinL"] + 1.5, p["sock"] / 2, p["sock"] / 2, 16).translate([0, 0, -1])
    return union([M.cylinder(p["pinL"] + .5 + 1, p["sock"] / 2, p["sock"] / 2, 40).translate([0, 0, -1]),
                  ring_grooves(p["groove"] / 2, p["grooves"], p["grooveH"])])


def peg_socket_top(H):
    """cut: the threaded hole in the top of a tube, a stop under it and a plain bore below (a magnet seat later)"""
    p = PEG
    if SIM:
        return M.cylinder(p["thL"] + 1, p["r"] + p["clr"] + p["e"], p["r"] + p["clr"] + p["e"], 16).translate([0, 0, H - p["thL"]])
    th = thread(p["r"] + p["clr"], p["thL"] + 1, p["e"], p["pitch"], H - p["thL"])   # same phase as the peg: it seats on the step at thL
    return union([th, M.cylinder(4.0, p["bore"] / 2, p["bore"] / 2, 32).translate([0, 0, H - p["thL"] - 4.0])])


def bay():
    b = BAY
    L, W, H, t = b["L"], b["W"], b["H"], b["t"]
    parts = []
    # side walls with pointed windows (45° tops print without support)
    wall = box(0, 0, 0, L, t, H)
    pitch = (L - 2 * 12.0) / b["nwin"]
    holes = []
    for k in range(b["nwin"]):
        cx, w = 12.0 + pitch * (k + .5), b["win"]
        prof = CS([[[cx - w / 2, b["winZ0"]], [cx + w / 2, b["winZ0"]], [cx + w / 2, b["winZ1"] - w / 2], [cx, b["winZ1"]], [cx - w / 2, b["winZ1"] - w / 2]]])
        holes.append(M.extrude(prof, t + 2).rotate([90, 0, 0]).translate([0, t + 1, 0]))
    wall = wall - union(holes)
    parts += [wall, wall.translate([0, W - t, 0])]
    # floor ties: front, middle, back, stepping down so a catch pan laid on them falls to the back
    for x0, h in [(0, b["tieF"]), (L / 2 - b["tie"] / 2, b["tieM"]), (L - b["tie"], b["tieB"])]:
        parts.append(box(x0, t - .01, 0, x0 + b["tie"], W - t + .01, h))
    # fin seats: a block on each wall under each long-side fin, slotted to locate the fin
    for fx in FINX_B:
        for yc in SEAT_YC:
            y0, y1 = yc - b["seatT"] / 2, yc + b["seatT"] / 2
            wy0, wy1 = (t - .01, y1) if yc < W / 2 else (y0, W - t + .01)
            parts.append(box(fx - b["seatW"] / 2, y0, 0, fx + b["seatW"] / 2, y1, SEAT_TOP))                  # plate
            parts.append(box(fx - b["seatW"] / 2, wy0, 0, fx + b["seatW"] / 2, wy1, b["webH"]))                # web to the wall
            for sx in (-1, 1):                                                                               # cheeks either side of the fin
                xa, xb = sorted((fx + sx * b["slotW"] / 2, fx + sx * b["seatW"] / 2))
                parts.append(box(xa, y0, SEAT_TOP - .01, xb, y1, SEAT_TOP + b["slotD"]))
    # peg tubes outside the walls: a bottom piece standing on the bed, a top piece held off the wall on a 45° cone
    R = b["tubeOD"] / 2
    for tx, ty in TUBES:
        wy = 0.0 if ty < 0 else W                      # the wall's outer face
        parts.append(M.cylinder(b["segB"], R, R, 40).translate([tx, ty, 0]))
        top = M.cylinder(b["segT"], R, R, 40).translate([tx, ty, H - b["segT"]])
        sliver = box(tx - R, wy - .5 if ty < 0 else wy, H - b["segT"] - b["cone"] - 2, tx + R, wy if ty < 0 else wy + .5, H - b["segT"] - b["cone"] - 1.99)
        cone = M.batch_hull([sliver, M.cylinder(.01, R, R, 40).translate([tx, ty, H - b["segT"]])])
        parts += [top, cone]
        # web joining the tube pieces to the wall
        parts.append(box(tx - 2, min(ty, wy), 0, tx + 2, max(ty, wy), b["segB"]))
    body = union(parts)
    cut = []
    for tx, ty in TUBES:
        cut.append(peg_socket_bottom().translate([tx, ty, 0]))
        cut.append(peg_socket_top(H).translate([tx, ty, 0]))
    for y in (-1, W - t - 1):
        cut.append(M.cylinder(t + 2, SPORT["hole"] / 2).rotate([-90, 0, 0]).translate([SPORT["x"], y, SPORT["z"]]))
    return body - union(cut)


def peg():
    """screws into the top of a tube on the bay below; its split, ribbed pin snaps into the tube above.
    Local axes: z up from the pin's... from the bottom of the thread; the bays meet at z = thL."""
    p = PEG
    th = thread(p["r"], p["thL"], p["e"], p["pitch"])
    pin = M.cylinder(p["pinL"] - 1, p["pin"] / 2, p["pin"] / 2, 40).translate([0, 0, p["thL"]])
    tip = M.cylinder(1.0, p["pin"] / 2, p["pin"] / 2 - .6, 40).translate([0, 0, p["thL"] + p["pinL"] - 1])
    ribs = ring_grooves(p["rib"] / 2, [p["thL"] + g + (p["grooveH"] - p["ribH"]) / 2 for g in p["grooves"]], p["ribH"])
    body = union([th, pin, tip, ribs])
    slot = box(-p["slot"] / 2, -5, p["thL"] + p["pinL"] - p["slotL"], p["slot"] / 2, 5, p["thL"] + p["pinL"] + 1)
    grip = box(-.8, -5, -1, .8, 5, 1.2)          # a screwdriver slot in the bottom, to wind it in
    return body - slot - grip


# =====================================================================
# THE SPLITTER — sheet 03, PROPOSED. Trough on the top bay; four equal holes in a sump; a spigot under each for
# 8 mm (inside) tube; the tubes go down to a push-in spout in each bay's side wall.
# =====================================================================
SPL = dict(L=120.0, W=BAY["W"], t=1.2, floor=1.6, H=34.0, sumpW=36.0, slope=4.0, hole=6.0, hpitch=18.0,
           spigOD=9.0, spigID=6.4, spigL=10.0, rib=1.2, ribs=(12.0, 34.0, 57.0, 80.0, 102.0))


def splitter():
    s, b = SPL, BAY
    x0 = b["L"] - s["L"]
    L, W, H, t = s["L"], s["W"], s["H"], s["t"]
    cxs, cys = x0 + L / 2, W / 2
    out_cs = rrect(x0, 0, x0 + L, W, 1)
    top_in = rrect(x0 + t, t, x0 + L - t, W - t, 4)
    sump = rrect(cxs - s["sumpW"] / 2, cys - s["sumpW"] / 2, cxs + s["sumpW"] / 2, cys + s["sumpW"] / 2, 3)
    sump_o = rrect(cxs - s["sumpW"] / 2 - t, cys - s["sumpW"] / 2 - t, cxs + s["sumpW"] / 2 + t, cys + s["sumpW"] / 2 + t, 3)
    # the floor is a shell of even thickness falling to the sump (underside sloped too, carried by the ribs)
    outer = M.batch_hull([slab(sump_o, 0, .01), slab(out_cs, s["slope"], s["slope"] + .01)]) + slab(out_cs, s["slope"], H)
    inner = M.batch_hull([slab(sump, s["floor"], s["floor"] + .01), slab(top_in, s["floor"] + s["slope"], s["floor"] + s["slope"] + .01)]) \
        + slab(top_in, s["floor"] + s["slope"], H + 1)
    body = outer - inner
    below = M.batch_hull([slab(sump_o, 0, .01), slab(out_cs, s["slope"], s["slope"] + .01)])   # for trimming ribs to the underside
    parts, cut = [body], []
    for dx in (-1, 1):
        for dy in (-1, 1):
            hx, hy = cxs + dx * s["hpitch"] / 2, cys + dy * s["hpitch"] / 2
            parts.append(M.cylinder(s["spigL"], s["spigOD"] / 2).translate([hx, hy, -s["spigL"]]))
            cut.append(M.cylinder(s["floor"] + 2, s["hole"] / 2).translate([hx, hy, -0.5]))
            cut.append(M.cylinder(s["spigL"] + .01, s["spigID"] / 2).translate([hx, hy, -s["spigL"] - .01]))
    # back feet: a lug over each back peg tube, with a snap socket for the peg; front feet on the side walls
    R = b["tubeOD"] / 2
    for tx, ty in TUBES[2:]:
        lug = M.cylinder(s["spigL"] + 6, R, R, 40).translate([tx, ty, -s["spigL"]])
        wy = 0.0 if ty < 0 else W
        web = box(tx - R, min(ty, wy) - .01, -s["spigL"], tx + R, max(ty, wy) + .01, 6)
        parts += [lug, web]
        cut.append(peg_socket_bottom().translate([tx, ty, -s["spigL"]]))
    for y in (0, b["W"] - b["t"] - 2):
        parts.append(box(x0, y, -s["spigL"], x0 + 8, y + b["t"] + 2, 0))
    # ribs along the trough under its floor: it prints standing on them and its spigots, no supports
    # (bridges of 23 at most); the tubes leave between them at the back
    under = box(x0, 0, -s["spigL"], x0 + L, W, s["slope"] + .01) - below    # the space under the sloped floor
    for y in s["ribs"]:
        parts.append(box(x0, y - s["rib"] / 2, -s["spigL"], x0 + L, y + s["rib"] / 2, s["slope"] + .01) ^ (under + box(x0, 0, -s["spigL"], x0 + L, W, 0.01)))
    # an end rib under each end wall, and one under each side wall, so no edge hangs in the air
    for xa in (x0, x0 + L - s["rib"]):
        rib = box(xa, 0, -s["spigL"], xa + s["rib"], W, s["slope"] + .01)
        if xa > x0:   # the back one leaves room for the four tubes to come out between the middle ribs
            rib = rib - box(xa - 1, s["ribs"][1] + s["rib"] / 2, -s["spigL"] - 1, xa + s["rib"] + 1, s["ribs"][3] - s["rib"] / 2, s["slope"] + 1) \
                + box(xa, s["ribs"][2] - s["rib"] / 2, -s["spigL"], xa + s["rib"], s["ribs"][2] + s["rib"] / 2, s["slope"] + .01)
        parts.append(rib ^ (under + box(x0, 0, -s["spigL"], x0 + L, W, 0.01)))
    for ya in (0, W - s["rib"]):
        parts.append(box(x0, ya, -s["spigL"], x0 + L, ya + s["rib"], s["slope"] + .01) ^ (under + box(x0, 0, -s["spigL"], x0 + L, W, 0.01)))
    return union(parts) - union(cut)


def spout():
    """pushed through the port in a bay's side wall from outside; the collar stops it; the nozzle drops into the near
    row of cells. Local axes: y from the wall's outer face inward, z up, centred on the port."""
    s = SPORT
    r = s["od"] / 2
    run = M.cylinder(s["out"] + s["reach"] + r, r).rotate([-90, 0, 0]).translate([0, -s["out"], 0])
    collar = M.cylinder(s["coll"], s["collD"] / 2).rotate([-90, 0, 0]).translate([0, -s["coll"], 0])
    drop = M.cylinder(s["z"] - s["tip"] + r, r).translate([0, s["reach"], s["tip"] - s["z"]])
    bore = union([M.cylinder(s["out"] + s["reach"] + 1, s["bore"] / 2).rotate([-90, 0, 0]).translate([0, -s["out"] - 1, 0]),
                  M.cylinder(s["z"] - s["tip"] + 2, s["bore"] / 2).translate([0, s["reach"], s["tip"] - s["z"] - 1])])
    return (union([run, collar, drop]) - bore).trim_by_plane([0, 0, 1], -s["collD"] / 2 + 0.6)


def plug():
    """sheet 03: stops one hole of the trough for a bay not in use (SO). A disc with a pull tab, the tapered pin standing
    on it; prints disc-down as modelled, and goes in pin-first from above."""
    disc = M.cylinder(1.6, 7.0, 7.0, 40) + box(0, -3, 0, 12, 3, 1.6)
    return union([disc, M.cylinder(7.0, 3.25, 2.75, 32).translate([0, 0, 1.6])])


# =====================================================================
# THE CASCADE PAN v3 — sheet 05, PROPOSED. Lies on the floor ties of a bay, under that bay's own tray; catches what
# the tray spills and drops it through a drain at the back into the tray of the bay below. Flat, so it prints flat;
# the ties step down (5, 3, 2) so it falls about 3 to the back.  Axes: the bay it sits in (z from the bay's underside).
# =====================================================================
CAS = dict(x0=-8.0, x1=208.0, y0=2.0, t=1.2, floor=1.2, rim=1.8, drain=8.0, dx=188.0, clr=0.6)
CAS["y1"] = BAY["W"] - CAS["y0"]
CAS["dy"] = BAY["W"] / 2


def catch_pan():
    """built flat (z up from its underside); placed tilted on the ties by the assembly"""
    c, b = CAS, BAY
    t, h = c["t"], c["floor"] + c["rim"]
    out = rrect(c["x0"], c["y0"], c["x1"], c["y1"], 3)
    body = slab(out, 0, h) - slab(rrect(c["x0"] + t, c["y0"] + t, c["x1"] - t, c["y1"] - t, 2), c["floor"], h + 1)
    k = c["clr"]
    seats = []
    for fx in FINX_B:
        for yc in SEAT_YC:
            y0, y1 = (0, yc + b["seatT"] / 2) if yc < b["W"] / 2 else (yc - b["seatT"] / 2, b["W"])
            seats.append((fx - b["seatW"] / 2, max(y0, c["y0"]), fx + b["seatW"] / 2, min(y1, c["y1"])))
    for x0, y0, x1, y1 in seats:   # wall round each fin seat, then clear the seat
        body = body + (box(x0 - k - t, y0 - k - t, 0, x1 + k + t, y1 + k + t, h) ^ slab(out, 0, h))
    body = body - union([box(x0 - k, y0 - k, -1, x1 + k, y1 + k, h + 1) for x0, y0, x1, y1 in seats])
    # drain, with a drip groove round it underneath so water lets go there instead of creeping along the underside
    body = body - M.cylinder(c["floor"] + 2, c["drain"] / 2).translate([c["dx"], c["dy"], -1])
    body = body - (M.cylinder(0.6 + 1, c["drain"] / 2 + 3, c["drain"] / 2 + 3, 40) - M.cylinder(2, c["drain"] / 2 + 2, c["drain"] / 2 + 2, 40)).translate([c["dx"], c["dy"], -1])
    return body


def pan_in_bay(p):
    """lay the flat pan on the ties: tilt it about y so it rests on the front tie (tieF) and the back tie (tieB)"""
    b = BAY
    xf, xb = b["tie"] / 2, b["L"] - b["tie"] / 2
    ang = math.degrees(math.atan2(b["tieF"] - b["tieB"], xb - xf))
    return p.translate([-xf, 0, 0]).rotate([0, ang, 0]).translate([xf, 0, b["tieF"] + .05])


# =====================================================================
# LEVELLING FEET — sheet 05, PROPOSED. An adaptor snaps into the bottom of each peg tube of the bottom bay (like a
# peg's pin) and holds a printed thread; a foot screws into it. A turn moves that corner 3.
# =====================================================================
FOOT = dict(thR=6.0, thE=1.0, thP=3.0, clr=0.35, bodyD=20.0, bodyH=14.0, hole=12.0, padD=26.0, padH=4.0, stem=12.0)


def foot_adaptor():
    """local z up from the adaptor's underside; its top meets the bay's underside at z = bodyH"""
    f, p = FOOT, PEG
    body = M.cylinder(f["bodyH"], f["bodyD"] / 2, f["bodyD"] / 2, 48)
    pin = M.cylinder(p["pinL"] - 1, p["pin"] / 2, p["pin"] / 2, 40).translate([0, 0, f["bodyH"]])
    tip = M.cylinder(1.0, p["pin"] / 2, p["pin"] / 2 - .6, 40).translate([0, 0, f["bodyH"] + p["pinL"] - 1])
    ribs = ring_grooves(p["rib"] / 2, [f["bodyH"] + g + (p["grooveH"] - p["ribH"]) / 2 for g in p["grooves"]], p["ribH"])
    a = union([body, pin, tip, ribs])
    a = a - box(-p["slot"] / 2, -5, f["bodyH"] + p["pinL"] - p["slotL"], p["slot"] / 2, 5, f["bodyH"] + p["pinL"] + 1)
    return a - thread(f["thR"] + f["clr"], f["hole"] + .01, f["thE"], f["thP"], -.01)


def foot():
    f = FOOT
    pad = M.cylinder(f["padH"], f["padD"] / 2, f["padD"] / 2, 48)
    notches = [M.cylinder(f["padH"] + 2, 1.5).translate([f["padD"] / 2 * math.cos(math.radians(i * 30)), f["padD"] / 2 * math.sin(math.radians(i * 30)), -1]) for i in range(12)]
    body = union([pad - union(notches), thread(f["thR"], f["stem"], f["thE"], f["thP"], f["padH"])])
    return body - M.cylinder(f["stem"] + 1, 2.5, 2.5, 24).translate([0, 0, f["padH"] + 1.2])   # hollow stem


# =====================================================================
# build
# =====================================================================
import json
report = {}


def build_all():
    P = {}
    P["plastic_tray"] = plastic_tray()
    P["bay"] = bay()
    P["peg"] = peg()
    P["splitter_trough"] = splitter()
    P["spout"] = spout()
    P["plug"] = plug()
    P["catch_pan"] = catch_pan()
    P["foot_adaptor"] = foot_adaptor()
    P["foot"] = foot()
    return P


P = build_all()
for k, v in P.items():
    note(k, v)
if "--stl" in sys.argv or True:
    for k, v in P.items():
        save(k, v)

N = 4
H = BAY["H"]
tray_in_bay = P["plastic_tray"].translate([TRAY_X0, TRAY_Y0, TRAY_Z0])
pan_b = pan_in_bay(P["catch_pan"])
# checks: nothing may overlap
chk = {
    "tray_vs_bay": P["bay"] ^ tray_in_bay,
    "tray_vs_bay_above": P["bay"].translate([0, 0, H]) ^ tray_in_bay,
    "pan_vs_bay": pan_b ^ P["bay"],
    "pan_vs_tray_above_it": pan_b ^ tray_in_bay,
    "pan_vs_tray_below": pan_b ^ tray_in_bay.translate([0, 0, -H]),
    "pan_vs_bay_below": pan_b ^ P["bay"].translate([0, 0, -H]),
    "trough_vs_top_bay": P["splitter_trough"].translate([0, 0, H + SPL["spigL"]]) ^ P["bay"],
}
pegs_at = [P["peg"].translate([tx, ty, H - PEG["thL"]]) for tx, ty in TUBES]
chk["pegs_vs_bay_below"] = union(pegs_at) ^ P["bay"]
chk["pegs_vs_bay_above"] = union(pegs_at) ^ P["bay"].translate([0, 0, H])
for k, v in chk.items():
    report["clash_" + k] = round(v.volume(), 2)
    if v.volume() > 0.5: report["where_" + k] = [round(q, 1) for q in v.bounding_box()]
# fins on their seats: the fin's lowest edge should sit on the slot floor
report["seat_top"] = SEAT_TOP
report["tray_top_in_bay"] = TRAY_Z0 + PH
report["room_above_tray"] = H - TRAY_Z0 - PH
report["pan_underside_to_tray_below"] = round(pan_b.bounding_box()[2] + H - (TRAY_Z0 + PH), 1)

# feet in place under the bottom bay: adaptor top at the bay's underside; foot screwed in 8 of 12
FEET_Z = FOOT["padH"] + FOOT["stem"] - 8.0             # foot pad bottom at 0, adaptor underside here... (phase-matched below)
FEET_Z = FOOT["padH"] + round((FOOT["stem"] - 8.0) / FOOT["thP"]) * FOOT["thP"]   # whole pitches, so the thread lines up
ZB = FEET_Z + FOOT["bodyH"]                            # underside of the bottom bay
feet_set = []
for tx, ty in TUBES:
    feet_set += [P["foot_adaptor"].translate([tx, ty, FEET_Z]), P["foot"].translate([tx, ty, 0])]
report["clash_feet"] = round((union([P["foot_adaptor"].translate([tx, ty, FEET_Z]) for tx, ty in TUBES]) ^ union([P["foot"].translate([tx, ty, 0]) for tx, ty in TUBES])).volume(), 2)
report["clash_adaptor_vs_bay"] = round((union([P["foot_adaptor"].translate([tx, ty, FEET_Z]) for tx, ty in TUBES]) ^ P["bay"].translate([0, 0, ZB])).volume(), 2)

stack = [P["bay"].translate([0, 0, ZB + k * H]) for k in range(N)]
trays = [tray_in_bay.translate([0, 0, ZB + k * H]) for k in range(N)]
pegs = [P["peg"].translate([tx, ty, ZB + k * H + H - PEG["thL"]]) for k in range(N - 1) for tx, ty in TUBES]
A = union(feet_set + stack + trays + pegs)
top = ZB + (N - 1) * H
sp_on = P["splitter_trough"].translate([0, 0, top + H + SPL["spigL"]])
pegs_top = [P["peg"].translate([tx, ty, top + H - PEG["thL"]]) for tx, ty in TUBES[2:]]
spouts = []
for k in range(N):   # k = 0 bottom bay; the top bay's spout on the left (y = 0), then alternating
    left = (N - 1 - k) % 2 == 0
    sk = P["spout"] if left else P["spout"].rotate([0, 0, 180])
    spouts.append(sk.translate([SPORT["x"], 0 if left else BAY["W"], ZB + k * H + SPORT["z"]]))
B = union(feet_set + stack + trays + pegs + pegs_top + [sp_on] + spouts)
pans = [pan_b.translate([0, 0, ZB + k * H]) for k in range(1, N)]   # under the trays of bays 1 to 3 (counting from the top)
C = union(feet_set + stack + trays + pegs + pans)
report["stack_tap_height"] = round(ZB + N * H, 1)
report["stack_splitter_height"] = round(top + H + SPL["spigL"] + SPL["H"], 1)
report["width_with_tubes"] = round(BAY["W"] - 2 * BAY["tubeY"] + BAY["tubeOD"], 1)
report["spout_z"] = SPORT["z"]

# lighter copies for the page's viewer
COARSE = True
Pv = {k: v for k, v in P.items()}
Pv["peg"], Pv["foot_adaptor"], Pv["foot"] = peg(), foot_adaptor(), foot()
Pv["bay"] = bay()
glb("plastic-tray", [fix(to_trimesh(P["plastic_tray"]))])
glb("bay", [fix(to_trimesh(Pv["bay"])), fix(to_trimesh(tray_in_bay))])
feet_v = []
for tx, ty in TUBES:
    feet_v += [Pv["foot_adaptor"].translate([tx, ty, FEET_Z]), Pv["foot"].translate([tx, ty, 0])]
stack_v = [Pv["bay"].translate([0, 0, ZB + k * H]) for k in range(N)]
pegs_v = [Pv["peg"].translate([tx, ty, ZB + k * H + H - PEG["thL"]]) for k in range(N - 1) for tx, ty in TUBES]
A_v = union(feet_v + stack_v + trays + pegs_v); save("rack_fill_at_tap_4", A_v)   # assemblies: coarse threads, for looking at
glb("rack-tap", [fix(to_trimesh(A_v))])
glb("splitter", [fix(to_trimesh(P["splitter_trough"]))])
pegs_top_v = [Pv["peg"].translate([tx, ty, top + H - PEG["thL"]]) for tx, ty in TUBES[2:]]
B_v = union(feet_v + stack_v + trays + pegs_v + pegs_top_v + [sp_on] + spouts); save("rack_with_splitter_4", B_v)
glb("rack-splitter", [fix(to_trimesh(B_v))])
glb("plug", [fix(to_trimesh(P["plug"]))])
glb("catch-pan", [fix(to_trimesh(P["catch_pan"]))])
C_v = union(feet_v + stack_v + trays + pegs_v + pans); save("rack_cascade_4", C_v)
glb("rack-cascade", [fix(to_trimesh(C_v))])
glb("pegs-feet", [fix(to_trimesh(Pv["peg"].translate([0, 0, 0]))), fix(to_trimesh(Pv["foot_adaptor"].translate([30, 0, 0]))), fix(to_trimesh(Pv["foot"].translate([60, 0, 0])))])
# a plain bay for Fusion's simulation: coarse, threads as plain bores
SIM = True
mf.set_circular_segments(16)
save("bay_for_simulation", bay())
json.dump(report, open(os.path.join(OUT, "report.json"), "w"), indent=1)
print(json.dumps(report, indent=1))
