import type {
  AgentRunResponse,
  AnalyzeResponse,
  BatchInput,
  OptimizeResponse,
  PredictResponse,
} from "./types";

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

export function runAgenticAnalysis(
  payload: BatchInput,
  objective = "Evaluate this planned batch and recommend lower-waste, lower-energy settings only when justified.",
) {
  return request<AgentRunResponse>("/api/agent/run", {
    method: "POST",
    body: JSON.stringify({ objective, batch: payload }),
  });
}

export function analyzeBatch(payload: BatchInput) {
  return request<AnalyzeResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
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
