# QR Code Workshop

Batch-generate branded QR codes (PNG + SVG). Each request is a self-contained folder.

## Project structure

```
root/
├── build.py              # Workshop runner — processes all request folders
├── qr_generator.py       # Core generator (PNG + SVG)
├── requirements.txt
├── request-template/     # Copy this to start a new request
│   ├── request.yaml      # Fill in your QR params here
│   ├── input/            # Drop logos/assets here
│   └── output/           # Generated files land here (gitignored)
└── my-project/           # Example request folder (same structure)
```

## Install

```
pip install -r requirements.txt
```

## Workflow

1. Copy `request-template/` and rename it (e.g. `my-brand/`)
2. Edit `my-brand/request.yaml`
3. Drop any logo into `my-brand/input/`
4. Run: `python build.py my-brand` (or `python build.py` to process all)
5. Outputs appear in `my-brand/output/`

## request.yaml fields

| Field | Default | Notes |
|---|---|---|
| `data` | required | URL or text to encode |
| `name` | folder name | Output filename (no extension) |
| `fill` | `#000000` | Module/foreground color |
| `back` | `#FFFFFF` | Background color |
| `shape` | `square` | `square` / `rounded` / `gapped` / `circle` |
| `logo` | null | Filename inside `input/`, e.g. `logo.png` |
| `logo_size_ratio` | `0.20` | `0.05`–`0.30` |

## Single QR (no batch)

```bash
python qr_generator.py --data "https://example.com" --name my_qr --fill "#1D4ED8" --back "#FFFFFF" --shape rounded

# With logo
python qr_generator.py --data "https://example.com" --name my_qr --logo my_logo.png --logo-size-ratio 0.18
```

## Notes

- PNG supports styling and logo embedding.
- SVG is exported as a clean vector file with color support.
- `*/output/` is gitignored — generated files are never committed.
