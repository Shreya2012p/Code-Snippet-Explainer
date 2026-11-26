const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function analyzeCode(payload) {
  const response = await fetch(`${API}/api/analyze`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Unable to analyze code.");
  return data;
}
export async function getHealth() {
  const response = await fetch(`${API}/api/health`);
  if (!response.ok) throw new Error("Backend is unavailable.");
  return response.json();
}
