import cv2
import numpy as np


def main() -> None:
    image = np.zeros((4, 6, 3), dtype=np.uint8)
    image[:] = (16, 16, 16)
    image[1:3, 2:5] = (0, 0, 255)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    pixel_bgr = tuple(int(channel) for channel in image[1, 2])
    print("shape={} dtype={}".format(image.shape, image.dtype))
    print("pixel_bgr[1, 2]={}".format(pixel_bgr))
    print(
        "gray[1, 2]={} threshold_nonzero={}".format(
            int(gray[1, 2]), int(cv2.countNonZero(mask))
        )
    )


if __name__ == "__main__":
    main()
