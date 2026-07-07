import { useRef, useState } from "react";
import { Upload, Sparkles, FileUp, AlertTriangle, Database, ChevronDown, ChevronUp } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";

export default function UploadPanel() {
    const fileRef = useRef<HTMLInputElement>(null);
    const [showTutorial, setShowTutorial] = useState(false);
    const { generate, upload, loading, error, datasetId, analysis } = useDatasetStore();

    const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) upload(file);
    };

    return (
        <div className="upload-panel">
            <div className="upload-panel__inner">
                {!datasetId ? (
                    <>
                        <div className="upload-panel__icon">
                            <Upload size={48} strokeWidth={1.5} />
                        </div>
                        <h2 className="upload-panel__title">Load Detection Data</h2>
                        <p className="upload-panel__desc">
                            Upload a CSV detection log or generate synthetic demo data
                        </p>
                        <div className="upload-panel__actions flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
                            <button
                                className="btn btn--primary w-full sm:w-auto min-h-[44px]"
                                onClick={() => generate(500)}
                                disabled={loading}
                            >
                                <Sparkles size={18} />
                                {loading ? "Generating..." : "Generate Demo Data"}
                            </button>
                            <span className="upload-panel__divider">or</span>
                            <button
                                className="btn btn--outline w-full sm:w-auto min-h-[44px]"
                                onClick={() => fileRef.current?.click()}
                                disabled={loading}
                            >
                                <FileUp size={18} />
                                Upload CSV
                            </button>
                            <input
                                ref={fileRef}
                                type="file"
                                accept=".csv"
                                onChange={handleFile}
                                className="hidden"
                            />
                        </div>

                        <button
                            className="btn btn--ghost btn--sm"
                            style={{ marginTop: "2rem" }}
                            onClick={() => setShowTutorial(!showTutorial)}
                        >
                            <Database size={14} />
                            {showTutorial ? "Hide Data Format Guide" : "How to format your own data?"}
                            {showTutorial ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>

                        {showTutorial && (
                            <div className="upload-tutorial">
                                <div className="upload-tutorial__header">
                                    <Database size={16} style={{ color: "var(--accent)" }} />
                                    CSV Format Requirements
                                </div>
                                <p className="upload-tutorial__desc">
                                    Your CSV file must contain the following exact column headers to be processed correctly.
                                </p>
                                <div className="upload-tutorial__table-wrapper">
                                    <table className="csv-table">
                                        <thead>
                                            <tr>
                                                <th>frame</th>
                                                <th>timestamp</th>
                                                <th>radar_conf</th>
                                                <th>camera_conf</th>
                                                <th>ground_truth</th>
                                                <th>weather</th>
                                                <th>time_of_day</th>
                                                <th>speed</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr><td>1</td><td>1625097600.0</td><td>0.85</td><td>0.92</td><td>1</td><td>clear</td><td>day</td><td>65.5</td></tr>
                                            <tr><td>2</td><td>1625097600.1</td><td>0.45</td><td>0.78</td><td>0</td><td>rain</td><td>night</td><td>45.0</td></tr>
                                            <tr><td>3</td><td>1625097600.2</td><td>0.12</td><td>0.30</td><td>0</td><td>fog</td><td>day</td><td>30.2</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="upload-panel__loaded">
                        <div className="upload-panel__badge">
                            <span className="upload-panel__badge-dot" />
                            Dataset Loaded
                        </div>
                        <p className="upload-panel__meta">
                            ID: <code>{datasetId}</code> · {analysis?.total_events ?? "..."} events
                        </p>
                        <div className="upload-panel__actions">
                            <button
                                className="btn btn--sm btn--outline"
                                onClick={() => generate(500)}
                                disabled={loading}
                            >
                                <Sparkles size={14} /> New Demo Data
                            </button>
                            <button
                                className="btn btn--sm btn--outline"
                                onClick={() => fileRef.current?.click()}
                                disabled={loading}
                            >
                                <FileUp size={14} /> Upload New CSV
                            </button>
                            <input
                                ref={fileRef}
                                type="file"
                                accept=".csv"
                                onChange={handleFile}
                                className="hidden"
                            />
                        </div>
                    </div>
                )}

                {error && (
                    <div className="upload-panel__error">
                        <AlertTriangle size={16} /> {error}
                    </div>
                )}
            </div>
        </div>
    );
}
