"""The key head drawing, as an SVG and a PNG.

    python mazda_key_blueprint_generator.py <out folder>     # needs: pip install cairosvg
"""
import os, sys
import cairosvg

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
INK, FILL, DARK, BLADE = "#1b2a4a", "#eef3fb", "#3a404b", "#c9ced8"
VCOL, ECOL, OK, NEED = "#c0392b", "#0f7c8c", "#1d8a4a", "#d2561e"
out = []
add = out.append

def text(x, y, s, size=12, anchor="start", weight=400, fill=INK):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{s}</text>')

class View:
    def __init__(self, ox, oy, s):
        self.ox, self.oy, self.s = ox, oy, s
        self.labels = []
    def p(self, x, y):
        return self.ox + x * self.s, self.oy + y * self.s
    def path(self, pts, fill="none", stroke=INK, w=2, close=True, dash=None):
        d = "M" + " L".join(f"{self.p(x, y)[0]:.1f},{self.p(x, y)[1]:.1f}" for x, y in pts) + (" Z" if close else "")
        da = f' stroke-dasharray="{dash}"' if dash else ""
        add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{da}/>')
    def v(self, name, x, y, dx=8, dy=-6):     # vertex
        self.labels.append(("v", name, x, y, dx, dy))
    def e(self, name, x, y, dx=0, dy=0):      # edge label at a point on the edge
        self.labels.append(("e", name, x, y, dx, dy))
    def draw_labels(self):
        for kind, name, x, y, dx, dy in sorted(self.labels, key=lambda t: t[0] == "v"):
            px, py = self.p(x, y)
            if kind == "v":
                if abs(dx) > 16 or abs(dy) > 20:
                    add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + dx * 0.9:.1f}" y2="{py + dy * 0.9:.1f}" stroke="{VCOL}" stroke-width="1"/>')
                add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="{VCOL}"/>')
                anchor = "start" if dx >= 0 else "end"
                for fill, stroke in (("white", 'stroke="white" stroke-width="4"'), (VCOL, "")):
                    add(f'<text x="{px + dx:.1f}" y="{py + dy + 4:.1f}" font-size="13" font-weight="700" text-anchor="{anchor}" fill="{fill}" {stroke}>{name}</text>')
            else:
                tx, ty = px + dx, py + dy
                wbox = 9 + 7.5 * len(name)
                add(f'<rect x="{tx - wbox / 2:.1f}" y="{ty - 9:.1f}" width="{wbox:.1f}" height="17" rx="4" fill="white" stroke="{ECOL}" stroke-width="1.4"/>')
                add(f'<text x="{tx:.1f}" y="{ty + 4:.1f}" font-size="12" font-weight="700" text-anchor="middle" fill="{ECOL}">{name}</text>')

W, H = 1840, 1380
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
add('<defs><pattern id="g" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M14 0H0V14" fill="none" stroke="#e3e9f4" stroke-width="0.6"/></pattern></defs>')
add(f'<rect width="{W}" height="{H}" fill="white"/><rect width="{W}" height="{H}" fill="url(#g)"/>')
text(30, 40, "Mazda flip key – blade head: points and edges (v3)", 22, weight=700)
add(f'<text x="30" y="64" font-size="13.5" fill="{INK}">'
    f'<tspan fill="{VCOL}" font-weight="700">● F1, B6, U7…</tspan> = points (corners and tips).   '
    f'<tspan fill="{ECOL}" font-weight="700">[f1] [u7]…</tspan> = edges.   '
    'Single capital letters (A–Z) = measurements, listed at the bottom.   Blade folded. Shapes approximate.</text>')

TOP_Y, EDGE, S_C, D_C = 8.3, 23.34, 25.3, 21.34
BASE_BOT, TAB_LEN, TIP = 26.2, 14.6, 23.34 + 39.12

def bot_front(x):   # logo face bottom edge: points DOWN in the middle
    return EDGE + (x / 15.95) * (S_C - EDGE) if x <= 15.95 else S_C - ((x - 15.95) / 15.95) * (S_C - EDGE)
