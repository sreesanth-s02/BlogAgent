let currentBlogId = null;

/* ================= LOAD BLOG ================= */
async function loadBlog(blogId) {
  currentBlogId = blogId;

  const editor = document.getElementById("editor");
  editor.innerHTML = "<p class='muted'>Loading blog…</p>";

  try {
    const data = await apiFetch(`/blog/${blogId}`);

    editor.innerHTML = "";

    // Title
    const title = document.createElement("h1");
    title.textContent = data.main_heading;
    editor.appendChild(title);

    // Paragraphs
    data.paragraphs.forEach(p => {
      const para = document.createElement("p");
      para.textContent = p.text; // SAFE (no innerHTML)

      if (p.similarity >= 0.75) {
        para.classList.add("high-similarity");
        para.title = `High similarity: ${p.similarity}`;

        para.addEventListener("click", () => {
          openRewriteModal(
            data.id,
            p.id,
            p.text,
            p.similarity
          );
        });
      }

      editor.appendChild(para);
    });

    updatePublishState(data);
  } catch (err) {
    editor.innerHTML = "<p class='error'>Failed to load blog.</p>";
  }
}

/* ================= PUBLISH STATE ================= */
function updatePublishState(blog) {
  const btn = document.getElementById("publishBtn");

  if (!btn) return;

  if (blog.is_published) {
    btn.disabled = true;
    btn.textContent = "✅ Published";
  } else if (blog.overall_similarity >= 0.75) {
    btn.disabled = true;
    btn.textContent = "⚠ Similarity Too High";
  } else {
    btn.disabled = false;
    btn.textContent = "🚀 Publish";
    btn.onclick = () => publishBlog(blog.id, btn);
  }
}
