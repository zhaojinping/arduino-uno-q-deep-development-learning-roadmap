import argparse
from pathlib import Path

import cv2


def parse_source(value):
    kind, separator, argument = value.partition(":")
    if not separator or not argument:
        raise argparse.ArgumentTypeError(
            "source must be camera:<non-negative index> or file:<local path>"
        )

    if kind == "camera":
        try:
            index = int(argument)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                "camera source index must be an integer"
            ) from exc
        if index < 0:
            raise argparse.ArgumentTypeError(
                "camera source index must be non-negative"
            )
        return index, "camera:{}".format(index)

    if kind == "file":
        path = Path(argument).expanduser()
        if not path.is_file():
            raise argparse.ArgumentTypeError(
                "local video file does not exist: {}".format(path)
            )
        return str(path), "file:{}".format(path)

    raise argparse.ArgumentTypeError(
        "source kind must be camera or file; network sources are not accepted"
    )


def positive_int(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def frame_is_structurally_valid(frame):
    if frame is None or frame.size == 0:
        return False
    if frame.ndim not in (2, 3):
        return False
    if any(dimension <= 0 for dimension in frame.shape):
        return False
    if frame.dtype.kind not in "buif":
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Inspect a finite sample from one explicit video source."
    )
    parser.add_argument(
        "--source",
        required=True,
        type=parse_source,
        metavar="camera:<index>|file:<path>",
        help="explicit camera index or existing local video file",
    )
    parser.add_argument(
        "--frames",
        type=positive_int,
        default=5,
        help="number of frames to inspect (default: 5)",
    )
    args = parser.parse_args()
    source, source_label = args.source

    capture = None
    try:
        capture = cv2.VideoCapture(source)
        if not capture.isOpened():
            print("opened=false source={}".format(source_label))
            return 2

        print("opened=true source={}".format(source_label))
        reported_properties = (
            ("width", cv2.CAP_PROP_FRAME_WIDTH),
            ("height", cv2.CAP_PROP_FRAME_HEIGHT),
            ("fps", cv2.CAP_PROP_FPS),
        )
        for name, property_id in reported_properties:
            value = capture.get(property_id)
            print("backend_reported_{}={:.3f}".format(name, value))

        for index in range(1, args.frames + 1):
            read_ok, frame = capture.read()
            if not read_ok or frame is None or frame.size == 0:
                print(
                    "frame={} status=INVALID read_ok={}".format(index, read_ok)
                )
                return 3

            if not frame_is_structurally_valid(frame):
                print(
                    "frame={} status=INVALID shape={} dtype={}".format(
                        index, getattr(frame, "shape", None),
                        getattr(frame, "dtype", None)
                    )
                )
                return 4

            print(
                "frame={} shape={} dtype={}".format(
                    index, frame.shape, frame.dtype
                )
            )

        print("result=FRAME_SAMPLE_PASS")
        return 0
    except cv2.error as exc:
        print("capture_error={}".format(exc))
        return 5
    finally:
        if capture is not None:
            capture.release()
            print("capture_released=true")


if __name__ == "__main__":
    raise SystemExit(main())
