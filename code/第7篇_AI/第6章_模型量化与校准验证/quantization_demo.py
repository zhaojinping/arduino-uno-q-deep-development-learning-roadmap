"""Demonstrate calibration-range effects with synthetic scalar values only."""

from __future__ import annotations

import json
import math
import statistics
from collections.abc import Sequence
from typing import Any


QUANT_MIN = -127
QUANT_MAX = 127
EVALUATION_VALUES = [-1.5, -0.1, 0.0, 0.1, 1.5]
CALIBRATION_SCENARIOS = {
    "narrow_calibration": [-1.0, -0.5, 0.0, 0.5, 1.0],
    "outlier_inclusive_calibration": [-8.0, -1.0, -0.5, 0.0, 0.5, 1.0, 8.0],
}


class QuantizationInputError(ValueError):
    """Raised when an educational quantization input is invalid."""


def _finite_values(values: Sequence[float], name: str) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence) or not values:
        raise QuantizationInputError(f"{name} must be a non-empty sequence of finite numbers")

    normalized: list[float] = []
    for index, value in enumerate(values):
        if type(value) not in (int, float):
            raise QuantizationInputError(f"{name}[{index}] must be a finite number, not a boolean or other type")
        try:
            number = float(value)
        except OverflowError as exc:
            raise QuantizationInputError(f"{name}[{index}] must be finite") from exc
        if not math.isfinite(number):
            raise QuantizationInputError(f"{name}[{index}] must be finite")
        normalized.append(number)
    return normalized


def simulate_quantization(
    calibration_values: Sequence[float], evaluation_values: Sequence[float]
) -> dict[str, Any]:
    """Simulate symmetric int8 quantize/dequantize for one numeric vector.

    This is a scalar teaching model: it does not load or transform a model,
    implement a framework operator, or predict target hardware behavior.
    """
    calibration = _finite_values(calibration_values, "calibration_values")
    evaluation = _finite_values(evaluation_values, "evaluation_values")
    calibration_abs_max = max(abs(value) for value in calibration)
    if calibration_abs_max == 0:
        raise QuantizationInputError("calibration range must contain a non-zero value")

    scale = calibration_abs_max / QUANT_MAX
    if not math.isfinite(scale) or scale <= 0:
        raise QuantizationInputError("calibration range cannot produce a positive finite scale")
    representable_abs_max = scale * QUANT_MAX
    if not math.isfinite(representable_abs_max):
        raise QuantizationInputError("scale produces an unrepresentable floating-point range")

    quantized_values: list[int] = []
    reconstructed_values: list[float] = []
    absolute_errors: list[float] = []
    clipped_count = 0
    for value in evaluation:
        if value > representable_abs_max:
            quantized = QUANT_MAX
            clipped_count += 1
        elif value < -representable_abs_max:
            quantized = QUANT_MIN
            clipped_count += 1
        else:
            quantized = max(QUANT_MIN, min(QUANT_MAX, round(value / scale)))

        reconstructed = quantized * scale
        error = abs(value - reconstructed)
        quantized_values.append(quantized)
        reconstructed_values.append(reconstructed)
        absolute_errors.append(error)

    return {
        "calibration_abs_max": calibration_abs_max,
        "scale": scale,
        "zero_point": 0,
        "integer_range": [QUANT_MIN, QUANT_MAX],
        "quantized_values": quantized_values,
        "reconstructed_values": reconstructed_values,
        "absolute_errors": absolute_errors,
        "clipped_count": clipped_count,
        "mean_absolute_error": statistics.fmean(absolute_errors),
        "max_absolute_error": max(absolute_errors),
    }


def build_report() -> dict[str, Any]:
    """Return a threshold-free report for the fixed synthetic lesson data."""
    scenarios = {
        name: {
            "calibration_values": calibration,
            **simulate_quantization(calibration, EVALUATION_VALUES),
        }
        for name, calibration in CALIBRATION_SCENARIOS.items()
    }
    evaluation_count = len(EVALUATION_VALUES)
    float32_bytes = evaluation_count * 4
    int8_bytes = evaluation_count
    return {
        "status": "REPORT_ONLY",
        "report_only": True,
        "thresholds_applied": False,
        "scope": "synthetic scalar-vector demonstration; no model, runtime, or hardware execution",
        "evaluation_values": EVALUATION_VALUES,
        "payload_estimate": {
            "element_count": evaluation_count,
            "float32_bytes": float32_bytes,
            "int8_bytes": int8_bytes,
            "ratio": float32_bytes / int8_bytes,
            "includes_model_overhead": False,
        },
        "scenarios": scenarios,
    }


def main() -> int:
    print(json.dumps(build_report(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
