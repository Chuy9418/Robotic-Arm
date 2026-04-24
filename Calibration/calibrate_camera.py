from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def build_object_points(pattern_size: tuple[int, int], square_size_mm: float) -> np.ndarray:
    cols, rows = pattern_size
    grid = np.zeros((rows * cols, 3), np.float32)
    grid[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    grid *= square_size_mm
    return grid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calibrate a camera from chessboard images."
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("calibration_images"),
        help="Folder containing chessboard calibration images.",
    )
    parser.add_argument(
        "--pattern-cols",
        type=int,
        default=9,
        help="Number of inner corners across the checkerboard.",
    )
    parser.add_argument(
        "--pattern-rows",
        type=int,
        default=6,
        help="Number of inner corners down the checkerboard.",
    )
    parser.add_argument(
        "--square-size-mm",
        type=float,
        default=25.0,
        help="Real checkerboard square size in millimeters.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("camera_calibration.npz"),
        help="Output file for camera matrix and distortion coefficients.",
    )
    parser.add_argument(
        "--preview",
        type=Path,
        default=None,
        help="Optional file path to save an undistorted preview image.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pattern_size = (args.pattern_cols, args.pattern_rows)
    image_paths = sorted(
        [
            *args.images.glob("*.jpg"),
            *args.images.glob("*.jpeg"),
            *args.images.glob("*.png"),
        ]
    )

    if not image_paths:
        raise SystemExit(
            f"No calibration images found in {args.images.resolve()}. "
            "Add chessboard photos first."
        )

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )
    object_template = build_object_points(pattern_size, args.square_size_mm)
    object_points: list[np.ndarray] = []
    image_points: list[np.ndarray] = []
    image_size: tuple[int, int] | None = None

    for image_path in image_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Skipping unreadable image: {image_path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray,
            pattern_size,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )

        if not found:
            print(f"Checkerboard not found: {image_path.name}")
            continue

        refined = cv2.cornerSubPix(
            gray,
            corners,
            winSize=(11, 11),
            zeroZone=(-1, -1),
            criteria=criteria,
        )

        object_points.append(object_template)
        image_points.append(refined)
        image_size = (gray.shape[1], gray.shape[0])
        print(f"Accepted: {image_path.name}")

    if len(object_points) < 8:
        raise SystemExit(
            "Need at least 8 good calibration images with detected corners. "
            f"Only found {len(object_points)}."
        )

    assert image_size is not None
    rms_error, camera_matrix, distortion, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        image_size,
        cameraMatrix=None,
        distCoeffs=None,
    )

    np.savez(
        args.output,
        camera_matrix=camera_matrix,
        distortion=distortion,
        rms_error=rms_error,
        rvecs=np.array(rvecs, dtype=object),
        tvecs=np.array(tvecs, dtype=object),
        image_size=np.array(image_size),
        pattern_size=np.array(pattern_size),
        square_size_mm=np.array(args.square_size_mm),
    )

    print(f"Saved calibration to {args.output.resolve()}")
    print(f"RMS reprojection error: {rms_error:.4f}")
    print("Camera matrix:")
    print(camera_matrix)
    print("Distortion coefficients:")
    print(distortion.ravel())

    if args.preview:
        preview_source = cv2.imread(str(image_paths[0]))
        undistorted = cv2.undistort(preview_source, camera_matrix, distortion)
        cv2.imwrite(str(args.preview), undistorted)
        print(f"Saved undistorted preview to {args.preview.resolve()}")


if __name__ == "__main__":
    main()
