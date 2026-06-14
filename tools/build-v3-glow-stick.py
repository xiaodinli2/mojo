#!/usr/bin/env python3
"""Add a concert glow stick accent to the Codex MOJO Carrot spritesheet.

The input is the v2 Codex spritesheet. The output keeps the same 8 x 9 layout
and only adds a small glow-stick overlay to selected expressive rows.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


CELL_W = 192
CELL_H = 208
COLS = 8
ROWS = [
    "idle",
    "right",
    "left",
    "wave",
    "jump",
    "fail",
    "wait",
    "run",
    "review",
]

GLOW_ROWS = {
    "wave": "handheld",
    "jump": "side-pop",
    "run": "trail",
    "review": "small-side",
}


def checkerboard(size: tuple[int, int], tile: int = 16) -> Image.Image:
    out = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2 == 0:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=(238, 238, 238, 255))
    return out


def glow_line(size: tuple[int, int], start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int], width: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line([start, end], fill=(*color, 80), width=width + 14)
    gd.line([start, end], fill=(*color, 120), width=width + 8)
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    layer.alpha_composite(glow)

    d = ImageDraw.Draw(layer)
    d.line([start, end], fill=(*color, 235), width=width)
    d.line([start, end], fill=(240, 255, 255, 220), width=max(1, width // 3))
    for point in (start, end):
        x, y = point
        d.ellipse((x - width * 0.7, y - width * 0.7, x + width * 0.7, y + width * 0.7), fill=(245, 255, 255, 230))
    return layer


def draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color: tuple[int, int, int, int]) -> None:
    draw.line((cx - r, cy, cx + r, cy), fill=color, width=2)
    draw.line((cx, cy - r, cx, cy + r), fill=color, width=2)


def glow_stick_overlay(row: str, frame: int) -> Image.Image:
    mode = GLOW_ROWS.get(row)
    overlay = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    if not mode:
        return overlay

    cyan = (34, 235, 240)
    mint = (96, 255, 160)
    blue = (68, 160, 255)
    phase = frame / max(1, COLS - 1)
    sway = math.sin(phase * math.tau)

    if mode == "handheld":
        x = 42 + 6 * sway
        y = 142 - 24 * abs(sway)
        angle = -0.9 + 0.45 * sway
        length = 58
        start = (x, y)
        end = (x + math.cos(angle) * length, y + math.sin(angle) * length)
        overlay.alpha_composite(glow_line((CELL_W, CELL_H), start, end, cyan if frame % 2 else mint, 5))
        d = ImageDraw.Draw(overlay)
        draw_star(d, 34, 116 + 4 * sway, 5, (116, 246, 255, 170))
        draw_star(d, 66, 102 - 5 * sway, 4, (255, 248, 120, 150))

    elif mode == "side-pop":
        x = 24 + 5 * sway
        y = 158 - 6 * abs(sway)
        angle = 0.48 + 0.18 * sway
        length = 46
        start = (x, y)
        end = (x + math.cos(angle) * length, y + math.sin(angle) * length)
        overlay.alpha_composite(glow_line((CELL_W, CELL_H), start, end, blue, 6))
        d = ImageDraw.Draw(overlay)
        draw_star(d, 24, 132, 5, (110, 230, 255, 160))

    elif mode == "trail":
        x = 22 + frame * 19
        y = 181 + 8 * math.sin(phase * math.tau * 2)
        start = (x - 38, y + 6)
        end = (x + 18, y - 8)
        overlay.alpha_composite(glow_line((CELL_W, CELL_H), start, end, mint if frame % 2 else cyan, 4))
        # A faint afterimage gives the row a running-concert feel without hiding the carrot.
        overlay.alpha_composite(glow_line((CELL_W, CELL_H), (start[0] - 18, start[1] + 5), (end[0] - 18, end[1] + 5), blue, 3))

    elif mode == "small-side":
        x = 26 + 3 * sway
        y = 190
        start = (x, y)
        end = (x + 42, y - 12 + 4 * sway)
        overlay.alpha_composite(glow_line((CELL_W, CELL_H), start, end, cyan, 4))

    return overlay


def build_motion_preview(sheet: Image.Image, out_path: Path) -> None:
    sequence = [
        (0, range(COLS)),
        (6, range(COLS)),
        (8, range(COLS)),
        (7, range(COLS)),
        (4, range(COLS)),
        (3, range(COLS)),
        (5, range(COLS)),
    ]
    frames = []
    for row_idx, cols in sequence:
        for col in cols:
            box = (col * CELL_W, row_idx * CELL_H, (col + 1) * CELL_W, (row_idx + 1) * CELL_H)
            frame = checkerboard((CELL_W, CELL_H))
            frame.alpha_composite(sheet.crop(box), (0, 0))
            frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))

    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=95,
        loop=0,
        disposal=2,
    )


def build(input_sheet: Path, out_dir: Path) -> None:
    sheet = Image.open(input_sheet).convert("RGBA")
    expected = (CELL_W * COLS, CELL_H * len(ROWS))
    if sheet.size != expected:
        raise ValueError(f"expected spritesheet {expected}, got {sheet.size}")

    out_dir.mkdir(parents=True, exist_ok=True)
    result = sheet.copy()
    contact = checkerboard(result.size)
    draw = ImageDraw.Draw(contact)

    for row_idx, row in enumerate(ROWS):
        draw.text((4, row_idx * CELL_H + 4), row, fill=(24, 130, 60, 255))
        for col in range(COLS):
            cell = result.crop((col * CELL_W, row_idx * CELL_H, (col + 1) * CELL_W, (row_idx + 1) * CELL_H))
            cell.alpha_composite(glow_stick_overlay(row, col))
            result.alpha_composite(cell, (col * CELL_W, row_idx * CELL_H))
            contact.alpha_composite(cell, (col * CELL_W, row_idx * CELL_H))
            x0, y0 = col * CELL_W, row_idx * CELL_H
            draw.rectangle((x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1), outline=(24, 140, 70, 255), width=2)

    sheet_path = out_dir / "spritesheet-v3.webp"
    contact_path = out_dir / "contact-sheet-v3.png"
    motion_path = out_dir / "motion-preview-v3.gif"
    mapping_path = out_dir / "animation-mapping-v3.md"

    result.save(sheet_path, lossless=True, quality=95, method=6)
    contact.convert("RGB").save(contact_path)
    build_motion_preview(result, motion_path)
    mapping_path.write_text(
        "\n".join(
            [
                "# V3 Glow Stick Mapping",
                "",
                "V3 keeps the v2 animation-cued Codex spritesheet and adds a small concert glow stick accent.",
                "No Electron runtime, Agent hooks, local HTTP server, or background desktop-pet app is included.",
                "",
                "| Codex row | Glow stick behavior |",
                "|---|---|",
                "| `idle` | none |",
                "| `right` | none |",
                "| `left` | none |",
                "| `wave` | handheld cyan/mint glow stick with sparkle accents |",
                "| `jump` | side pop blue glow stick |",
                "| `fail` | none |",
                "| `wait` | none |",
                "| `run` | moving glow trail |",
                "| `review` | small side glow stick |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(sheet_path)
    print(contact_path)
    print(motion_path)
    print(mapping_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-sheet", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("previews/v3-generated"), type=Path)
    args = parser.parse_args()
    build(args.input_sheet, args.out_dir)


if __name__ == "__main__":
    main()
