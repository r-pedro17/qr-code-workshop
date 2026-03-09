Install:
pip install -r requirements.txt

Example:
python qr_generator.py --data "https://example.com" --name my_qr --fill "#1D4ED8" --back "#FFFFFF" --shape rounded

With logo:
python qr_generator.py --data "https://example.com" --name my_qr --logo my_logo.png --logo-size-ratio 0.18

Notes:
- PNG supports styling and logo embedding.
- SVG is exported as a clean vector file with color support.
- Logo embedding is limited to PNG to keep the code lean and reliable.
