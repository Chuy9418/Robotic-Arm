# IMX219 Calibration And Test Detection

This starter project gives you two pieces:

- `calibrate_camera.py`: computes camera intrinsics from checkerboard photos.
- `detect_hardware.py`: runs a first-pass top-down detector for nuts, bolts, and washers.

## 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Collect calibration images

Print a checkerboard and take `12-20` photos with the IMX219 camera:

- Use a flat board with known square size, for example `25 mm`.
- Capture the board at different positions and tilts.
- Fill different parts of the image, not just the center.
- Avoid motion blur and harsh reflections.

Put the photos in `calibration_images/`.

## 3. Run camera calibration

If your checkerboard has `9 x 6` inner corners and `25 mm` squares:

```bash
python3 calibrate_camera.py \
  --images calibration_images \
  --pattern-cols 9 \
  --pattern-rows 6 \
  --square-size-mm 25 \
  --output camera_calibration.npz \
  --preview undistorted_preview.png
```

This saves:

- `camera_calibration.npz`
- `undistorted_preview.png`

The script prints an `RMS reprojection error`. Lower is better; under about `0.5` pixels is a good target for a controlled setup.

## 4. Run a test image

Place one top-down image in the workspace, for example `test_image.jpg`, then run:

```bash
python3 detect_hardware.py test_image.jpg --calibration camera_calibration.npz
```

This produces `annotated_detection.png`.

## 5. What the code is doing

### Calibration

`calibrate_camera.py`:

- finds checkerboard corners
- refines them to subpixel accuracy
- estimates the camera matrix and lens distortion
- saves the result for later undistortion

### Detection

`detect_hardware.py`:

- optionally undistorts the image
- thresholds the top-down photo against the background
- finds object contours
- checks for shape cues like holes, circularity, polygon sides, and elongation
- labels each object as a likely `washer`, `nut`, or `bolt`

## 6. Important notes for metal hardware

- Use a matte, dark background.
- Use diffuse lighting to reduce glare.
- Keep objects separated.
- Make sure each object is large enough in the image to show its outline clearly.

For bolts, try to keep the whole shaft visible from above. If you only see the bolt head, it can be confused with a nut.

## 7. Next improvement

Once you have a few sample images working, the next step is to convert detections from pixel coordinates into workspace coordinates using a known reference plane. That is the step that tells you where the object is in real-world `x, y`.