def bot_back(x):    # rivet face bottom edge: points UP in the middle
    return EDGE - (x / 15.95) * (EDGE - D_C) if x <= 15.95 else D_C + ((x - 15.95) / 15.95) * (EDGE - D_C)

def head_outline(vw, bottom_fn):
    pts = [(0, EDGE), (0.25, TOP_Y)]
    import math
    for i in range(1, 30):        # dome as a smooth curve
        t = i / 30
        x = 0.25 + 31.4 * t
        y = TOP_Y - TOP_Y * math.sqrt(max(0, 1 - (2 * t - 1) ** 2)) ** 0.75
        pts.append((x, y))
    pts += [(31.65, TOP_Y), (31.9, EDGE), (15.95, bottom_fn(15.95))]
    vw.path(pts, fill=FILL)

def blade_front(vw, x_in, x_out, mirror):
    top = bot_front(x_in) if not mirror else bot_back(x_in)
    pts = [(x_out, EDGE)]
    tip_x = x_in + (x_out - x_in) * 0.26
    pts += [(x_out, TIP - 4), (tip_x, TIP)]
    n = 8
    for i in range(n, -1, -1):
        y = top + 4 + i * (TIP - 9 - top) / n
        pts.append((x_in + (0.7 if i % 2 else 0) * (1 if x_out > x_in else -1), y))
    pts.append((x_in, top))
    vw.path(pts, fill=BLADE, w=1.5)

def tab_front(vw, x1, x2, hook_x):
    vw.path([(x1, BASE_BOT), (x1, BASE_BOT + TAB_LEN), (hook_x, BASE_BOT + TAB_LEN), (hook_x, BASE_BOT + TAB_LEN - 1.4),
             (x2, BASE_BOT + TAB_LEN - 1.8), (x2, BASE_BOT)], fill=DARK, w=1.3)
    lo, hi = min(x1, x2), max(x1, x2)
    for i in range(3):
        px, py = vw.p(lo + 1.6, BASE_BOT + 2.2 + i * 3.3)
        add(f'<rect x="{px:.1f}" y="{py:.1f}" width="{(hi - lo - 3.2) * vw.s:.1f}" height="{1.9 * vw.s:.1f}" fill="{FILL}"/>')

# ======================= VIEW 1: FRONT (logo face) =======================
v1 = View(120, 150, 9.0)
text(v1.ox - 70, v1.oy - 50, "1  FRONT — logo face towards you", 16, weight=700)
text(v1.ox - 70, v1.oy - 32, "blade on the RIGHT · bottom edge points DOWN in the middle", 12.5)
blade_front(v1, 21.9, 31.9, False)
head_outline(v1, bot_front)
v1.path([(7, bot_front(7) - 1.2), (7, BASE_BOT), (20, BASE_BOT), (20, bot_front(20) - 1.2)], fill="#5b6270", w=1.3)
tab_front(v1, 9.5, 16.54, 18.34)
px, py = v1.p(15.95, 14); text(px, py, "LOGO FACE", 14, "middle")
for n, x, y, dx, dy in [("F1", 0, EDGE, -10, 2), ("F2", 0.25, TOP_Y, -10, 0), ("F3", 15.95, 0, 8, -10), ("F4", 31.65, TOP_Y, 10, 0),
                        ("F5", 31.9, EDGE, 10, -4), ("F6", 15.95, S_C, 10, -36),
                        ("F7", 7, bot_front(7), -4, -40), ("F8", 7, BASE_BOT, -38, 14), ("F9", 20, BASE_BOT, 36, 16), ("F10", 20, bot_front(20), 6, -28),
                        ("F11", 9.5, BASE_BOT, -26, 36), ("F12", 9.5, BASE_BOT + TAB_LEN, -10, 6), ("F13", 18.34, BASE_BOT + TAB_LEN, -4, 22),
                        ("F14", 18.34, BASE_BOT + TAB_LEN - 1.4, 26, -14), ("F15", 16.54, BASE_BOT + TAB_LEN - 1.8, 30, -30), ("F16", 16.54, BASE_BOT, 26, 30),
                        ("F17", 21.9, bot_front(21.9), 36, -6), ("F18", 21.9 + 2.6, TIP, -10, 10), ("F19", 31.9, TIP - 4, 10, 4)]:
    v1.v(n, x, y, dx, dy)
