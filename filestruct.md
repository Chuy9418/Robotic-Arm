# Project File Structure

```
Robotic-Arm/
│
├── detection/                             # Goal 1 — Detection Model
│   ├── __init__.py
│   ├── detector.py                        # detect(frame) → List[Detection]
│   ├── model.py                           # YOLO26n + TensorRT loading
│   └── schemas.py                         # Detection dataclass (label, confidence, bbox)
│
├── vision/                                # Goal 2 — Vision & Localization
│   ├── __init__.py
│   ├── calibration.py                     # OpenCV checkerboard calibration → saves camera matrix
│   ├── homography.py                      # Pixel → table mm transformation
│   └── scene.py                           # analyze_scene() → objects with table positions
│
├── camera/                                # Goal 2 — Camera stream
│   ├── __init__.py
│   └── stream.py                          # Frame producer (IMX219 CSI)
│
├── calibration_data/                      # Goal 2 — Saved calibration files (generated)
│   ├── camera_matrix.npy                  # Saved after running calibration
│   ├── dist_coeffs.npy                    # Saved after running calibration
│   └── homography.npy                     # Saved after running homography
│
├── kinematics/                            # Goal 3 — Inverse Kinematics
│   ├── __init__.py
│   ├── arm_chain.py                       # ikpy chain definition + arm geometry
│   └── solver.py                          # solve(x_mm, y_mm) → [base, shoulder, elbow, wrist]
│
├── control/                               # Goal 4 — Serial Control
│   ├── __init__.py
│   ├── arm_controller.py                  # ArmController + MockArmController
│   └── command_protocol.py               # Serial command definitions
│
├── api/                                   # Goal 5 — Backend FastAPI
│   ├── __init__.py
│   ├── main.py                            # App entry point + shared events deque
│   ├── models.py                          # Pydantic response models
│   ├── overlay.py                         # Draws bboxes + table coords on frame
│   └── routes/
│       ├── stream.py                      # GET  /stream        → MJPEG video
│       ├── metrics.py                     # GET  /metrics       → live stats
│       ├── logs.py                        # GET  /logs          → recent events
│       └── control.py                     # POST /control/start|stop|home
│
├── frontend/                              # Goal 5 — Frontend React
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── VideoFeed.jsx              # Live camera stream
│           ├── SceneView.jsx              # Camera + bounding box overlay
│           ├── MetricsBar.jsx             # FPS, latency, total sorted, success %
│           ├── SortingLog.jsx             # Scrollable table of recent events
│           └── ControlPanel.jsx          # Start / Stop / Home buttons
│
├── pipeline/                              # Goal 6 — Integration
│   ├── __init__.py
│   ├── planner.py                         # plan() — detections → ordered sort plan
│   └── sorter.py                          # Sorter — executes plan, appends to event log
│
├── scripts/                               # Utility + validation scripts
│   ├── run_calibration.py                 # Checkerboard intrinsic calibration
│   ├── run_homography.py                  # Table marker homography
│   ├── export_tensorrt.py                 # Export YOLO to TensorRT (run on Jetson)
│   ├── benchmark.py                       # Print mAP / FPS / latency table
│   ├── test_serial.py                     # Mock serial loopback test
│   ├── test_ik.py                         # Sweep 10×10 grid, verify IK accuracy
│   └── run_pipeline.py                    # Main entry point — full sorting loop
│
├── models/                                # Trained model files (git-ignored)
│   ├── yolo26n.pt                         # PyTorch weights
│   └── yolo26n.engine                     # TensorRT engine (Jetson only)
│
├── requirements/
│   ├── base.txt                           # Laptop / dev dependencies
│   └── jetson.txt                         # Jetson Orin Nano dependencies
│
├── docker-compose.yml                     # API + frontend services
├── README.md
├── ROADMAP.md                             # Task list + acceptance criteria
└── filestruct.md                          # This file
```

## Build order

```
Goal 4 (control/)              ──┐
Goal 3 (kinematics/)           ──┤
Goal 1 (detection/)            ──┼──→ Goal 6 (pipeline/)
Goal 2 (vision/ + camera/)     ──┘
Goal 5 (api/ + frontend/)      ──→ Goal 6 (pipeline/)
```

Goals 1–5 are built in parallel. Goal 6 starts only after Goals 1–4 pass their acceptance tests.
