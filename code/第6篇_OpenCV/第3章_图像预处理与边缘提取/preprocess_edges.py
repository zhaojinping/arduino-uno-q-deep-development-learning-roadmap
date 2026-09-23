import argparse
import math
import sys

import cv2
import numpy as np


IMAGE_HEIGHT = 128
IMAGE_WIDTH = 160


def non_negative_int(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return number


def non_negative_float(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a finite non-negative number") from exc
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite non-negative number")
    return number


def validate_gray_u8(image, label):
    if not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("{} must be a non-empty NumPy array".format(label))
    if image.ndim != 2:
        raise ValueError("{} must be a two-dimensional grayscale image".format(label))
    if image.dtype != np.uint8:
        raise ValueError("{} must use uint8 data".format(label))


def create_synthetic_images(seed):
    clean = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH), dtype=np.uint8)
    cv2.rectangle(clean, (20, 18), (139, 109), 180, thickness=-1)
    cv2.circle(clean, (80, 64), 26, 240, thickness=-1)

    rng = np.random.default_rng(seed)
    gaussian_noise = rng.normal(0.0, 22.0, clean.shape)
    gaussian_noisy = np.clip(
        clean.astype(np.float32) + gaussian_noise, 0, 255
    ).astype(np.uint8)

    salt_pepper_noisy = clean.copy()
    impulse_mask = rng.random(clean.shape)
    salt_pepper_noisy[impulse_mask < 0.025] = 0
    salt_pepper_noisy[impulse_mask > 0.975] = 255

    return clean, gaussian_noisy, salt_pepper_noisy


def root_mean_square_error(image, reference):
    difference = image.astype(np.float32) - reference.astype(np.float32)
    return float(np.sqrt(np.mean(difference * difference)))


def run_demo(seed, low_threshold, high_threshold):
    clean, gaussian_noisy, salt_pepper_noisy = create_synthetic_images(seed)
    validate_gray_u8(clean, "clean reference")
    validate_gray_u8(gaussian_noisy, "Gaussian-noisy image")
    validate_gray_u8(salt_pepper_noisy, "salt-and-pepper-noisy image")

    gaussian_filtered = cv2.GaussianBlur(gaussian_noisy, (5, 5), 0)
    median_filtered = cv2.medianBlur(salt_pepper_noisy, 3)
    validate_gray_u8(gaussian_filtered, "Gaussian-filter output")
    validate_gray_u8(median_filtered, "median-filter output")

    gaussian_edges = cv2.Canny(
        gaussian_filtered, low_threshold, high_threshold
    )
    median_edges = cv2.Canny(median_filtered, low_threshold, high_threshold)
    validate_gray_u8(gaussian_edges, "Gaussian-path edge map")
    validate_gray_u8(median_edges, "median-path edge map")

    if gaussian_edges.shape != clean.shape or median_edges.shape != clean.shape:
        raise ValueError("edge-map dimensions must match the source image")

    gaussian_before = root_mean_square_error(gaussian_noisy, clean)
    gaussian_after = root_mean_square_error(gaussian_filtered, clean)
    salt_pepper_before = root_mean_square_error(salt_pepper_noisy, clean)
    salt_pepper_after = root_mean_square_error(median_filtered, clean)

    print(
        "input_shape={} dtype={}".format(clean.shape, clean.dtype)
    )
    print(
        "gaussian_rmse_before={:.3f} gaussian_rmse_after={:.3f}".format(
            gaussian_before, gaussian_after
        )
    )
    print(
        "salt_pepper_rmse_before={:.3f} salt_pepper_rmse_after={:.3f}".format(
            salt_pepper_before, salt_pepper_after
        )
    )
    print(
        "canny_low={:.1f} canny_high={:.1f}".format(
            low_threshold, high_threshold
        )
    )
    print("gaussian_edge_pixels={}".format(cv2.countNonZero(gaussian_edges)))
    print("median_edge_pixels={}".format(cv2.countNonZero(median_edges)))
    edge_values = sorted(int(value) for value in np.unique(gaussian_edges))
    print(
        "edge_map_shape={} dtype={} values={}".format(
            gaussian_edges.shape, gaussian_edges.dtype, edge_values
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare two denoising filters and Canny on synthetic grayscale images."
    )
    parser.add_argument(
        "--seed",
        type=non_negative_int,
        default=2026,
        help="random seed for reproducible synthetic noise (default: 2026)",
    )
    parser.add_argument(
        "--low-threshold",
        type=non_negative_float,
        default=50.0,
        help="Canny lower threshold (default: 50)",
    )
    parser.add_argument(
        "--high-threshold",
        type=non_negative_float,
        default=150.0,
        help="Canny upper threshold (default: 150)",
    )
    args = parser.parse_args()
    if args.high_threshold <= args.low_threshold:
        parser.error("high threshold must be greater than low threshold")

    try:
        run_demo(args.seed, args.low_threshold, args.high_threshold)
    except (ValueError, cv2.error) as exc:
        print("processing_error={}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
