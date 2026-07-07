import { Download } from "lucide-react";
import { useDatasetStore } from "../store/useDatasetStore";
import { getExportUrl } from "../api/client";

export default function ExportButton() {
    const { datasetId, threshold, radarWeight, cameraWeight } = useDatasetStore();

    if (!datasetId) return null;

    const handleExport = () => {
        const url = getExportUrl(datasetId, threshold, radarWeight, cameraWeight);
        window.open(url, "_blank");
    };

    return (
        <button className="btn btn--outline btn--sm" onClick={handleExport}>
            <Download size={16} />
            Export Report CSV
        </button>
    );
}
