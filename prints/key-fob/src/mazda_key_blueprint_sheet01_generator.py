"""
Mazda flip key - blade head measurement blueprint, sheet 01.
Styled with the Drafting Table design system (A2 landscape, 594 x 420 mm).
Writes a self-contained HTML sheet; print it from a browser at A2 (or scaled to A3).

    python mazda_key_blueprint_sheet01_generator.py <out folder>
"""
import math, html, os, sys

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

# ---------------- measured geometry (mm) ----------------
TOP_Y, EDGE, S_C, D_C = 8.3, 23.34, 29.10, 21.34
BASE_BOT, TAB_END, TIP, T = 24.34, 39.04, 23.34 + 39.12, 15.8
TB1, TB2, HK = 15.30, 15.30 + 7.04, 15.30 - 1.8
BB1, BB2, GAP = 11.75, 11.75 + 15.60, 11.50
TY1, TY2, BY1, BY2 = 7.95, 7.95 + 5.50, 8.20, 8.20 + 5.50
GAPTOP, AE_T, AF_IN = EDGE - 7.30, 2.80, 1.44
FT1, FT2, FHK, FB1, FB2 = 31.9 - TB2, 31.9 - TB1, 31.9 - HK, 31.9 - BB2, 31.9 - BB1

INK, INK2, PAPER, ALERT = "#1C1C1A", "#6B6862", "#F7F5F0", "#B0453A"
FILL_STRUCT, STRUCT_TINT, SHADE = "#D9D4C9", "#E9E6DE", "#ECEAE5"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,monospace"
SANS = "Archivo,'Helvetica Neue',Helvetica,Arial,sans-serif"

botF = lambda x: EDGE + (x / 15.95) * (S_C - EDGE) if x <= 15.95 else S_C - ((x - 15.95) / 15.95) * (S_C - EDGE)
botB = lambda x: EDGE - (x / 15.95) * (EDGE - D_C) if x <= 15.95 else D_C + ((x - 15.95) / 15.95) * (EDGE - D_C)
lx = lambda r: T - r

VIEWS = {  # origin (mm on the sheet), drawing scale, label-offset factor (old px -> mm)
    "front": dict(ox=40, oy=78, s=2.5, k=2.5 / 9),
    "back": dict(ox=165, oy=78, s=2.5, k=2.5 / 9),
    "side": dict(ox=300, oy=78, s=2.5, k=2.5 / 9),
    "bottom": dict(ox=215, oy=274, s=5.0, k=5.0 / 16),
}
def P(v, x, y):
    V = VIEWS[v]; return V["ox"] + x * V["s"], V["oy"] + y * V["s"]

out = []
add = out.append
def path(v, pts, fill="none", stroke=INK, w=0.5, close=True, dash=None):
    d = "M" + " L".join("%.2f,%.2f" % P(v, x, y) for x, y in pts) + (" Z" if close else "")
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
def text(x, y, s, size=3.6, anchor="start", weight=400, fill=INK, font=SANS, ls=0, halo=False, extra=""):
    h = f' stroke="{PAPER}" stroke-width="1.1" paint-order="stroke" stroke-linejoin="round"' if halo else ""
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" letter-spacing="{ls}"{h} {extra}>{html.escape(s)}</text>')

def dome():
    return [(0.25 + 31.4 * i / 30, TOP_Y - TOP_Y * math.sqrt(max(0, 1 - (2 * i / 30 - 1) ** 2)) ** 0.75) for i in range(31)]
def side_top():
    return [(0, 3)] + [(T * i / 12, 1.6 - 1.6 * math.sin(math.pi * i / 12)) for i in range(1, 12)] + [(T, 3)]
def teeth(x_in, x_out, top):
    sgn = 1 if x_out > x_in else -1
    pts = [(x_in, top)] + [(x_in + (0.7 if i % 2 else 0) * sgn, top + 4 + i * (TIP - 9 - top) / 8) for i in range(9)]
    return pts + [(x_in + (x_out - x_in) * 0.26, TIP)]
