import { ShieldAlert } from "lucide-react";
import UploadPanel from "./components/UploadPanel";
import MetricsCards from "./components/MetricsCards";
import ThresholdSlider from "./components/ThresholdSlider";
import RootCauseCharts from "./components/RootCauseCharts";
import ConfidenceTimeline from "./components/ConfidenceTimeline";
import EventExplainer from "./components/EventExplainer";
import FilterBar from "./components/FilterBar";
import ExportButton from "./components/ExportButton";

import { useDatasetStore } from "./store/useDatasetStore";

function App() {
  const datasetId = useDatasetStore((s) => s.datasetId);

  return (
    <div className="layout">
      {/* Dynamic Background */}
      <div className="bg-glow bg-glow--1" />
      <div className="bg-glow bg-glow--2" />

      {/* Header */}
      <header className="header">
        <div className="header__brand">
          <div className="header__logo">
            <ShieldAlert size={24} />
          </div>
          <div>
            <h1 className="header__title">ADAS False-Positive Engine</h1>
            <p className="header__subtitle">Root Cause Diagnostic System v2</p>
          </div>
        </div>
        <div className="header__actions">
          {datasetId && <ExportButton />}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content container">
        {!datasetId ? (
          <div className="max-w-2xl mx-auto mt-12">
            <UploadPanel />
          </div>
        ) : (
          <div className="dashboard-content">
            <div className="mb-4rem max-w-3xl mx-auto">
              <UploadPanel />
            </div>

            {/* Row 2: Metrics + Slider */}
            <div className="grid-2col gap-3rem mb-4rem">
              <MetricsCards />
              <ThresholdSlider />
            </div>

            {/* Row 3: Root Cause + Timeline */}
            <div className="grid-2col gap-3rem mb-4rem">
              <RootCauseCharts />
              <ConfidenceTimeline />
            </div>

            {/* Row 4: Filters + Events */}
            <div className="event-section-wrapper mb-4rem">
              <FilterBar />
              <div className="mt-6">
                <EventExplainer />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
