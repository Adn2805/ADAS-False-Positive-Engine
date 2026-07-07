import {
    PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
    CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { useDatasetStore } from "../store/useDatasetStore";

const COLORS: Record<string, string> = {
    sensor_ambiguity: "#4a90d9", // Muted sky blue
    environmental: "#f59e0b",    // Amber
    threshold_error: "#8b5cf6",  // Violet
    fusion_conflict: "#10b981",  // Emerald
    unknown: "#94a3b8",          // Slate
};

const LABELS: Record<string, string> = {
    sensor_ambiguity: "Sensor Ambiguity",
    environmental: "Environmental",
    threshold_error: "Threshold Error",
    fusion_conflict: "Fusion Conflict",
    unknown: "Unknown",
};

export default function RootCauseCharts() {
    const analysis = useDatasetStore((s) => s.analysis);
    const setFilter = useDatasetStore((s) => s.setFilter);
    if (!analysis) return null;

    const data = analysis.root_cause_breakdown.map((d) => ({
        ...d,
        name: LABELS[d.category] ?? d.category,
        fill: COLORS[d.category] ?? "#6b7280",
    }));

    return (
        <div className="charts-section">
            <h3 className="section-title">Root Cause Breakdown</h3>
            <div className="charts-row">
                {/* Pie chart */}
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={data}
                                dataKey="count"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                innerRadius={50}
                                paddingAngle={3}
                                onClick={(entry: any) => setFilter("rootCause", entry.payload.category)}
                                style={{ cursor: "pointer" }}
                            >
                                {data.map((d, i) => (
                                    <Cell key={i} fill={d.fill} stroke="transparent" />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, color: "#f8fafc", backdropFilter: "blur(12px)" }}
                                formatter={(value: any, name: any) => [`${value} events`, name]}
                            />
                            <Legend
                                formatter={(value: string) => <span style={{ color: "#cbd5e1" }}>{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Bar chart */}
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={data} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis type="number" stroke="#94a3b8" />
                            <YAxis dataKey="name" type="category" stroke="#94a3b8" width={120} tick={{ fontSize: 12, fill: "#e2e8f0" }} />
                            <Tooltip
                                contentStyle={{ background: "rgba(15, 23, 42, 0.8)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, color: "#f8fafc", backdropFilter: "blur(12px)" }}
                            />
                            <Bar
                                dataKey="count"
                                radius={[0, 6, 6, 0]}
                                onClick={(entry: any) => setFilter("rootCause", entry.payload.category)}
                                style={{ cursor: "pointer" }}
                            >
                                {data.map((d, i) => (
                                    <Cell key={i} fill={d.fill} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
