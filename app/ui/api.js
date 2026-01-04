const API_BASE = "/api/v1";

/* ================= TOKEN ================= */
function getToken() {
  return localStorage.getItem("token");
}

/* ================= API FETCH ================= */
async function apiFetch(path, options = {}) {
  const token = getToken();

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });

  // Global auth handling
  if (res.status === 401) {
    showToast("Session expired. Please login again.", "error");
    logout();
    throw new Error("Unauthorized");
  }

  if (res.status === 403) {
    showToast("Access denied.", "error");
    throw new Error("Forbidden");
  }

  if (res.status === 429) {
    showToast("Too many requests. Slow down.", "error");
    throw new Error("Rate limited");
  }

  if (!res.ok) {
    const msg = await res.text();
    showToast(msg || "API Error", "error");
    throw new Error(msg);
  }

  // Some endpoints may return empty body
  try {
    return await res.json();
  } catch {
    return {};
  }
}