for n, x, y, dx, dy in [("f1", 0, 16, -22, 0), ("f2", 8, 1.6, -8, -14), ("f3", 31.8, 16, -24, 0), ("f4", 27.5, bot_front(27.5), 0, -16),
                        ("f5", 3, bot_front(3), 0, -18), ("f6", 7, 25.5, -22, 0), ("f7", 13, BASE_BOT, 0, 0), ("f8", 20, 25.5, 14, 0),
                        ("f9", 9.5, 34, -22, 0), ("f10", 13.5, BASE_BOT + TAB_LEN, 0, 14), ("f11", 18.34, 40.1, 26, 14),
                        ("f12", 17.4, 39.2, 4, -16), ("f13", 16.54, 33, 18, 0), ("f14", 21.9, 50, -22, 0), ("f15", 27.5, TIP - 1.6, 14, 14),
                        ("f16", 31.9, 45, 22, 0)]:
    v1.e(n, x, y, dx, dy)
v1.draw_labels()

# ======================= VIEW 2: BACK (rivet face) =======================
v2 = View(640, 150, 9.0)
text(v2.ox - 70, v2.oy - 50, "2  BACK — rivet face towards you", 16, weight=700)
text(v2.ox - 70, v2.oy - 32, "blade on the LEFT · bottom edge points UP in the middle", 12.5)
blade_front(v2, 10.0, 0.0, True)
head_outline(v2, bot_back)
v2.path([(11.9, bot_back(11.9) - 1.2), (11.9, BASE_BOT), (24.9, BASE_BOT), (24.9, bot_back(24.9) - 1.2)], fill="#5b6270", w=1.3)
tab_front(v2, 22.4, 15.36, 13.56)
px, py = v2.p(8.7, 7.5); add(f'<circle cx="{px}" cy="{py}" r="{2.2 * v2.s}" fill="#b9c0cc" stroke="{INK}" stroke-width="1.5"/>')
px, py = v2.p(18, 15); text(px, py, "RIVET FACE", 14, "middle")
for n, x, y, dx, dy in [("B1", 0, EDGE, -10, -4), ("B2", 0.25, TOP_Y, -10, 0), ("B3", 15.95, 0, 8, -10), ("B4", 31.65, TOP_Y, 10, 0),
                        ("B5", 31.9, EDGE, 10, 2), ("B6", 15.95, D_C, 4, -12), ("B7", 8.7, 7.5, 24, 4),
                        ("B8", 11.9, bot_back(11.9), 6, -30), ("B9", 11.9, BASE_BOT, -30, 32), ("B10", 24.9, BASE_BOT, 30, 10), ("B11", 24.9, bot_back(24.9), -8, -16),
                        ("B12", 22.4, BASE_BOT, 8, 36), ("B13", 22.4, BASE_BOT + TAB_LEN, 8, 6), ("B14", 13.56, BASE_BOT + TAB_LEN, -30, 18),
                        ("B15", 13.56, BASE_BOT + TAB_LEN - 1.4, -26, -14), ("B16", 15.36, BASE_BOT + TAB_LEN - 1.8, -34, -24), ("B17", 15.36, BASE_BOT, -26, 42),
                        ("B18", 10.0, bot_back(10.0), -26, -24), ("B19", 10 - 2.6, TIP, 10, 10), ("B20", 0, TIP - 4, -10, 4)]:
    v2.v(n, x, y, dx, dy)
