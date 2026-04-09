"""
Batch QR generator — scans subfolders for request.yaml and generates QR codes.

Usage:
  python build.py                  # process all
  python build.py my-project       # process one
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


def process(folder: Path):
    req_file = folder / "request.yaml"
    if not req_file.exists():
        return
    cfg = yaml.safe_load(req_file.read_text(encoding="utf-8"))

    data = cfg.get("data", "").strip()
    if not data:
        print(f"[SKIP] {folder.name}: 'data' is empty")
        return

    logo_rel = cfg.get("logo")
    logo = folder / "input" / logo_rel if logo_rel else None
    if logo and not logo.exists():
        raise SystemExit(f"[ERROR] {folder.name}: logo not found at {logo}")

    outdir = folder / "output"
    outdir.mkdir(parents=True, exist_ok=True)

    fill, back, name = cfg.get("fill", "#000000"), cfg.get("back", "#FFFFFF"), cfg.get("name", folder.name)
    logo_ratio = float(cfg.get("logo_size_ratio", 0.20))
    qr = make_qr(data)

    build_png(qr, outdir / f"{name}.png", fill, back, cfg.get("shape", "square"), logo, logo_ratio)
    build_svg(qr, outdir / f"{name}.svg", fill, back, logo, logo_ratio)
    print(f"[OK] {folder.name} → {outdir.relative_to(ROOT)}/")


def main():
    folders = [ROOT / t for t in sys.argv[1:]] or sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p != TEMPLATE_DIR
    )
    if not folders:
        print("No request folders found.")
        return
    for folder in folders:
        try:
            process(folder)
        except Exception as e:
            print(f"[ERROR] {folder.name}: {e}")


if __name__ == "__main__":
    main()
