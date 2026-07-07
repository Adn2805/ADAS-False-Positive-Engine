"""Sensor fusion and confusion-matrix metrics — all NumPy-vectorized."""

import pandas as pd
import numpy as np


def compute_fused_confidence(
    df: pd.DataFrame,
    radar_weight: float = 0.5,
    camera_weight: float = 0.5,
) -> pd.DataFrame:
    """
    Compute weighted sensor fusion confidence.
    Weights are exposed as tunables (unlike the reference project).
    """
    df = df.copy()
    total = radar_weight + camera_weight
    rw = radar_weight / total
    cw = camera_weight / total
    df["fused_confidence"] = (
        df["radar_confidence"] * rw + df["camera_confidence"] * cw
    )
    return df


def compute_confusion_metrics(df: pd.DataFrame, threshold: float) -> dict:
    """
    Given a decision threshold `t`, a detection is flagged positive if
    fused_confidence >= t.  Compare against ground_truth to build a
    confusion matrix and derive precision, recall, F1, and FP rate.
    """
    flagged_positive = df["fused_confidence"] >= threshold
    actual_positive = df["ground_truth"].isin(["TP", "FN"])

    tp = int((flagged_positive & actual_positive).sum())
    fp = int((flagged_positive & ~actual_positive).sum())
    fn = int((~flagged_positive & actual_positive).sum())
    tn = int((~flagged_positive & ~actual_positive).sum())

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fp_rate = fp / (fp + tn) if (fp + tn) else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "fp_rate": round(fp_rate, 4),
    }
