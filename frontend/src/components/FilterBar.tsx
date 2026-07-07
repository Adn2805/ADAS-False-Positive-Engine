import { Filter, X } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";

const ROOT_CAUSES = [
    { value: "sensor_ambiguity", label: "Sensor Ambiguity" },
    { value: "environmental", label: "Environmental" },
    { value: "threshold_error", label: "Threshold Error" },
    { value: "fusion_conflict", label: "Fusion Conflict" },
    { value: "unknown", label: "Unknown" },
];

const CONFIDENCE_BUCKETS = [
    { value: "0-0.25", label: "0 – 0.25" },
    { value: "0.25-0.5", label: "0.25 – 0.50" },
    { value: "0.5-0.75", label: "0.50 – 0.75" },
    { value: "0.75-1.01", label: "0.75 – 1.00" },
];

export default function FilterBar() {
    const { filters, setFilter, clearFilters, analysis } = useDatasetStore();
    if (!analysis) return null;

    const hasAnyFilter = Object.values(filters).some(Boolean);

    return (
        <div className="filter-bar">
            <div className="filter-bar__header">
                <Filter size={16} />
                <span>Filters</span>
                {hasAnyFilter && (
                    <button className="btn btn--xs btn--ghost" onClick={clearFilters}>
                        <X size={14} /> Clear
                    </button>
                )}
            </div>
            <div className="filter-bar__groups">
                <FilterGroup label="Root Cause" options={ROOT_CAUSES} value={filters.rootCause} onChange={(v) => setFilter("rootCause", v)} />
                <FilterGroup label="Confidence" options={CONFIDENCE_BUCKETS} value={filters.confidenceBucket} onChange={(v) => setFilter("confidenceBucket", v)} />
            </div>
        </div>
    );
}

function FilterGroup({
    label,
    options,
    value,
    onChange,
}: {
    label: string;
    options: { value: string; label: string }[];
    value: string | null;
    onChange: (v: string | null) => void;
}) {
    return (
        <div className="filter-group">
            <span className="filter-group__label">{label}</span>
            <div className="filter-group__chips">
                {options.map((opt) => (
                    <button
                        key={opt.value}
                        className={`filter-chip ${value === opt.value ? "filter-chip--active" : ""}`}
                        onClick={() => onChange(value === opt.value ? null : opt.value)}
                    >
                        {opt.label}
                    </button>
                ))}
            </div>
        </div>
    );
}