for n, x, y, dx, dy in [("b1", 0, 16, 24, 0), ("b2", 24, 1.6, 8, -14), ("b3", 31.8, 16, 24, 0), ("b4", 28.5, bot_back(28.5), 0, -16),
                        ("b5", 5, bot_back(5), 0, 16), ("b6", 11.9, 24.6, -22, 0), ("b7", 18.4, BASE_BOT, 0, 0), ("b8", 24.9, 25.0, 22, 0),
                        ("b9", 22.4, 34, 22, 0), ("b10", 18.4, BASE_BOT + TAB_LEN, 0, 14), ("b11", 13.56, 40.1, -30, 4),
                        ("b12", 14.5, 39.2, 12, -16), ("b13", 15.36, 30.5, 0, 0), ("b14", 10.0, 45, 20, 0), ("b15", 4.4, TIP - 1.6, -14, 14),
                        ("b16", 0, 45, -22, 0)]:
    v2.e(n, x, y, dx, dy)
v2.draw_labels()

# ======================= VIEW 3: SIDE (blade side) =======================
v3 = View(1170, 150, 9.0)
text(v3.ox - 60, v3.oy - 50, "3  SIDE — looking at the blade side", 16, weight=700)
text(v3.ox - 60, v3.oy - 32, "logo face on the LEFT · rivet face on the RIGHT", 12.5)
T = 15.8
lx = lambda from_rivet: T - from_rivet          # rivet-face measurements -> x from logo face
# base (behind) and tab (behind the blade)
v3.path([(lx(14.5), EDGE), (lx(14.5), BASE_BOT), (lx(5.2), BASE_BOT), (lx(5.2), EDGE)], fill="#5b6270", w=1.2)
v3.path([(lx(13.45), BASE_BOT), (lx(13.45), BASE_BOT + TAB_LEN), (lx(7.95), BASE_BOT + TAB_LEN), (lx(7.95), BASE_BOT)], fill=DARK, w=1.2)
# head side silhouette
import math
side = [(0, EDGE), (-0.3, 12), (0, 3)]
for i in range(1, 12):
    t = i / 12
    side.append((0 + T * t, 1.6 - 1.6 * math.sin(math.pi * t)))
side += [(T, 3), (T + 0.3, 12), (T, EDGE)]
v3.path(side, fill=FILL)
v3.path([(0, S_C), (T, D_C)], close=False, w=1.2, dash="5 3")
# blade gap on the side face + blade
v3.path([(lx(11.13), EDGE), (lx(11.13), 5.5), (lx(7.53), 5.5), (lx(7.53), EDGE)], fill="white", w=1.3, close=False)
v3.path([(lx(10.63), 6.0), (lx(10.63), TIP), (lx(8.03), TIP), (lx(8.03), 6.0)], fill=BLADE, w=1.3)
for n, x, y, dx, dy in [("S1", 0, EDGE, -12, -8), ("S2", 0, 3, -10, 0), ("S3", T, 3, 10, 0), ("S4", T, EDGE, 10, 4),
                        ("S5", 0, S_C, -30, 6), ("S6", T, D_C, 10, -6),
                        ("S7", lx(11.13), 5.5, -10, -6), ("S8", lx(7.53), 5.5, 10, -6),
                        ("S9", lx(14.5), BASE_BOT, -26, 28), ("S10", lx(5.2), BASE_BOT, 10, 8),
                        ("S11", lx(13.45), BASE_BOT + TAB_LEN, -10, 8), ("S12", lx(7.95), BASE_BOT + TAB_LEN, 10, 8),
                        ("S13", lx(10.63), TIP, -10, 8), ("S14", lx(8.03), TIP, 10, 8)]:
    v3.v(n, x, y, dx, dy)
for n, x, y, dx, dy in [("s1", -0.2, 15, -22, 0), ("s2", 8, 0.1, 0, -14), ("s3", T + 0.2, 15, 22, 0), ("s4", 2.5, EDGE, 0, 0),
                        ("s5", 13, D_C + 0.5, 22, 10), ("s6", lx(11.13), 14, -20, 0), ("s7", lx(9.3), 5.5, 0, -14), ("s8", lx(7.53), 11, 20, 0),
                        ("s9", lx(9.85), BASE_BOT, 0, 2), ("s10", lx(10.7), 36, -20, 0), ("s11", lx(9.3), TIP, 0, 16)]:
    v3.e(n, x, y, dx, dy)
