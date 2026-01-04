/* ================= IMAGE KEYWORDS ================= */
async function generateImageKeywords(title, summary) {
  if (!title || title.length > 200) {
    showToast("Invalid title for image generation", "error");
    return;
  }

  try {
    const res = await apiFetch("/image/keywords", {
      method: "POST",
      body: JSON.stringify({
        blog_title: title,
        blog_summary: summary.slice(0, 500)
      })
    });

    renderKeywords(res.keywords);
  } catch {
    showToast("Failed to generate image keywords", "error");
  }
}

function renderKeywords(keywords) {
  const box = document.getElementById("imageKeywords");
  box.innerHTML = "";

  if (!keywords.length) {
    box.innerHTML = "<p class='muted'>No keywords found</p>";
    return;
  }

  keywords.forEach(k => {
    const chip = document.createElement("span");
    chip.className = "keyword-chip";
    chip.textContent = k;
    chip.onclick = () => searchImages(k);
    box.appendChild(chip);
  });
}

/* ================= IMAGE SEARCH ================= */
async function searchImages(query) {
  if (query.length < 3 || query.length > 50) {
    showToast("Search must be 3–50 characters", "error");
    return;
  }

  const grid = document.getElementById("imageResults");
  grid.innerHTML = "<p class='muted'>Searching images…</p>";

  try {
    const res = await apiFetch(`/image/search?q=${encodeURIComponent(query)}`);

    grid.innerHTML = "";

    if (!res.results.length) {
      grid.innerHTML = "<p class='muted'>No images found</p>";
      return;
    }

    res.results.forEach(img => {
      const el = document.createElement("img");
      el.src = img.thumb;
      el.alt = query;
      el.onclick = () => selectImage(img.full);
      grid.appendChild(el);
    });
  } catch {
    grid.innerHTML = "<p class='error'>Image search failed</p>";
  }
}

/* ================= IMAGE SELECT ================= */
async function selectImage(url) {
  if (!currentBlogId) {
    showToast("Select a blog first", "error");
    return;
  }

  try {
    await apiFetch("/image/select", {
      method: "POST",
      body: JSON.stringify({
        blog_id: currentBlogId,
        image_url: url,
        position: "top"
      })
    });

    showToast("Image attached to blog", "success");
  } catch {
    showToast("Failed to attach image", "error");
  }
}
