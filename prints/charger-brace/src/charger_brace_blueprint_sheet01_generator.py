"""
Laptop charger brace - plug and rear-port measurement blueprint, sheet 01.
Styled with the Drafting Table design system (A2 landscape, 594 x 420 mm).
Writes a self-contained HTML sheet; print it from a browser at A2 (or scaled to A3).

REV A: first drawing, from photos. NOTHING HERE IS MEASURED. The numbers below only set
the proportions of the drawing; they are not dimensions and must not be used for CAD.
"""
import math, html, os

# ---------------- drawing proportions only (NOT measurements) ----------------
SL, RS = 12.0, 3.7            # metal sleeve length, radius
BL, RB = 27.0, 5.5            # body length, radius
RL, RR = 3.5, 5.8             # light ring length, radius
GAP = 3.5                     # torn gap
FL, RF1, RF2 = 18.0, 4.4, 3.2 # strain relief length, radii
RC = 2.75                     # cable radius
U_BODY, U_RING, U_GAP, U_REL = SL, SL + BL, SL + BL + RL, SL + BL + RL + GAP
U_RELEND = U_REL + FL
THK = 22.0                    # laptop thickness at the rear
ST1, ST2 = 4.0, 18.0          # rear strip lower / upper line
JX, JY = 68.0, 11.0           # jack centre
VENT1, VENT2 = 9.0, 58.0
SCREW_X, HD1, HD2, HD_OUT = 80.0, 92.0, 110.0, 22.0
RIDGE, RIB1, RIB2 = 14.0, 17.0, 24.0
OUT = BL + RL                 # rear face to ring end, plug home (sleeve fully in)
WALL = 42.0

INK, INK2, PAPER, ALERT = "#1C1C1A", "#6B6862", "#F7F5F0", "#B0453A"
FILL_STRUCT, STRUCT_TINT, SHADE = "#D9D4C9", "#E9E6DE", "#ECEAE5"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"
SANS = "Archivo,'Helvetica Neue',Helvetica,Arial,sans-serif"
HID = "2.4 1.8"; CENTRE = "9 2.4 2.4 2.4"; PROV = "6 2.4 1.4 2.4"

# view transforms: local (a, b) in mm -> sheet mm
VIEWS = {
    "plug": lambda u, v: (40 + u * 3.4, 106 + v * 3.4),        # u from the tip, v from the axis (down +)
    "top":  lambda x, z: (36 + x * 1.0, 224 - z * 1.0),        # x from the vent-end corner, z out of the rear face (up)
    "rear": lambda x, y: (376 - x * 1.5, 221 - y * 1.5),       # mirrored: corner on the right, y up from the underside
    "sect": lambda z, y: (284 + z * 1.7, 346 - y * 1.7),       # z out of the rear face (right), y up from the underside
}
def P(v, a, b): return VIEWS[v](a, b)

out = []
add = out.append
def path(v, pts, fill="none", stroke=INK, w=0.5, close=True, dash=None):
    d = "M" + " L".join("%.2f,%.2f" % P(v, a, b) for a, b in pts) + (" Z" if close else "")
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
def line(x1, y1, x2, y2, stroke=INK, w=0.22, dash=None):
    add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
def circle(v, a, b, r, fill="none", stroke=INK, w=0.5, dash=None):
    cx, cy = P(v, a, b)
    add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
def text(x, y, s, size=3.6, anchor="start", weight=400, fill=INK, font=SANS, ls=0, halo=False, extra=""):
    h = f' stroke="{PAPER}" stroke-width="1.1" paint-order="stroke" stroke-linejoin="round"' if halo else ""
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" letter-spacing="{ls}"{h} {extra}>{html.escape(s)}</text>')
def cap(v, a, b, s, dx=0, dy=0, anchor="middle", fill=INK2):
    px, py = P(v, a, b); text(px + dx, py + dy, s, 3.6, anchor, 500, fill, ls=0.5, halo=True)

# ---------------- view titles ----------------
TITLES = [
    ("1  PLUG, SIDE ON", ["PLUG LYING ON THE DESK · METAL TIP ON THE LEFT · CABLE TO THE RIGHT"], 22, 54),
    ("2  LAPTOP FROM ABOVE", ["KEYBOARD TOWARDS YOU · REAR EDGE AT THE TOP", "VENT CORNER ON THE LEFT · PLUG IN"], 22, 160),
    ("3  LAPTOP REAR FACE", ["REAR FACE TOWARDS YOU · KEYBOARD SIDE UP", "MIRRORED FROM VIEW 2: VENT CORNER ON THE RIGHT"], 204, 160),
    ("4  SECTION THROUGH THE JACK", ["LOOKING FROM THE VENT CORNER · KEYBOARD LEFT · REAR FACE RIGHT · PLUG IN"], 198, 262),
]
for t, subs, x, y in TITLES:
    text(x, y, t, 4.6, weight=700, ls=0.6)
    for i, s in enumerate(subs):
        text(x, y + 5 + i * 4.4, s, 3.6, fill=INK2, ls=0.3)
    text(x, y + 5 + len(subs) * 4.4, "NOT TO SCALE (IND.) · PROPORTIONS FROM PHOTOS", 3.6, weight=600, fill=ALERT, font=MONO)

