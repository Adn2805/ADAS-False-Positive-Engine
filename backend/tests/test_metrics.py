"""Tests for metrics.py — sensor fusion and confusion matrix metrics."""

import pandas as pd
import numpy as np
from app.metrics import compute_fused_confidence, compute_confusion_metrics


class TestFusedConfidence:
    def test_equal_weights(self):
        df = pd.DataFrame({
            "radar_confidence": [0.8, 0.4],
            "camera_confidence": [0.6, 0.8],
        })
        result = compute_fused_confidence(df)
        expected = [0.7, 0.6]
        np.testing.assert_allclose(result["fused_confidence"], expected, atol=1e-6)

    def test_custom_weights(self):
        df = pd.DataFrame({
            "radar_confidence": [1.0, 0.0],
            "camera_confidence": [0.0, 1.0],
        })
        result = compute_fused_confidence(df, radar_weight=0.7, camera_weight=0.3)
        np.testing.assert_allclose(result["fused_confidence"], [0.7, 0.3], atol=1e-6)

    def test_does_not_mutate_input(self):
        df = pd.DataFrame({
            "radar_confidence": [0.5],
            "camera_confidence": [0.5],
        })
        original_id = id(df)
        result = compute_fused_confidence(df)
        assert id(result) != original_id  # should be a copy


class TestConfusionMetrics:
    def test_perfect_classifier(self):
        """All positives correctly flagged, no false positives."""
        df = pd.DataFrame({
            "fused_confidence": [0.9, 0.8, 0.1, 0.2],
            "ground_truth": ["TP", "FN", "FP", "TN"],
        })
        # threshold=0.5: flagged=[True, True, False, False]
        # actual_positive = [TP, FN] → [True, True, False, False]
        # TP=2, FP=0, FN=0, TN=2
        m = compute_confusion_metrics(df, threshold=0.5)
        assert m["tp"] == 2
        assert m["fp"] == 0
        assert m["fn"] == 0
        assert m["tn"] == 2
        assert m["precision"] == 1.0
        assert m["recall"] == 1.0
        assert m["fp_rate"] == 0.0

    def test_all_flagged(self):
        """Threshold so low everything is flagged positive."""
        df = pd.DataFrame({
            "fused_confidence": [0.9, 0.8, 0.6, 0.7],
            "ground_truth": ["TP", "FN", "FP", "TN"],
        })
        m = compute_confusion_metrics(df, threshold=0.01)
        # Everything flagged → tp=2, fp=2, fn=0, tn=0
        assert m["tp"] == 2
        assert m["fp"] == 2
        assert m["precision"] == 0.5
        assert m["recall"] == 1.0

    def test_nothing_flagged(self):
        """Threshold so high nothing is flagged positive."""
        df = pd.DataFrame({
            "fused_confidence": [0.3, 0.4, 0.2, 0.1],
            "ground_truth": ["TP", "FN", "FP", "TN"],
        })
        m = compute_confusion_metrics(df, threshold=0.99)
        assert m["tp"] == 0
        assert m["fp"] == 0
        assert m["fn"] == 2
        assert m["tn"] == 2
        assert m["recall"] == 0.0
        assert m["fp_rate"] == 0.0

    def test_known_confusion_matrix(self):
        """Hand-computed: threshold=0.5 on specific data."""
        df = pd.DataFrame({
            "fused_confidence": [0.9, 0.6, 0.3, 0.7, 0.4, 0.8],
            "ground_truth":     ["TP", "FP", "TP", "TN", "FN", "FN"],
        })
        # flagged (>=0.5): [T, T, F, T, F, T]
        # actual_pos (TP/FN): [T, F, T, F, T, T]
        # TP: flagged & actual → idx 0, 5 → 2
        # FP: flagged & ~actual → idx 1, 3 → 2
        # FN: ~flagged & actual → idx 2, 4 → 2
        # TN: ~flagged & ~actual → 0
        m = compute_confusion_metrics(df, threshold=0.5)
        assert m["tp"] == 2
        assert m["fp"] == 2
        assert m["fn"] == 2
        assert m["tn"] == 0
        assert m["precision"] == 0.5
        assert m["recall"] == 0.5
