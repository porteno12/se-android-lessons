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
    themeBtn.setAttribute("title", isDark() ? "מצב בהיר" : "מצב כהה");
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

  function render() {
    screens.forEach(function (s, i) { s.classList.toggle("active", i === current); });
    segs.forEach(function (d, i) {
      d.classList.toggle("active", i === current);
      d.classList.toggle("done", i < current);
    });
    label.textContent = (current + 1) + " / " + screens.length;
    titleEl.textContent = screens[current].getAttribute("data-title") || "";
    nextBtn.textContent = current === screens.length - 1 ? nextLabel : "הבא ←";
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
    if (current < screens.length - 1) go(current + 1);
    else if (nextPage) window.location.href = nextPage;
  });
  window.addEventListener("hashchange", function () {
    current = fromHash();
    render();
  });

  current = fromHash();
  render();
})();
