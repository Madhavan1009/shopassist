(function () {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const SUGGEST = {
    C101: ["Where is my water bottle?", "Can I return my earbuds?", "How much refund will I get for the earbuds, and when?", "Can I return the kurta I bought?", "Do you have running shoes under ₹3,500?", "Show me order SE-2001"],
    C102: ["Show me my orders", "Can I return my smartwatch?", "Can I return the honey?", "If I return the running shoes, when do I get my money?", "What is the return window for electronics?", "Is the Smartwatch Fit 2 in stock?"],
    C103: ["Can I cancel my book order?", "My mixer grinder arrived damaged. What refund will I get?", "How long does standard delivery take?", "Is delivery free for orders above ₹499?", "Is Cash on Delivery available?", "Do you have a yoga mat?"]
  };
  let people = [];
  let current = null;
  let hasKey = false;
  let busy = false;

  function saved(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) {
      return null;
    }
    return null;
  }

  async function api(path, options) {
    const res = await fetch(path, options);
    let body = null;
    try { body = await res.json(); } catch (e) { body = null; }
    if (!res.ok) throw new Error(body && body.detail ? body.detail : "Request failed (" + res.status + ")");
    return body;
  }

  function inline(t) {
    return esc(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
  }

  function markdown(text) {
    const out = [];
    let list = null;
    String(text || "").split(/\r?\n/).forEach((raw) => {
      const line = raw.trim();
      const item = line.match(/^(?:[-*•]|\d+[.)])\s+(.*)$/);
      if (item) {
        if (!list) { list = []; }
        list.push("<li>" + inline(item[1]) + "</li>");
        return;
      }
      if (list) { out.push("<ul>" + list.join("") + "</ul>"); list = null; }
      if (!line) return;
      const head = line.replace(/^#{1,6}\s+/, "");
      const cls = /^source:/i.test(head.replace(/\*/g, "")) ? ' class="src"' : "";
      out.push("<p" + cls + ">" + (head !== line ? "<strong>" + inline(head) + "</strong>" : inline(line)) + "</p>");
    });
    if (list) out.push("<ul>" + list.join("") + "</ul>");
    return out.join("");
  }

  function scrollDown() {
    const t = $("#thread");
    t.scrollTop = t.scrollHeight;
  }

  function addMessage(role, html, extra) {
    const row = document.createElement("div");
    row.className = "msg " + role;
    row.innerHTML = '<span class="who">' + (role === "user" ? initials(current.name) : "SA") + '</span><div class="bubble' + (extra || "") + '">' + html + "</div>";
    $("#thread").appendChild(row);
    scrollDown();
    return row;
  }

  function initials(name) {
    return name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
  }

  function stepsHtml(steps) {
    return steps.map((s, i) => {
      const what = s.kind === "delegate"
        ? "<b>ShopAssist</b> delegated to <b>" + esc(s.to || "a desk") + "</b>"
        : "<b>" + esc(s.agent) + "</b> called <code>" + esc(s.tool) + "(" + esc(Object.entries(s.args || {}).map((a) => a[0] + "=" + JSON.stringify(a[1])).join(", ")) + ")</code>";
      return '<div class="step"><span class="n">' + (i + 1) + "</span><div>" + what + "<br><code>" + esc(s.detail || "") + "</code></div></div>";
    }).join("");
  }

  function renderAnswer(row, r) {
    const bubble = row.querySelector(".bubble");
    if (r.status !== "ok") {
      bubble.classList.add("err");
      bubble.innerHTML = "<p>" + esc(r.answer) + "</p>";
      return;
    }
    const tools = [];
    (r.steps || []).forEach((s) => { if (s.kind === "tool" && tools.indexOf(s.tool) < 0) tools.push(s.tool); });
    const tags = (r.agents || []).map((a) => '<span class="tag agent">' + esc(a) + "</span>")
      .concat(tools.map((t) => '<span class="tag tool">' + esc(t) + "</span>"))
      .concat((r.pages || []).map((p) => '<span class="tag page">Policy p.' + p + "</span>"))
      .concat(['<span class="tag time">' + r.seconds + " s</span>"]);
    if ((r.steps || []).length) tags.push('<button type="button" class="tag steps-btn">Show steps</button>');
    bubble.innerHTML = markdown(r.answer) + '<div class="meta">' + tags.join("") + "</div>" + ((r.steps || []).length ? '<div class="steps" hidden>' + stepsHtml(r.steps) + "</div>" : "");
    const btn = bubble.querySelector(".steps-btn");
    if (btn) btn.addEventListener("click", () => {
      const box = bubble.querySelector(".steps");
      box.hidden = !box.hidden;
      btn.textContent = box.hidden ? "Show steps" : "Hide steps";
    });
  }

  async function ask(text) {
    const q = text.trim();
    if (!q || busy || !current) return;
    busy = true;
    $("#send").disabled = true;
    $("#welcome").hidden = true;
    addMessage("user", "<p>" + esc(q) + "</p>");
    const row = addMessage("bot", '<span class="typing"><i></i><i></i><i></i></span>');
    try {
      const r = await api("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ customer_id: current.customer_id, message: q }) });
      renderAnswer(row, r);
    } catch (e) {
      renderAnswer(row, { status: "error", answer: e.message });
    } finally {
      busy = false;
      $("#send").disabled = false;
      scrollDown();
    }
  }

  function renderPeople() {
    $("#people").innerHTML = people.map((p) => '<button type="button" class="person' + (current && p.customer_id === current.customer_id ? " on" : "") + '" data-id="' + p.customer_id + '"><span class="av">' + initials(p.name) + "</span><span><b>" + esc(p.name) + "</b><small>" + esc(p.city) + " &middot; " + p.orders.length + " orders</small></span></button>").join("");
    document.querySelectorAll(".person").forEach((b) => b.addEventListener("click", () => select(b.dataset.id)));
  }

  function select(id) {
    current = people.find((p) => p.customer_id === id) || people[0];
    saved("shopassist.customer", current.customer_id);
    renderPeople();
    $("#orders").innerHTML = current.orders.map((o) => "<li><code>" + esc(o.order_id) + "</code><span>" + esc(o.product) + '</span><span class="st ' + esc(o.status) + '">' + esc(o.status) + "</span></li>").join("");
    resetThread();
  }

  function resetThread() {
    document.querySelectorAll("#thread .msg").forEach((m) => m.remove());
    $("#welcome").hidden = false;
    $("#w-name").textContent = current.name.split(" ")[0];
    $("#suggest").innerHTML = (SUGGEST[current.customer_id] || []).map((q) => '<button type="button">' + esc(q) + "</button>").join("");
    document.querySelectorAll("#suggest button").forEach((b) => b.addEventListener("click", () => ask(b.textContent)));
  }

  async function newChat() {
    if (!current || busy) return;
    try { await api("/api/memory/" + current.customer_id, { method: "DELETE" }); } catch (e) { }
    resetThread();
  }

  function chip(id, cls, text) {
    const c = $(id);
    c.className = "chip " + cls;
    c.innerHTML = "<i></i>" + esc(text);
  }

  async function init() {
    try {
      const s = await api("/api/status");
      hasKey = s.has_api_key;
      chip("#chip-host", s.running_on === "Azure App Service" ? "az" : "ok", s.running_on);
      chip("#chip-model", "ok", s.model);
      chip("#chip-key", hasKey ? "ok" : "bad", hasKey ? "API key set" : "API key missing");
      if (!hasKey) {
        const n = $("#notice");
        n.textContent = "OPENAI_API_KEY is not set. Add it to .env on your laptop, or to Environment variables in Azure App Service, then restart the app.";
        n.hidden = false;
      }
      people = await api("/api/customers");
      select(saved("shopassist.customer") || people[0].customer_id);
    } catch (e) {
      chip("#chip-host", "bad", "Server not reachable");
    }
  }

  $("#composer").addEventListener("submit", (e) => {
    e.preventDefault();
    const box = $("#input");
    const text = box.value;
    box.value = "";
    box.style.height = "";
    ask(text);
  });
  $("#input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      $("#composer").requestSubmit();
    }
  });
  $("#input").addEventListener("input", (e) => {
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + "px";
  });
  $("#new-chat").addEventListener("click", newChat);
  init();
})();
