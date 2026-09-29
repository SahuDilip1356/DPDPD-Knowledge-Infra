const configuredApiUrl = (import.meta.env.VITE_API_URL || "").trim();

export const API_BASE_URL = configuredApiUrl || (import.meta.env.DEV ? "http://localhost:8000" : "");
export const API_CONFIGURED = Boolean(API_BASE_URL);

export function apiUrl(path) {
  if (!API_CONFIGURED) {
    throw new Error("The API endpoint is not configured for this deployment.");
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, "")}${normalizedPath}`;
}

export async function apiFetch(path, options = {}) {
  return fetch(apiUrl(path), options);
}
