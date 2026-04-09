import argparse
import base64
import re
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    CircleModuleDrawer, GappedSquareModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer,
)
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.svg import SvgPathImage

DRAWERS = {
    "square": SquareModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "gapped": GappedSquareModuleDrawer,
    "circle": CircleModuleDrawer,
}


def parse_hex(value):
    v = value.lstrip("#")
    if len(v) != 6:
        raise ValueError(f"Invalid color: {value}")
    return tuple(int(v[i:i+2], 16) for i in (0, 2, 4))


def make_qr(data):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return qr


def build_png(qr, output, fill, back, shape, logo=None, logo_ratio=0.20):
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=DRAWERS[shape](),
        color_mask=SolidFillColorMask(front_color=parse_hex(fill), back_color=parse_hex(back)),
    ).convert("RGBA")

    if logo:
        logo_img = Image.open(logo).convert("RGBA")
        side = int(min(img.size) * logo_ratio)
        logo_img.thumbnail((side, side))
        img.paste(logo_img, ((img.width - logo_img.width) // 2, (img.height - logo_img.height) // 2), logo_img)

    img.save(output, format="PNG")


def build_svg(qr, output, fill, back, logo=None, logo_ratio=0.20):
    raw = qr.make_image(image_factory=SvgPathImage).to_string()
    svg = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    svg = re.sub(r'fill="(black|#000000)"', f'fill="{fill}"', svg)

    vb = re.search(r'viewBox="([^"]+)"', svg)
    vb_w, vb_h = (float(x) for x in vb.group(1).split()[2:4]) if vb else (54.0, 54.0)

    svg = svg.replace(">", f'>\n<rect width="100%" height="100%" fill="{back}"/>', 1)

    if logo:
        img = Image.open(logo).convert("RGBA")
        img.thumbnail((400, 400))
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        scale = min(vb_w, vb_h) * logo_ratio / max(img.width, img.height)
        w, h = img.width * scale, img.height * scale
        x, y = (vb_w - w) / 2, (vb_h - h) / 2
        img_tag = f'<image x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" href="data:image/png;base64,{b64}"/>'
        svg = svg.replace("</svg>", img_tag + "\n</svg>")

    output.write_text(svg, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Generate a styled QR code in PNG and SVG.")
    p.add_argument("--data", required=True)
    p.add_argument("--name", default="qr_code")
    p.add_argument("--outdir", default=".")
    p.add_argument("--fill", default="#000000")
    p.add_argument("--back", default="#FFFFFF")
    p.add_argument("--shape", choices=sorted(DRAWERS.keys()), default="square")
    p.add_argument("--logo")
    p.add_argument("--logo-size-ratio", type=float, default=0.20)
    args = p.parse_args()

    if not 0.05 <= args.logo_size_ratio <= 0.30:
        raise SystemExit("--logo-size-ratio must be between 0.05 and 0.30")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    qr = make_qr(args.data)
    stem = outdir / args.name

    build_png(qr, stem.with_suffix(".png"), args.fill, args.back, args.shape, args.logo, args.logo_size_ratio)
    build_svg(qr, stem.with_suffix(".svg"), args.fill, args.back, args.logo, args.logo_size_ratio)
    print(f"Saved: {stem}.png  {stem}.svg")


if __name__ == "__main__":
    main()
