import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_API_URL || "http://localhost:4000/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 8000,
});

export async function predictDisease(payload) {
  const { data } = await api.post("/predict", payload);
  return data;
}

export default api;