# ================= VIEW 1: PLUG, SIDE ON =================
def plug_shapes(v, T, tip_hidden=False):
    """T maps (u, r) -> local coords of view v. Draws sleeve, body, ring, torn gap, strain relief."""
    def pp(pts, **kw): path(v, [T(u, r) for u, r in pts], **kw)
    if not tip_hidden:
        pp([(0.6, -RS), (SL, -RS), (SL, RS), (0.6, RS), (0, RS - 0.6), (0, -RS + 0.6)], fill=SHADE, w=0.7)
    pp([(SL, -RB + 1.0), (SL + 1.3, -RB), (U_RING, -RB), (U_RING, RB), (SL + 1.3, RB), (SL, RB - 1.0)], fill=FILL_STRUCT, w=0.9)
    pp([(U_RING, -RR), (U_GAP - 0.8, -RR), (U_GAP, -RR + 0.9), (U_GAP, RR - 0.9), (U_GAP - 0.8, RR), (U_RING, RR)], fill=PAPER, w=0.7)
    # torn gap: bare inner cores, drawn provisional
    pp([(U_GAP, -1.9), (U_GAP + 1.2, -2.4), (U_GAP + 2.2, -1.6), (U_REL, -2.0), (U_REL, 2.0), (U_GAP + 2.4, 2.4), (U_GAP + 1.0, 1.7), (U_GAP, 2.1)],
       fill="rgba(176,69,58,0.07)", stroke=ALERT, w=0.35, dash=PROV)
    pp([(U_REL, -RF1), (U_RELEND, -RF2), (U_RELEND, RF2), (U_REL, RF1)], fill=STRUCT_TINT, w=0.7)
    for i in range(1, 5):
        u = U_REL + i * 2.6; r = RF1 - (RF1 - RF2) * (u - U_REL) / FL
        pp([(u, -r), (u, r)], w=0.35, close=False)

T1 = lambda u, r: (u, r)
plug_shapes("plug", T1)
CAB_END = U_RELEND + 16
path("plug", [(U_RELEND, -RC), (CAB_END, -RC)], w=0.7, close=False)
path("plug", [(U_RELEND, RC), (CAB_END, RC)], w=0.7, close=False)
path("plug", [(CAB_END, -RC - 1.2), (CAB_END - 0.8, -1), (CAB_END + 0.8, 1), (CAB_END, RC + 1.2)], stroke=INK2, w=0.35, close=False)
x1, y1 = P("plug", -4, 0); x2, y2 = P("plug", CAB_END + 3, 0)
line(x1, y1, x2, y2, INK2, 0.25, CENTRE)
yrow = 34
cap("plug", SL / 2 - 1, 0, "METAL SLEEVE", dy=yrow)
cap("plug", SL + BL / 2 + 2, 0, "BLACK BODY", dy=yrow)
cap("plug", U_REL + FL / 2 + 1, 0, "STRAIN RELIEF", dy=yrow)
cap("plug", U_RELEND + 9, 0, "CABLE", dy=yrow)
cap("plug", U_RING, 0, "LIGHT RING", dx=-6, dy=yrow + 8, anchor="end")
cap("plug", U_REL, 0, "TORN (IND.)", dx=6, dy=yrow + 8, anchor="start", fill=ALERT)
lx_, ly_ = P("plug", U_RING + RL / 2, RR); line(lx_, ly_ + 0.8, lx_ - 7.2, P("plug", 0, 0)[1] + yrow + 6.6, INK2, 0.15)
lx_, ly_ = P("plug", U_GAP + GAP / 2, 2.3); line(lx_, ly_ + 0.8, lx_ + 7.2, P("plug", 0, 0)[1] + yrow + 6.6, ALERT, 0.15)

# ================= VIEW 2: LAPTOP FROM ABOVE =================
XR, DECK = 130.0, 18.0
# deck (keyboard side), rear edge along z = 0
path("top", [(4, 0), (XR, 0), (XR, -DECK), (0, -DECK), (0, -4), (1.2, -1.2)], fill=PAPER, w=0.9)
# break lines
path("top", [(XR, 2), (XR - 1, -6), (XR + 1, -13), (XR, -DECK - 2)], stroke=INK2, w=0.35, close=False)
path("top", [(-2, -DECK), (40, -DECK - 0.8), (80, -DECK + 0.8), (XR + 2, -DECK)], stroke=INK2, w=0.35, close=False)
# vent, shown as a hatched band just inside the rear edge
path("top", [(VENT1, 0), (VENT2, 0), (VENT2, -2.2), (VENT1, -2.2)], fill=FILL_STRUCT, w=0.35)
for i in range(int((VENT2 - VENT1) / 2.4)):
    a = VENT1 + 1.2 + i * 2.4
    path("top", [(a, -2.2), (a + 1.2, 0)], w=0.25, close=False)
# ridge and slot row on the deck (position not known)
path("top", [(0, -RIDGE), (XR - 0.5, -RIDGE)], stroke=ALERT, w=0.35, close=False, dash=PROV)
for i in range(49):
    a = 6 + i * 2.5
    path("top", [(a, -RIDGE - 2.2), (a, -RIDGE - 4.6)], stroke=INK2, w=0.3, close=False)
# hinge pocket near the corner (lid removed)
path("top", [(4, -5), (13, -5), (13, -11), (8, -11)], fill=SHADE, stroke=ALERT, w=0.35, dash=PROV)
# cable: forced over at the tear, then along the wall
def cable_top(w, col):
    a_ = P("top", JX, OUT); b_ = P("top", JX, OUT + 8.5); c_ = P("top", JX + 2, WALL - 4); d_ = P("top", JX + 14, WALL - 4); e_ = P("top", XR - 6, WALL - 4)
    add(f'<path d="M{a_[0]:.2f},{a_[1]:.2f} C{b_[0]:.2f},{b_[1]:.2f} {c_[0]:.2f},{c_[1]:.2f} {d_[0]:.2f},{d_[1]:.2f} L{e_[0]:.2f},{e_[1]:.2f}" fill="none" stroke="{col}" stroke-width="{w}"/>')
