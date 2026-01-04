let activeMenu = null;

/* ================= LOAD SIDEBAR ================= */
async function loadSidebar(archived = false) {
  const list = document.getElementById("sidebarList");
  list.textContent = "Loading…";

  try {
    const blogs = await apiFetch(`/blogs?archived=${archived}`);
    list.innerHTML = "";

    if (!blogs.length) {
      list.textContent = archived ? "No archived blogs" : "No blogs yet";
      return;
    }

    blogs.forEach(blog => {
      const row = document.createElement("div");
      row.className = "sidebar-row";

      const title = document.createElement("span");
      title.textContent = blog.content_name;
      title.onclick = () => loadBlog(blog.id);

      const menuBtn = document.createElement("button");
      menuBtn.className = "menu-btn";
      menuBtn.textContent = "⋮";

      menuBtn.onclick = e => {
        e.stopPropagation();
        toggleMenu(blog, menuBtn);
      };

      row.append(title, menuBtn);
      list.appendChild(row);
    });
  } catch {
    list.textContent = "Failed to load blogs";
  }
}

/* ================= MENU ================= */
function toggleMenu(blog, anchor) {
  closeMenu();

  const menu = document.createElement("div");
  menu.className = "context-menu";

  const actions = [
    ["📌 Pin", () => pinBlog(blog.id)],
    ["✏ Rename", () => renameBlog(blog.id)],
    ["📁 Archive", () => archiveBlog(blog.id)],
    ["🗑 Delete", () => deleteBlog(blog.id)],
    ["🔗 Share", () => shareBlog(blog.id)]
  ];

  actions.forEach(([label, handler]) => {
    const item = document.createElement("div");
    item.textContent = label;
    item.onclick = async () => {
      closeMenu();
      await handler();
    };
    menu.appendChild(item);
  });

  document.body.appendChild(menu);

  const rect = anchor.getBoundingClientRect();
  menu.style.top = `${rect.bottom + 6}px`;
  menu.style.left = `${rect.left}px`;

  activeMenu = menu;
  document.addEventListener("click", closeMenu);
}

function closeMenu() {
  if (activeMenu) {
    activeMenu.remove();
    activeMenu = null;
    document.removeEventListener("click", closeMenu);
  }
}

/* ================= ACTIONS ================= */
async function pinBlog(id) {
  await apiFetch(`/blog/${id}/pin`, { method: "POST" });
  showToast("Pinned", "success");
  loadSidebar();
}

async function archiveBlog(id) {
  await apiFetch(`/blog/${id}/archive`, { method: "POST" });
  showToast("Archived", "success");
  loadSidebar();
}

async function deleteBlog(id) {
  if (!confirm("Delete this blog permanently?")) return;
  await apiFetch(`/blog/${id}`, { method: "DELETE" });
  document.getElementById("editor").innerHTML = "";
  showToast("Deleted", "success");
  loadSidebar();
}

async function renameBlog(id) {
  const name = prompt("New blog name (max 80 chars):");
  if (!name || name.length > 80) {
    showToast("Invalid name", "error");
    return;
  }

  await apiFetch(`/blog/${id}/rename`, {
    method: "PUT",
    body: JSON.stringify({ content_name: name.trim() })
  });

  showToast("Renamed", "success");
  loadSidebar();
}

async function shareBlog(id) {
  try {
    const data = await apiFetch(`/blog/${id}/share`, { method: "POST" });
    await navigator.clipboard.writeText(location.origin + data.share_url);
    showToast("Share link copied", "success");
  } catch {
    showToast("Failed to copy link", "error");
  }
}
