# QR Code Workshop

Batch QR code generator. Each request is a folder with a `request.yaml` + optional logo in `input/`.

- `qr_generator.py` — single QR via CLI
- `build.py` — batch runner, processes all request folders
- `request-template/` — copy this to start a new request
- `*/output/` is gitignored; never commit generated files
