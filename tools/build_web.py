"""Write prints.json for the portfolio, and check the files it points at.

    python tools/build_web.py            # check, then write prints.json
    python tools/build_web.py --fix      # also decimate any web GLB that is over budget
    python tools/build_web.py --check    # check only, write nothing (what CI runs first)

prints.json is the whole contract between this repository and the portfolio site: the site
fetches it at load, so a push here shows up there without a redeploy. Nothing else on the site
reads this repo.

Per print, the text comes from that print's README.md -- its H1 is the title, the first
paragraph is the description, and the "Status:" line is the status -- so there is one place to
edit prose. meta.json holds only what prose cannot carry: the order prints appear in, and which
render and model to lead with.

Checks, with reasons:
  - every web GLB is at or under GLB_BUDGET. A page that has to pull 6 MB before it can draw
    anything feels broken on a phone. --fix decimates in place (needs trimesh).
  - no file is anywhere near FILE_WARN. GitHub refuses a push over 100 MB per file and warns
    at 50; releases are the answer for anything that big, not the repository.
  - nothing published is tracked by git-lfs. raw.githubusercontent and jsDelivr serve the LFS
    pointer text, not the file, so an LFS'd model is a silently broken model on the web.
  - every path meta.json names exists.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRINTS = os.path.join(ROOT, "prints")
OUT = os.path.join(ROOT, "prints.json")

REPO = "mehdiacho/3d-prints"
BRANCH = "main"
RAW = "https://raw.githubusercontent.com/%s/%s/" % (REPO, BRANCH)

GLB_BUDGET = 2_000_000          # bytes, per model on the web
GLB_TARGET_FACES = 40_000       # what --fix decimates down to
FILE_WARN = 40_000_000          # bytes; GitHub warns at 50 MB and refuses at 100 MB

RENDER_EXT = (".webp", ".png", ".jpg", ".jpeg")
PAGE_TITLES = {                 # a nicer name than the file stem, where the stem is terse
    "blueprint": "Blueprint",
    "simulation": "Fill simulation",
    "part-sheet": "Part sheet",
    "sheet-01-print": "Sheet 01, for paper",
}

problems, notes = [], []


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def git(*args):
    try:
        return subprocess.run(("git",) + args, cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def strip_markdown(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)      # links keep their text
    s = re.sub(r"[*_`]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def read_readme(folder, slug):
    """title, status and description out of the print's README."""
    path = os.path.join(folder, "README.md")
    if not os.path.exists(path):
        problems.append("%s: no README.md" % slug)
        return slug, "", ""
    text = open(path, encoding="utf-8").read()

    m = re.search(r"^#\s+(.+)$", text, re.M)
    title = m.group(1).strip() if m else slug
    if not m:
        problems.append("%s: README.md has no '# ' heading to take a title from" % slug)

    # the first paragraph after the H1 that is prose: not an image, a heading or a bold-only line
    body = text[m.end():] if m else text
    description = ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para or para[:1] in "#!|-*>`":
            continue
        if para.startswith("**") and para.endswith("**"):
            continue
        description = re.sub(r"\s+", " ", para)
        break
    if not description:
        problems.append("%s: README.md has no description paragraph" % slug)

    m = re.search(r"\*\*Status:?\s*(.+?)\*\*", text, re.S)
    status = re.sub(r"\s+", " ", m.group(1)).strip(" .") if m else ""
    if not status:
        problems.append("%s: README.md has no '**Status: ...**' line" % slug)

    return title, status, description


def lfs_paths():
    out = git("lfs", "ls-files", "-n")
    return {p.strip() for p in out.splitlines() if p.strip()}


def fix_glb(path):
    """Decimate a GLB that is over budget, in place. Returns the new size, or None."""
    try:
        import trimesh
    except ImportError:
        problems.append("%s: over the GLB budget and trimesh is not installed, so --fix cannot "
                        "decimate it (pip install trimesh fast_simplification)" % rel(path))
        return None
    scene = trimesh.load(path)
    geoms = getattr(scene, "geometry", None)
    if not geoms:
        problems.append("%s: over budget and holds no mesh to decimate" % rel(path))
        return None
    total = sum(len(g.faces) for g in geoms.values())
    if total <= GLB_TARGET_FACES:
        problems.append("%s: over budget at only %d faces -- decimating will not help, look at "
                        "what else is in the file (textures?)" % (rel(path), total))
        return None
    out = trimesh.Scene()
    for name, g in geoms.items():
        share = max(500, int(GLB_TARGET_FACES * len(g.faces) / total))
        out.add_geometry(g.simplify_quadric_decimation(face_count=share), node_name=name)
    data = out.export(file_type="glb")
    open(path, "wb").write(data)
    notes.append("%s: decimated %d faces -> about %d, %.2f MB"
                 % (rel(path), total, GLB_TARGET_FACES, len(data) / 1e6))
    return len(data)


