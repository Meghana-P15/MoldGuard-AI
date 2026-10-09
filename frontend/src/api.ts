import type { BatchInput, PredictResponse, OptimizeResponse } from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function predictBatch(payload: BatchInput) {
  return request<PredictResponse>("/api/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function optimizeBatch(payload: BatchInput) {
  return request<OptimizeResponse>("/api/optimize", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
