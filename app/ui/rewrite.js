let rewriteTarget = null;

/* ================= OPEN MODAL ================= */
function openRewriteModal(blogId, sentenceId, text, similarity) {
  if (!blogId || !sentenceId) return;

  rewriteTarget = { blogId, sentenceId };

  document.getElementById("rewriteOriginal").textContent = text;
  document.getElementById("rewriteSimilarity").textContent =
    `Similarity: ${(similarity * 100).toFixed(1)}%`;

  document.getElementById("rewriteInstruction").value = "";
  document.getElementById("rewriteModal").classList.remove("hidden");
}

/* ================= CLOSE MODAL ================= */
function closeRewriteModal() {
  rewriteTarget = null;
  document.getElementById("rewriteModal").classList.add("hidden");
}

/* ================= SUBMIT ================= */
async function submitRewrite() {
  if (!rewriteTarget) return;

  const textarea = document.getElementById("rewriteInstruction");
  const instruction = textarea.value.trim();

  if (!instruction || instruction.length > 200) {
    showToast("Instruction must be under 200 characters", "error");
    return;
  }

  textarea.disabled = true;

  try {
    await apiFetch("/rewrite", {
      method: "POST",
      body: JSON.stringify({
        blog_id: rewriteTarget.blogId,
        sentence_id: rewriteTarget.sentenceId,
        instruction
      })
    });

    showToast("Sentence rewritten", "success");
    closeRewriteModal();
    loadBlog(rewriteTarget.blogId);
  } catch {
    showToast("Rewrite failed", "error");
  } finally {
    textarea.disabled = false;
  }
}
