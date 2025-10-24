async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`HTTP ${res.status}: ${t}`);
  }
  return res.json();
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("yt-form");
  const loader = document.getElementById("loader");
  const results = document.getElementById("results");
  const summary = document.getElementById("summary");
  const transcript = document.getElementById("transcript");
  const video = document.getElementById("video");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    results.classList.add("hidden");
    loader.classList.remove("hidden");

    const formData = new FormData(form);
    const payload = {
      yt_url: formData.get("yt_url"),
      target_lang: formData.get("target_lang") || null,
      length: formData.get("length") || "medium",
      style: formData.get("style") || "bullets",
      translate: formData.get("translate") === "on",
    };

    try {
      const data = await postJSON("/api/process", payload);
      summary.textContent = data.summary || "";
      transcript.textContent = data.transcript || "";

      const url = data.video?.webpage_url || payload.yt_url;
      video.innerHTML = `<iframe width="100%" height="315" src="https://www.youtube.com/embed/${extractId(url)}" frameborder="0" allowfullscreen></iframe>`;

      results.classList.remove("hidden");
    } catch (err) {
      alert(err.message);
    } finally {
      loader.classList.add("hidden");
    }
  });

  function extractId(url) {
    const m = String(url).match(/[?&]v=([^&]+)/) || String(url).match(/youtu\\.be\/([^?]+)/);
    return m ? m[1] : "";
  }
});