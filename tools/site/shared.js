/* TID-CMM site — shared behaviour. Theme persistence shared with the assessment tool. */
(function () {
  var KEY = "tid-cmm-theme";
  function recall(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }

  function paint(t) {
    document.documentElement.setAttribute("data-theme", t);
    var b = document.getElementById("themebtn");
    if (b) {
      b.textContent = t === "dark" ? "☀ Light" : "☾ Dark";
      b.setAttribute("aria-pressed", String(t === "dark"));
    }
  }
  window.toggleTheme = function () {
    var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    save(KEY, next);
    paint(next);
  };
  var saved = recall(KEY);
  if (saved) paint(saved);
  else paint(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  document.addEventListener("DOMContentLoaded", function () {
    paint(document.documentElement.getAttribute("data-theme"));
    // mark the current page in the nav
    var path = location.pathname.replace(/\/$/, "") || "/";
    document.querySelectorAll(".topbar nav a").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.charAt(0) !== "/") return;
      var h = href.replace(/\/$/, "") || "/";
      if (h === path && !a.classList.contains("cta")) a.classList.add("here");
    });
  });
})();