DOME = dome()
F_CUT, B_CUT = teeth(21.9, 31.9, botF(21.9)), teeth(10, 0, botB(10))
HID = "2.4 1.8"; CENTRE = "9 2.4 2.4 2.4"; PROV = "6 2.4 1.4 2.4"

# ---------------- view titles ----------------
TITLES = {
    "front": ("1  FRONT", ["LOGO FACE TOWARDS YOU · BLADE ON THE RIGHT", "BOTTOM EDGE POINTS DOWN IN THE MIDDLE"], 22, 54),
    "back": ("2  BACK", ["RIVET FACE TOWARDS YOU · BLADE ON THE LEFT", "BOTTOM EDGE POINTS UP IN THE MIDDLE"], 150, 54),
    "side": ("3  SIDE", ["LOOKING AT THE BLADE SIDE", "LOGO FACE LEFT · RIVET FACE RIGHT"], 282, 54),
    "bottom": ("4  BOTTOM", ["BOTTOM TOWARDS YOU · LOGO FACE DOWN", "BLADE ON THE LEFT"], 198, 254),
}
for v, (t, subs, x, y) in TITLES.items():
    text(x, y, t, 4.6, weight=700, ls=0.6)
    for i, s in enumerate(subs):
        text(x, y + 5 + i * 4.4, s, 3.6, fill=INK2, ls=0.3)

# ---------------- geometry ----------------
# front (logo face): tab sits behind the head; the base is hidden behind the logo-face skirt
path("front", [(31.9, EDGE), (31.9, TIP - 4)] + F_CUT[::-1], fill=SHADE, w=0.5)
path("front", [(FT1, BASE_BOT), (FT1, TAB_END), (FHK, TAB_END), (FHK, TAB_END - 1.4), (FT2, TAB_END - 1.8), (FT2, BASE_BOT)], fill=FILL_STRUCT, w=0.7)
for i in range(3):
    y0 = max(BASE_BOT + 2.2 + i * 3.3, 0)
    path("front", [(FT1 + 1.6, y0), (FT2 - 1.6, y0), (FT2 - 1.6, y0 + 1.9), (FT1 + 1.6, y0 + 1.9)], fill=PAPER, w=0.35)
path("front", [(0, EDGE)] + DOME + [(31.9, EDGE), (15.95, S_C)], fill=PAPER, w=0.9)
path("front", [(FB1, BASE_BOT - 2), (FB1, BASE_BOT), (FB2, BASE_BOT), (FB2, BASE_BOT - 2)], stroke=INK2, w=0.35, close=False, dash=HID)
# back (rivet face): logo-face skirt hangs behind the base and tab
path("back", [(0, EDGE), (0, TIP - 4)] + B_CUT[::-1], fill=SHADE, w=0.5)
path("back", [(0, EDGE), (15.95, S_C), (31.9, EDGE), (15.95, D_C)], fill=STRUCT_TINT, stroke=INK2, w=0.35)
path("back", [(0, EDGE)] + DOME + [(31.9, EDGE), (15.95, D_C)], fill=PAPER, w=0.9)
path("back", [(BB1, botB(BB1)), (BB1, BASE_BOT), (BB2, BASE_BOT), (BB2, botB(BB2)), (15.95, D_C)], fill=STRUCT_TINT, w=0.5)
tabB = [(TB2, BASE_BOT), (TB2, TAB_END), (HK, TAB_END), (HK, TAB_END - 1.4), (TB1, TAB_END - 1.8), (TB1, BASE_BOT)]
path("back", tabB, fill=FILL_STRUCT, w=0.7)
for i in range(3):
    y0 = BASE_BOT + 2.2 + i * 3.3
    path("back", [(TB1 + 1.6, y0), (TB2 - 1.6, y0), (TB2 - 1.6, y0 + 1.9), (TB1 + 1.6, y0 + 1.9)], fill=PAPER, w=0.35)
