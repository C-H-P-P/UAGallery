const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

function getToken() {
  return localStorage.getItem("authToken");
}

export async function http<T>(
  path: string,
  options: {
    method?: HttpMethod;
    body?: unknown;
    auth?: boolean;
  } = {}
): Promise<T> {
  const method = options.method ?? "GET";

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.auth) {
    const token = getToken();
    if (token) headers.Authorization = `Token ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const text = await res.text();
  let data: any = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }

  if (!res.ok) {
    throw new Error(data?.detail || `HTTP ${res.status}`);
  }

  return data as T;
}