def collect(slug, fix):
    folder = os.path.join(PRINTS, slug)
    meta_path = os.path.join(folder, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8"))
    else:
        meta = {}
        problems.append("%s: no meta.json" % slug)

    title, status, description = read_readme(folder, slug)

    # pages: every html in the print's own folder, blueprint first
    pages = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        stem = name[:-5]
        pages.append({"title": PAGE_TITLES.get(stem, stem.replace("-", " ").capitalize()),
                      "path": "prints/%s/%s" % (slug, name)})
    pages.sort(key=lambda p: (not p["path"].endswith("/blueprint.html"), p["title"]))
    blueprint = next((p["path"] for p in pages if p["path"].endswith("/blueprint.html")), None)
    if not blueprint:
        notes.append("%s: no blueprint.html" % slug)

    # models on the web, checked against the budget
    models = []
    web = os.path.join(folder, "web")
    for name in sorted(os.listdir(web)) if os.path.isdir(web) else []:
        if not name.endswith(".glb"):
            continue
        path = os.path.join(web, name)
        size = os.path.getsize(path)
        if size > GLB_BUDGET:
            new = fix_glb(path) if fix else None
            if new is None:
                problems.append("prints/%s/web/%s: %.2f MB, over the %.1f MB web budget -- run "
                                "with --fix" % (slug, name, size / 1e6, GLB_BUDGET / 1e6))
            else:
                size = new
        models.append({"name": name[:-4], "path": "prints/%s/web/%s" % (slug, name),
                       "bytes": size})

    # printable and reference geometry, counted rather than listed: the site does not serve these
    models_dir = os.path.join(folder, "models")
    stl = sum(1 for r, _, fs in os.walk(models_dir) for f in fs
              if f.endswith(".stl")) if os.path.isdir(models_dir) else 0

    hero = meta.get("hero")
    if hero is None:
        renders = os.path.join(folder, "renders")
        hero = next(("prints/%s/renders/%s" % (slug, n) for n in sorted(os.listdir(renders))
                     if n.lower().endswith(RENDER_EXT) and not n.startswith("sheet-")),
                    None) if os.path.isdir(renders) else None
    elif not os.path.exists(os.path.join(folder, hero)):
        problems.append("%s: meta.json hero '%s' does not exist" % (slug, hero))
        hero = None
    else:
        hero = "prints/%s/%s" % (slug, hero)

    model = meta.get("model")
    if model is not None:
        if not os.path.exists(os.path.join(folder, model)):
            problems.append("%s: meta.json model '%s' does not exist" % (slug, model))
            model = None
        else:
            model = "prints/%s/%s" % (slug, model)
    elif models:
        model = models[0]["path"]

    return {
        "slug": slug,
        "order": meta.get("order", 99),
        "title": strip_markdown(title),
        "status": strip_markdown(status),
        "description": strip_markdown(description),
        "updated": git("log", "-1", "--format=%cI", "--", "prints/%s" % slug) or None,
        "thumbnail": hero,
        "model": model,
        "models": models,
        "blueprint": blueprint,
        "pages": pages,
        "stl_count": stl,
        "readme": "prints/%s/README.md" % slug,
    }


def main():
    fix = "--fix" in sys.argv
    check_only = "--check" in sys.argv

    slugs = sorted(d for d in os.listdir(PRINTS) if os.path.isdir(os.path.join(PRINTS, d)))
    prints = sorted((collect(s, fix) for s in slugs), key=lambda p: (p["order"], p["slug"]))

    # repository-wide checks
    lfs = lfs_paths()
    for r, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", ".github", "tools")]
        for f in files:
            p = os.path.join(r, f)
            if os.path.getsize(p) > FILE_WARN:
                problems.append("%s: %.1f MB -- GitHub warns at 50 MB and refuses at 100. Put "
                                "it in a release instead." % (rel(p), os.path.getsize(p) / 1e6))
            if rel(p) in lfs:
                problems.append("%s: tracked by git-lfs. raw.githubusercontent and jsDelivr "
                                "serve the pointer, not the file. Untrack it." % rel(p))

    doc = {
        "generated": git("log", "-1", "--format=%cI") or None,
        "repo": REPO,
        "base": RAW,
        "jsdelivr": "https://cdn.jsdelivr.net/gh/%s@%s/" % (REPO, BRANCH),
        "count": len(prints),
        "prints": prints,
    }

    for n in notes:
        print("note:", n)
    for p in problems:
        print("PROBLEM:", p)

    if problems:
        print("\n%d problem(s). prints.json not written." % len(problems))
        return 1

    if check_only:
        print("ok: %d prints, nothing written (--check)" % len(prints))
        return 0

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("ok: %d prints -> %s" % (len(prints), rel(OUT)))
    for p in prints:
        print("  %d. %-16s %-38s %d glb, %d stl"
              % (p["order"], p["slug"], p["status"] or "-", len(p["models"]), p["stl_count"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
