import axios from "axios";

function normalizeBaseUrl(rawUrl) {
  const fallback = "http://localhost:4000/api/v1";
  const value = (rawUrl || fallback).trim().replace(/\/+$/, "");

  if (value.endsWith("/api/v1")) {
    return value;
  }

  return `${value}/api/v1`;
}

const api = axios.create({
  baseURL: normalizeBaseUrl(import.meta.env.VITE_BACKEND_API_URL),
  headers: { "Content-Type": "application/json" },
  timeout: 8000,
});

export async function predictDisease(payload) {
  const { data } = await api.post("/predict", payload);
  return data;
}

export default api;
