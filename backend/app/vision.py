"""Bounding-box IoU calculation and ground-truth labeling via OpenCV/NumPy."""

import numpy as np
from typing import Optional


def iou(box_a: list[float], box_b: list[float]) -> float:
    """
    Compute Intersection over Union for two bounding boxes.
    Each box is [x1, y1, x2, y2] where (x1,y1) is top-left, (x2,y2) is bottom-right.
    """
    xa1, ya1, xa2, ya2 = box_a
    xb1, yb1, xb2, yb2 = box_b

    inter_x1 = max(xa1, xb1)
    inter_y1 = max(ya1, yb1)
    inter_x2 = min(xa2, xb2)
    inter_y2 = min(ya2, yb2)

    inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)

    area_a = (xa2 - xa1) * (ya2 - ya1)
    area_b = (xb2 - xb1) * (yb2 - yb1)
    union = area_a + area_b - inter_area

    return float(inter_area / union) if union > 0 else 0.0


def label_from_iou(
    pred_box: Optional[list[float]],
    true_box: Optional[list[float]],
    iou_threshold: float = 0.5,
) -> str:
    """
    Derive ground-truth label from predicted and actual bounding boxes.
    Returns one of: TP, FP, TN, FN.
    """
    if pred_box is None and true_box is not None:
        return "FN"      # missed a real object
    if pred_box is not None and true_box is None:
        return "FP"      # detected something that wasn't there
    if pred_box is None and true_box is None:
        return "TN"      # correctly found nothing
    # Both boxes present — compare IoU
    score = iou(pred_box, true_box)  # type: ignore
    return "TP" if score >= iou_threshold else "FP"


def batch_label_from_iou(
    pred_boxes: list[Optional[list[float]]],
    true_boxes: list[Optional[list[float]]],
    iou_threshold: float = 0.5,
) -> list[str]:
    """Label a batch of detection events by IoU."""
    return [
        label_from_iou(p, t, iou_threshold)
        for p, t in zip(pred_boxes, true_boxes)
    ]
