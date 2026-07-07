"""Pydantic schemas for the ADAS False-Positive Root Cause Engine."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class DetectionEvent(BaseModel):
    """A single ADAS detection event — the core data unit."""
    id: str
    timestamp: float                    # seconds or frame index
    frame_id: int
    speed_kph: float
    radar_confidence: float = Field(ge=0, le=1)
    camera_confidence: float = Field(ge=0, le=1)
    fused_confidence: float = Field(ge=0, le=1, default=0.0)
    environment: Literal["clear", "rain", "fog", "night", "glare"]
    adas_action: Literal["brake", "steer", "alert", "none"]
    ground_truth: Literal["TP", "FP", "TN", "FN"]
    root_cause: Optional[str] = None

    # Optional bounding boxes for OpenCV/IoU labeling
    pred_bbox: Optional[list[float]] = None   # [x1, y1, x2, y2]
    true_bbox: Optional[list[float]] = None   # [x1, y1, x2, y2]


class ConfusionMetrics(BaseModel):
    """Confusion matrix derived metrics."""
    tp: int
    fp: int
    fn: int
    tn: int
    precision: float
    recall: float
    f1: float
    fp_rate: float


class RootCauseCount(BaseModel):
    """Count per root cause category."""
    category: str
    count: int
    percentage: float


class AnalysisResponse(BaseModel):
    """Full response from the /analyze endpoint."""
    dataset_id: str
    threshold: float
    radar_weight: float
    camera_weight: float
    total_events: int
    metrics: ConfusionMetrics
    root_cause_breakdown: list[RootCauseCount]
    events: list[DetectionEvent]


class OptimizeResponse(BaseModel):
    """Response from the /optimize endpoint."""
    dataset_id: str
    target_recall: float
    before_threshold: float
    before_metrics: ConfusionMetrics
    optimal_threshold: float
    after_metrics: ConfusionMetrics
    fp_reduction_percent: float
    recall_held: bool


class UploadResponse(BaseModel):
    """Response after uploading a CSV."""
    dataset_id: str
    total_rows: int
    valid_rows: int
    warnings: list[str]


class GenerateRequest(BaseModel):
    """Request to generate synthetic data."""
    n_events: int = Field(default=500, ge=10, le=10000)
