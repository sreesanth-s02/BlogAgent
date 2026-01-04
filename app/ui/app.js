/* =====================================================
   GLOBAL APP CONTROLLER — ENTERPRISE READY
===================================================== */

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
  requireAuth();
  initTheme();
  checkBloggerStatus();
});

/* ================= DARK MODE ================= */
function toggleDarkMode() {
  document.body.classList.toggle("dark");
  localStorage.setItem(
    "dark",
    document.body.classList.contains("dark") ? "1" : "0"
  );
}

function initTheme() {
  if (localStorage.getItem("dark") === "1") {
    document.body.classList.add("dark");
  }
}

/* ================= TOAST ================= */
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerText = message;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 50);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/* ================= LOADING ================= */
function setLoading(btn, loading = true) {
  if (!btn) return;

  if (loading) {
    btn.disabled = true;
    btn.dataset.text = btn.innerText;
    btn.innerText = "⏳ Please wait...";
  } else {
    btn.disabled = false;
    btn.innerText = btn.dataset.text || btn.innerText;
  }
}

/* ================= BLOGGER ================= */
async function checkBloggerStatus() {
  try {
    const res = await apiFetch("/blogger/status");
    const el = document.getElementById("bloggerStatus");

    if (!el) return;

    if (res.connected) {
      el.innerText = "✅ Blogger Connected";
    } else {
      el.innerHTML = `<a href="/auth/blogger">🔗 Connect Blogger</a>`;
    }
  } catch {
    const el = document.getElementById("bloggerStatus");
    if (el) el.innerText = "⚠ Blogger error";
  }
}

/* ================= SIDEBAR MENU ================= */
function openMenu(e, blogId) {
  e.stopPropagation();
  closeMenu();

  const menu = document.createElement("div");
  menu.className = "menu";
  menu.innerHTML = `
    <div onclick="pinBlog(${blogId})">📌 Pin</div>
    <div onclick="renameBlog(${blogId})">✏️ Rename</div>
    <div onclick="archiveBlog(${blogId})">🗄 Archive</div>
    <div onclick="deleteBlog(${blogId})">🗑 Delete</div>
    <div onclick="shareBlog(${blogId})">🔗 Share</div>
  `;

  document.body.appendChild(menu);
  menu.style.top = `${e.clientY}px`;
  menu.style.left = `${e.clientX}px`;
}

function closeMenu() {
  document.querySelectorAll(".menu").forEach(m => m.remove());
}

document.addEventListener("click", closeMenu);

/* ================= MENU ACTIONS ================= */

async function deleteBlog(id) {
  if (!confirm("Delete this blog permanently?")) return;
  await apiFetch(`/blog/${id}`, { method: "DELETE" });
  showToast("Blog deleted", "success");
  loadSidebar();
}

async function archiveBlog(id) {
  await apiFetch(`/blog/${id}/archive`, { method: "POST" });
  showToast("Blog archived", "success");
  loadSidebar();
}

async function pinBlog(id) {
  await apiFetch(`/blog/${id}/pin`, { method: "POST" });
  showToast("Pin updated", "success");
  loadSidebar();
}

async function renameBlog(id) {
  const name = prompt("New blog name:");
  if (!name || name.length > 60) {
    showToast("Invalid name", "error");
    return;
  }

  await apiFetch(`/blog/${id}/rename`, {
    method: "PUT",
    body: JSON.stringify({ content_name: name })
  });

  showToast("Blog renamed", "success");
  loadSidebar();
}

async function shareBlog(id) {
  const res = await apiFetch(`/blog/${id}/share`, { method: "POST" });
  const url = location.origin + res.share_url;
  navigator.clipboard.writeText(url);
  showToast("Share link copied", "success");
}

/* ================= IMAGE PIPELINE ================= */

async function generateImageKeywords(title, summary) {
  return apiFetch("/image/keywords", {
    method: "POST",
    body: JSON.stringify({
      blog_title: title,
      blog_summary: summary
    })
  });
}

async function searchImages(query) {
  if (query.length < 3 || query.length > 50) {
    showToast("Search query must be 3–50 chars", "error");
    return;
  }
  return apiFetch(`/image/search?q=${encodeURIComponent(query)}`);
}

async function selectImage(blogId, imageUrl, position = "top") {
  await apiFetch("/image/select", {
    method: "POST",
    body: JSON.stringify({
      blog_id: blogId,
      image_url: imageUrl,
      position
    })
  });

  showToast("Image attached", "success");
}

/* ================= PUBLISH ================= */
async function publishBlog(blogId, btn) {
  if (!confirm("Publish this blog to Blogger?")) return;

  setLoading(btn, true);

  try {
    const res = await apiFetch("/publish", {
      method: "POST",
      body: JSON.stringify({ blog_id: blogId })
    });

    showToast("Published successfully!", "success");
    setLoading(btn, false);
    loadSidebar();
  } catch {
    setLoading(btn, false);
  }
}
