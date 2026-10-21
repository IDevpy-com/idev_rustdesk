#!/usr/bin/env python3
"""Generate the Soporte iDev macOS branding assets from the iDev logo.

Complements make_icons.py (Windows/Flutter assets), which is left untouched so
the Windows icons stay byte-identical. Requires Pillow. Run from the repository
root:

    python idev/tools/make_macos_icons.py

Generated files are committed, so the CI build does not need Pillow.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_icons import OUT_BRANDING, load_logo, p, symbol_mark  # noqa: E402

# Sizes stored in the .icns (Pillow writes the ic07..ic14 PNG entries).
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def mac_icon(mark, size):
    # macOS app icon grid: 824/1024 rounded square centered on a transparent
    # canvas, with a soft shadow, as Apple's templates since Big Sur.
    scale = 4  # supersample for smooth edges
    s = size * scale
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    body = int(s * 824 / 1024)
    off = (s - body) // 2
    radius = int(body * 0.2237)

    shadow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (off, off + int(s * 0.012), off + body, off + body + int(s * 0.012)),
        radius=radius, fill=(0, 0, 0, 70))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(s * 0.012)))

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((off, off, off + body - 1, off + body - 1), radius=radius,
                           fill=(255, 255, 255, 255), outline=(26, 93, 159, 255),
                           width=max(scale, int(body * 0.012)))
    max_w = int(body * 0.72)
    m = mark.resize((max_w, int(mark.height * max_w / mark.width)), Image.LANCZOS)
    canvas.alpha_composite(m, ((s - m.width) // 2, (s - m.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def tray_template(mark, size, mode):
    # Menu bar icon, used by tray.rs as a template image: only alpha matters.
    pad = int(size * 0.08)
    w = size - 2 * pad
    m = mark.resize((w, int(mark.height * w / mark.width)), Image.LANCZOS)
    alpha = Image.new("L", (size, size), 0)
    alpha.paste(m.getchannel("A"), (pad, (size - m.height) // 2))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.putalpha(alpha)
    return img.convert(mode) if mode != "RGBA" else img


def main():
    mark = symbol_mark(load_logo())

    icon = mac_icon(mark, 1024)
    icns = p("flutter", "macos", "Runner", "AppIcon.icns")
    icon.save(icns, format="ICNS",
              append_images=[mac_icon(mark, sz) for sz in ICNS_SIZES if sz != 1024])
    print("wrote", icns)
    icon.save(p("res", "mac-icon.png"))
    print("wrote", p("res", "mac-icon.png"))

    tray_template(mark, 60, "RGBA").save(p("res", "mac-tray-dark-x2.png"))
    tray_template(mark, 48, "LA").save(p("res", "mac-tray-light-x2.png"))
    print("wrote res/mac-tray-*.png")

    mac_icon(mark, 512).save(os.path.join(OUT_BRANDING, "soporte-idev-macos-icon-512.png"))
    print("done")


if __name__ == "__main__":
    sys.exit(main())
