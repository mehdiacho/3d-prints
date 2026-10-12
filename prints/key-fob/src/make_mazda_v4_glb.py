"""GLBs of the v4 body for the blueprint page's 3D views.

    python make_mazda_v4_glb.py <cover.stl> <out folder>

Writes <out>/body-v4.glb.b64.txt and <out>/fit-test-v4.glb.b64.txt: base64 text rather than
binary, because the page these were written for could not serve .glb. Both show the two halves
8 mm apart so you can see into the sockets.

The cover STL is a downloaded TPU fob cover of unrecorded origin and is NOT in this repo —
see the README. Without it this script cannot run, and the 3D views on the published page show
"3D VIEW UNAVAILABLE" instead. The 2D sheets are complete without it.
"""
import sys, os, base64, importlib.util
import numpy as np, trimesh

COVER = sys.argv[1] if len(sys.argv) > 1 else "Mazda_5_Fob_Cover.stl"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
HERE = os.path.dirname(os.path.abspath(__file__))

sys.argv = ["b4", COVER, OUT]
spec = importlib.util.spec_from_file_location("b4", os.path.join(HERE, "build_mazda_body_v4.py"))
b4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b4)


def three(m, dy=0.0):
    """corrected model frame (X = x, Y = y, Z = -z) -> three.js (X, Z up, -Y); mm -> m. A proper rotation, not a mirror."""
    t = b4.to_mesh(m)
    parts = [p for p in t.split(only_watertight=False) if abs(p.volume) > 1.0]
    t = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    v = t.vertices
    return trimesh.Trimesh(np.c_[v[:, 0], v[:, 2], -(v[:, 1] + dy)] / 1000.0, t.faces, process=False)


def glb(meshes, name):
    sc = trimesh.Scene()
    for i, m in enumerate(meshes):
        sc.add_geometry(m, node_name=f"part{i}")
    data = sc.export(file_type="glb")
    with open(os.path.join(OUT, f"{name}.glb.b64.txt"), "w") as f:
        f.write(base64.b64encode(data).decode())
    print(name, len(data), "bytes glb")


whole = b4.build(0.25, 0.0, 2)
fixed = b4.fix_handedness(whole)
r, l = b4.halves(fixed)
glb([three(r), three(l, 8.0)], "body-v4")
fit = b4.fix_handedness(whole ^ b4.box(-5, 40, -5, 25, 0, b4.FIT_TEST_Z))
fr, fl = b4.halves(fit)
glb([three(fr), three(fl, 8.0)], "fit-test-v4")