v3.draw_labels()
px, py = v3.p(-3.5, 31); text(px, py, "dashed s5 =", 10.5, "end"); text(px, py + 13, "bottom centre line", 10.5, "end"); text(px, py + 26, "(S5 low → S6 high)", 10.5, "end")
px, py = v3.p(T + 3, 46); text(px, py, "blade in gap,", 10.5); text(px, py + 13, "tab and base", 10.5); text(px, py + 26, "behind it", 10.5)

# ======================= VIEW 4: BOTTOM =======================
v4 = View(110, 930, 18.0)
text(v4.ox - 60, v4.oy - 100, "4  BOTTOM — held the way you hold it", 16, weight=700)
text(v4.ox - 60, v4.oy - 82, "bottom towards you · logo face DOWN · blade on the LEFT", 12.5)
px, py = v4.p(0, 0)
add(f'<rect x="{px}" y="{py}" width="{31.9 * v4.s}" height="{15.8 * v4.s}" rx="34" fill="{FILL}" stroke="{INK}" stroke-width="2"/>')
v4.path([(15.95, 0), (15.95, 15.8)], close=False, w=1.2, dash="5 3")
v4.path([(-0.2, 7.53), (11.5, 7.53), (11.5, 11.13), (-0.2, 11.13)], fill="white", w=1.3, close=False)
v4.path([(0, 8.03), (10, 8.03), (10, 10.63), (0, 10.63)], fill=BLADE, w=1.2)
v4.path([(13, 5.2), (25, 5.2), (25, 14.5), (13, 14.5)], w=1.4, dash="6 3")
v4.path([(15.2, 7.95), (22.24, 7.95), (22.24, 13.45), (15.2, 13.45)], fill=DARK, w=1.2)
v4.path([(13.4, 9.2), (15.2, 9.2), (15.2, 12.2), (13.4, 12.2)], fill="#7d8592", w=1)
px, py = v4.p(15.95, -1.1); text(px, py - 4, "RIVET FACE", 11.5, "middle")
px, py = v4.p(15.95, 16.9); text(px, py + 10, "LOGO FACE", 11.5, "middle")
for n, x, y, dx, dy in [("U1", 0.9, 0.9, -14, -12), ("U2", 31.0, 0.9, 12, -12), ("U3", 31.0, 14.9, 12, 14), ("U4", 0.9, 14.9, -14, 14),
                        ("U5", 15.95, 0, 6, -12), ("U6", 15.95, 15.8, 6, 16),
                        ("U7", 0, 7.53, -12, -4), ("U8", 11.5, 7.53, -6, -12), ("U9", 11.5, 11.13, -6, 16), ("U10", 0, 11.13, -12, 8),
                        ("U11", 10, 8.03, -8, 14), ("U12", 10, 10.63, -8, -6),
                        ("U13", 13, 5.2, -10, -8), ("U14", 25, 5.2, 8, -8), ("U15", 25, 14.5, 8, 12), ("U16", 13, 14.5, -10, 12),
                        ("U17", 15.2, 7.95, 6, -8), ("U18", 22.24, 7.95, 6, -8), ("U19", 22.24, 13.45, 6, 14), ("U20", 15.2, 13.45, 6, 16),
                        ("U21", 13.4, 9.2, -30, -24), ("U22", 13.4, 12.2, -30, 26)]:
    v4.v(n, x, y, dx, dy)
for n, x, y, dx, dy in [("u1", 8, 0, 0, 0), ("u2", 24, 0, 0, 0), ("u3", 31.9, 4, 0, 0), ("u4", 28.5, 15.8, 0, 0), ("u5", 6, 15.8, 0, 0),
                        ("u6", 0, 3.5, 0, 0), ("u7", 15.95, 2.6, 18, 0),
                        ("u8", 5.5, 7.53, 0, -12), ("u9", 11.5, 9.33, 0, 0), ("u10", 5.5, 11.13, 0, 12),
                        ("u11", 19, 5.2, 0, -12), ("u12", 25, 9.8, 0, 0), ("u13", 19.5, 14.5, 0, 11), ("u14", 13, 6.4, 0, 0),
                        ("u15", 18.7, 7.95, 0, 0), ("u16", 22.24, 10.7, 0, 0), ("u17", 18.7, 13.45, 0, 0), ("u18", 15.2, 8.7, 0, 0),
                        ("u19", 13.4, 10.7, 0, 0)]:
    v4.e(n, x, y, dx, dy)
