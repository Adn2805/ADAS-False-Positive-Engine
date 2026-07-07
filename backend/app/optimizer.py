"""Threshold optimizer — grid search for optimal FP/recall tradeoff."""

import numpy as np
import pandas as pd
from app.metrics import compute_confusion_metrics


def find_optimal_threshold(
    df: pd.DataFrame,
    target_recall: float = 0.95,
    search_min: float = 0.05,
    search_max: float = 0.95,
    step: float = 0.01,
) -> dict:
    """
    Grid-search over thresholds to find the one that minimizes false-positive
    rate while keeping recall >= target_recall.

    Returns the best threshold, its metrics, and the before/after comparison.
    """
    # Compute "before" metrics at the default threshold of 0.5
    before = compute_confusion_metrics(df, 0.5)

    best = None
    thresholds = np.arange(search_min, search_max + step, step)

    for t in thresholds:
        t_rounded = round(float(t), 2)
        m = compute_confusion_metrics(df, t_rounded)

        if m["recall"] >= target_recall:
            if best is None or m["fp_rate"] < best["fp_rate"]:
                best = {"threshold": t_rounded, **m}

    # If no threshold meets the recall target, pick the one with best recall
    if best is None:
        best_recall = None
        for t in thresholds:
            t_rounded = round(float(t), 2)
            m = compute_confusion_metrics(df, t_rounded)
            if best_recall is None or m["recall"] > best_recall["recall"]:
                best_recall = {"threshold": t_rounded, **m}
            elif m["recall"] == best_recall["recall"] and m["fp_rate"] < best_recall["fp_rate"]:
                best_recall = {"threshold": t_rounded, **m}
        best = best_recall

    # Calculate FP reduction
    if before["fp_rate"] > 0 and best is not None:
        fp_reduction = ((before["fp_rate"] - best["fp_rate"]) / before["fp_rate"]) * 100
    else:
        fp_reduction = 0.0

    return {
        "before_threshold": 0.5,
        "before_metrics": before,
        "optimal_threshold": best["threshold"] if best else 0.5,
        "after_metrics": best if best else before,
        "fp_reduction_percent": round(fp_reduction, 2),
        "target_recall": target_recall,
        "recall_held": best["recall"] >= target_recall if best else False,
    }
