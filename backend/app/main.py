"""
ADAS False-Positive Root Cause Engine API
FastAPI routes — thin orchestration layer calling tested core functions.
"""

import io
import uuid
from typing import Optional

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import Request
import traceback

from app.metrics import compute_fused_confidence, compute_confusion_metrics
from app.classifier import classify_root_cause, get_root_cause_explanation
from app.optimizer import find_optimal_threshold
from app.synthetic import generate_synthetic_data
from app.vision import batch_label_from_iou
from app.schemas import (
    AnalysisResponse, ConfusionMetrics, RootCauseCount,
    OptimizeResponse, UploadResponse, DetectionEvent, GenerateRequest,
)

app = FastAPI(
    title="ADAS False-Positive Root Cause Engine API",
    description="Analyze, classify, and optimize ADAS false-positive detections with real metrics.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("FATAL ERROR CAUGHT:", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Vercel Backend Crash: {str(exc)} | TRACE: {traceback.format_exc()}"}
    )

# In-memory dataset store (keyed by dataset_id)
_datasets: dict[str, pd.DataFrame] = {}

REQUIRED_COLUMNS = {
    "timestamp", "frame_id", "speed_kph",
    "radar_confidence", "camera_confidence",
    "environment", "adas_action",
}

VALID_ENVIRONMENTS = {"clear", "rain", "fog", "night", "glare"}
VALID_ACTIONS = {"brake", "steer", "alert", "none"}
VALID_GROUND_TRUTH = {"TP", "FP", "TN", "FN"}


def _prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure IDs exist and types are correct."""
    if "id" not in df.columns:
        df["id"] = [str(uuid.uuid4())[:8] for _ in range(len(df))]
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["frame_id"] = pd.to_numeric(df["frame_id"], errors="coerce").astype(int)
    df["speed_kph"] = pd.to_numeric(df["speed_kph"], errors="coerce")
    df["radar_confidence"] = pd.to_numeric(df["radar_confidence"], errors="coerce").clip(0, 1)
    df["camera_confidence"] = pd.to_numeric(df["camera_confidence"], errors="coerce").clip(0, 1)
    return df


def _run_full_pipeline(
    df: pd.DataFrame,
    threshold: float,
    radar_weight: float,
    camera_weight: float,
) -> pd.DataFrame:
    """Run the full analysis pipeline on a DataFrame."""
    df = compute_fused_confidence(df, radar_weight, camera_weight)
    df = classify_root_cause(df, threshold)
    return df


def _displayed_label(fused_confidence: float, ground_truth: str, threshold: float) -> str:
    """Computes the current event's TP/FP/TN/FN label based on live threshold."""
    actual_positive = ground_truth in ("TP", "FN")
    flagged = fused_confidence >= threshold

    if flagged and actual_positive:
        return "TP"
    if flagged and not actual_positive:
        return "FP"
    if not flagged and actual_positive:
        return "FN"
    return "TN"


def _df_to_analysis_response(
    df: pd.DataFrame,
    dataset_id: str,
    threshold: float,
    radar_weight: float,
    camera_weight: float,
) -> AnalysisResponse:
    """Convert a fully-processed DataFrame into an AnalysisResponse."""
    metrics = compute_confusion_metrics(df, threshold)

    # Root cause breakdown
    rc_counts = df["root_cause"].value_counts()
    total = len(df)
    breakdown = [
        RootCauseCount(
            category=cat,
            count=int(cnt),
            percentage=round(cnt / total * 100, 1) if total > 0 else 0,
        )
        for cat, cnt in rc_counts.items()
    ]

    # Convert events
    events = []
    for _, row in df.iterrows():
        event_dict = row.to_dict()
        # Clean NaN values
        for k, v in event_dict.items():
            if pd.isna(v):
                event_dict[k] = None
        
        # Override the ground_truth with dynamic label for the UI
        event_dict["ground_truth"] = _displayed_label(
            event_dict["fused_confidence"], 
            event_dict["ground_truth"], 
            threshold
        )

        # Add explainability
        explanation = get_root_cause_explanation(event_dict, threshold)
        event_dict["explanation"] = explanation
        events.append(event_dict)

    return AnalysisResponse(
        dataset_id=dataset_id,
        threshold=threshold,
        radar_weight=radar_weight,
        camera_weight=camera_weight,
        total_events=total,
        metrics=ConfusionMetrics(**metrics),
        root_cause_breakdown=breakdown,
        events=events,
    )


# ─────────────────────────── ROUTES ───────────────────────────


