"""Offline HSV segmentation and pixel-coordinate candidate selection."""

import argparse
import math

import cv2
import numpy as np


GREEN_LOW = (35, 80, 80)
GREEN_HIGH = (85, 255, 255)


def positive_finite(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("min-area must be positive finite") from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("min-area must be positive finite")
    return number


def validate_bounds(lower, upper):
    limits = (179, 255, 255)
    if not isinstance(lower, (tuple, list)) or not isinstance(upper, (tuple, list)):
        raise ValueError("HSV bounds must be three-element sequences")
    if len(lower) != 3 or len(upper) != 3:
        raise ValueError("HSV bounds must be three-element sequences")
    for low, high, limit in zip(lower, upper, limits):
        if (
            isinstance(low, bool) or isinstance(high, bool)
            or not isinstance(low, (int, np.integer))
            or not isinstance(high, (int, np.integer))
            or not (0 <= low <= high <= limit)
        ):
            raise ValueError("HSV bounds must be ordered integer values in range")


def make_synthetic_scene():
    frame = np.full((128, 160, 3), 30, dtype=np.uint8)
    frame[20:60, 15:55] = (0, 180, 0)
    frame[75:95, 90:115] = (0, 180, 0)
    frame[20:55, 100:145] = (0, 0, 180)
    frame[5, 5] = (0, 180, 0)
    return frame


def locate_hsv_region(frame, lower, upper, min_area=100, kernel_size=3):
    """Return one largest eligible color-region candidate, or None."""
    if (
        not isinstance(frame, np.ndarray) or frame.size == 0
        or frame.ndim != 3 or frame.shape[2] != 3
        or frame.dtype != np.uint8
    ):
        raise ValueError("frame must be a non-empty HxWx3 uint8 BGR array")
    validate_bounds(lower, upper)
    if isinstance(min_area, (bool, np.bool_)):
        raise ValueError("min_area must be positive finite")
    try:
        area_limit = float(min_area)
    except (TypeError, ValueError) as exc:
        raise ValueError("min_area must be positive finite") from exc
    if not math.isfinite(area_limit) or area_limit <= 0:
        raise ValueError("min_area must be positive finite")
    if (
        isinstance(kernel_size, bool) or not isinstance(kernel_size, int)
        or kernel_size < 1 or kernel_size % 2 == 0
    ):
        raise ValueError("kernel_size must be a positive odd integer")

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    raw_mask = cv2.inRange(hsv, lower, upper)
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    clean_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel)
    contours, _hierarchy = cv2.findContours(
        clean_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    candidates = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < area_limit:
            continue
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue
        x, y, width, height = cv2.boundingRect(contour)
        candidates.append({
            "area": area,
            "bbox": (int(x), int(y), int(width), int(height)),
            "centroid": (
                float(moments["m10"] / moments["m00"]),
                float(moments["m01"] / moments["m00"]),
            ),
        })
    candidates.sort(key=lambda item: (-item["area"], item["bbox"][0], item["bbox"][1]))
    return {
        "raw_pixels": int(np.count_nonzero(raw_mask)),
        "clean_pixels": int(np.count_nonzero(clean_mask)),
        "contour_count": len(contours),
        "eligible_count": len(candidates),
        "target": candidates[0] if candidates else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Locate a green region in an offline synthetic BGR scene."
    )
    parser.add_argument(
        "--min-area", type=positive_finite, default=100.0,
        help="minimum contour area in pixel-coordinate squared units (default: 100)",
    )
    args = parser.parse_args()
    frame = make_synthetic_scene()
    result = locate_hsv_region(frame, GREEN_LOW, GREEN_HIGH, args.min_area, 3)
    print("frame_shape={} dtype={} source=synthetic".format(frame.shape, frame.dtype))
    print("hsv_lower={} hsv_upper={} opening_kernel=3 min_area_px2={:.1f}".format(
        GREEN_LOW, GREEN_HIGH, args.min_area
    ))
    print("raw_pixels={} clean_pixels={}".format(
        result["raw_pixels"], result["clean_pixels"]
    ))
    print("contours={} eligible={}".format(
        result["contour_count"], result["eligible_count"]
    ))
    target = result["target"]
    if target is None:
        print("target=NO_CANDIDATE")
    else:
        print("target=PIXEL_CANDIDATE area_px2={:.1f} bbox={} centroid_px=({:.1f}, {:.1f})".format(
            target["area"], target["bbox"],
            target["centroid"][0], target["centroid"][1]
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