v4.draw_labels()
px, py = v4.p(1, 20.8)
for i, s in enumerate(["dark = tab (hook = lighter, toward the blade) · dashed box = base",
                       "white channel = blade gap · grey = blade · dashed u7 = bottom centre line"]):
    text(px - 40, py + i * 16, s, 11)

# ======================= MEASUREMENT KEY =======================
M = [
    ("A", "31.40", "F2 – F4  width where the dome starts"),
    ("B", "31.90", "F1 – F5  width at the bottom corners"),
    ("C", "15.80", "u1 – u5  thickness (S2 – S3 at the widest)"),
    ("D", "21.34", "B3 → B6  dome tip to rivet-face centre"),
    ("E", "23.34", "F3 → F1/F5 level  dome tip to bottom corners"),
    ("F", "14.60*", "f7 → f10  base bottom to tab tip"),
    ("G", "39.04", "F3 → f10  dome tip to tab tip"),
    ("H", "7.04", "F11 – F16  tab width"),
    ("I", "9.00", "F12 – F13  tab width incl. hook"),
    ("J", None, "u6 → u18  blade-side edge to tab"),
    ("K", None, "u3 → u16  other edge to tab"),
    ("L", "5.50", "u15 – u17  tab thickness"),
    ("M", "7.95", "u1 → u15  rivet face to tab"),
    ("N", "39.12", "F5 → F18/F19 level  corner to blade tip"),
    ("O", "0.00", "f16 flush with f3  blade to blade-side edge"),
    ("P", "10.00", "F17 – f16  blade width"),
    ("Q", "2.60", "S13 – S14  blade thickness"),
    ("R", "8.03", "u1 → U11 line  rivet face to blade"),
    ("S", None, "F3 → F6  dome tip to logo-face centre"),
    ("T", "3.60", "u8 – u10  blade gap width"),
    ("U", None, "F6 → f7  logo-face centre to base bottom"),
    ("V", None, "U13 – U14  base width"),
    ("W", None, "U14 – U15  base thickness"),
    ("X", None, "u6 → U13  blade-side edge to base"),
    ("Y", None, "u1 → U13  rivet face to base"),
    ("Z", None, "u6 → u9  how deep the blade gap goes in"),
    ("—", None, "S7/S8 → F3 level  how far up the side the gap runs"),
]
ky = 840
text(760, ky, "Measurements as points and edges (check I've put each one in the right place)", 16, weight=700)
rows = 14
for i, (k, val, desc) in enumerate(M):
    col, row = divmod(i, rows)
    x = 760 + col * 545
    y = ky + 34 + row * 30
    c = OK if val else NEED
    add(f'<circle cx="{x + 11}" cy="{y - 4}" r="11" fill="white" stroke="{c}" stroke-width="2"/>'
        f'<text x="{x + 11}" y="{y + 0.5}" font-size="12.5" font-weight="700" text-anchor="middle" fill="{c}">{k}</text>')
    text(x + 30, y, desc, 13)
    text(x + 525, y, val or "?", 13, "end", 700, c)
ny = ky + 34 + rows * 30 + 10
for i, (s, c) in enumerate([
    ("* F: please confirm it was measured from the bottom of the base (edge f7), not from the head.", NEED),
    ("Anything without a label: describe it by the points/edges it sits between (e.g. \"a step on f6, 2 mm below F7\").", INK),
    ("Positions of the base, tab and blade gap that are still unmeasured are drawn where I currently guess they are.", INK),
]):
    text(760, ny + i * 20, s, 12.5, fill=c)
add("</svg>")

svg = "\n".join(out)
open(os.path.join(OUT, "mazda_key_head_blueprint.svg"), "w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, "mazda_key_head_blueprint.png"), output_width=W * 2)
print("ok")
