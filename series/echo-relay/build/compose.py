"""Compose 1080x1920 9:16 stills for ECHO RELAY EP01 from 1184x896 boards.

Blur-fill the landscape boards into a vertical frame, feather the edges,
and render the title card. Output: ../stills/s01.png .. s11.png
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "boards" / "src"
OUT = HERE.parent / "stills"
OUT.mkdir(exist_ok=True)

W, H = 1080, 1920
FONT_BOLD = None
import matplotlib
FONT_DIR = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"
FONT_BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
FONT_REG = str(FONT_DIR / "DejaVuSans.ttf")

BOARDS = [f"f{i:02d}.jpg" for i in range(1, 11)]

# caption lines use \\n for two-line wraps
CAPTIONS = {
    1: "THIS STATION RELAYS\nEVERY SIGNAL PAST SATURN",
    2: "ONE CREW.  HER.",
    3: "TONIGHT ONE SIGNAL STOPS",
    4: "A DISTRESS BEACON",
    5: "BUT IT KNOWS HER NAME",
    6: "LOGGED: FOURTEEN DAYS FROM NOW",
    7: "THE VOICE IS HERS",
    8: '"DO NOT OPEN THE AIRLOCK"',
    9: "SHE HAS A CHOICE",
    10: "THE COUNTDOWN IS ON",
}


def feather_mask(w, h, feather=110):
    m = np.ones((h, w), dtype=np.float32)
    ramp = np.linspace(0.0, 1.0, feather, dtype=np.float32)
    m[:feather, :] *= ramp[:, None]
    m[-feather:, :] *= ramp[::-1][:, None]
    return Image.fromarray((m * 255).astype(np.uint8), "L")


def blur_fill(img):
    bg = img.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(38))
    bg = Image.eval(bg, lambda px: int(px * 0.45))
    sharp_w = W
    sharp_h = int(img.height * W / img.width)
    sharp = img.resize((sharp_w, sharp_h), Image.LANCZOS)
    top = (H - sharp_h) // 2 - 60
    mask = feather_mask(sharp_w, sharp_h)
    bg.paste(sharp, (0, top), mask)
    return bg


def add_caption(frame, text):
    d = ImageDraw.Draw(frame)
    font = ImageFont.truetype(FONT_BOLD, 58)
    lines = text.split("\n")
    widths = [d.textlength(line, font=font) for line in lines]
    line_h = 74
    total_h = line_h * len(lines)
    y0 = int(H * 0.855) - total_h // 2
    # soft shadow plate
    for i, line in enumerate(lines):
        w = widths[i]
        x = (W - w) / 2
        y = y0 + i * line_h
        for dx, dy, blur in ((4, 5, 10), (3, 4, 6), (2, 3, 3), (1, 2, 0)):
            d.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        d.text((x, y), line, font=font, fill=(255, 255, 255))
    return frame


def title_card():
    base = Image.open(SRC / "f10.jpg")
    frame = blur_fill(base)
    frame = Image.eval(frame, lambda px: int(px * 0.30))
    d = ImageDraw.Draw(frame)
    f_main = ImageFont.truetype(FONT_BOLD, 150)
    f_sub = ImageFont.truetype(FONT_REG, 52)
    f_ep = ImageFont.truetype(FONT_BOLD, 64)

    t = "ECHO RELAY"
    w = d.textlength(t, font=f_main)
    d.text(((W - w) / 2 + 5, 700 + 5), t, font=f_main, fill=(0, 0, 0))
    d.text(((W - w) / 2, 700), t, font=f_main, fill=(235, 240, 255))

    t2 = "EPISODE 1"
    w = d.textlength(t2, font=f_ep)
    d.text(((W - w) / 2, 910), t2, font=f_ep, fill=(255, 190, 90))

    t3 = "THE VOICE THAT CALLED AHEAD"
    w = d.textlength(t3, font=f_sub)
    d.text(((W - w) / 2, 1010), t3, font=f_sub, fill=(190, 200, 220))
    return frame


def main():
    for i, name in enumerate(BOARDS, start=1):
        img = Image.open(SRC / name).convert("RGB")
        frame = blur_fill(img)
        if i in CAPTIONS:
            frame = add_caption(frame, CAPTIONS[i])
        frame.save(OUT / f"s{i:02d}.png")
        print(f"s{i:02d}.png")
    title_card().save(OUT / "s11.png")
    print("s11.png")


if __name__ == "__main__":
    main()