cx, cy = P("back", 8.7, 7.5)
add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{2.2 * 2.5:.2f}" fill="{SHADE}" stroke="{ALERT}" stroke-width="0.45" stroke-dasharray="{PROV}"/>')
# side
path("side", [(lx(BY2), EDGE), (lx(BY2), BASE_BOT), (lx(BY1), BASE_BOT), (lx(BY1), EDGE)], fill=STRUCT_TINT, w=0.5)
path("side", [(lx(TY2), BASE_BOT), (lx(TY2), TAB_END), (lx(TY1), TAB_END), (lx(TY1), BASE_BOT)], fill=FILL_STRUCT, w=0.7)
path("side", [(0, EDGE), (-0.3, 12)] + side_top() + [(T + 0.3, 12), (T, EDGE)], fill=PAPER, w=0.9)
path("side", [(0, EDGE), (0, S_C), (AE_T, S_C), (AE_T, EDGE)], fill=PAPER, w=0.7)
path("side", [(0, S_C), (T, D_C)], stroke=INK2, w=0.25, close=False, dash=CENTRE)
path("side", [(lx(11.13), EDGE), (lx(11.13), GAPTOP), (lx(7.53), GAPTOP), (lx(7.53), EDGE)], fill=PAPER, w=0.5, close=False)
path("side", [(lx(10.63), GAPTOP + 0.4), (lx(10.63), TIP), (lx(8.03), TIP), (lx(8.03), GAPTOP + 0.4)], fill=SHADE, w=0.5)
# bottom
x0, y0 = P("bottom", 0, 0)
add(f'<rect x="{x0}" y="{y0}" width="{31.9 * 5}" height="{T * 5}" rx="9.4" fill="{PAPER}" stroke="{INK}" stroke-width="0.9"/>')
x1, y1 = P("bottom", AF_IN, AF_IN)
add(f'<rect x="{x1:.2f}" y="{y1:.2f}" width="{(31.9 - 2 * AF_IN) * 5:.2f}" height="{(T - 2 * AF_IN) * 5:.2f}" rx="7.4" fill="none" stroke="{INK2}" stroke-width="0.35" stroke-dasharray="{HID}"/>')
# the logo-face skirt thickness: read in a tight spot, so drawn as provisional
path("bottom", [(1.9, T - AE_T), (10.9, T - AE_T), (10.9, T), (1.9, T)], fill="rgba(176,69,58,0.07)", stroke=ALERT, w=0.35, dash=PROV)
path("bottom", [(15.95, 0), (15.95, T)], stroke=INK2, w=0.25, close=False, dash=CENTRE)
path("bottom", [(0, 7.53), (GAP, 7.53), (GAP, 11.13), (0, 11.13)], fill=PAPER, w=0.5, close=False)
path("bottom", [(0, 8.03), (10, 8.03), (10, 10.63), (0, 10.63)], fill=SHADE, w=0.5)
path("bottom", [(BB1, BY1), (BB2, BY1), (BB2, BY2), (BB1, BY2)], stroke=INK2, w=0.35, dash=HID)
path("bottom", [(TB1, TY1), (TB2, TY1), (TB2, TY2), (TB1, TY2)], fill=FILL_STRUCT, w=0.7)
path("bottom", [(HK, 9.2), (TB1, 9.2), (TB1, 12.2), (HK, 12.2)], fill=STRUCT_TINT, w=0.5)

def face(v, x, y, s, **kw):
    px, py = P(v, x, y); text(px, py, s, 3.6, "middle", 500, INK2, ls=0.5, **kw)
