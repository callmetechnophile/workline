/**
 * Workline Frontend Centralized API Client
 * Connects the Next.js frontend strictly to Render R1 Core Gateway.
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:10000"
    : "http://localhost:10000");

export async function fetchApi<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<{ data: T | null; error: string | null; status: number }> {
  const url = `${API_BASE_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      return {
        data: null,
        error: `API error: HTTP ${res.status} ${res.statusText}`,
        status: res.status,
      };
    }

    const data = await res.json();
    return { data, error: null, status: res.status };
  } catch (err: any) {
    return {
      data: null,
      error: err?.message || "Network request failed",
      status: 0,
    };
  }
}
