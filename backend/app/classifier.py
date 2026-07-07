"""Rule-based root cause classifier — deterministic, vectorized with NumPy."""

import pandas as pd
import numpy as np


def classify_root_cause(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Classify each false-positive event's root cause based on numeric features.
    Priority order (first matching rule wins):
      1. sensor_ambiguity  — |radar - camera| > 0.35
      2. environmental     — non-clear env AND fused_conf < 0.6
      3. threshold_error   — |fused_conf - threshold| < 0.05  (near boundary)
      4. fusion_conflict   — 0.15 < |radar - camera| <= 0.35
      5. unknown           — default
    """
    df = df.copy()
    conf_gap = (df["radar_confidence"] - df["camera_confidence"]).abs()

    conditions = [
        conf_gap > 0.35,
        (df["environment"] != "clear") & (df["fused_confidence"] < 0.6),
        (df["fused_confidence"] - threshold).abs() < 0.05,
        (conf_gap > 0.15) & (conf_gap <= 0.35),
    ]
    choices = [
        "sensor_ambiguity",
        "environmental",
        "threshold_error",
        "fusion_conflict",
    ]

    df["root_cause"] = np.select(conditions, choices, default="unknown")
    return df


def get_root_cause_explanation(event: dict, threshold: float) -> dict:
    """
    Return a human-readable explanation of WHY a specific root cause was assigned.
    Used by the Explainability panel in the frontend.
    """
    radar = event.get("radar_confidence", 0)
    camera = event.get("camera_confidence", 0)
    fused = event.get("fused_confidence", 0)
    env = event.get("environment", "clear")
    root = event.get("root_cause", "unknown")
    conf_gap = abs(radar - camera)

    explanations = {
        "sensor_ambiguity": {
            "rule": "|radar_confidence - camera_confidence| > 0.35",
            "detail": (
                f"Radar confidence ({radar:.3f}) and camera confidence ({camera:.3f}) "
                f"differ by {conf_gap:.3f}, exceeding the 0.35 ambiguity threshold. "
                f"This indicates the two sensors disagree significantly on whether "
                f"an object is present."
            ),
            "recommendation": (
                "Calibrate radar-camera alignment. Check for sensor mounting drift "
                "or interference. Consider temporal fusion to smooth transient disagreements."
            ),
        },
        "environmental": {
            "rule": 'environment != "clear" AND fused_confidence < 0.6',
            "detail": (
                f"Environment is '{env}' (non-clear) and fused confidence ({fused:.3f}) "
                f"is below 0.6, suggesting weather/lighting conditions degraded sensor "
                f"reliability enough to trigger a false detection."
            ),
            "recommendation": (
                f"Increase confidence threshold in '{env}' conditions. Add environment-aware "
                f"dynamic thresholding. Consider additional sensor modalities (e.g., LiDAR) "
                f"for weather resilience."
            ),
        },
        "threshold_error": {
            "rule": "|fused_confidence - threshold| < 0.05",
            "detail": (
                f"Fused confidence ({fused:.3f}) is within 0.05 of the decision threshold "
                f"({threshold:.3f}), placing it in the uncertainty zone. Small noise fluctuations "
                f"pushed it across the boundary."
            ),
            "recommendation": (
                "Implement hysteresis (different thresholds for activation vs. deactivation). "
                "Add a 'pending' state for near-boundary detections requiring additional frames "
                "of confirmation before triggering an ADAS action."
            ),
        },
        "fusion_conflict": {
            "rule": "0.15 < |radar_confidence - camera_confidence| <= 0.35",
            "detail": (
                f"Radar ({radar:.3f}) and camera ({camera:.3f}) show moderate disagreement "
                f"(gap: {conf_gap:.3f}). The fusion algorithm averaged conflicting signals, "
                f"producing an unreliable combined score."
            ),
            "recommendation": (
                "Use a conflict-aware fusion strategy (e.g., Dempster-Shafer instead of "
                "weighted average). Log conflicting frames for offline review."
            ),
        },
        "unknown": {
            "rule": "No specific rule matched",
            "detail": (
                f"This event (radar={radar:.3f}, camera={camera:.3f}, fused={fused:.3f}, "
                f"env='{env}') does not match any known failure pattern. It may represent "
                f"an edge case or a novel failure mode."
            ),
            "recommendation": (
                "Flag for human review. Collect additional telemetry (LiDAR, ultrasonic) "
                "for this scenario. Consider adding this as a new rule after analysis."
            ),
        },
    }

    info = explanations.get(root, explanations["unknown"])
    return {
        "root_cause": root,
        "rule_fired": info["rule"],
        "explanation": info["detail"],
        "recommendation": info["recommendation"],
        "raw_values": {
            "radar_confidence": radar,
            "camera_confidence": camera,
            "fused_confidence": fused,
            "confidence_gap": round(conf_gap, 4),
            "threshold": threshold,
            "distance_to_threshold": round(abs(fused - threshold), 4),
            "environment": env,
        },
    }
