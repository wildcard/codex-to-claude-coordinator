#!/usr/bin/env python3
"""Create privacy-checked, metadata-free image or text derivatives."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPLACEMENTS = (
    (
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
        "[REDACTED_EMAIL]",
    ),
    (re.compile(r"/Users/[^/\s]+/"), "[REDACTED_HOME]/"),
    (re.compile(r"/home/[^/\s]+/"), "[REDACTED_HOME]/"),
    (
        re.compile(r"[A-Z]:\\Users\\[^\\\s]+\\", re.I),
        "[REDACTED_HOME]/",
    ),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"), "[REDACTED_SECRET]"),
    (
        re.compile(r"\b(?:api[_-]?key|access[_-]?token)\s*[:=]\s*\S+", re.I),
        "[REDACTED_CREDENTIAL]",
    ),
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def redact_text(text: str) -> str:
    for pattern, replacement in REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def parse_rect(value: str) -> tuple[int, int, int, int]:
    try:
        rectangle = tuple(int(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("rectangles use x1,y1,x2,y2") from exc
    if len(rectangle) != 4:
        raise argparse.ArgumentTypeError("rectangles use x1,y1,x2,y2")
    x1, y1, x2, y2 = rectangle
    if min(rectangle) < 0 or x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("rectangle coordinates are invalid")
    return rectangle


def _require_derivative(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("redaction output must not overwrite the raw input")
    if ".redacted." not in output_path.name:
        raise ValueError("redaction output filename must contain .redacted.")


def redact_image(
    input_path: Path,
    output_path: Path,
    rectangles: list[tuple[int, int, int, int]],
) -> None:
    if not rectangles:
        raise ValueError("image redaction requires at least one opaque rectangle")
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError(
            "install requirements.txt from the coordination-conformance skill "
            "for image redaction"
        ) from exc
    with Image.open(input_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for rectangle in rectangles:
        x1, y1, x2, y2 = rectangle
        if x2 > width or y2 > height:
            raise ValueError("redaction rectangle exceeds image bounds")
        draw.rectangle(rectangle, fill=(0, 0, 0))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean = Image.new("RGB", image.size)
    clean.paste(image)
    clean.save(output_path)


def redact_file(
    input_path: Path,
    output_path: Path,
    rectangles: list[tuple[int, int, int, int]],
) -> None:
    _require_derivative(input_path, output_path)
    if input_path.suffix.lower() in IMAGE_SUFFIXES:
        redact_image(input_path, output_path, rectangles)
        return
    if rectangles:
        raise ValueError("--rect is only valid for image evidence")
    text = input_path.read_text(encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(redact_text(text), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--rect", action="append", type=parse_rect, default=[])
    args = parser.parse_args()
    try:
        redact_file(args.input, args.output, args.rect)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
