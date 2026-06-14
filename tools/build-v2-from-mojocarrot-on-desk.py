#!/usr/bin/env python3
"""Build a Codex custom-pet spritesheet from Mojocarrot-on-Desk animation cues.

This script is intentionally narrow: it reads transparent GIF previews from a
local checkout of lukelei2025/mojocarrot-on-desk and converts selected motion
ideas into the simple 8 x 9 spritesheet format used by Codex custom pets.

It does not install hooks, start Electron, or copy the source project.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageSequence


CELL_W = 192
CELL_H = 208
COLS = 8

ROWS = [
    ("idle", "clawd-idle-follow.gif", "calm idle with eye tracking"),
    ("right", "clawd-react-right.gif", "right-side glance reaction"),
    ("left", "clawd-react-left.gif", "left-side glance reaction"),
    ("wave", "clawd-happy.gif", "happy celebration"),
    ("jump", "clawd-react-double-jump.gif", "surprised jump"),
    ("fail", "clawd-error.gif", "error state"),
    ("wait", "clawd-working-thinking.gif", "thinking / waiting"),
    ("run", "clawd-working-carrying.gif", "busy movement"),
    ("review", "clawd-idle-reading.gif", "reading / review"),
]


def alpha_bbox(img: Image.Image):
    return img.getchannel("A").getbbox()


def union_bbox(frames: Iterable[Image.Image]):
    boxes = [alpha_bbox(frame) for frame in frames]
    boxes = [box for box in boxes if box]
    if not boxes:
        return None
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def sample_indices(total: int, count: int = COLS) -> list[int]:
    if total <= 0:
        raise ValueError("cannot sample empty animation")
    if total == 1:
        return [0] * count
    return [round(i * (total - 1) / (count - 1)) for i in range(count)]


def load_sampled_frames(path: Path) -> list[Image.Image]:
    img = Image.open(path)
    all_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(img)]
    if not all_frames:
        raise ValueError(f"no frames found: {path}")

    box = union_bbox(all_frames)
    if box is None:
        raise ValueError(f"no visible pixels found: {path}")

    sampled = []
    for idx in sample_indices(len(all_frames)):
        sampled.append(all_frames[idx].crop(box))
    return sampled


def fit_to_cell(frame: Image.Image) -> Image.Image:
    # Leave room for Codex's window chrome and for effects such as sparkles.
    scale = min(172 / frame.width, 188 / frame.height)
    w = max(1, round(frame.width * scale))
    h = max(1, round(frame.height * scale))
    return frame.resize((w, h), Image.Resampling.LANCZOS)


def checkerboard(size: tuple[int, int], tile: int = 16) -> Image.Image:
    out = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2 == 0:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=(238, 238, 238, 255))
    return out


def paste_centered(cell: Image.Image, sprite: Image.Image) -> None:
    x = (CELL_W - sprite.width) // 2
    y = CELL_H - sprite.height - 6
    cell.alpha_composite(sprite, (x, y))


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
            box = (
                col * CELL_W,
                row_idx * CELL_H,
                (col + 1) * CELL_W,
                (row_idx + 1) * CELL_H,
            )
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


def build(reference_root: Path, out_dir: Path) -> None:
    gif_dir = reference_root / "assets" / "gif"
    missing = [filename for _, filename, _ in ROWS if not (gif_dir / filename).exists()]
    if missing:
        raise FileNotFoundError("missing reference GIFs: " + ", ".join(missing))

    out_dir.mkdir(parents=True, exist_ok=True)

    sheet = Image.new("RGBA", (CELL_W * COLS, CELL_H * len(ROWS)), (0, 0, 0, 0))
    contact = checkerboard(sheet.size)
    draw = ImageDraw.Draw(contact)

    manifest_lines = [
        "# V2 Animation Mapping",
        "",
        "Generated from selected animation cues in `lukelei2025/mojocarrot-on-desk`.",
        "The Codex pet remains a static custom-pet spritesheet; no Electron runtime or hooks are included.",
        "",
        "| Codex row | Reference cue | Use |",
        "|---|---|---|",
    ]

    for row_idx, (row_name, filename, note) in enumerate(ROWS):
        frames = load_sampled_frames(gif_dir / filename)
        manifest_lines.append(f"| `{row_name}` | `{filename}` | {note} |")
        draw.text((4, row_idx * CELL_H + 4), row_name, fill=(24, 130, 60, 255))

        for col, frame in enumerate(frames):
            sprite = fit_to_cell(frame)
            cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
            paste_centered(cell, sprite)

            x0 = col * CELL_W
            y0 = row_idx * CELL_H
            sheet.alpha_composite(cell, (x0, y0))
            contact.alpha_composite(cell, (x0, y0))
            draw.rectangle((x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1), outline=(24, 140, 70, 255), width=2)

    sheet_path = out_dir / "spritesheet-v2.webp"
    contact_path = out_dir / "contact-sheet-v2.png"
    motion_path = out_dir / "motion-preview-v2.gif"
    manifest_path = out_dir / "animation-mapping-v2.md"

    sheet.save(sheet_path, lossless=True, quality=95, method=6)
    contact.convert("RGB").save(contact_path)
    build_motion_preview(sheet, motion_path)
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print(sheet_path)
    print(contact_path)
    print(motion_path)
    print(manifest_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-root", default="/tmp/mojocarrot-on-desk", type=Path)
    parser.add_argument("--out-dir", default=Path("previews/v2-generated"), type=Path)
    args = parser.parse_args()
    build(args.reference_root, args.out_dir)


if __name__ == "__main__":
    main()
