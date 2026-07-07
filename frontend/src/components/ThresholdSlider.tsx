import { useCallback, useEffect, useRef } from "react";
import { SlidersHorizontal, Zap } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";

export default function ThresholdSlider() {
    const {
        threshold, radarWeight, cameraWeight, datasetId,
        setThreshold, setRadarWeight, setCameraWeight,
        fetchAnalysis, fetchOptimize, optimizeResult,
        applyOptimalThreshold, loading,
    } = useDatasetStore();

    const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

    // Debounced fetch when threshold/weights change
    const debouncedFetch = useCallback(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            fetchAnalysis();
        }, 150);
    }, [fetchAnalysis]);

    useEffect(() => {
        if (datasetId) debouncedFetch();
        return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    }, [threshold, radarWeight, cameraWeight, datasetId, debouncedFetch]);

    if (!datasetId) return null;

    return (
        <div className="threshold-panel">
            <div className="threshold-panel__header">
                <SlidersHorizontal size={20} />
                <h3>Threshold & Sensor Weights</h3>
            </div>

            <div className="threshold-panel__controls">
                {/* Decision threshold */}
                <div className="slider-group">
                    <div className="slider-group__label">
                        <span>Decision Threshold</span>
                        <span className="slider-group__value">{threshold.toFixed(2)}</span>
                    </div>
                    <input
                        type="range"
                        min={0.05}
                        max={0.95}
                        step={0.01}
                        value={threshold}
                        onChange={(e) => setThreshold(parseFloat(e.target.value))}
                        className="slider"
                    />
                    <div className="slider-group__labels">
                        <span>More detections</span>
                        <span>Fewer false positives</span>
                    </div>
                </div>

                {/* Radar weight */}
                <div className="slider-group">
                    <div className="slider-group__label">
                        <span>Radar Weight</span>
                        <span className="slider-group__value">{radarWeight.toFixed(2)}</span>
                    </div>
                    <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={radarWeight}
                        onChange={(e) => setRadarWeight(parseFloat(e.target.value))}
                        className="slider"
                    />
                </div>

                {/* Camera weight */}
                <div className="slider-group">
                    <div className="slider-group__label">
                        <span>Camera Weight</span>
                        <span className="slider-group__value">{cameraWeight.toFixed(2)}</span>
                    </div>
                    <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={cameraWeight}
                        onChange={(e) => setCameraWeight(parseFloat(e.target.value))}
                        className="slider"
                    />
                </div>

                {/* Smart tune button */}
                <button
                    className="btn btn--accent"
                    onClick={() => fetchOptimize()}
                    disabled={loading}
                >
                    <Zap size={16} />
                    {loading ? "Optimizing..." : "Smart Tune"}
                </button>

                {/* Optimize result */}
                {optimizeResult && (
                    <div className="optimize-result">
                        <div className="optimize-result__header">Optimization Result</div>
                        <div className="optimize-result__grid">
                            <div className="optimize-result__item">
                                <span className="optimize-result__label">Optimal Threshold</span>
                                <span className="optimize-result__val">{optimizeResult.optimal_threshold.toFixed(2)}</span>
                            </div>
                            <div className="optimize-result__item">
                                <span className="optimize-result__label">Before FP Rate</span>
                                <span className="optimize-result__val">
                                    {(optimizeResult.before_metrics.fp_rate * 100).toFixed(1)}%
                                </span>
                            </div>
                            <div className="optimize-result__item">
                                <span className="optimize-result__label">After FP Rate</span>
                                <span className="optimize-result__val optimize-result__val--green">
                                    {(optimizeResult.after_metrics.fp_rate * 100).toFixed(1)}%
                                </span>
                            </div>
                        </div>
                        {optimizeResult.after_metrics.fp_rate >= optimizeResult.before_metrics.fp_rate && (
                            <p className="optimize-result__note text-xs text-slate-400 mb-3 leading-relaxed">
                                <strong className="text-slate-200 font-medium">Recall-constrained:</strong> Threshold is chosen to minimize FP rate while keeping recall &ge; {optimizeResult.target_recall * 100}%.
                                If the original threshold already had a lower FP rate, tuning may trade some FP rate increase for the recall guarantee.
                            </p>
                        )}
                        <button
                            className="btn btn--sm btn--primary w-full"
                            onClick={applyOptimalThreshold}
                        >
                            Apply Optimal Threshold
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
