import {
    Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend, ReferenceLine, ComposedChart,
} from "recharts";
import { useDatasetStore } from "../store/useDatasetStore";
import type { DetectionEvent } from "../types";

export default function ConfidenceTimeline() {
    const analysis = useDatasetStore((s) => s.analysis);
    const threshold = useDatasetStore((s) => s.threshold);

    if (!analysis) return null;

    // Prepare timeline data sorted by timestamp
    const sorted = [...analysis.events].sort((a, b) => a.timestamp - b.timestamp);

    const timelineData = sorted.map((e: DetectionEvent, i: number) => ({
        index: i,
        frame: e.frame_id,
        fused: e.fused_confidence,
        isFP: e.ground_truth === "FP" ? e.fused_confidence : null,
    }));

    return (
        <div className="charts-section">
            <h3 className="section-title">Confidence Timeline</h3>

            {/* Confidence lines */}
            <div className="chart-container chart-container--wide">
                <ResponsiveContainer width="100%" height={350}>
                    <ComposedChart data={timelineData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="frame" stroke="#94a3b8" tick={{ fill: "#cbd5e1" }} label={{ value: "Frame", position: "bottom", fill: "#cbd5e1" }} />
                        <YAxis stroke="#94a3b8" domain={[0, 1]} tick={{ fill: "#cbd5e1" }} label={{ value: "Confidence", angle: -90, position: "insideLeft", fill: "#cbd5e1" }} />
                        <Tooltip
                            contentStyle={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, color: "#f8fafc", backdropFilter: "blur(12px)" }}
                            formatter={(value: any, name: any) => [value?.toFixed(3) ?? "—", name]}
                        />
                        <Legend
                            wrapperStyle={{ paddingTop: "10px" }}
                            formatter={(value: string) => (
                                <span style={{ color: "#cbd5e1" }}>
                                    {value === "False Positive" ? "FP" : value}
                                </span>
                            )}
                        />

                        <ReferenceLine y={threshold} stroke="#f87171" strokeDasharray="8 4" label={{ value: `Threshold ${threshold.toFixed(2)}`, fill: "#f87171", fontSize: 11 }} />

                        <Line type="monotone" dataKey="fused" name="Fused Confidence" stroke="#22d3ee" dot={false} strokeWidth={2} />

                        {/* FP markers */}
                        <Line
                            type="monotone"
                            dataKey="isFP"
                            name="False Positive"
                            stroke="transparent"
                            dot={{ fill: "#ef4444", r: 4, stroke: "#ef4444" }}
                            legendType="circle"
                            connectNulls={false}
                        />

                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
