"""
Workshop builder — scans every subfolder for a request.yaml and generates QR codes.

Usage:
  python build.py                  # process all requests
  python build.py my-project       # process one specific request folder
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("Missing dependency: pip install pyyaml")

from qr_generator import make_qr, build_png, build_svg

ROOT = Path(__file__).parent
TEMPLATE_DIR = ROOT / "request-template"


def load_request(folder: Path) -> dict | None:
    req_file = folder / "request.yaml"
    if not req_file.exists():
        return None
    with req_file.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def process(folder: Path):
    cfg = load_request(folder)
    if cfg is None:
        return

    data = cfg.get("data", "").strip()
    if not data:
        print(f"[SKIP] {folder.name}: 'data' is empty")
        return

    name        = cfg.get("name", folder.name)
    fill        = cfg.get("fill", "#000000")
    back        = cfg.get("back", "#FFFFFF")
    shape       = cfg.get("shape", "square")
    logo_rel    = cfg.get("logo")
    logo_ratio  = float(cfg.get("logo_size_ratio", 0.20))

    logo_path = None
    if logo_rel:
        logo_path = folder / "input" / logo_rel
        if not logo_path.exists():
            raise SystemExit(f"[ERROR] {folder.name}: logo not found at {logo_path}")

    outdir = folder / "output"
    outdir.mkdir(parents=True, exist_ok=True)

    qr = make_qr(data)
    build_png(qr, outdir / (name + ".png"), fill, back, shape, logo_path, logo_ratio)
    build_svg(qr, outdir / (name + ".svg"), fill, back, logo_path, logo_ratio)

    print(f"[OK] {folder.name} → {outdir.relative_to(ROOT)}/")


def main():
    targets = sys.argv[1:]

    if targets:
        folders = [ROOT / t for t in targets]
    else:
        # All subfolders except the template and hidden dirs
        folders = [
            p for p in ROOT.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and p != TEMPLATE_DIR
        ]

    if not folders:
        print("No request folders found.")
        return

    for folder in sorted(folders):
        try:
            process(folder)
        except Exception as e:
            print(f"[ERROR] {folder.name}: {e}")


if __name__ == "__main__":
    main()
