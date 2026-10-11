(() => {
  const root = document.getElementById("chat-widget");
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  const tab = $("chat-tab"), tabWrap = $("chat-tab-wrap"), dock = $("chat-dock"), scroller = $("chat-scroll"), log = $("chat-log"), help = $("chat-help"),
    helpAsk = $("chat-help-ask"), helpDo = $("chat-help-do"), form = $("chat-form"), input = $("chat-input"), sendBtn = $("chat-send"),
    modeLabel = $("chat-mode"), teaser = $("chat-teaser"), teaserText = $("chat-teaser-text"), html = document.documentElement;
  let teasers = [];
  try { teasers = JSON.parse(root.dataset.teasers || "[]"); } catch (e) { teasers = []; }

  const store = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
  };
  const KEY_OPEN = "sitelogChatOpen", KEY_OFF = "sitelogChatTeaserOff", KEY_COUNT = "sitelogChatTeaserCount";
  const nodes = {};
  let loadPromise = null, busy = false, current = null, showTimer = null, hideTimer = null;

  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const isOpen = () => !dock.classList.contains("hidden");
  const scrollDown = () => { scroller.scrollTop = scroller.scrollHeight; };
  const safeHref = (h) => typeof h === "string" && h.startsWith("/") && !h.startsWith("//");

  // Until something has been run, the suggestion list is shown instead of an empty screen.
  function syncLayout() { help.classList.toggle("hidden", Object.keys(nodes).length > 0 || log.children.length > 0); }

  async function api(path, body) {
    const opts = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    let res;
    try { res = await fetch(path, opts); } catch (e) { throw new Error("Could not reach the assistant. Check your connection and try again."); }
    if (res.redirected) throw new Error("Your session has expired. Reload the page to sign in again.");
    let data = null;
    try { data = await res.json(); } catch (e) { /* not JSON */ }
    if (!res.ok || !data) throw new Error((data && data.error) || "Something went wrong. Please try again.");
    return data;
  }

  const tagFor = (label) => (!label ? "DEMO ANSWER" : label === "Help" ? "HELP" : label.startsWith("AI") ? "AI ANSWER" : "DEMO ANSWER");
  const modelFrom = (label) => { const m = /\((.+)\)/.exec(label || ""); return m ? m[1] : ""; };

  function actionButton(label, primary, onClick) {
    const b = el("button", primary ? "rounded bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-[#0b1220] shadow-[0_0_12px_rgba(52,211,153,.5)] hover:bg-emerald-400 disabled:opacity-50"
      : "rounded border border-slate-500 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-white/10 disabled:opacity-50", label);
    b.type = "button";
    b.addEventListener("click", onClick);
    return b;
  }

  // One entry per message: what you ran as a prompt line, what came back as a plain output block (no chat bubbles).
  function renderMessage(m) {
    if (m.role === "user") {
      const line = el("div", "break-words font-mono text-[13px] text-emerald-300");
      line.append(el("span", "mr-2 text-emerald-500", "\u203A"), document.createTextNode(m.text));
      return line;
    }
    const block = el("div", "border-l-2 border-slate-600 pl-3");
    block.append(el("div", "whitespace-pre-line text-slate-200", m.text));
    const meta = el("div", "mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs");
    const model = modelFrom(m.label);
    const tag = el("span", "break-all rounded border px-1.5 py-0.5 text-[10px] font-semibold tracking-wide " + (tagFor(m.label) === "AI ANSWER" ? "border-sky-400/60 text-sky-300 shadow-[0_0_10px_rgba(56,189,248,.35)]" : "border-slate-500 text-slate-400"),
      tagFor(m.label) + (model ? " \u00B7 " + model : ""));
    if (m.label) tag.title = m.label;
    meta.append(tag);
    (m.sources || []).forEach((s) => meta.append(el("span", "text-slate-500", s)));
    (m.links || []).filter((l) => safeHref(l.href)).forEach((l) => { const a = el("a", "text-emerald-300 underline hover:text-emerald-200", l.label); a.href = l.href; meta.append(a); });
    block.append(meta);
    if (m.pending_status === "pending") {
      const card = el("div", "mt-3 rounded-md border border-amber-400/40 bg-amber-400/10 p-3 shadow-[0_0_18px_rgba(251,191,36,.18)]");
      card.append(el("div", "text-[11px] font-semibold uppercase tracking-wide text-amber-300", "Ready to run - please review"));
      card.append(el("div", "mt-1 text-slate-100", m.pending_summary || ""));
      const row = el("div", "mt-3 flex gap-2");
      const yes = actionButton("Confirm", true, () => resolve(m.id, "confirm", [yes, no]));
      const no = actionButton("Cancel", false, () => resolve(m.id, "cancel", [yes, no]));
      row.append(yes, no); card.append(row); block.append(card);
    } else if (m.result) {
      const done = m.pending_status === "confirmed";
      const line = el("div", "mt-2 flex flex-wrap items-center gap-2 text-xs font-medium " + (done ? "text-emerald-300" : "text-slate-400"), (done ? "\u2713 " : "") + m.result);
      if (done && safeHref(m.result_href)) { const a = el("a", "underline", "View record"); a.href = m.result_href; line.append(a); }
      if (done) line.append(actionButton("Refresh page", false, () => location.reload()));
      block.append(line);
    }
    return block;
  }

  function addMessage(m) {
    const n = renderMessage(m);
    nodes[m.id] = n;
    log.append(n);
    syncLayout();
  }

  function showError(text) {
    const n = el("div", "rounded-md border border-red-400/40 bg-red-400/10 px-3 py-2 text-xs text-red-200", text);
    n.setAttribute("role", "alert");
    log.append(n); syncLayout(); scrollDown();
    setTimeout(() => { n.remove(); syncLayout(); }, 8000);
  }

  async function resolve(id, decision, buttons) {
    buttons.forEach((b) => { b.disabled = true; });
    try {
      const data = await api("/assistant/api/" + encodeURIComponent(id) + "/" + decision, {});
      if (data.error) showError(data.error);
      if (data.message && nodes[id]) { const fresh = renderMessage(data.message); nodes[id].replaceWith(fresh); nodes[id] = fresh; }
    } catch (e) { buttons.forEach((b) => { b.disabled = false; }); showError(e.message); }
    scrollDown();
  }

  async function send(text) {
    text = (text || "").trim();
    if (!text || busy) return;
    busy = true; sendBtn.disabled = true;
    await ensureLoaded();
    const temp = renderMessage({ role: "user", text });
    const working = el("div", "font-mono text-xs text-slate-500", "Working...");
    log.append(temp, working); syncLayout(); scrollDown();
    try {
      const data = await api("/assistant/api/ask", { message: text });
      temp.remove(); working.remove();
      data.messages.forEach(addMessage);
      input.value = "";
    } catch (e) { temp.remove(); working.remove(); syncLayout(); showError(e.message); }
    busy = false; sendBtn.disabled = false; scrollDown(); input.focus();
  }

  function suggestion(text, onClick) {
    const li = el("li");
    const b = el("button", "w-full rounded px-2 py-1.5 text-left text-slate-300 hover:bg-white/10 hover:text-white focus:outline-none focus:ring-1 focus:ring-emerald-400");
    b.type = "button";
    b.append(el("span", "mr-2 font-mono text-emerald-500", "\u203A"), document.createTextNode(text));
    b.addEventListener("click", onClick);
    li.append(b);
    return li;
  }

  async function loadHistory() {
    try {
      const data = await api("/assistant/api/history");
      modeLabel.textContent = data.ai_mode === "groq" ? "Model: " + data.model + " (Groq)" : "Demo mode: no AI model, keyword matching";
      log.replaceChildren();
      Object.keys(nodes).forEach((k) => delete nodes[k]);
      data.messages.forEach(addMessage);
      helpAsk.replaceChildren(...data.examples.map((ex) => suggestion(ex, () => send(ex))));
      helpDo.replaceChildren(...data.commands.map((c) => suggestion(c, () => { input.value = c; input.focus(); })));
      syncLayout(); scrollDown();
      return true;
    } catch (e) { showError(e.message); return false; }
  }

  // History loads once. Anything that sends a message waits for it so the two can't overwrite each other.
  function ensureLoaded() {
    if (!loadPromise) loadPromise = loadHistory().then((ok) => { if (!ok) loadPromise = null; });
    return loadPromise;
  }

  function openDock(focus) {
    stopTeasers();
    dock.classList.remove("hidden");
    tabWrap.classList.add("hidden");
    html.classList.add("assistant-open");
    tab.setAttribute("aria-expanded", "true");
    store.set(KEY_OPEN, "1");
    ensureLoaded();
    if (focus) input.focus();
  }
  function closeDock(focusTab) {
    dock.classList.add("hidden");
    tabWrap.classList.remove("hidden");
    html.classList.remove("assistant-open");
    tab.setAttribute("aria-expanded", "false");
    store.set(KEY_OPEN, "0");
    if (focusTab) tab.focus();
  }

  // ---- encouragement note: rotates through different messages, never nags once dismissed or used ----
  function stopTeasers() { clearTimeout(showTimer); clearTimeout(hideTimer); teaser.classList.add("hidden"); }
  function showTeaser() {
    const count = parseInt(store.get(KEY_COUNT) || "0", 10) || 0;
    if (isOpen() || store.get(KEY_OFF) || !teasers.length || count >= 12) return;
    current = teasers[count % teasers.length];
    teaserText.textContent = current.text;
    teaser.classList.remove("hidden");
    store.set(KEY_COUNT, String(count + 1));
    hideTimer = setTimeout(() => { teaser.classList.add("hidden"); showTimer = setTimeout(showTeaser, 25000); }, 9000);
  }

  tab.addEventListener("click", () => openDock(true));
  $("chat-collapse").addEventListener("click", () => closeDock(true));
  $("chat-clear").addEventListener("click", async () => {
    try { await api("/assistant/api/clear", {}); log.replaceChildren(); Object.keys(nodes).forEach((k) => delete nodes[k]); syncLayout(); input.focus(); }
    catch (e) { showError(e.message); }
  });
  form.addEventListener("submit", (e) => { e.preventDefault(); send(input.value); });
  teaserText.addEventListener("click", () => {
    const t = current; openDock(true);
    if (t && t.send) send(t.prompt); else if (t) { input.value = t.prompt; input.focus(); }
  });
  $("chat-teaser-close").addEventListener("click", () => { store.set(KEY_OFF, "1"); stopTeasers(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && isOpen()) closeDock(true); });

  syncLayout();
  if (store.get(KEY_OPEN) === "1") openDock(false); else showTimer = setTimeout(showTeaser, 3500);
})();
