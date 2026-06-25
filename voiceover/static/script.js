/* AI Voice Over — Frontend Logic */

/**
 * Show/hide UI sections.
 */
function setUIState(state) {
  const spinner  = document.getElementById("spinner");
  const audio    = document.getElementById("audioSection");
  const narr     = document.getElementById("narrationSection");
  const empty    = document.getElementById("emptyState");
  const status   = document.getElementById("status");

  // Hide everything first
  [spinner, audio, narr, empty, status].forEach((el) => {
    el.classList.add("d-none");
    el.classList.remove("d-flex");
  });

  switch (state) {
    case "idle":
      empty.classList.remove("d-none");
      break;
    case "loading":
      spinner.classList.remove("d-none");
      break;
    case "done":
      audio.classList.remove("d-none");
      audio.classList.add("d-flex");
      break;
    case "error":
      status.classList.remove("d-none");
      break;
  }
}

/**
 * Display a status message.
 */
function showStatus(message, type = "info") {
  const el = document.getElementById("status");
  el.className = `alert alert-${type} py-2 mb-3`;
  el.textContent = message;
  el.classList.remove("d-none");
}

/**
 * Populate the Ollama models dropdown on page load.
 */
async function loadModels() {
  try {
    const resp  = await fetch("/api/models");
    const data  = await resp.json();
    const sel   = document.getElementById("model");
    const models = data.models || [];
    if (models.length) {
      sel.innerHTML = models
        .map((m) => `<option value="${escHtml(m)}">${escHtml(m)}</option>`)
        .join("");
    }
  } catch (_) {
    /* silently keep default "llama3" option */
  }
}

/**
 * Disable/enable the voice dropdown based on selected TTS engine.
 */
function onEngineChange() {
  const engine = document.getElementById("ttsEngine").value;
  const voiceSel = document.getElementById("voice");
  voiceSel.disabled = engine !== "edge_tts";
}

/**
 * Main generation function.
 */
async function generateVoice() {
  const text = document.getElementById("inputText").value.trim();
  if (!text) {
    showStatus("⚠️  Please enter some text first.", "warning");
    return;
  }

  const btn = document.getElementById("generateBtn");
  btn.disabled = true;

  setUIState("loading");
  document.getElementById("spinnerMsg").textContent =
    document.getElementById("useLlm").checked
      ? "Sending to LLama for narration…"
      : "Synthesizing voice…";

  const payload = {
    text,
    model:      document.getElementById("model").value,
    character:  document.getElementById("character").value,
    tts_engine: document.getElementById("ttsEngine").value,
    voice:      document.getElementById("voice").value,
    use_llm:    document.getElementById("useLlm").checked,
  };

  try {
    const resp = await fetch("/api/generate", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || "Unknown server error");
    }

    // Read audio blob
    const blob      = await resp.blob();
    const audioURL  = URL.createObjectURL(blob);
    const processed = resp.headers.get("X-Processed-Text") || text;

    // Update audio player
    const player = document.getElementById("audioPlayer");
    player.src   = audioURL;
    player.load();
    player.play().catch(() => {}); // auto-play (may be blocked by browser policy)

    // Update download link
    const ext  = payload.tts_engine === "edge_tts" ? "mp3" : "wav";
    const link = document.getElementById("downloadLink");
    link.href  = audioURL;
    link.download = `voiceover.${ext}`;

    // Show narration text
    const narrEl = document.getElementById("narrationText");
    narrEl.textContent = processed;
    document.getElementById("narrationSection").classList.remove("d-none");

    setUIState("done");
  } catch (err) {
    setUIState("error");
    showStatus(`❌ Error: ${err.message}`, "danger");
  } finally {
    btn.disabled = false;
  }
}

/**
 * Clear all inputs and reset UI.
 */
function clearAll() {
  document.getElementById("inputText").value = "";
  const player = document.getElementById("audioPlayer");
  player.src   = "";
  setUIState("idle");
}

/**
 * Simple HTML escape helper.
 */
function escHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  loadModels();
  document.getElementById("ttsEngine").addEventListener("change", onEngineChange);

  // Allow Ctrl+Enter to submit
  document.getElementById("inputText").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      generateVoice();
    }
  });

  setUIState("idle");
});
