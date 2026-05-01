from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
from api.models import LogEvent, Metrics

# ── Shared state ────────────────────────────────────────────────────────────
# These are shared across all routes via app.state

# Stores the last 100 sorting events
event_log: deque[LogEvent] = deque(maxlen=100)

# Live metrics (updated by the pipeline as it runs)
live_metrics: Metrics = Metrics(
    fps=0.0,
    latency_ms=0.0,
    total_sorted=0,
    success_rate=0.0,
)

# Whether the sorting pipeline is currently running
is_running: bool = False

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Robotic Arm API",
    description="Controls and monitors the robotic sorting arm.",
    version="0.1.0",
)

# Allow the React frontend (running on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach shared state so routes can access it via request.app.state
app.state.event_log    = event_log
app.state.live_metrics = live_metrics
app.state.is_running   = is_running

# ── Register routes ──────────────────────────────────────────────────────────
from api.routes import metrics, logs, control  # noqa: E402

app.include_router(metrics.router)
app.include_router(logs.router)
app.include_router(control.router)


@app.get("/")
def root():
    return {"message": "Robotic Arm API is running. Visit /docs for the full API reference."}