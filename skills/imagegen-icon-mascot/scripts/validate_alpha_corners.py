#!/usr/bin/env python3
"""Validate that image corners are truly alpha-transparent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether all four image corners have real alpha transparency."
    )
    parser.add_argument("image", type=Path, help="PNG/WebP image to validate")
    parser.add_argument(
        "--max-alpha",
        type=int,
        default=0,
        help="Maximum allowed corner alpha. Default 0 means fully transparent.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=8,
        help="Square sample size in pixels at each corner.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.image.exists():
        print(f"FAIL: file not found: {args.image}", file=sys.stderr)
        return 2

    with Image.open(args.image) as image:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        sample = max(1, min(args.sample, width, height))
        boxes = {
            "top-left": (0, 0, sample, sample),
            "top-right": (width - sample, 0, width, sample),
            "bottom-left": (0, height - sample, sample, height),
            "bottom-right": (width - sample, height - sample, width, height),
        }

        failures: list[str] = []
        for name, box in boxes.items():
            crop = rgba.crop(box)
            max_alpha = max(pixel[3] for pixel in crop.getdata())
            if max_alpha > args.max_alpha:
                failures.append(f"{name} max alpha {max_alpha}")

    if failures:
        print("FAIL: corners are not truly transparent:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"PASS: all four {sample}x{sample} corner samples have alpha <= {args.max_alpha}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
