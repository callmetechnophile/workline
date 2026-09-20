/**
 * Workline / ArmourFlow Frontend Centralized API Client
 * Seamlessly interfaces with Amazon API Gateway, CloudFront, or local development backend.
 */

import { getValidCognitoIdToken } from "./cognito";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://n70vojh6j7.execute-api.us-east-1.amazonaws.com/dev";

export async function fetchApi<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<{ data: T | null; error: string | null; status: number }> {
  const url = `${API_BASE_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;

  let authHeader: Record<string, string> = {};
  try {
    const token = await getValidCognitoIdToken();
    if (token) {
      authHeader["Authorization"] = `Bearer ${token}`;
    }
  } catch {}

  const headers = {
    "Content-Type": "application/json",
    ...authHeader,
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
