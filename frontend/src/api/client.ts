/* ───────────── Typed API client — all backend calls go through here ───────────── */

import type { AnalysisResponse, OptimizeResponse, UploadResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, init);
    if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(body.detail || `API error ${res.status}`);
    }
    return res.json();
}

export async function uploadCSV(file: File): Promise<UploadResponse> {
    const form = new FormData();
    form.append("file", file);
    return request<UploadResponse>("/upload", { method: "POST", body: form });
}

export async function generateData(nEvents: number = 500): Promise<UploadResponse> {
    return request<UploadResponse>("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ n_events: nEvents }),
    });
}

export async function analyze(
    datasetId: string,
    threshold: number = 0.5,
    radarWeight: number = 0.5,
    cameraWeight: number = 0.5,
): Promise<AnalysisResponse> {
    const params = new URLSearchParams({
        dataset_id: datasetId,
        threshold: threshold.toString(),
        radar_weight: radarWeight.toString(),
        camera_weight: cameraWeight.toString(),
    });
    return request<AnalysisResponse>(`/analyze?${params}`);
}

export async function optimize(
    datasetId: string,
    targetRecall: number = 0.95,
    radarWeight: number = 0.5,
    cameraWeight: number = 0.5,
): Promise<OptimizeResponse> {
    const params = new URLSearchParams({
        dataset_id: datasetId,
        target_recall: targetRecall.toString(),
        radar_weight: radarWeight.toString(),
        camera_weight: cameraWeight.toString(),
    });
    return request<OptimizeResponse>(`/optimize?${params}`);
}

export function getExportUrl(
    datasetId: string,
    threshold: number,
    radarWeight: number = 0.5,
    cameraWeight: number = 0.5,
): string {
    const params = new URLSearchParams({
        dataset_id: datasetId,
        threshold: threshold.toString(),
        radar_weight: radarWeight.toString(),
        camera_weight: cameraWeight.toString(),
    });
    return `${API_BASE}/export?${params}`;
}