cable_top(2 * RC, INK); cable_top(2 * RC - 1.2, PAPER)
ex, ey = P("top", XR - 6, WALL - 4)
add(f'<path d="M{ex:.2f},{ey - 4.2:.2f} L{ex - 0.8:.2f},{ey - 1:.2f} L{ex + 0.8:.2f},{ey + 1:.2f} L{ex:.2f},{ey + 4.2:.2f}" fill="none" stroke="{INK2}" stroke-width="0.35"/>')
# plug standing out of the rear face (sleeve inside the laptop)
T2 = lambda u, r: (JX + r, u - SL)
path("top", [T2(u, r) for u, r in [(SL, -RB), (U_RING, -RB), (U_RING, RB), (SL, RB)]], fill=FILL_STRUCT, w=0.9)
path("top", [T2(u, r) for u, r in [(U_RING, -RR), (U_GAP - 0.8, -RR), (U_GAP, -RR + 0.9), (U_GAP, RR - 0.9), (U_GAP - 0.8, RR), (U_RING, RR)]], fill=PAPER, w=0.7)
# HDMI plug
path("top", [(HD1, 0), (HD1, HD_OUT), (HD2, HD_OUT), (HD2, 0)], fill=STRUCT_TINT, w=0.6, close=False)
path("top", [(HD1 + 5, HD_OUT), (HD1 + 6, HD_OUT + 7), (HD2 - 6, HD_OUT + 7), (HD2 - 5, HD_OUT)], fill=STRUCT_TINT, w=0.5, close=False)
# screw position on the rear face
sx, sy = P("top", SCREW_X, 0); line(sx, sy - 1.6, sx, sy + 1.6, INK, 0.5)
# wall
wx1, wy = P("top", -4, WALL); wx2, _ = P("top", XR + 2, WALL)
line(wx1, wy, wx2, wy, ALERT, 0.45, PROV)
for i in range(34):
    hx = wx1 + 2 + i * 4.1
    line(hx, wy, hx + 2.2, wy - 2.2, ALERT, 0.2)
text(wx2, wy - 3.2, "WALL (IND.)", 3.6, "end", 600, ALERT, MONO)
cap("top", 31, -9, "TOP DECK", dy=1.2)
cap("top", HD1 + 9, HD_OUT / 2, "HDMI", dy=1.2)
cap("top", 8, 13, "VENT ON REAR FACE", dy=1.2, anchor="start")
vx_, vy_ = P("top", 24, 0); line(vx_, vy_ - 1, vx_, vy_ - 10.5, INK2, 0.15)

# ================= VIEW 3: LAPTOP REAR FACE =================
XB = 108.0
path("rear", [(3, 0), (XB, 0), (XB, THK), (3, THK), (0, THK - 3), (0, 3)], fill=PAPER, w=0.9)
path("rear", [(XB, -1.5), (XB - 0.8, 7), (XB + 0.8, 14), (XB, THK + 1.5)], stroke=INK2, w=0.35, close=False)
# strip loop (stadium end near the corner), outer and inner line
def loop(inset, w, stroke=INK):
    r = (ST2 - ST1) / 2 - inset; cyl = (ST1 + ST2) / 2; xe = 4.5 + inset + r
    pts = [(XB - 0.6, ST2 - inset)] + [(xe - r * math.sin(math.pi * i / 12), cyl + r * math.cos(math.pi * i / 12)) for i in range(13)] + [(XB - 0.6, ST1 + inset)]
    path("rear", pts, stroke=stroke, w=w, close=False)
