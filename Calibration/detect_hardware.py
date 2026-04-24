from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


MIN_AREA = 500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and roughly classify nuts, bolts, and washers from a top-down image."
    )
    parser.add_argument("image", type=Path, help="Path to the test image.")
    parser.add_argument(
        "--calibration",
        type=Path,
        default=None,
        help="Optional .npz file from calibrate_camera.py",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("annotated_detection.png"),
        help="Output image with labels and contours.",
    )
    return parser.parse_args()


def load_calibration(calibration_path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(calibration_path)
    return data["camera_matrix"], data["distortion"]


def preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu works well on a plain, high-contrast background.
    _, mask = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    kernel = np.ones((3, 3), np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
    return cleaned


def classify_contour(
    contour: np.ndarray, hierarchy_entry: np.ndarray | None
) -> tuple[str, dict[str, float]]:
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / float(h)

    circularity = 0.0
    if perimeter > 0:
        circularity = (4 * np.pi * area) / (perimeter * perimeter)

    polygon = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
    vertices = len(polygon)

    has_hole = False
    if hierarchy_entry is not None:
        child_index = hierarchy_entry[2]
        has_hole = child_index != -1

    label = "unknown"
    if has_hole and circularity > 0.65:
        label = "washer"
    elif has_hole and 5 <= vertices <= 8:
        label = "nut"
    elif aspect_ratio > 1.4 or aspect_ratio < 0.72:
        label = "bolt"
    elif not has_hole and circularity < 0.55:
        label = "bolt"
    elif has_hole:
        label = "nut"

    metrics = {
        "area": area,
        "aspect_ratio": aspect_ratio,
        "circularity": circularity,
        "vertices": float(vertices),
        "has_hole": float(has_hole),
    }
    return label, metrics


def annotate_image(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )
    annotated = image.copy()
    hierarchy_array = hierarchy[0] if hierarchy is not None else None

    for index, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area < MIN_AREA:
            continue

        if hierarchy_array is not None and hierarchy_array[index][3] != -1:
            # Skip child contours; the outer contour already carries the object label.
            continue

        label, metrics = classify_contour(
            contour,
            hierarchy_array[index] if hierarchy_array is not None else None,
        )

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.drawContours(annotated, [contour], -1, (255, 0, 0), 2)
        text = (
            f"{label} "
            f"A:{metrics['area']:.0f} "
            f"C:{metrics['circularity']:.2f}"
        )
        cv2.putText(
            annotated,
            text,
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    return annotated


def main() -> None:
    args = parse_args()
    image = cv2.imread(str(args.image))
    if image is None:
        raise SystemExit(f"Could not read image: {args.image.resolve()}")

    if args.calibration:
        camera_matrix, distortion = load_calibration(args.calibration)
        image = cv2.undistort(image, camera_matrix, distortion)

    mask = preprocess(image)
    annotated = annotate_image(image, mask)
    cv2.imwrite(str(args.output), annotated)
    print(f"Saved annotated detection to {args.output.resolve()}")


if __name__ == "__main__":
    main()
