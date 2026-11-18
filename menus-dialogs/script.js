(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- theme ---------- */
  var themeBtn = document.querySelector(".theme-btn");
  function isDark() { return root.getAttribute("data-theme") === "dark"; }
  function labelTheme() {
    if (!themeBtn) return;
    themeBtn.setAttribute("aria-label", isDark() ? "מעבר למצב בהיר" : "מעבר למצב כהה");
    var txt = themeBtn.querySelector(".txt");
    if (txt) txt.textContent = isDark() ? "מצב בהיר" : "מצב כהה";
  }
  if (themeBtn) {
    labelTheme();
    themeBtn.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("md-theme", next); } catch (e) { /* storage unavailable */ }
      labelTheme();
    });
  }

  /* ---------- part 2 opens only after every screen of part 1 was visited ---------- */
  var storageOk = true;
  function getItem(k) { try { return localStorage.getItem(k); } catch (e) { storageOk = false; return null; } }
  function setItem(k, v) { try { localStorage.setItem(k, v); } catch (e) { storageOk = false; } }
  if (/[?&]unlock\b/.test(window.location.search)) setItem("md-done-p1", "1");
  function part1Done() { var v = getItem("md-done-p1"); return !storageOk || v === "1"; }
  var isPart1 = document.body.classList.contains("p1");
  var isPart2 = document.body.classList.contains("p2");

  if (isPart2 && !part1Done()) { window.location.replace("index.html"); return; }

  if (getItem("md-done-p1") === "1") {
    document.querySelectorAll(".part:not(.two)").forEach(function (a) { a.classList.add("is-done"); });
  }
  if (getItem("md-done-p2") === "1") {
    document.querySelectorAll(".part.two").forEach(function (a) { a.classList.add("is-done"); });
  }

  if (!part1Done()) {
    document.querySelectorAll('.tabs a[href="part2.html"]').forEach(function (a) {
      a.classList.add("locked");
      a.setAttribute("aria-disabled", "true");
      a.title = "נפתח אחרי שמסיימים את חלק 1";
      a.addEventListener("click", function (e) { e.preventDefault(); });
    });
    document.querySelectorAll(".part.two").forEach(function (a) {
      a.classList.add("locked");
      a.setAttribute("aria-disabled", "true");
      a.addEventListener("click", function (e) {
        e.preventDefault();
        a.classList.remove("shake");
        void a.offsetWidth;
        a.classList.add("shake");
      });
    });
  }

  /* ---------- copy buttons ---------- */
  document.querySelectorAll(".code").forEach(function (block) {
    var btn = block.querySelector(".copy-btn");
    var pre = block.querySelector("pre");
    if (!btn || !pre) return;
    btn.addEventListener("click", function () {
      var text = pre.innerText;
      function done() {
        btn.textContent = "הועתק";
        btn.classList.add("copied");
        setTimeout(function () {
          btn.textContent = "העתקה";
          btn.classList.remove("copied");
        }, 1500);
      }
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { /* ignore */ }
        document.body.removeChild(ta);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }
    });
  });

  /* ---------- confetti ---------- */
  function confetti(el) {
    if (calm) return;
    var box = el.getBoundingClientRect();
    var layer = document.createElement("div");
    layer.className = "confetti";
    var colors = ["#ffc93c", "#2ec4a0", "#ff6f59", "#ffffff"];
    for (var i = 0; i < 26; i++) {
      var p = document.createElement("i");
      var angle = Math.random() * Math.PI * 2;
      var dist = 90 + Math.random() * 170;
      p.style.left = box.left + box.width / 2 + "px";
      p.style.top = box.top + box.height / 2 + "px";
      p.style.background = colors[i % colors.length];
      p.style.setProperty("--dx", Math.cos(angle) * dist + "px");
      p.style.setProperty("--dy", Math.sin(angle) * dist + 60 + "px");
      p.style.setProperty("--r", Math.random() * 720 - 360 + "deg");
      layer.appendChild(p);
    }
    document.body.appendChild(layer);
    setTimeout(function () { layer.remove(); }, 1300);
  }

  /* ---------- clickable phones ---------- */
  function flash(el) {
    el.classList.remove("flash");
    void el.offsetWidth;
    el.classList.add("flash");
  }

  document.querySelectorAll('.phone.live[data-live="menu"]').forEach(function (phone) {
    var dots = phone.querySelector(".p-dots");
    var status = phone.querySelector(".p-status");
    dots.addEventListener("click", function (e) {
      e.stopPropagation();
      phone.classList.toggle("open");
      phone.classList.add("used");
    });
    phone.querySelectorAll(".p-menu button").forEach(function (item) {
      item.addEventListener("click", function (e) {
        e.stopPropagation();
        status.textContent = "בחרת: " + item.textContent;
        phone.classList.remove("open");
        flash(status);
      });
    });
    phone.addEventListener("click", function () { phone.classList.remove("open"); });
  });

  document.querySelectorAll('.phone.live[data-live="dialog"]').forEach(function (phone) {
    var btn = phone.querySelector(".p-btn");
    var status = phone.querySelector(".p-status");
    var original = status.textContent;
    var timer = null;
    btn.addEventListener("click", function () {
      phone.classList.add("open", "used");
    });
    phone.querySelector(".p-scrim").addEventListener("click", function () {
      phone.classList.remove("open");
    });
    phone.querySelectorAll(".p-dialog .b button").forEach(function (b) {
      b.addEventListener("click", function () {
        phone.classList.remove("open");
        if (b.getAttribute("data-a") === "yes") {
          status.textContent = "";
          clearTimeout(timer);
          timer = setTimeout(function () {
            status.textContent = original;
            flash(status);
          }, 2200);
        }
      });
    });
  });

  /* ---------- checkpoint checklist ---------- */
  document.querySelectorAll(".check.live").forEach(function (list) {
    var items = Array.prototype.slice.call(list.querySelectorAll("button"));
    var good = list.parentNode.querySelector(".all-good");
    items.forEach(function (b) {
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () {
        var on = b.classList.toggle("on");
        b.setAttribute("aria-pressed", on ? "true" : "false");
        var all = items.every(function (x) { return x.classList.contains("on"); });
        if (good) {
          var was = good.classList.contains("show-it");
          good.classList.toggle("show-it", all);
          if (all && !was) confetti(good);
        }
      });
    });
  });

  /* ---------- screens ---------- */
  var screens = Array.prototype.slice.call(document.querySelectorAll(".screen"));
  if (!screens.length) return;

  var body = document.body;
  var prevPage = body.getAttribute("data-prev");
  var nextPage = body.getAttribute("data-next");
  var nextLabel = body.getAttribute("data-next-label") || "הבא ←";

  var label = document.querySelector(".progress-count");
  var titleEl = document.querySelector(".progress-title");
  var segsEl = document.querySelector(".segs");
  var prevBtn = document.querySelector("#prevBtn");
  var nextBtn = document.querySelector("#nextBtn");
  var current = 0;
  var helpBtn = document.querySelector("#helpBtn");
  var helpIndex = -1;
  screens.forEach(function (s, i) { if (s.classList.contains("mistakes")) helpIndex = i; });
  if (helpBtn) helpBtn.addEventListener("click", function () { if (helpIndex >= 0) go(helpIndex); });

  screens.forEach(function (s, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.title = s.getAttribute("data-title") || "";
    b.setAttribute("aria-label", "מסך " + (i + 1) + ": " + b.title);
    b.addEventListener("click", function () { go(i); });
    segsEl.appendChild(b);
  });
  var segs = Array.prototype.slice.call(segsEl.children);

  function fromHash() {
    var h = window.location.hash.replace("#", "");
    if (h === "last") return screens.length - 1;
    var n = parseInt(h, 10);
    if (!isNaN(n) && n >= 1 && n <= screens.length) return n - 1;
    return 0;
  }

  var seen = {};
  if (isPart1) {
    (getItem("md-seen-p1") || "").split(",").forEach(function (n) { if (n !== "") seen[n] = true; });
  }
  function markSeen() {
    if (!isPart1) return;
    seen[current] = true;
    setItem("md-seen-p1", Object.keys(seen).join(","));
    if (allSeen()) {
      setItem("md-done-p1", "1");
      document.querySelectorAll(".tabs a.locked").forEach(function (a) {
        var fresh = a.cloneNode(true);
        fresh.classList.remove("locked");
        fresh.removeAttribute("aria-disabled");
        fresh.removeAttribute("title");
        a.parentNode.replaceChild(fresh, a);
      });
    }
  }
  function allSeen() {
    for (var i = 0; i < screens.length; i++) if (!seen[i]) return false;
    return true;
  }

  function render() {
    screens.forEach(function (s, i) { s.classList.toggle("active", i === current); });
    markSeen();
    var note = document.querySelector(".pager-note");
    if (note) note.classList.remove("show-it");
    segs.forEach(function (d, i) {
      d.classList.toggle("active", i === current);
      d.classList.toggle("done", i < current);
    });
    label.textContent = (current + 1) + " / " + screens.length;
    titleEl.textContent = screens[current].getAttribute("data-title") || "";
    nextBtn.textContent = current === screens.length - 1 ? nextLabel : "הבא ←";
    if (helpBtn) helpBtn.hidden = helpIndex < 0 || current >= helpIndex;
    if (isPart2 && current === screens.length - 1 && getItem("md-done-p2") !== "1") {
      setItem("md-done-p2", "1");
      var mark = screens[current].querySelector(".big-check");
      if (mark) setTimeout(function () { confetti(mark); }, 500);
    }
  }

  function go(i) {
    current = i;
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", "#" + (i + 1));
    } else {
      window.location.hash = String(i + 1);
    }
    render();
    window.scrollTo(0, 0);
  }

  prevBtn.addEventListener("click", function () {
    if (current > 0) go(current - 1);
    else if (prevPage) window.location.href = prevPage;
  });
  nextBtn.addEventListener("click", function () {
    if (current < screens.length - 1) { go(current + 1); return; }
    if (isPart1 && storageOk && !allSeen()) {
      segs.forEach(function (d, i) {
        d.classList.remove("todo");
        if (!seen[i]) { void d.offsetWidth; d.classList.add("todo"); }
      });
      var note = document.querySelector(".pager-note");
      if (note) note.classList.add("show-it");
      return;
    }
    if (nextPage) window.location.href = nextPage;
  });
  window.addEventListener("hashchange", function () {
    current = fromHash();
    render();
  });

  current = fromHash();
  render();
})();