face("front", 15.95, 14.5, "LOGO FACE"); face("back", 18.5, 15.5, "RIVET FACE")
face("front", 12.35, BASE_BOT - 2.9, "BASE (HIDDEN)")
face("bottom", 15.95, -1.6, "RIVET FACE")
px, py = P("bottom", 26, T); text(px, py + 10.5, "LOGO FACE", 3.6, "middle", 500, INK2, ls=0.5)
px, py = P("bottom", 0.9, T); text(px, py + 9.2, "AE 2.80 · AH ≈10 (IND.)", 3.6, "start", 600, ALERT, MONO)
px, py = P("back", 8.7, 7.5); text(px + 8.2, py + 6.2, "(IND.)", 3.6, "start", 600, ALERT, MONO)

# ---------------- dimension lines (overall sizes only; the rest is in the schedule) ----------------
def dim_h(x1, x2, y, label, wit_from):
    for x in (x1, x2):
        add(f'<line x1="{x:.2f}" y1="{wit_from:.2f}" x2="{x:.2f}" y2="{y - 1.6 if y < wit_from else y + 1.6:.2f}" stroke="{INK2}" stroke-width="0.15"/>')
        add(f'<line x1="{x - 1.6:.2f}" y1="{y + 1.6:.2f}" x2="{x + 1.6:.2f}" y2="{y - 1.6:.2f}" stroke="{INK}" stroke-width="0.35"/>')
    add(f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.22"/>')
    text((x1 + x2) / 2, y - 1.6, label, 3.6, "middle", 500, INK, MONO)
def dim_v(y1, y2, x, label, wit_to):
    for y, wt in zip((y1, y2), wit_to):
        add(f'<line x1="{x - 1.6:.2f}" y1="{y:.2f}" x2="{wt:.2f}" y2="{y:.2f}" stroke="{INK2}" stroke-width="0.15"/>')
        add(f'<line x1="{x - 1.6:.2f}" y1="{y + 1.6:.2f}" x2="{x + 1.6:.2f}" y2="{y - 1.6:.2f}" stroke="{INK}" stroke-width="0.35"/>')
    add(f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.22"/>')
    ym = (y1 + y2) / 2
    text(x - 1.8, ym, label, 3.6, "middle", 500, INK, MONO, extra=f'transform="rotate(-90 {x - 1.8:.2f} {ym:.2f})"')
dim_v(P("front", 0, 0)[1], P("front", 0, EDGE)[1], 24, "E 23.34", (P("front", 15.95, 0)[0] - 1.5, P("front", 0, 0)[0] - 1.5))
dim_h(P("side", 0, 0)[0], P("side", T, 0)[0], 70, "C 15.80", P("side", 0, 3)[1])
dim_h(P("bottom", 0, 0)[0], P("bottom", 31.9, 0)[0], P("bottom", 0, T)[1] + 19, "B 31.90", P("bottom", 0, T)[1] - 9)

# ---------------- scale bars ----------------
def scale_bar(x, y, seg, marks, caption):
    for i in range(len(marks) - 1):
        add(f'<rect x="{x + i * seg:.2f}" y="{y}" width="{seg}" height="1.6" fill="{INK if i % 2 == 0 else PAPER}" stroke="{INK}" stroke-width="0.25"/>')
    for i, m in enumerate(marks):
        text(x + i * seg, y + 6, m, 3.6, "middle", 500, INK, MONO)
    text(x, y - 2, caption, 3.6, "start", 600, INK2, ls=0.5)
scale_bar(322, 258, 25, ["0", "10", "20 mm"], "VIEWS 1–3 · 2.5:1")
scale_bar(215, 386, 25, ["0", "5", "10 mm"], "VIEW 4 · 5:1")

# ---------------- points and edges ----------------
POINTS = [
  ("F1","front",0,EDGE,-10,2),("F2","front",0.25,TOP_Y,-10,0),("F3","front",15.95,0,8,-10),("F4","front",31.65,TOP_Y,10,0),("F5","front",31.9,EDGE,10,-4),("F6","front",15.95,S_C,12,14),
  ("F8","front",FB1,BASE_BOT,8,-10),("F9","front",FB2,BASE_BOT,8,-10),
  ("F11","front",FT1,botF(FT1),-26,20),("F12","front",FT1,TAB_END,-10,6),("F13","front",FHK,TAB_END,-4,22),("F14","front",FHK,TAB_END-1.4,26,-14),("F15","front",FT2,TAB_END-1.8,44,-30),("F16","front",FT2,botF(FT2),14,-22),
  ("F17","front",21.9,botF(21.9),36,-6),("F18","front",24.5,TIP,-10,10),("F19","front",31.9,TIP-4,10,4),
  ("B1","back",0,EDGE,-10,-4),("B2","back",0.25,TOP_Y,-10,0),("B3","back",15.95,0,8,-10),("B4","back",31.65,TOP_Y,10,0),("B5","back",31.9,EDGE,10,2),("B6","back",15.95,D_C,4,-12),("B7","back",8.7,7.5,24,4),
  ("B8","back",BB1,botB(BB1),6,-30),("B9","back",BB1,BASE_BOT,-30,28),("B10","back",BB2,BASE_BOT,30,10),("B11","back",BB2,botB(BB2),-8,-16),
  ("B12","back",TB2,BASE_BOT,8,30),("B13","back",TB2,TAB_END,8,6),("B14","back",HK,TAB_END,-30,18),("B15","back",HK,TAB_END-1.4,-26,-14),("B16","back",TB1,TAB_END-1.8,-34,-24),("B17","back",TB1,BASE_BOT,-26,38),
  ("B18","back",10,botB(10),-26,-24),("B19","back",7.4,TIP,10,10),("B20","back",0,TIP-4,-10,4),
  ("S1","side",0,EDGE,-12,-8),("S2","side",0,3,-10,0),("S3","side",T,3,10,0),("S4","side",T,EDGE,10,4),("S5","side",0,S_C,-30,6),("S6","side",T,D_C,10,-6),
  ("S7","side",lx(11.13),GAPTOP,-10,-6),("S8","side",lx(7.53),GAPTOP,10,-6),("S15","side",AE_T,S_C,8,10),("S9","side",lx(BY2),BASE_BOT,-26,26),("S10","side",lx(BY1),BASE_BOT,12,10),
  ("S11","side",lx(TY2),TAB_END,-10,8),("S12","side",lx(TY1),TAB_END,10,8),("S13","side",lx(10.63),TIP,-10,8),("S14","side",lx(8.03),TIP,10,8),
  ("U1","bottom",0.9,0.9,-14,-12),("U2","bottom",31,0.9,12,-12),("U3","bottom",31,14.9,12,14),("U4","bottom",0.9,14.9,-14,14),("U5","bottom",15.95,0,6,-12),("U6","bottom",15.95,T,6,16),
  ("U7","bottom",0,7.53,-12,-4),("U8","bottom",GAP,7.53,-14,-8),("U9","bottom",GAP,11.13,-8,18),("U10","bottom",0,11.13,-12,8),("U11","bottom",10,8.03,-8,14),("U12","bottom",10,10.63,-8,-6),
  ("U13","bottom",BB1,BY1,-4,-34),("U14","bottom",BB2,BY1,8,-8),("U15","bottom",BB2,BY2,8,12),("U16","bottom",BB1,BY2,-10,14),
  ("U17","bottom",TB1,TY1,8,-12),("U18","bottom",TB2,TY1,6,-10),("U19","bottom",TB2,TY2,6,14),("U20","bottom",TB1,TY2,6,16),("U21","bottom",HK,9.2,-2,-36),("U22","bottom",HK,12.2,-2,34),
]
EDGES = [  # id, view, label x, y, dx, dy
  ("f1","front",0,16,-22,0),("f2","front",8,1.6,-8,-14),("f3","front",31.8,16,-24,0),("f4","front",27.5,botF(27.5),0,-16),("f5","front",3,botF(3),0,-18),
  ("f7","front",12.35,BASE_BOT,0,0),("f9","front",FT1,33,-22,0),("f10","front",14,TAB_END,0,14),("f11","front",FHK,38.4,26,14),("f12","front",17.5,37.4,4,-16),("f13","front",FT2,33,18,0),
  ("f14","front",21.9,50,-22,0),("f15","front",27.5,TIP-1.6,14,14),("f16","front",31.9,45,22,0),
  ("b1","back",0,16,24,0),("b2","back",24,1.6,8,-14),("b3","back",31.8,16,24,0),("b4","back",29.5,botB(29.5),0,-16),("b5","back",5,botB(5),0,16),
  ("b6","back",BB1,23.1,-22,0),("b7","back",19.5,BASE_BOT,0,0),("b8","back",BB2,23.6,22,0),("b9","back",TB2,32,22,0),("b10","back",18.4,TAB_END,0,14),("b11","back",HK,38.4,-30,4),
  ("b12","back",14.5,37.4,12,-16),("b13","back",TB1,29.5,0,0),("b14","back",10,45,20,0),("b15","back",4.4,TIP-1.6,-14,14),("b16","back",0,45,-22,0),
  ("s1","side",-0.2,15,-22,0),("s2","side",8,0.1,0,-14),("s3","side",T+0.2,15,22,0),("s4","side",1.6,EDGE,0,-12),("s5","side",13,D_C+0.9,8,-6),
  ("s6","side",lx(11.13),19.2,-20,0),("s7","side",lx(9.3),GAPTOP,0,-14),("s8","side",lx(7.53),19.2,20,0),("s12","side",AE_T,27,16,0),("s13","side",AE_T/2,S_C,-22,14),
  ("s9","side",lx(10.95),BASE_BOT,0,2),("s10","side",lx(TY2),33,-20,0),("s11","side",lx(9.3),TIP,0,16),
  ("u1","bottom",8,0,0,0),("u2","bottom",24,0,0,0),("u3","bottom",31.9,4,0,0),("u4","bottom",28.5,T,0,0),("u5","bottom",6,T,0,0),("u6","bottom",0,3.5,0,0),("u7","bottom",15.95,2.6,18,0),
  ("u8","bottom",5.5,7.53,0,-12),("u9","bottom",GAP,9.33,-14,0),("u10","bottom",5.5,11.13,0,12),
  ("u11","bottom",25.3,BY1,0,-12),("u12","bottom",BB2,11,0,0),("u13","bottom",25.6,BY2,0,12),("u14","bottom",BB1,13,0,0),
  ("u15","bottom",18.8,TY1,0,0),("u16","bottom",TB2,10.7,0,0),("u17","bottom",18.8,TY2,0,0),("u18","bottom",TB1,8.9,4,0),("u19","bottom",HK,10.7,0,0),("u20","bottom",8,AF_IN,0,12),
]
for pid, v, x, y, dx, dy in POINTS:
    k = VIEWS[v]["k"]; px, py = P(v, x, y)
    if abs(dx) > 16 or abs(dy) > 20:
        add(f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{px + dx * k * 0.9:.2f}" y2="{py + dy * k * 0.9:.2f}" stroke="{INK2}" stroke-width="0.15"/>')
for eid, v, x, y, dx, dy in EDGES:
    k = VIEWS[v]["k"]; px, py = P(v, x, y); tx, ty = px + dx * k, py + dy * k
    w = 2.4 + 2.16 * len(eid)
    add(f'<rect x="{tx - w / 2:.2f}" y="{ty - 2.5:.2f}" width="{w:.2f}" height="5" fill="{PAPER}" stroke="{INK2}" stroke-width="0.25"/>')
    text(tx, ty + 1.3, eid, 3.6, "middle", 500, INK2, MONO)
for pid, v, x, y, dx, dy in POINTS:
    k = VIEWS[v]["k"]; px, py = P(v, x, y)
    add(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="0.9" fill="{INK}"/>')
    text(px + dx * k, py + dy * k + 1.25, pid, 3.6, "start" if dx >= 0 else "end", 600, INK, MONO, halo=True)

SVG = "\n".join(out)

# ---------------- schedule, notes, open items ----------------
SCHEDULE = [
    ("HEAD OUTLINE", [
        ("A", "F2–F4", "Width at the top of the straight sides", "31.40", ""),
        ("B", "F1–F5", "Width at the bottom corners", "31.90", ""),
        ("C", "u1–u5", "Thickness, logo face to rivet face", "15.80", ""),
        ("D", "B3→B6", "Dome tip to rivet-face centre (edge points up)", "21.34", ""),
        ("E", "F3→F1", "Dome tip to the bottom corners", "23.34", ""),
        ("S", "F3→F6", "Dome tip to logo-face centre (edge points down)", "29.10", ""),
        ("AB", "B3→b7", "Dome tip to the flat bottom face", "24.34", ""),
        ("AF", "u20→u1", "Bottom face set in from the rivet face", "1.44", ""),
        ("AE", "s12–S15", "Logo-face skirt thickness at the U4 end", "2.80", "(IND.)"),
        ("AG", "U16→s12", "Between the 2.80 part and the base", "1.53", "(IND.)"),
        ("AH", "U4→U6", "Length of the 2.80 part", "≈10", "(IND.)"),
    ]),
    ("SNAP TAB", [
        ("F", "b7→b10", "Tab length, bottom face to tip", "14.60", ""),
        ("G", "F3→f10", "Dome tip to tab tip", "39.04", ""),
        ("H", "F11–F16", "Tab width, body only", "7.04", ""),
        ("I", "F12–F13", "Tab width including the hook", "9.00", ""),
        ("J", "u6→u18", "Blade-side edge to tab", "15.30", ""),
        ("K", "u3→u16", "Other edge to tab", "9.60", ""),
        ("L", "u15–u17", "Tab thickness", "5.50", ""),
        ("M", "u1→u15", "Rivet face to tab", "7.95", ""),
    ]),
    ("TAB BASE", [
        ("U", "b6→b7", "Base below the rivet-face edge", "2.25", ""),
        ("V", "U13–U14", "Base width", "15.60", ""),
        ("W", "U14–U15", "Base thickness", "5.50", ""),
        ("X", "u6→U13", "Blade-side edge to base", "11.75", ""),
        ("Y", "u1→U13", "Rivet face to base", "8.20", ""),
    ]),
    ("FOLDED BLADE AND GAP", [
        ("N", "F5→F18", "Bottom corner to blade tip", "39.12", ""),
        ("O", "f16–f3", "Blade to blade-side edge (flush)", "0.00", ""),
        ("P", "F17–f16", "Blade width", "10.00", ""),
        ("Q", "S13–S14", "Blade thickness", "2.60", ""),
        ("R", "u1→U11", "Rivet face to blade", "8.03", ""),
        ("T", "u8–u10", "Blade gap width", "3.60", ""),
        ("Z", "u6→u9", "Blade gap depth from the blade side", "11.50", ""),
        ("AA", "s4→s7", "Blade gap length up the side", "7.30", ""),
    ]),
]
rows = []
for group, items in SCHEDULE:
    rows.append(f'<div class="grp">{group}</div>')
    for k, refs, desc, val, flag in items:
        cls = ' class="row unk"' if flag else ' class="row"'
        rows.append(f'<div{cls}><span class="k">{k}</span><span class="r">{html.escape(refs)}</span><span class="d">{html.escape(desc)}</span>'
                    f'<span class="v">{val}{" " + flag if flag else ""}</span></div>')
NOTES = [
    ("1", "FRONT AND BACK ARE NOT MIRROR IMAGES.", "The logo-face edge drops to S in the middle; the rivet-face edge rises to D. Both views are needed."),
    ("2", "THE BASE IS HIDDEN FROM THE FRONT.", "The logo-face skirt covers it. Tab, base and skirt are one piece with no gap between them."),
    ("3", "THE HOOK POINTS AT THE BLADE.", "It sets which wall of the socket carries the catch."),
    ("4", "THE BLADE SWINGS OUT ON THE RIVET.", "The gap is open on the blade side; fully open, the blade points out of the dome top."),
]
notes = "".join(f'<div class="note"><span class="n">{n}</span><span><b>{a}</b> <i>{b}</i></span></div>' for n, a, b in NOTES)
KEY = [
    ("F1", "POINT. A corner or tip. The capital letter is the view: F front, B back, S side, U underside."),
    ("f1", "EDGE. Lower-case, in a box. Same view letters."),
    ("A", "MEASUREMENT. Listed in the schedule with the points or edges it runs between."),
    ("- - -", "HIDDEN. Behind another part in this view."),
    ("x y z", "x from the blade-side edge · y from the rivet face · z from the dome tip."),
]
key = "".join(f'<div class="sr"><span class="tag">{t}</span><span>{html.escape(d)}</span></div>' for t, d in KEY)
OPEN = [
    ("AE", "2.80 was read in a tight spot. The body notch is cut 3.0 deep along the whole logo face. Resolved by FIT TEST v3 A/B/C."),
    ("AG", "1.53 is taken as the skirt thickness between the 2.80 part and the base. It may be a distance along the width. Re-measure."),
    ("AH", "Length of the 2.80 part from U4 is about 10. Not used by the body. Re-measure before narrowing the notch."),
    ("U3", "Skirt thickness on the tab side of the base: TBD."),
    ("B7", "Rivet position, dome curve and blade profile are drawn approximate. Not used by the body."),
]
open_items = "".join(f'<div class="oi"><span class="ref">{r}</span><span>{html.escape(t)}</span></div>' for r, t in OPEN)

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>01 Key head measurement blueprint</title>
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
.row .d {{ flex:1; overflow:hidden; text-overflow:clip; }}
.row .v {{ font-family:var(--font-mono); font-weight:600; flex:none; text-align:right; }}
.row.unk, .row.unk .k, .row.unk .r {{ color:var(--alert); }}
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
.oi .ref {{ font-family:var(--font-mono); font-weight:700; color:var(--alert); width:9mm; flex:none; }}
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
<div class="title">KEY HEAD — POINTS, EDGES, MEASUREMENTS</div>
<div class="sub">SCALE 2.5:1 AND 5:1 @ A2 · ALL DIMS IN mm · BLADE FOLDED</div>
<div class="label">MAZDA FLIP KEY</div>
<div class="meta">ATENZA 2007 · CALIPER MEASURED</div>
<div class="hrule"></div>
<svg class="draw" viewBox="0 0 594 420" xmlns="http://www.w3.org/2000/svg">
{SVG}
</svg>
<div class="panel" style="left:399mm; top:48mm;"><div class="ph">MEASUREMENT SCHEDULE</div><div class="pb">{"".join(rows)}</div></div>
<div class="panel" style="left:399mm; top:254mm;"><div class="ph">KEYED NOTES</div><div class="pb">{notes}</div></div>
<div class="panel" style="left:15mm; top:262mm; width:175mm;"><div class="ph">READING THIS SHEET</div><div class="pb">{key}</div></div>
<div class="open"><div class="oh"><b>OPEN</b><span>UNRESOLVED ON THIS SHEET</span></div><div class="ob">{open_items}</div></div>
<div class="tb">
  <div class="p">3D PRINTS · MAZDA KEY FOB BODY</div>
  <div class="t"><span class="n">01</span><span class="s">KEY HEAD MEASUREMENT BLUEPRINT</span></div>
  <div class="m">SCALE 2.5:1 (VIEWS 1–3) · 5:1 (VIEW 4) @ A2 · DIMS IN mm</div>
  <div class="m">REV C · 2026-10-04</div>
  <div class="st">STATUS: MEASURED — FIT TEST PENDING</div>
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
open(os.path.join(OUT_DIR, "mazda_key_blueprint_sheet01.html"), "w").write(HTML)
print("ok", len(HTML))
