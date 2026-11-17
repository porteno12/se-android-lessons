(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---------- copy buttons ---------- */
  document.querySelectorAll(".code").forEach(function (block) {
    var btn = block.querySelector(".copy-btn");
    var pre = block.querySelector("pre");
    if (!btn || !pre) return;
    btn.addEventListener("click", function () {
      var text = pre.innerText;
      function done() {
        btn.textContent = "הועתק ✓";
        btn.classList.add("copied");
        setTimeout(function () {
          btn.textContent = "העתקה";
          btn.classList.remove("copied");
        }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
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
    });
  });

  /* ---------- screens ---------- */
  var screens = Array.prototype.slice.call(document.querySelectorAll(".screen"));
  if (!screens.length) return;

  var body = document.body;
  var prevPage = body.getAttribute("data-prev");
  var nextPage = body.getAttribute("data-next");
  var nextLabel = body.getAttribute("data-next-label") || "הבא";

  var fill = document.querySelector(".progress-fill");
  var label = document.querySelector(".progress-count");
  var titleEl = document.querySelector(".progress-title");
  var dotsEl = document.querySelector(".segs");
  var prevBtn = document.querySelector("#prevBtn");
  var nextBtn = document.querySelector("#nextBtn");
  var current = 0;

  screens.forEach(function (s, i) {
    var b = document.createElement("button");
    b.type = "button";
    b.title = s.getAttribute("data-title") || "";
    b.setAttribute("aria-label", "מסך " + (i + 1) + ": " + b.title);
    b.addEventListener("click", function () { go(i); });
    dotsEl.appendChild(b);
  });
  var dots = Array.prototype.slice.call(dotsEl.children);

  function fromHash() {
    var h = window.location.hash.replace("#", "");
    if (h === "last") return screens.length - 1;
    var n = parseInt(h, 10);
    if (!isNaN(n) && n >= 1 && n <= screens.length) return n - 1;
    return 0;
  }

  function render() {
    screens.forEach(function (s, i) { s.classList.toggle("active", i === current); });
    dots.forEach(function (d, i) {
      d.classList.toggle("active", i === current);
      d.classList.toggle("done", i < current);
    });
    if (fill) fill.style.width = ((current + 1) / screens.length) * 100 + "%";
    label.textContent = "מסך " + (current + 1) + " מתוך " + screens.length;
    titleEl.textContent = screens[current].getAttribute("data-title") || "";
    nextBtn.textContent = current === screens.length - 1 ? nextLabel : "הבא ←";
    prevBtn.textContent = "→ הקודם";
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
