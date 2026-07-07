import { Shield, Target, Activity, AlertOctagon } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";

const CARDS = [
    { key: "precision", label: "Precision", icon: Target, color: "#4a90d9" },
    { key: "recall", label: "Recall", icon: Shield, color: "#8b5cf6" },
    { key: "f1", label: "F1 Score", icon: Activity, color: "#10b981" },
    { key: "fp_rate", label: "FP Rate", icon: AlertOctagon, color: "#f43f5e" },
] as const;

export default function MetricsCards() {
    const analysis = useDatasetStore((s) => s.analysis);
    if (!analysis) return null;

    const { metrics, total_events } = analysis;

    return (
        <div className="metrics-grid">
            {CARDS.map(({ key, label, icon: Icon, color }) => (
                <div key={key} className="metric-card" style={{ "--accent": color } as React.CSSProperties}>
                    <div className="metric-card__header">
                        <Icon size={20} style={{ color }} />
                        <span className="metric-card__label">{label}</span>
                    </div>
                    <div className="metric-card__value" style={{ color: "var(--text-primary)" }}>
                        {(metrics[key] * 100).toFixed(1)}%
                    </div>
                    <div className="metric-card__bar">
                        <div
                            className="metric-card__bar-fill"
                            style={{ width: `${metrics[key] * 100}%`, background: color }}
                        />
                    </div>
                </div>
            ))}

            {/* Summary cards */}
            <div className="metric-card">
                <div className="metric-card__header">
                    <span className="metric-card__label">Total Events</span>
                </div>
                <div className="metric-card__value" style={{ color: "var(--text-primary)" }}>
                    {total_events.toLocaleString()}
                </div>
            </div>



            <div className="metric-card">
                <div className="metric-card__header">
                    <span className="metric-card__label">Confusion Matrix</span>
                </div>
                <div className="metric-card__matrix">
                    <div className="matrix-cell matrix-cell--tp">TP {metrics.tp}</div>
                    <div className="matrix-cell matrix-cell--fp">FP {metrics.fp}</div>
                    <div className="matrix-cell matrix-cell--fn">FN {metrics.fn}</div>
                    <div className="matrix-cell matrix-cell--tn">TN {metrics.tn}</div>
                </div>
            </div>
        </div>
    );
}
