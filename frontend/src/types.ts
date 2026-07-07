/* ───────────── TypeScript types mirroring backend Pydantic schemas ───────────── */

export interface DetectionEvent {
    id: string;
    timestamp: number;
    frame_id: number;
    speed_kph: number;
    radar_confidence: number;
    camera_confidence: number;
    fused_confidence: number;
    environment: "clear" | "rain" | "fog" | "night" | "glare";
    adas_action: "brake" | "steer" | "alert" | "none";
    ground_truth: "TP" | "FP" | "TN" | "FN";
    root_cause: string | null;
    z_score: number | null;
    is_anomaly: boolean | null;
    explanation?: EventExplanation;
}

export interface EventExplanation {
    root_cause: string;
    rule_fired: string;
    explanation: string;
    recommendation: string;
    raw_values: {
        radar_confidence: number;
        camera_confidence: number;
        fused_confidence: number;
        confidence_gap: number;
        threshold: number;
        distance_to_threshold: number;
        environment: string;
    };
}

export interface ConfusionMetrics {
    tp: number;
    fp: number;
    fn: number;
    tn: number;
    precision: number;
    recall: number;
    f1: number;
    fp_rate: number;
}

export interface RootCauseCount {
    category: string;
    count: number;
    percentage: number;
}

export interface AnalysisResponse {
    dataset_id: string;
    threshold: number;
    radar_weight: number;
    camera_weight: number;
    total_events: number;
    metrics: ConfusionMetrics;
    root_cause_breakdown: RootCauseCount[];
    events: DetectionEvent[];
    anomaly_count: number;
}

export interface OptimizeResponse {
    dataset_id: string;
    target_recall: number;
    before_threshold: number;
    before_metrics: ConfusionMetrics;
    optimal_threshold: number;
    after_metrics: ConfusionMetrics;
    fp_reduction_percent: number;
    recall_held: boolean;
}

export interface UploadResponse {
    dataset_id: string;
    total_rows: number;
    valid_rows: number;
    warnings: string[];
}
