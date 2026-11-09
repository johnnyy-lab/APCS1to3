/* 程式識讀的打勾只用 pyth_apcs_reading_done。
   不讀、不寫學習地圖的 pyth_apcs_completed_units 與 pyth_apcs_last_visited。
   深淺色沿用學習地圖的 pyth_apcs_theme。 */
(function () {
  var THEME_KEY = "pyth_apcs_theme";
  var DONE_KEY = "pyth_apcs_reading_done";

  function isLight() {
    return document.documentElement.getAttribute("data-theme") === "light";
  }

  function setTheme(light) {
    if (light) {
      document.documentElement.setAttribute("data-theme", "light");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    try {
      localStorage.setItem(THEME_KEY, light ? "light" : "dark");
    } catch (e) {}
    var btn = document.getElementById("btnThemeToggle");
    if (btn) {
      btn.textContent = light ? "🌙 深色模式" : "☀️ 淺色模式";
      btn.setAttribute("aria-pressed", light ? "true" : "false");
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", light ? "#f8fafc" : "#0a0f1d");
  }

  var themeBtn = document.getElementById("btnThemeToggle");
  if (themeBtn) {
    setTheme(isLight());
    themeBtn.addEventListener("click", function () {
      setTheme(!isLight());
    });
  }

  function loadDone() {
    try {
      var raw = JSON.parse(localStorage.getItem(DONE_KEY) || "[]");
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (id) {
        return typeof id === "string" && (/^[RFPDL]\d{2}$/.test(id) || /^Q-\d{2}-\d{2}-[RFPDL]\d{2}$/.test(id));
      });
    } catch (e) {
      return [];
    }
  }

  function saveDone(ids) {
    var unique = [];
    ids.forEach(function (id) {
      if (unique.indexOf(id) < 0) unique.push(id);
    });
    unique.sort();
    try {
      localStorage.setItem(DONE_KEY, JSON.stringify(unique));
    } catch (e) {}
  }

  document.querySelectorAll("input[data-qid]").forEach(function (box) {
    var id = box.getAttribute("data-qid");
    box.checked = loadDone().indexOf(id) >= 0;
    box.addEventListener("change", function () {
      var next = loadDone().filter(function (item) { return item !== id; });
      if (box.checked) next.push(id);
      saveDone(next);
    });
  });

  document.querySelectorAll("[data-type-count]").forEach(function (el) {
    var prefix = el.getAttribute("data-type-count");
    var count = loadDone().filter(function (id) {
      return id.charAt(0) === prefix;
    }).length;
    el.textContent = String(count);
  });
})();
