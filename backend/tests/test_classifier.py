"""Tests for classifier.py — root cause classification rules."""

import pandas as pd
import numpy as np
from app.classifier import classify_root_cause, get_root_cause_explanation


class TestClassifyRootCause:
    def test_sensor_ambiguity(self):
        """Large radar-camera gap (>0.35) → sensor_ambiguity."""
        df = pd.DataFrame({
            "radar_confidence": [0.9],
            "camera_confidence": [0.3],
            "fused_confidence": [0.6],
            "environment": ["clear"],
        })
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "sensor_ambiguity"

    def test_environmental(self):
        """Non-clear env + low fused confidence → environmental."""
        df = pd.DataFrame({
            "radar_confidence": [0.5],
            "camera_confidence": [0.4],
            "fused_confidence": [0.45],
            "environment": ["fog"],
        })
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "environmental"

    def test_threshold_error(self):
        """Fused confidence very close to threshold → threshold_error."""
        df = pd.DataFrame({
            "radar_confidence": [0.5],
            "camera_confidence": [0.5],
            "fused_confidence": [0.52],
            "environment": ["clear"],
        })
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "threshold_error"

    def test_fusion_conflict(self):
        """Moderate gap (0.15 < gap <= 0.35) → fusion_conflict."""
        df = pd.DataFrame({
            "radar_confidence": [0.7],
            "camera_confidence": [0.45],
            "fused_confidence": [0.575],
            "environment": ["clear"],
        })
        # Gap = 0.25, which is > 0.15 and <= 0.35
        # Not near threshold (0.575 - 0.5 = 0.075 > 0.05)
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "fusion_conflict"

    def test_unknown(self):
        """No rules match → unknown."""
        df = pd.DataFrame({
            "radar_confidence": [0.5],
            "camera_confidence": [0.5],
            "fused_confidence": [0.8],
            "environment": ["clear"],
        })
        # Gap = 0, clear env, far from threshold
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "unknown"

    def test_priority_order(self):
        """sensor_ambiguity should take priority over environmental."""
        df = pd.DataFrame({
            "radar_confidence": [0.9],
            "camera_confidence": [0.2],
            "fused_confidence": [0.55],
            "environment": ["fog"],
        })
        # Gap = 0.7 (>0.35 → sensor_ambiguity)
        # Also: fog + 0.55 < 0.6 → environmental
        # But sensor_ambiguity has higher priority
        result = classify_root_cause(df, threshold=0.5)
        assert result["root_cause"].iloc[0] == "sensor_ambiguity"

    def test_does_not_mutate(self):
        df = pd.DataFrame({
            "radar_confidence": [0.5],
            "camera_confidence": [0.5],
            "fused_confidence": [0.5],
            "environment": ["clear"],
        })
        assert "root_cause" not in df.columns
        result = classify_root_cause(df, threshold=0.5)
        assert "root_cause" in result.columns
        assert "root_cause" not in df.columns  # original unchanged


class TestExplainability:
    def test_explanation_has_required_fields(self):
        event = {
            "radar_confidence": 0.9,
            "camera_confidence": 0.3,
            "fused_confidence": 0.6,
            "environment": "clear",
            "root_cause": "sensor_ambiguity",
        }
        exp = get_root_cause_explanation(event, threshold=0.5)
        assert "rule_fired" in exp
        assert "explanation" in exp
        assert "recommendation" in exp
        assert "raw_values" in exp
        assert exp["root_cause"] == "sensor_ambiguity"
        assert "0.35" in exp["rule_fired"]

    def test_unknown_explanation(self):
        event = {
            "radar_confidence": 0.5,
            "camera_confidence": 0.5,
            "fused_confidence": 0.8,
            "environment": "clear",
            "root_cause": "unknown",
        }
        exp = get_root_cause_explanation(event, threshold=0.5)
        assert exp["root_cause"] == "unknown"
        assert "edge case" in exp["explanation"].lower() or "novel" in exp["explanation"].lower()
