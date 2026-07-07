/* ───────────── Zustand store — single source of truth for app state ───────────── */

import { create } from "zustand";
import type { AnalysisResponse, OptimizeResponse } from "../types";
import { analyze, optimize, generateData, uploadCSV } from "../api/client";

interface Filters {
    rootCause: string | null;
    confidenceBucket: string | null;
}

interface DatasetState {
    /* Data */
    datasetId: string | null;
    analysis: AnalysisResponse | null;
    optimizeResult: OptimizeResponse | null;

    /* Controls */
    threshold: number;
    radarWeight: number;
    cameraWeight: number;
    filters: Filters;

    /* UI */
    loading: boolean;
    error: string | null;
    selectedEventId: string | null;

    /* Actions */
    generate: (n?: number) => Promise<void>;
    upload: (file: File) => Promise<void>;
    fetchAnalysis: () => Promise<void>;
    fetchOptimize: (targetRecall?: number) => Promise<void>;
    setThreshold: (t: number) => void;
    setRadarWeight: (w: number) => void;
    setCameraWeight: (w: number) => void;
    setFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
    clearFilters: () => void;
    selectEvent: (id: string | null) => void;
    applyOptimalThreshold: () => void;
}

const INITIAL_FILTERS: Filters = {
    rootCause: null,
    confidenceBucket: null,
};

export const useDatasetStore = create<DatasetState>((set, get) => ({
    datasetId: null,
    analysis: null,
    optimizeResult: null,
    threshold: 0.5,
    radarWeight: 0.5,
    cameraWeight: 0.5,
    filters: { ...INITIAL_FILTERS },
    loading: false,
    error: null,
    selectedEventId: null,

    generate: async (n = 500) => {
        set({ loading: true, error: null });
        try {
            const res = await generateData(n);
            set({ datasetId: res.dataset_id });
            await get().fetchAnalysis();
        } catch (e: unknown) {
            set({ error: (e as Error).message, loading: false });
        }
    },

    upload: async (file: File) => {
        set({ loading: true, error: null });
        try {
            const res = await uploadCSV(file);
            set({ datasetId: res.dataset_id });
            await get().fetchAnalysis();
        } catch (e: unknown) {
            set({ error: (e as Error).message, loading: false });
        }
    },

    fetchAnalysis: async () => {
        const { datasetId, threshold, radarWeight, cameraWeight } = get();
        if (!datasetId) return;
        set({ loading: true, error: null });
        try {
            const result = await analyze(datasetId, threshold, radarWeight, cameraWeight);
            set({ analysis: result, loading: false });
        } catch (e: unknown) {
            set({ error: (e as Error).message, loading: false });
        }
    },

    fetchOptimize: async (targetRecall = 0.95) => {
        const { datasetId, radarWeight, cameraWeight } = get();
        if (!datasetId) return;
        set({ loading: true, error: null });
        try {
            const result = await optimize(datasetId, targetRecall, radarWeight, cameraWeight);
            set({ optimizeResult: result, loading: false });
        } catch (e: unknown) {
            set({ error: (e as Error).message, loading: false });
        }
    },

    setThreshold: (t) => set({ threshold: t }),
    setRadarWeight: (w) => set({ radarWeight: w }),
    setCameraWeight: (w) => set({ cameraWeight: w }),
    setFilter: (key, value) =>
        set((s) => ({ filters: { ...s.filters, [key]: value } })),
    clearFilters: () => set({ filters: { ...INITIAL_FILTERS } }),
    selectEvent: (id) => set({ selectedEventId: id }),

    applyOptimalThreshold: () => {
        const { optimizeResult } = get();
        if (optimizeResult) {
            set({ threshold: optimizeResult.optimal_threshold });
        }
    },
}));
