const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${path} (${res.status})`);
  }
  return res.json();
}

export function getDashboard() {
  return request("/api/dashboard");
}

export function getDateWiseReport({ from, to, shift }) {
  const params = new URLSearchParams({ from, to });
  if (shift) params.set("shift", shift);
  return request(`/api/reports/date-wise?${params.toString()}`);
}

export function getSkuWiseReport({ from, to, shift, sku }) {
  const params = new URLSearchParams({ from, to });
  if (shift) params.set("shift", shift);
  if (sku) params.set("sku", sku);
  return request(`/api/reports/sku-wise?${params.toString()}`);
}

export async function resetCounts(note) {
  const res = await fetch(`${BASE_URL}/api/counts/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note }),
  });
  if (!res.ok) throw new Error("Reset failed");
  return res.json();
}
