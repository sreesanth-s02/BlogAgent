/* ================= AUTH HELPERS ================= */

function saveToken(token) {
  localStorage.setItem("token", token);
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/ui/login.html";
}

/* ================= GUARD ================= */

function requireAuth() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "/ui/login.html";
  }
}

/* ================= LOGIN ================= */

async function login(username, password) {
  username = username.trim();
  password = password.trim();

  // UX-level validation
  if (!username || !password) {
    throw new Error("Both fields are required");
  }

  if (username.length > 50 || password.length > 50) {
    throw new Error("Input too long");
  }

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });

  if (!res.ok) {
    throw new Error("Invalid credentials");
  }

  const data = await res.json();
  saveToken(data.access_token);
}