loop(0, 0.6); loop(1.0, 0.3, INK2)
# honeycomb vent
hx_r = 1.9
row = 0; yy = ST1 + 2.6
while yy < ST2 - 1.5:
    xx = VENT1 + 2 + (hx_r * 0.87 if row % 2 else 0)
    while xx < VENT2 - 1:
        pts = [(xx + hx_r * 0.86 * math.cos(math.pi / 6 + i * math.pi / 3), yy + hx_r * 0.86 * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
        path("rear", pts, fill=SHADE, stroke=INK2, w=0.25)
        xx += hx_r * 1.74
    yy += hx_r * 1.5; row += 1
# jack: collar, hole, pin
circle("rear", JX, JY, 5.5 * 1.5, fill=STRUCT_TINT, w=0.7)
circle("rear", JX, JY, 3.8 * 1.5, fill=SHADE, w=0.5)
circle("rear", JX, JY, 0.8 * 1.5, fill=INK, w=0.2)
# screw
circle("rear", SCREW_X, JY, 1.6 * 1.5, fill=PAPER, w=0.5)
sx, sy = P("rear", SCREW_X, JY); line(sx - 1.5, sy, sx + 1.5, sy, INK, 0.3); line(sx, sy - 1.5, sx, sy + 1.5, INK, 0.3)
# HDMI plug body
path("rear", [(HD1, ST1 + 0.5), (XB - 0.6, ST1 + 0.5)], w=0.6, close=False)
path("rear", [(HD1, ST1 + 0.5), (HD1, ST2 - 0.5), (XB - 0.6, ST2 - 0.5)], fill="none", w=0.6, close=False)
cap("rear", 100.5, JY, "HDMI", dy=1.2)
cap("rear", 22, THK, "KEYBOARD SIDE", dy=-2.2)
cap("rear", 22, 0, "UNDERSIDE", dy=5)

# ================= VIEW 4: SECTION THROUGH THE JACK =================
ZL = -40.0
# laptop body
body = [(ZL, 0), (-RIB2, 0), (-RIB2 + 0.8, -1.5), (-RIB1 - 0.8, -1.5), (-RIB1, 0), (-2, 0), (0, 2), (0, THK - 2), (-2, THK), (-RIDGE, THK), (-RIDGE - 1, THK - 1.3), (ZL, THK - 1.3)]
path("sect", body, fill=STRUCT_TINT, stroke="none", w=0)
path("sect", [(-RIB1, 0), (-2, 0), (0, 2), (0, THK - 2), (-2, THK), (-RIDGE, THK)], w=0.9, close=False)
path("sect", [(-RIDGE, THK), (-RIDGE - 1, THK - 1.3), (ZL, THK - 1.3)], stroke=ALERT, w=0.45, close=False, dash=PROV)
path("sect", [(ZL, 0), (-RIB2, 0), (-RIB2 + 0.8, -1.5), (-RIB1 - 0.8, -1.5), (-RIB1, 0)], stroke=ALERT, w=0.45, close=False, dash=PROV)
path("sect", [(ZL, -2.5), (ZL - 0.8, 6), (ZL + 0.8, 14), (ZL, THK + 1)], stroke=INK2, w=0.35, close=False)
# socket (hidden) and collar
path("sect", [(0, JY - RS - 0.4), (-13, JY - RS - 0.4), (-13, JY + RS + 0.4), (0, JY + RS + 0.4)], fill=PAPER, stroke=INK2, w=0.35, close=False, dash=HID)
path("sect", [(0, JY - 5.5), (0.9, JY - 5.5), (0.9, JY + 5.5), (0, JY + 5.5)], fill=STRUCT_TINT, w=0.5, close=False)
# plug, sleeve inside the socket
T4 = lambda u, r: (u - SL, JY - r)
path("sect", [T4(0.6, -RS), T4(SL, -RS), T4(SL, RS), T4(0.6, RS)], fill=SHADE, stroke=INK2, w=0.35, close=False, dash=HID)
plug_shapes("sect", T4, tip_hidden=True)
ZC = U_RELEND - SL
path("sect", [(ZC, JY - RC), (ZC + 6, JY - RC)], w=0.7, close=False)
path("sect", [(ZC, JY + RC), (ZC + 6, JY + RC)], w=0.7, close=False)
path("sect", [(ZC + 6, JY - RC - 1.2), (ZC + 5.4, JY - 1), (ZC + 6.6, JY + 1), (ZC + 6, JY + RC + 1.2)], stroke=INK2, w=0.35, close=False)
x1, y1 = P("sect", ZL - 9.5, JY); x2, y2 = P("sect", ZC + 8, JY)
line(x1, y1, x2, y2, INK2, 0.25, CENTRE)
cap("sect", -27, THK / 2 + 4.5, "LAPTOP", dy=1.2)

# ---------------- dimension lines: each carries its schedule letter; red because unmeasured ----------------
def tick(x, y): line(x - 1.4, y + 1.4, x + 1.4, y - 1.4, ALERT, 0.35)
def dim_h(x1, x2, y, label, w1=None, w2=None, lab_dx=0, lab_dy=-1.6, anchor="middle"):
    for x, wf in ((x1, w1), (x2, w2)):
        if wf is not None: line(x, wf, x, y + (-1.6 if y < wf else 1.6), INK2, 0.15)
        tick(x, y)
    line(x1, x2 and y and x1, y, x2, y, ALERT, 0.22) if False else line(x1, y, x2, y, ALERT, 0.22)
    text((x1 + x2) / 2 + lab_dx, y + lab_dy, label, 3.8, anchor, 700, ALERT, MONO, halo=True)
def dim_v(y1, y2, x, label, w1=None, w2=None, lab_dx=-1.8, lab_dy=1.3, anchor="end"):
    for y, wf in ((y1, w1), (y2, w2)):
        if wf is not None: line(wf, y, x + (-1.6 if x < wf else 1.6), y, INK2, 0.15)
        tick(x, y)
    line(x, y1, x, y2, ALERT, 0.22)
    text(x + lab_dx, (y1 + y2) / 2 + lab_dy, label, 3.8, anchor, 700, ALERT, MONO, halo=True)
def dia(v, a, r, label, side=1, lab=None):
    """diameter drawn across the part at local station a"""
    x, ya = P(v, a, -r); _, yb = P(v, a, r)
    dim_v(ya, yb, x, label, lab_dx=2.0 * side, anchor="start" if side > 0 else "end")

# view 1 — lengths chained above, diameters across the part
yc = P("plug", 0, 0)[1] - 30
top_of = {0: -RS, U_BODY: -RB, U_RING: -RR, U_GAP: -RR, U_REL: -RF1, U_RELEND: -RF2}
def px(u): return P("plug", u, 0)[0]
def pt(u): return P("plug", u, top_of[u])[1] - 1.2
dim_h(px(0), px(U_BODY), yc, "B", pt(0), pt(U_BODY))
dim_h(px(U_BODY), px(U_RING), yc, "E", None, pt(U_RING))
dim_h(px(U_RING), px(U_GAP), yc, "G", None, pt(U_GAP))
dim_h(px(U_GAP), px(U_REL), yc, "H", None, pt(U_REL))
dim_h(px(U_REL), px(U_RELEND), yc, "J", None, pt(U_RELEND))
dia("plug", 5.5, RS, "A")
dia("plug", SL + 4.5, RB, "C")
dia("plug", U_RING - 3.5, RB, "D", side=-1)
dia("plug", U_RELEND + 7, RC, "K")
# F and I: short stations, labelled below with the dimension outside
xa, ya = P("plug", U_RING, RR); xb, yb = P("plug", U_RING, -RR)
dim_v(P("plug", 0, -RR)[1], P("plug", 0, RR)[1], px(U_RING) + RL * 3.4 / 2, "F", lab_dx=-2.2)
dim_v(P("plug", 0, -RF1)[1], P("plug", 0, RF1)[1], px(U_REL) + 3.2, "I", lab_dx=2.0, anchor="start")

# view 2
rf = P("top", 0, 0)[1]
jx_ = P("top", JX, 0)[0]
dim_h(P("top", VENT2, 0)[0], P("top", JX - 5.5, 0)[0], rf - 7, "V", rf - 0.8, None, lab_dx=-5.5, lab_dy=1.3)
yb1 = P("top", 0, -DECK)[1] + 6
dim_h(jx_, P("top", SCREW_X, 0)[0], yb1, "W", rf + 0.8, rf + 2.4)
dim_h(jx_, P("top", HD1, 0)[0], yb1 + 6.5, "X", None, rf + 0.8)
dim_h(P("top", 0, 0)[0], jx_, yb1 + 13, "U", P("top", 0, -DECK)[1] + 1, None)
line(jx_, yb1, jx_, yb1 + 14.6, INK2, 0.15)
xm = P("top", JX + 9.5, 0)[0]
dim_v(rf, P("top", 0, OUT)[1], xm, "M", None, P("top", JX + RR, 0)[0] + 0.6, lab_dx=2.0, anchor="start")
xy = P("top", HD2 + 7, 0)[0]
dim_v(rf, P("top", 0, HD_OUT)[1], xy, "Y", None, P("top", HD2, 0)[0] + 0.6, lab_dx=2.0, anchor="start")
xw = P("top", -7, 0)[0]
dim_v(rf, wy, xw, "AD", P("top", 0.6, 0)[0], None, lab_dx=-1.8)
# O: side-to-side play at the ring end
ox1, oy1 = P("top", JX - 16, OUT - 2.2); ox2, _ = P("top", JX - RR - 0.8, OUT - 2.2)
line(ox1, oy1, ox2, oy1, ALERT, 0.3)
add(f'<path d="M{ox1 + 2:.2f},{oy1 - 1.2:.2f} L{ox1:.2f},{oy1:.2f} L{ox1 + 2:.2f},{oy1 + 1.2:.2f} M{ox2 - 2:.2f},{oy1 - 1.2:.2f} L{ox2:.2f},{oy1:.2f} L{ox2 - 2:.2f},{oy1 + 1.2:.2f}" fill="none" stroke="{ALERT}" stroke-width="0.3"/>')
text(ox1 - 1.5, oy1 + 1.3, "O", 3.8, "end", 700, ALERT, MONO, halo=True)

# view 3
rt = P("rear", 0, THK)[1]; rb_ = P("rear", 0, 0)[1]
dim_v(rt, rb_, 386.5, "P", P("rear", 0, 0)[0] + 0.8, P("rear", 0, 0)[0] + 0.8, lab_dx=2.0, anchor="start")
xq = P("rear", XB, 0)[0] - 7
dim_v(P("rear", 0, ST2)[1], P("rear", 0, ST1)[1], xq, "Q", P("rear", XB, 0)[0] - 1.2, P("rear", XB, 0)[0] - 1.2)
dim_h(P("rear", JX + 5.5, 0)[0], P("rear", JX - 5.5, 0)[0], rb_ + 9, "S", P("rear", 0, JY)[1] + 9, P("rear", 0, JY)[1] + 9, lab_dy=5.0)

# view 4
s0 = P("sect", 0, 0)[0]; st = P("sect", 0, THK)[1]; sb = P("sect", 0, 0)[1]; sj = P("sect", 0, JY)[1]
dim_h(s0, P("sect", OUT, 0)[0], st - 12, "M", st - 0.5, P("sect", 0, JY + RR)[1] - 1)
dim_h(P("sect", -RIDGE, 0)[0], s0, st - 6, "Z", st - 1, None)
xaa = P("sect", -RIDGE - 4, 0)[0]
dim_v(st, P("sect", 0, THK - 1.3)[1], xaa, "AA", None, None, lab_dx=-2.0, lab_dy=-2.6)
xp = P("sect", ZL, 0)[0] - 6
dim_v(st, sb, xp, "P", xp + 4.5, xp + 4.5, lab_dy=-6)
xr = xp - 7.5
dim_v(sj, sb, xr, "R", None, xp + 4.5)
dim_h(P("sect", -RIB1, 0)[0], s0, sb + 11, "AB", sb + 3.4, sb + 0.8)
xac = P("sect", -RIB2 - 4, 0)[0]
dim_v(sb, P("sect", 0, -1.5)[1], xac, "AC", None, None, lab_dx=-2.0, lab_dy=4.2)
line(xac, P("sect", 0, -1.5)[1], P("sect", -RIB2 + 0.8, 0)[0], P("sect", 0, -1.5)[1], INK2, 0.15)
# N and T: leaders at the collar, below the plug
nx, ny = P("sect", 0.3, JY - RB)
line(nx + 0.4, ny + 0.6, nx + 12, ny + 8, ALERT, 0.2); text(nx + 12.6, ny + 9.6, "N", 3.8, "start", 700, ALERT, MONO, halo=True)
tx_, ty_ = P("sect", 0.9, JY - 5.5)
line(tx_, ty_ + 0.4, tx_ + 4.5, ty_ + 13, ALERT, 0.2); text(tx_ + 5, ty_ + 15.6, "T", 3.8, "start", 700, ALERT, MONO, halo=True)

# ---------------- points and edges (sheet-mm label offsets) ----------------
POINTS = [  # id, view, a, b, dx, dy
  ("P1","plug",0,-RS,-3,-2.5),("P2","plug",0,RS,-3,5),("P3","plug",SL,-RS,-2.5,-2.5),("P4","plug",SL+1.3,-RB,2.5,-2.5),("P5","plug",SL+1.3,RB,2.2,5.6),
  ("P6","plug",U_RING,-RB,-3,-2.5),("P7","plug",U_GAP,-RR+0.9,2.2,-4.5),("P8","plug",U_GAP,RR-0.9,2.5,5.2),("P9","plug",U_REL,-RF1,2.5,-2.5),
  ("P10","plug",U_RELEND,-RF2,-1,-3),("P11","plug",U_RELEND+12,-RC,0,-3),("P12","plug",U_RELEND+12,RC,0,5.5),
  ("T1","top",0,0,-2.5,5),("T2","top",VENT2,0,-2.5,-2.2),("T3","top",JX,0,-9.5,5.2),("T4","top",JX,OUT,-7.5,-3),("T5","top",SCREW_X,0,-2.5,5.4),
  ("T6","top",HD1,0,1.8,5.4),("T7","top",HD2,HD_OUT,2.2,-1.5),("T8","top",XR-14,-RIDGE,1.5,-2.2),
  ("R1","rear",0,THK,-1,-2.5),("R2","rear",0,0,-1,5.5),("R3","rear",JX,JY,2.5,-12.2),("R4","rear",SCREW_X,JY,-1.5,-4.6),("R5","rear",VENT2,JY,2.5,14.6),
  ("R6","rear",HD1,JY,2,9),
  ("S1","sect",0,THK-2,2.6,0.2),("S2","sect",0,2,-3,7.2),("S3","sect",-RIDGE,THK,1.6,5.4),("S4","sect",-RIB1,0,1.6,-2.4),("S5","sect",OUT,JY+RR-0.9,2.4,-3),
  ("S6","sect",0.9,JY-5.5,-3.2,5.2),
]
EDGES = [  # id, view, a, b, dx, dy
  ("p1","plug",0,0,-7,0),("p2","plug",4.5,RS,0,7),("p3","plug",SL,RB-1,-7,10),("p4","plug",SL+15,RB,0,7),("p5","plug",U_RING+RL/2,RR,-10,8),
  ("p6","plug",U_GAP+GAP/2,2.3,11,13),("p7","plug",U_REL+11,RF1-1.5,0,9),("p8","plug",U_RELEND+7,RC,-6,9),
  ("t1","top",XR-6,0,0,0),("t2","top",22,WALL,0,-4.5),("t3","top",47,-RIDGE,0,0),("t4","top",JX-RB,21,-6.5,0),
  ("r1","rear",48,THK,0,0),("r2","rear",48,0,0,0),("r3","rear",30,ST2,0,0),("r4","rear",30,ST1,0,0),("r5","rear",JX+3,JY-4.6,-12,14.6),("r6","rear",0,JY,0,0),
  ("s1","sect",0,THK-6,-6,0),("s2","sect",-5,THK,0,0),("s3","sect",-8,0,0,0),("s4","sect",-27,THK-1.3,0,0),("s5","sect",12,JY+RB,0,-5.5),
]
for pid, v, a, b, dx, dy in POINTS:
    px_, py_ = P(v, a, b)
    if abs(dx) > 6.4 or abs(dy) > 7.4:
        line(px_, py_, px_ + dx * 0.8, py_ + dy * 0.8, INK2, 0.15)
for eid, v, a, b, dx, dy in EDGES:
    px_, py_ = P(v, a, b); tx, ty = px_ + dx, py_ + dy
    if abs(dx) > 7 or abs(dy) > 9: line(px_, py_, tx, ty, INK2, 0.15)
    w = 2.4 + 2.16 * len(eid)
    add(f'<rect x="{tx - w / 2:.2f}" y="{ty - 2.5:.2f}" width="{w:.2f}" height="5" fill="{PAPER}" stroke="{INK2}" stroke-width="0.25"/>')
    text(tx, ty + 1.3, eid, 3.6, "middle", 500, INK2, MONO)
for pid, v, a, b, dx, dy in POINTS:
    px_, py_ = P(v, a, b)
    add(f'<circle cx="{px_:.2f}" cy="{py_:.2f}" r="0.9" fill="{INK}"/>')
    text(px_ + dx, py_ + dy, pid, 3.6, "start" if dx >= 0 else "end", 600, INK, MONO, halo=True)

SVG = "\n".join(out)

# ---------------- schedule, notes, open items ----------------
SCHEDULE = [
    ("PLUG · VIEW 1", [
        ("A", "P1–P2", "Metal sleeve outside diameter", "7.4", "(IND.)"),
        ("B", "P1→P3", "Sleeve length, tip to the body", "TBD", "x"),
        ("C", "P4–P5", "Body diameter at the sleeve end", "TBD", "x"),
        ("D", "p4 at P6", "Body diameter at the ring end", "TBD", "x"),
        ("E", "P3→P6", "Body length, sleeve to light ring", "TBD", "x"),
        ("F", "p5", "Light ring diameter", "TBD", "x"),
        ("G", "P6→P7", "Light ring length", "TBD", "x"),
        ("H", "P7→P9", "Torn gap, cable pulled straight", "TBD", "x"),
        ("I", "at P9", "Strain relief diameter, thick end", "TBD", "x"),
        ("J", "P9→P10", "Strain relief length", "TBD", "x"),
        ("K", "P11–P12", "Cable diameter", "TBD", "x"),
    ]),
    ("PLUG IN THE LAPTOP · VIEWS 2, 4", [
        ("M", "t1→T4", "Rear face to the ring end, plug pushed home", "TBD", "x"),
        ("N", "s1→p3", "Sleeve left showing, plug pushed home", "TBD", "x"),
        ("O", "at T4", "Side-to-side play of the ring end", "TBD", "x"),
    ]),
    ("REAR FACE · VIEWS 2, 3", [
        ("P", "R1–R2", "Laptop thickness at the rear", "TBD", "x"),
        ("Q", "r3–r4", "Height of the recessed strip", "TBD", "x"),
        ("S", "r5", "Jack collar outside diameter", "TBD", "x"),
        ("T", "S6→s1", "Collar proud of (+) or sunk in (−) the strip", "TBD", "x"),
        ("U", "T1→T3", "Vent corner to jack centre", "TBD", "x"),
        ("V", "T2→r5", "Vent end to the jack collar", "TBD", "x"),
        ("W", "T3→T5", "Jack centre to screw centre", "TBD", "x"),
        ("X", "T3→T6", "Jack centre to the HDMI plug", "TBD", "x"),
        ("Y", "T6→T7", "HDMI plug sticks out of the rear face", "TBD", "x"),
    ]),
    ("REAR PROFILE · VIEW 4", [
        ("R", "s3→axis", "Underside to the centre of the jack", "TBD", "x"),
        ("Z", "s1→S3", "Rear face to the ridge on the top deck", "TBD", "x"),
        ("AA", "s2→s4", "Step height at the ridge", "TBD", "x"),
        ("AB", "s1→S4", "Rear face to the foot rib underneath", "TBD", "x"),
        ("AC", "at S4", "Foot rib height", "TBD", "x"),
    ]),
    ("ROOM BEHIND THE LAPTOP", [
        ("AD", "t1→t2", "Rear face to the wall, laptop on the desk", "TBD", "x"),
        ("AE", "—", "Rear face to nearest obstruction, under the desk", "TBD", "x"),
    ]),
]
rows = []
for group, items in SCHEDULE:
    rows.append(f'<div class="grp">{group}</div>')
    for k, refs, desc, val, flag in items:
        cls = ' class="row unk"' if flag else ' class="row"'
        fl = "" if flag == "x" else " " + flag
        rows.append(f'<div{cls}><span class="k">{k}</span><span class="r">{html.escape(refs)}</span><span class="d">{html.escape(desc)}</span>'
                    f'<span class="v">{val}{fl}</span></div>')
NOTES = [
    ("1", "THE CABLE HAS ALREADY TORN AT THE LIGHT RING.", "The strain relief has pulled out of the head and the cores are bare. The brace has to carry the cable past the tear, not only hold the head."),
    ("2", "THE VENT STARTS RIGHT BESIDE THE JACK.", "Nothing may cover it. Any grip on the laptop goes above, below or towards the screw."),
    ("3", "THE PLUG LEAVES STRAIGHT OUT OF THE REAR.", "Against the wall the cable is forced over at the head. The brace should turn it through a set radius instead."),
    ("4", "THE LAPTOP HAS NO LID.", "The hinge pockets are open. A printed head is a later print on this same rear edge; the brace stays clear of it."),
]
notes = "".join(f'<div class="note"><span class="n">{n}</span><span><b>{a}</b> <i>{b}</i></span></div>' for n, a, b in NOTES)
KEY = [
    ("P1", "POINT. The capital letter is the view: P plug, T top, R rear, S section."),
    ("p1", "EDGE or surface. Lower-case, in a box. Same view letters."),
    ("A", "MEASUREMENT. Red on the drawing until it is measured."),
    ("- - -", "HIDDEN behind another part. A red broken line is drawn from a guess."),
    ("x y z", "x along the rear from the vent corner · y up from the underside · z out of the rear face."),
]
key = "".join(f'<div class="sr"><span class="tag">{t}</span><span>{html.escape(d)}</span></div>' for t, d in KEY)
OPEN = [
    ("ALL", "Nothing is measured. Check the drawing first, then measure A to AE by caliper. Scale bars follow."),
    ("A", "7.4 is the nominal size of this type of barrel plug, not a reading. Confirm."),
    ("V4", "Ridge, deck step, foot rib and hinge pocket are drawn from angled photos. Correct before measuring."),
    ("GRIP", "How the brace holds the laptop is not decided: clip over the rear edge, the screw at T5, or adhesive."),
    ("TEAR", "Bare cores at the tear. Insulate or replace the lead before it is braced: TBD."),
    ("AE", "Where the laptop sits under the desk, and what is behind the plug there: TBD."),
]
open_items = "".join(f'<div class="oi"><span class="ref">{r}</span><span>{html.escape(t)}</span></div>' for r, t in OPEN)

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>01 Charger plug and rear port blueprint</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --paper:#F7F5F0; --ink-primary:#1C1C1A; --ink-secondary:#6B6862; --rule:#C9C4B8; --fill-structure:#D9D4C9;
  --alert:#B0453A; --alert-fill:rgba(176,69,58,0.045);
  --font-display:{SANS}; --font-mono:{MONO};
}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; background:#4A4844; }}
.desk {{ padding:12mm; }}
.sheet {{ position:relative; width:594mm; height:420mm; background:var(--paper); color:var(--ink-primary);
  font-family:var(--font-display); overflow:hidden; transform-origin:top left; -webkit-font-smoothing:antialiased; }}
.border {{ position:absolute; inset:8mm; border:0.25mm solid var(--ink-secondary); pointer-events:none; }}
.num {{ position:absolute; left:15mm; top:11mm; font-family:var(--font-mono); font-size:54pt; font-weight:600; line-height:.86; letter-spacing:-.02em; }}
.title {{ position:absolute; left:62mm; top:16mm; font-size:22pt; font-weight:700; letter-spacing:.2em; line-height:1; white-space:nowrap; }}
.sub {{ position:absolute; left:63mm; top:29mm; font-size:11pt; letter-spacing:.2em; color:var(--ink-secondary); white-space:nowrap; }}
.label {{ position:absolute; right:15mm; top:16mm; font-size:13pt; font-weight:600; letter-spacing:.3em; white-space:nowrap; }}
.meta {{ position:absolute; right:15mm; top:29mm; font-family:var(--font-mono); font-size:10pt; color:var(--ink-secondary); white-space:nowrap; }}
.hrule {{ position:absolute; left:15mm; right:15mm; top:44mm; height:.5mm; background:var(--ink-primary); }}
svg.draw {{ position:absolute; left:0; top:0; width:594mm; height:420mm; }}
.panel {{ position:absolute; width:180mm; border:.25mm solid var(--ink-secondary); }}
.panel > .ph {{ padding:2.3mm 4mm 1.8mm; border-bottom:.25mm solid var(--ink-secondary); font-size:10pt; font-weight:600; letter-spacing:.22em; color:var(--ink-secondary); }}
.panel > .pb {{ padding:3mm 4mm; font-size:10pt; line-height:1.3; }}
.grp {{ font-size:10pt; font-weight:600; letter-spacing:.22em; color:var(--ink-secondary); border-bottom:.2mm solid var(--rule); margin:1.6mm 0 .8mm; padding-bottom:.5mm; }}
.grp:first-child {{ margin-top:0; }}
.row {{ display:flex; gap:2mm; align-items:baseline; white-space:nowrap; }}
.row .k {{ font-family:var(--font-mono); font-weight:700; width:9mm; flex:none; }}
.row .r {{ font-family:var(--font-mono); width:25mm; flex:none; color:var(--ink-secondary); }}
.row .d {{ flex:1; overflow:hidden; text-overflow:clip; color:var(--ink-primary); }}
.row .v {{ font-family:var(--font-mono); font-weight:600; flex:none; text-align:right; }}
.row.unk .k, .row.unk .v {{ color:var(--alert); }}
.note {{ display:flex; gap:3mm; margin-bottom:2mm; }}
.note:last-child {{ margin-bottom:0; }}
.note .n {{ font-family:var(--font-mono); font-weight:700; width:5mm; flex:none; }}
.note b {{ font-weight:700; }} .note i {{ font-style:normal; color:var(--ink-secondary); }}
.sr {{ display:flex; gap:3mm; margin-bottom:1.6mm; }}
.sr:last-child {{ margin-bottom:0; }}
.sr .tag {{ font-family:var(--font-mono); font-weight:600; width:16mm; flex:none; }}
.open {{ position:absolute; left:15mm; top:320mm; width:175mm; height:85mm; border:.35mm solid var(--alert); background:var(--alert-fill); }}
.open .oh {{ display:flex; align-items:baseline; gap:3mm; padding:2.4mm 4mm 1.9mm; border-bottom:.25mm solid var(--alert); }}
.open .oh b {{ font-size:11pt; font-weight:700; letter-spacing:.22em; color:var(--alert); }}
.open .oh span {{ font-size:10pt; letter-spacing:.14em; color:var(--ink-secondary); }}
.open .ob {{ padding:2.6mm 4mm; display:flex; flex-direction:column; gap:1.5mm; }}
.oi {{ display:flex; gap:3.5mm; align-items:baseline; font-size:10pt; line-height:1.25; }}
.oi .ref {{ font-family:var(--font-mono); font-weight:700; color:var(--alert); width:11mm; flex:none; }}
.tb {{ position:absolute; left:399mm; top:315mm; width:180mm; height:90mm; border:.45mm solid var(--ink-primary); display:flex; flex-direction:column; background:var(--paper); }}
.tb > div {{ flex:none; border-bottom:.25mm solid var(--ink-secondary); padding:0 5mm; display:flex; align-items:center; }}
.tb .p {{ height:16mm; font-size:12pt; font-weight:700; letter-spacing:.16em; }}
.tb .t {{ height:22mm; gap:5mm; }}
.tb .t .n {{ font-family:var(--font-mono); font-size:22pt; font-weight:600; }}
.tb .t .s {{ font-size:14pt; font-weight:600; letter-spacing:.1em; }}
.tb .m {{ height:14mm; font-family:var(--font-mono); font-size:10pt; }}
.tb .st {{ flex:1; border-bottom:0; background:var(--fill-structure); font-size:11.5pt; font-weight:700; letter-spacing:.14em; }}
@page {{ size:594mm 420mm; margin:0; }}
@media print {{ html, body {{ background:var(--paper); }} .desk {{ padding:0; }} .sheet {{ transform:none !important; }} .desk {{ height:auto !important; }} }}
</style></head>
<body><div class="desk"><section class="sheet" id="sheet">
<div class="border"></div>
<div class="num">01</div>
<div class="title">PLUG AND REAR PORT — POINTS, EDGES, MEASUREMENTS</div>
<div class="sub">NOT TO SCALE · ALL DIMS IN mm · DRAWN FROM PHOTOS, NOTHING MEASURED YET</div>
<div class="label">LAPTOP CHARGER BRACE</div>
<div class="meta">ALIENWARE m15 R7 · BARREL PLUG</div>
<div class="hrule"></div>
<svg class="draw" viewBox="0 0 594 420" xmlns="http://www.w3.org/2000/svg">
{SVG}
</svg>
<div class="panel" style="left:399mm; top:48mm;"><div class="ph">MEASUREMENT SCHEDULE</div><div class="pb">{"".join(rows)}</div></div>
<div class="panel" style="left:399mm; top:250mm;"><div class="ph">KEYED NOTES</div><div class="pb">{notes}</div></div>
<div class="panel" style="left:15mm; top:270mm; width:175mm;"><div class="ph">READING THIS SHEET</div><div class="pb">{key}</div></div>
<div class="open"><div class="oh"><b>OPEN</b><span>UNRESOLVED ON THIS SHEET</span></div><div class="ob">{open_items}</div></div>
<div class="tb">
  <div class="p">3D PRINTS · LAPTOP CHARGER BRACE</div>
  <div class="t"><span class="n">01</span><span class="s">PLUG AND REAR PORT BLUEPRINT</span></div>
  <div class="m">NOT TO SCALE @ A2 · DIMS IN mm</div>
  <div class="m">REV A · 2026-10-04</div>
  <div class="st">STATUS: FIRST DRAWING — CHECK, THEN MEASURE</div>
</div>
</section></div>
<script>
(function () {{
  var s = document.getElementById('sheet'), d = s.parentNode;
  function fit() {{
    if (window.matchMedia('print').matches) return;
    var pad = 24, k = Math.min(1, (window.innerWidth - pad * 2) / s.offsetWidth);
    s.style.transform = 'scale(' + k + ')';
    d.style.padding = pad + 'px';
    d.style.height = (s.offsetHeight * k + pad * 2) + 'px';
  }}
  window.addEventListener('resize', fit); fit();
}})();
</script>
</body></html>"""
here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "charger_brace_blueprint_sheet01.html"), "w", encoding="utf-8").write(HTML)
print("ok", len(HTML))