@app.get("/")
def root():
    return {
        "name": "ADAS False-Positive Root Cause Engine API",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV detection log."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "File must be a CSV (.csv extension).")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(400, f"Could not parse CSV: {str(e)}")

    # Validate required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            400,
            f"Missing required columns: {', '.join(sorted(missing))}. "
            f"Required: {', '.join(sorted(REQUIRED_COLUMNS))}",
        )

    warnings = []
    total_rows = len(df)

    # Validate environment / action values
    invalid_env = set(df["environment"].unique()) - VALID_ENVIRONMENTS
    if invalid_env:
        warnings.append(f"Invalid environment values will be set to 'clear': {invalid_env}")
        df.loc[~df["environment"].isin(VALID_ENVIRONMENTS), "environment"] = "clear"

    invalid_act = set(df["adas_action"].unique()) - VALID_ACTIONS
    if invalid_act:
        warnings.append(f"Invalid adas_action values will be set to 'none': {invalid_act}")
        df.loc[~df["adas_action"].isin(VALID_ACTIONS), "adas_action"] = "none"

    # Handle ground truth
    if "ground_truth" not in df.columns:
        # Check if bounding boxes are available for IoU labeling
        if "pred_bbox" in df.columns or "true_bbox" in df.columns:
            warnings.append("Computing ground_truth from bounding boxes via IoU.")
            pred_boxes = df.get("pred_bbox", pd.Series([None] * len(df))).tolist()
            true_boxes = df.get("true_bbox", pd.Series([None] * len(df))).tolist()

            # Parse string bboxes if needed
            def parse_bbox(v):
                if v is None or (isinstance(v, float) and pd.isna(v)):
                    return None
                if isinstance(v, str):
                    try:
                        return [float(x) for x in v.strip("[]()").split(",")]
                    except ValueError:
                        return None
                return v

            pred_boxes = [parse_bbox(b) for b in pred_boxes]
            true_boxes = [parse_bbox(b) for b in true_boxes]
            df["ground_truth"] = batch_label_from_iou(pred_boxes, true_boxes)
        else:
            warnings.append(
                "No 'ground_truth' column and no bounding boxes found. "
                "Defaulting all events to 'FP' — upload a labeled CSV for real metrics."
            )
            df["ground_truth"] = "FP"
    else:
        invalid_gt = set(df["ground_truth"].unique()) - VALID_GROUND_TRUTH
        if invalid_gt:
            warnings.append(f"Invalid ground_truth values set to 'FP': {invalid_gt}")
            df.loc[~df["ground_truth"].isin(VALID_GROUND_TRUTH), "ground_truth"] = "FP"

    df = _prepare_dataset(df)
    # Drop rows with NaN in critical columns
    df = df.dropna(subset=["timestamp", "radar_confidence", "camera_confidence"])
    valid_rows = len(df)

    if valid_rows == 0:
        raise HTTPException(400, "No valid rows after cleaning. Check your data.")

    dataset_id = str(uuid.uuid4())[:12]
    _datasets[dataset_id] = df

    return UploadResponse(
        dataset_id=dataset_id,
        total_rows=total_rows,
        valid_rows=valid_rows,
        warnings=warnings,
    )


@app.post("/generate", response_model=UploadResponse)
def generate_data(request: GenerateRequest):
    """Generate synthetic demo data."""
    df = generate_synthetic_data(n_events=request.n_events)
    dataset_id = str(uuid.uuid4())[:12]
    _datasets[dataset_id] = df

    return UploadResponse(
        dataset_id=dataset_id,
        total_rows=request.n_events,
        valid_rows=len(df),
        warnings=["Synthetic data generated for demo purposes."],
    )


@app.get("/analyze")
def analyze(
    dataset_id: str = Query(..., description="Dataset ID from /upload or /generate"),
    threshold: float = Query(0.5, ge=0.01, le=0.99, description="Decision threshold"),
    radar_weight: float = Query(0.5, ge=0.0, le=1.0, description="Radar sensor weight"),
    camera_weight: float = Query(0.5, ge=0.0, le=1.0, description="Camera sensor weight"),
):
    """Analyze a dataset: compute fusion, classify root causes, compute metrics."""
    if dataset_id not in _datasets:
        raise HTTPException(404, f"Dataset '{dataset_id}' not found. Upload or generate data first.")

    df = _datasets[dataset_id].copy()
    df = _run_full_pipeline(df, threshold, radar_weight, camera_weight)

    return _df_to_analysis_response(df, dataset_id, threshold, radar_weight, camera_weight)


@app.get("/optimize")
def optimize(
    dataset_id: str = Query(..., description="Dataset ID"),
    target_recall: float = Query(0.95, ge=0.5, le=1.0, description="Minimum recall to maintain"),
    radar_weight: float = Query(0.5, ge=0.0, le=1.0),
    camera_weight: float = Query(0.5, ge=0.0, le=1.0),
):
    """Find the optimal threshold that minimizes FP rate while keeping recall >= target."""
    if dataset_id not in _datasets:
        raise HTTPException(404, f"Dataset '{dataset_id}' not found.")

    df = _datasets[dataset_id].copy()
    df = compute_fused_confidence(df, radar_weight, camera_weight)

    result = find_optimal_threshold(df, target_recall=target_recall)

    before_metrics = ConfusionMetrics(**result["before_metrics"])
    after_raw = result["after_metrics"]
    # after_raw may have 'threshold' key from the optimizer — remove non-metric keys
    after_clean = {k: v for k, v in after_raw.items() if k in ConfusionMetrics.model_fields}
    after_metrics = ConfusionMetrics(**after_clean)

    return OptimizeResponse(
        dataset_id=dataset_id,
        target_recall=target_recall,
        before_threshold=result["before_threshold"],
        before_metrics=before_metrics,
        optimal_threshold=result["optimal_threshold"],
        after_metrics=after_metrics,
        fp_reduction_percent=result["fp_reduction_percent"],
        recall_held=result["recall_held"],
    )


@app.get("/export")
def export_report(
    dataset_id: str = Query(...),
    threshold: float = Query(0.5, ge=0.01, le=0.99),
    radar_weight: float = Query(0.5, ge=0.0, le=1.0),
    camera_weight: float = Query(0.5, ge=0.0, le=1.0),
):
    """Export analysis results as a downloadable CSV."""
    if dataset_id not in _datasets:
        raise HTTPException(404, f"Dataset '{dataset_id}' not found.")

    df = _datasets[dataset_id].copy()
    df = _run_full_pipeline(df, threshold, radar_weight, camera_weight)

    # Add decision column
    df["flagged_positive"] = df["fused_confidence"] >= threshold

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=adas_report_{dataset_id}.csv"},
    )


@app.get("/datasets")
def list_datasets():
    """List all loaded datasets."""
    return {
        did: {"rows": len(df), "columns": list(df.columns)}
        for did, df in _datasets.items()
    }
