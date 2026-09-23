"""Offline contour-geometry exercise on a synthetic binary mask."""

import argparse
import math

import cv2
import numpy as np


def positive_finite(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("min-area must be positive finite") from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("min-area must be positive finite")
    return number


def make_synthetic_mask():
    """Return two rectangular regions and one isolated small speck."""
    mask = np.zeros((128, 160), dtype=np.uint8)
    mask[20:50, 15:55] = 255
    mask[60:105, 90:140] = 255
    mask[4:7, 5:8] = 255
    return mask


def measure_contours(mask, min_area):
    """Measure external contours in pixel coordinates, with no I/O or control."""
    if not isinstance(mask, np.ndarray) or mask.size == 0:
        raise ValueError("mask must be a non-empty NumPy array")
    if mask.ndim != 2 or mask.dtype != np.uint8:
        raise ValueError("mask must be a two-dimensional uint8 array")
    if np.any((mask != 0) & (mask != 255)):
        raise ValueError("mask values must be 0 or 255")
    try:
        threshold = float(min_area)
    except (TypeError, ValueError) as exc:
        raise ValueError("min_area must be positive finite") from exc
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("min_area must be positive finite")

    contours, _hierarchy = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    accepted = []
    rejected_count = 0
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < threshold:
            rejected_count += 1
            continue
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            rejected_count += 1
            continue
        x, y, width, height = cv2.boundingRect(contour)
        accepted.append({
            "area": area,
            "perimeter": float(cv2.arcLength(contour, True)),
            "bbox": (int(x), int(y), int(width), int(height)),
            "centroid": (
                float(moments["m10"] / moments["m00"]),
                float(moments["m01"] / moments["m00"]),
            ),
        })

    # OpenCV does not promise contour enumeration order; sort for repeatable output.
    accepted.sort(key=lambda item: (item["bbox"][0], item["bbox"][1]))
    return {
        "raw_count": len(contours),
        "rejected_count": rejected_count,
        "accepted": accepted,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Measure external contours of a synthetic binary mask."
    )
    parser.add_argument(
        "--min-area", type=positive_finite, default=100.0,
        help="minimum contour area in pixel-coordinate squared units (default: 100)",
    )
    args = parser.parse_args()
    mask = make_synthetic_mask()
    result = measure_contours(mask, min_area=args.min_area)
    print("mask_shape={} dtype={} foreground_pixels={}".format(
        mask.shape, mask.dtype, int(np.count_nonzero(mask))
    ))
    print("raw_contours={} accepted={} rejected={}".format(
        result["raw_count"], len(result["accepted"]), result["rejected_count"]
    ))
    for index, shape in enumerate(result["accepted"], start=1):
        print("shape_{} area_px2={:.1f} perimeter_px={:.1f} bbox={} centroid_px=({:.1f}, {:.1f})".format(
            index, shape["area"], shape["perimeter"], shape["bbox"],
            shape["centroid"][0], shape["centroid"][1]
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
