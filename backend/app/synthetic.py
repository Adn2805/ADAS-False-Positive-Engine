"""Synthetic data generator — realistic ADAS detection events with proper ground-truth."""

import numpy as np
import pandas as pd
import uuid


def generate_synthetic_data(n_events: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic ADAS detection events.

    Unlike the reference project's random labels, this generator:
    - Creates correlated radar/camera confidence values
    - Models environment-dependent sensor degradation
    - Assigns ground_truth based on realistic detection logic (not random)
    - Produces a realistic ~20-30% false-positive rate
    """
    rng = np.random.default_rng(seed)

    environments = ["clear", "rain", "fog", "night", "glare"]
    env_weights = [0.40, 0.20, 0.10, 0.20, 0.10]  # clear is most common
    adas_actions = ["brake", "steer", "alert", "none"]
    action_weights = [0.25, 0.15, 0.30, 0.30]

    # Generate base data
    env_choices = rng.choice(environments, size=n_events, p=env_weights)
    action_choices = rng.choice(adas_actions, size=n_events, p=action_weights)

    # Speed: highway-like distribution (40-140 kph)
    speeds = rng.normal(loc=80, scale=25, size=n_events).clip(20, 160)

    # Base confidence: most detections are reasonably confident
    base_confidence = rng.beta(5, 2, size=n_events)  # skewed toward higher values

    # Radar confidence: slightly noisy version of base
    radar_noise = rng.normal(0, 0.08, size=n_events)
    radar_conf = (base_confidence + radar_noise).clip(0, 1)

    # Camera confidence: more affected by environment
    camera_noise = rng.normal(0, 0.06, size=n_events)
    camera_conf = base_confidence + camera_noise

    # Environmental degradation on camera
    env_degradation = {
        "clear": 0.0,
        "rain": -0.12,
        "fog": -0.20,
        "night": -0.15,
        "glare": -0.18,
    }
    for i in range(n_events):
        camera_conf[i] += env_degradation[env_choices[i]]
    camera_conf = camera_conf.clip(0, 1)

    # Fused confidence (simple average for generation, re-computed later)
    fused_conf = (radar_conf * 0.5 + camera_conf * 0.5)

    # Ground truth assignment — realistic logic:
    # High fused confidence + clear env → likely TP
    # Low fused confidence → likely FP or TN
    # Big sensor disagreement → higher FP chance
    ground_truths = []
    conf_gap = np.abs(radar_conf - camera_conf)

    for i in range(n_events):
        fc = fused_conf[i]
        gap = conf_gap[i]
        env = env_choices[i]
        action = action_choices[i]

        # Probability of actually being a real object
        real_object_prob = 0.70  # base rate

        # High confidence → more likely real
        if fc > 0.7:
            real_object_prob += 0.20
        elif fc < 0.4:
            real_object_prob -= 0.30

        # Big sensor gap → less reliable
        if gap > 0.3:
            real_object_prob -= 0.25

        # Bad weather → less reliable
        if env in ("fog", "glare"):
            real_object_prob -= 0.15
        elif env in ("rain", "night"):
            real_object_prob -= 0.08

        real_object_prob = max(0.05, min(0.95, real_object_prob))
        is_real = rng.random() < real_object_prob

        # Determine if the system detected it
        system_detected = action != "none"

        if system_detected and is_real:
            ground_truths.append("TP")
        elif system_detected and not is_real:
            ground_truths.append("FP")
        elif not system_detected and is_real:
            ground_truths.append("FN")
        else:
            ground_truths.append("TN")

    # Build DataFrame
    df = pd.DataFrame({
        "id": [str(uuid.uuid4())[:8] for _ in range(n_events)],
        "timestamp": np.cumsum(rng.exponential(0.5, size=n_events)),
        "frame_id": np.arange(1, n_events + 1),
        "speed_kph": np.round(speeds, 1),
        "radar_confidence": np.round(radar_conf, 4),
        "camera_confidence": np.round(camera_conf, 4),
        "fused_confidence": np.round(fused_conf, 4),
        "environment": env_choices,
        "adas_action": action_choices,
        "ground_truth": ground_truths,
    })

    return df
