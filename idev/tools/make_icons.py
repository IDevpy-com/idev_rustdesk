#!/usr/bin/env python3
"""Generate Soporte iDev branding assets from the iDev logo.

Source: idev/branding/idev-logo-source.png (logo published at https://idevpy.com).
Requires Pillow. Run from the repository root:

    python idev/tools/make_icons.py

Generated files are committed, so the CI build does not need Pillow.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "idev", "branding", "idev-logo-source.png")
OUT_BRANDING = os.path.join(ROOT, "idev", "branding")

ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def p(*parts):
    return os.path.join(ROOT, *parts)


def load_logo():
    logo = Image.open(SRC).convert("RGBA")
    return logo.crop(logo.getbbox())


def symbol_mark(logo):
    # The "</>" mark is the blue part on the left; the wordmark starts after a
    # fully transparent column gap.
    alpha = logo.getchannel("A")
    w, h = logo.size
    x_end = None
    for x in range(w // 10, w):
        if alpha.crop((x, 0, x + 1, h)).getbbox() is None:
            x_end = x
            break
    mark = logo.crop((0, 0, x_end or w // 3, h))
    return mark.crop(mark.getbbox())


def rounded_icon(mark, size):
    scale = 4  # supersample for smooth edges
    s = size * scale
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    radius = int(s * 0.22)
    draw.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius, fill=(255, 255, 255, 255),
                           outline=(26, 93, 159, 255), width=max(scale, int(s * 0.02)))
    pad = 0.14 if size >= 32 else 0.08
    max_w = int(s * (1 - 2 * pad))
    ratio = max_w / mark.width
    m = mark.resize((max_w, int(mark.height * ratio)), Image.LANCZOS)
    canvas.alpha_composite(m, ((s - m.width) // 2, (s - m.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def save_ico(mark, path, sizes):
    images = [rounded_icon(mark, w) for (w, _) in sizes]
    images[-1].save(path, format="ICO", sizes=sizes, append_images=images[:-1])
    print("wrote", path)


def recolor_dark_pixels(logo, rgb):
    # Wordmark is black; turn it white for dark theme, keep the blue mark.
    px = logo.load()
    out = logo.copy()
    po = out.load()
    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) < 90:
                po[x, y] = (*rgb, a)
    return out


def fit(img, max_w, max_h):
    ratio = min(max_w / img.width, max_h / img.height)
    return img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)


def loading_label(path):
    # Replaces libs/portable/src/res/label.png ("Loading...", 96x32, white text).
    w, h = 96, 32
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = None
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(name, 17)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    draw.text((2, h // 2), "Cargando...", font=font, fill=(255, 255, 255, 255), anchor="lm")
    img.save(path)
    print("wrote", path)


def main():
    logo = load_logo()
    mark = symbol_mark(logo)

    # Windows icons: exe/window (Flutter runner), dll + portable packer, tray.
    save_ico(mark, p("flutter", "windows", "runner", "resources", "app_icon.ico"), ICO_SIZES)
    save_ico(mark, p("res", "icon.ico"), ICO_SIZES)
    save_ico(mark, p("res", "tray-icon.ico"), [(16, 16), (24, 24), (32, 32), (48, 48)])
    # Copy used at runtime by the installer for shortcuts (custom client icon).
    save_ico(mark, p("flutter", "assets", "icon.ico"), ICO_SIZES)

    # PNG icons: Flutter in-app icon + tray (assets/icon.png), launcher source.
    rounded_icon(mark, 256).save(p("flutter", "assets", "icon.png"))
    rounded_icon(mark, 1024).save(p("res", "icon.png"))
    for sz, name in ((32, "32x32.png"), (64, "64x64.png"), (128, "128x128.png"), (256, "128x128@2x.png")):
        rounded_icon(mark, sz).save(p("res", name))

    # Home page logo (max 300x60 shown); 2x resolution for HiDPI.
    light = fit(logo, 600, 120)
    light.save(p("flutter", "assets", "logo.png"))
    light.save(p("flutter", "assets", "logo_light.png"))
    fit(recolor_dark_pixels(logo, (255, 255, 255)), 600, 120).save(p("flutter", "assets", "logo_dark.png"))

    loading_label(p("libs", "portable", "src", "res", "label.png"))

    # Preview copies for documentation.
    rounded_icon(mark, 256).save(os.path.join(OUT_BRANDING, "soporte-idev-icon-256.png"))
    print("done")


if __name__ == "__main__":
    sys.exit(main())
