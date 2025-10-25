export async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch (error) {
      // Ignore JSON parsing failures, fall back to status text.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function normaliseList(value) {
  if (!value) {
    return [];
  }
  if (Array.isArray(value)) {
    return value;
  }
  return String(value)
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean);
}
