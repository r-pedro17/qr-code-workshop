import argparse
import base64
import re
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, GappedSquareModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.svg import SvgPathImage

DRAWERS = {
    "square": SquareModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "gapped": GappedSquareModuleDrawer,
    "circle": CircleModuleDrawer,
}

def parse_hex_color(value):
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError("Use 6-digit hex colors, for example: #000000")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def make_qr(data):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr

def build_png(qr, output, fill, back, shape, logo, logo_ratio):
    color_mask = SolidFillColorMask(
        front_color=parse_hex_color(fill),
        back_color=parse_hex_color(back),
    )
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=DRAWERS[shape](),
        color_mask=color_mask,
    ).convert("RGBA")

    if logo:
        logo_img = Image.open(logo).convert("RGBA")
        side = int(min(img.size) * logo_ratio)
        logo_img.thumbnail((side, side))
        x = (img.width - logo_img.width) // 2
        y = (img.height - logo_img.height) // 2
        img.paste(logo_img, (x, y), logo_img)

    img.save(output, format="PNG")

def build_svg(qr, output, fill, back, logo=None, logo_ratio=0.20):
    raw = qr.make_image(image_factory=SvgPathImage).to_string()
    svg = raw.decode("utf-8") if isinstance(raw, bytes) else raw

    svg = re.sub(r'fill="(black|#000000)"', f'fill="{fill}"', svg)

    # Parse viewBox to get dimensions
    vb = re.search(r'viewBox="([^"]+)"', svg)
    if vb:
        parts = vb.group(1).split()
        vb_w, vb_h = float(parts[2]), float(parts[3])
    else:
        vb_w, vb_h = 54.0, 54.0

    # Insert background rect (always, so white is explicit)
    insert = '<rect width="100%%" height="100%%" fill="%s"/>' % back
    svg = svg.replace(">", ">\n" + insert, 1)

    # Embed logo as base64 image centered in SVG
    if logo:
        img = Image.open(logo).convert("RGBA")
        # Resize to a good pixel resolution for quality (independent of viewBox units)
        px_size = 400
        img.thumbnail((px_size, px_size))
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        # Display size and position in viewBox units — fit within side_svg × side_svg
        side_svg = min(vb_w, vb_h) * logo_ratio
        if img.width >= img.height:
            w_svg = side_svg
            h_svg = side_svg * (img.height / img.width)
        else:
            h_svg = side_svg
            w_svg = side_svg * (img.width / img.height)
        x = (vb_w - w_svg) / 2
        y = (vb_h - h_svg) / 2
        img_tag = '<image x="%g" y="%g" width="%g" height="%g" href="data:image/png;base64,%s"/>' % (
            x, y, w_svg, h_svg, b64)
        svg = svg.replace("</svg>", img_tag + "\n</svg>")

    output.write_text(svg, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Generate a styled QR code in PNG and SVG.")
    parser.add_argument("--data", required=True, help="Text or URL to encode")
    parser.add_argument("--name", default="qr_code", help="Base output name, without extension")
    parser.add_argument("--outdir", default=".", help="Output directory")
    parser.add_argument("--fill", default="#000000", help="QR foreground color in hex")
    parser.add_argument("--back", default="#FFFFFF", help="Background color in hex")
    parser.add_argument("--shape", choices=sorted(DRAWERS.keys()), default="square", help="PNG module style")
    parser.add_argument("--logo", help="Path to logo image for PNG")
    parser.add_argument("--logo-size-ratio", type=float, default=0.20, help="Logo size ratio, e.g. 0.20")
    args = parser.parse_args()

    if not 0.05 <= args.logo_size_ratio <= 0.30:
        raise SystemExit("--logo-size-ratio must be between 0.05 and 0.30")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    qr = make_qr(args.data)
    png_path = outdir / (args.name + ".png")
    svg_path = outdir / (args.name + ".svg")

    build_png(qr, png_path, args.fill, args.back, args.shape, args.logo, args.logo_size_ratio)
    build_svg(qr, svg_path, args.fill, args.back, args.logo, args.logo_size_ratio)

    print("Saved:", png_path)
    print("Saved:", svg_path)

if __name__ == "__main__":
    main()
