import { useState } from "react";
import { ChevronDown, ChevronUp, Info, Wrench } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";
import type { DetectionEvent } from "../types";

const ROOT_CAUSE_COLORS: Record<string, string> = {
    sensor_ambiguity: "#4a90d9",
    environmental: "#f59e0b",
    threshold_error: "#8b5cf6",
    fusion_conflict: "#10b981",
    unknown: "#94a3b8",
};

const ROOT_CAUSE_LABELS: Record<string, string> = {
    sensor_ambiguity: "Sensor Ambiguity",
    environmental: "Environmental",
    threshold_error: "Threshold Error",
    fusion_conflict: "Fusion Conflict",
    unknown: "Unknown",
};

const GT_COLORS: Record<string, string> = {
    TP: "#10b981",
    FP: "#f43f5e",
    FN: "#eab308",
    TN: "#64748b",
};

export default function EventExplainer() {
    const analysis = useDatasetStore((s) => s.analysis);
    const selectedEventId = useDatasetStore((s) => s.selectedEventId);
    const selectEvent = useDatasetStore((s) => s.selectEvent);
    const filters = useDatasetStore((s) => s.filters);
    const [page, setPage] = useState(0);
    const PAGE_SIZE = 20;

    if (!analysis) return null;

    // Apply client-side filters
    let events = analysis.events;
    if (filters.rootCause) events = events.filter((e) => e.root_cause === filters.rootCause);
    if (filters.confidenceBucket) {
        const [lo, hi] = filters.confidenceBucket.split("-").map(Number);
        events = events.filter(
            (e) => e.fused_confidence >= lo && e.fused_confidence < hi,
        );
    }

    const totalPages = Math.ceil(events.length / PAGE_SIZE);
    const paginated = events.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

    const selectedEvent = analysis.events.find((e) => e.id === selectedEventId);

    return (
        <div className="events-section">
            <div className="events-section__main">
                <h3 className="section-title">
                    Detection Events <span className="section-title__count">({events.length})</span>
                </h3>

                <div className="events-list">
                    {paginated.map((event) => (
                        <EventCard
                            key={event.id}
                            event={event}
                            isSelected={event.id === selectedEventId}
                            onSelect={() => selectEvent(event.id === selectedEventId ? null : event.id)}
                        />
                    ))}
                </div>

                {totalPages > 1 && (
                    <div className="events-pagination">
                        <button disabled={page === 0} onClick={() => setPage(page - 1)} className="btn btn--sm btn--outline">
                            Prev
                        </button>
                        <span className="events-pagination__info">
                            Page {page + 1} / {totalPages}
                        </span>
                        <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)} className="btn btn--sm btn--outline">
                            Next
                        </button>
                    </div>
                )}
            </div>

            {/* Detail panel */}
            {selectedEvent && selectedEvent.explanation && (
                <div className="explainer-panel">
                    <h3 className="section-title">
                        <Info size={18} /> Explainability
                    </h3>
                    <div className="explainer-panel__content">
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label">Root Cause</span>
                            <span
                                className="tag"
                                style={{ background: ROOT_CAUSE_COLORS[selectedEvent.root_cause ?? ""] + "22", color: ROOT_CAUSE_COLORS[selectedEvent.root_cause ?? ""] }}
                            >
                                {ROOT_CAUSE_LABELS[selectedEvent.root_cause ?? ""] ?? selectedEvent.root_cause}
                            </span>
                        </div>
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label">Action Context</span>
                            <p className="explainer-panel__text">
                                Frame: {selectedEvent.frame_id} | Speed: {selectedEvent.speed_kph.toFixed(0)} km/h | Target Action: {selectedEvent.adas_action}
                            </p>
                        </div>
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label">Rule Fired</span>
                            <code className="explainer-panel__code">{selectedEvent.explanation.rule_fired}</code>
                        </div>
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label">Explanation</span>
                            <p className="explainer-panel__text">{selectedEvent.explanation.explanation}</p>
                        </div>
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label"><Wrench size={14} /> Recommendation</span>
                            <p className="explainer-panel__text explainer-panel__text--rec">
                                {selectedEvent.explanation.recommendation}
                            </p>
                        </div>
                        <div className="explainer-panel__field">
                            <span className="explainer-panel__label">Raw Values</span>
                            <div className="explainer-panel__raw">
                                {Object.entries(selectedEvent.explanation.raw_values).map(([k, v]) => (
                                    <div key={k} className="explainer-panel__raw-item">
                                        <span>{k.replace(/_/g, " ")}</span>
                                        <span>{typeof v === "number" ? v.toFixed(4) : v}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function EventCard({
    event,
    isSelected,
    onSelect,
}: {
    event: DetectionEvent;
    isSelected: boolean;
    onSelect: () => void;
}) {
    const rc = event.root_cause ?? "unknown";
    return (
        <div
            className={`event-card ${isSelected ? "event-card--selected" : ""}`}
            onClick={onSelect}
        >
            <div className="event-card__top flex flex-wrap items-center gap-2 mb-2 pr-6 relative">
                <span className="tag" style={{ background: (GT_COLORS[event.ground_truth] ?? "#6b7280") + "22", color: GT_COLORS[event.ground_truth] }}>
                    {event.ground_truth}
                </span>
                <span
                    className="tag"
                    style={{ background: (ROOT_CAUSE_COLORS[rc] ?? "#6b7280") + "22", color: ROOT_CAUSE_COLORS[rc] }}
                >
                    {ROOT_CAUSE_LABELS[rc] ?? rc}
                </span>
                <span className="event-card__env tag tag--sm">{event.environment}</span>
                <div className="absolute right-0 top-0 mt-0.5 opacity-50">
                    {isSelected ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
            </div>
            <div className="event-card__bottom">
                <span>Confidence: {event.fused_confidence.toFixed(3)}</span>
            </div>
        </div>
    );
}
