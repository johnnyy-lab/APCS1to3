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

  // =========================================================================
  // 章節題庫全新互動作答、即時回饋、速解顯現與焦點單題模式
  // =========================================================================
  var MODE_KEY = "pyth_apcs_reading_view_mode";
  var questions = Array.prototype.slice.call(document.querySelectorAll(".question-list-container .item"));

  if (questions.length > 0) {
    var currentIndex = 0;
    var currentMode = localStorage.getItem(MODE_KEY) || "card"; // 預設單題焦點模式

    function setViewMode(mode) {
      currentMode = mode;
      localStorage.setItem(MODE_KEY, mode);
      var btnCard = document.getElementById("btnModeCard");
      var btnList = document.getElementById("btnModeList");
      if (mode === "card") {
        document.body.classList.remove("mode-list");
        document.body.classList.add("mode-card");
        if (btnCard) btnCard.classList.add("active");
        if (btnList) btnList.classList.remove("active");
        updateCardView();
      } else {
        document.body.classList.remove("mode-card");
        document.body.classList.add("mode-list");
        if (btnCard) btnCard.classList.remove("active");
        if (btnList) btnList.classList.add("active");
        questions.forEach(function (q) {
          q.classList.remove("active-card");
        });
      }
    }

    function updateCardView() {
      if (currentMode !== "card") return;
      questions.forEach(function (q, idx) {
        if (idx === currentIndex) {
          q.classList.add("active-card");
        } else {
          q.classList.remove("active-card");
        }
      });
      var curNumEl = document.getElementById("currentQNum");
      var totalNumEl = document.getElementById("totalQNum");
      var badgeEl = document.getElementById("currentQBadge");
      var btnPrev = document.getElementById("btnPrevQ");
      var btnNext = document.getElementById("btnNextQ");
      var btnPrevB = document.getElementById("btnPrevQBottom");
      var btnNextB = document.getElementById("btnNextQBottom");

      if (curNumEl) curNumEl.textContent = String(currentIndex + 1);
      if (totalNumEl) totalNumEl.textContent = String(questions.length);

      var curQ = questions[currentIndex];
      if (curQ && badgeEl) {
        var tag = curQ.querySelector(".type-tag");
        if (tag) badgeEl.textContent = tag.textContent;
      }

      var hasPrev = currentIndex > 0;
      var hasNext = currentIndex < questions.length - 1;

      [btnPrev, btnPrevB].forEach(function (btn) {
        if (btn) btn.disabled = !hasPrev;
      });
      [btnNext, btnNextB].forEach(function (btn) {
        if (btn) btn.disabled = !hasNext;
      });
    }

    function goToIndex(idx) {
      if (idx < 0 || idx >= questions.length) return;
      currentIndex = idx;
      updateCardView();
      if (currentMode === "card") {
        var cardNav = document.getElementById("cardNavBar");
        if (cardNav) {
          cardNav.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }
    }

    var btnModeCard = document.getElementById("btnModeCard");
    var btnModeList = document.getElementById("btnModeList");
    if (btnModeCard) {
      btnModeCard.addEventListener("click", function () { setViewMode("card"); });
    }
    if (btnModeList) {
      btnModeList.addEventListener("click", function () { setViewMode("list"); });
    }

    var btnPrev = document.getElementById("btnPrevQ");
    var btnNext = document.getElementById("btnNextQ");
    var btnPrevB = document.getElementById("btnPrevQBottom");
    var btnNextB = document.getElementById("btnNextQBottom");

    if (btnPrev) btnPrev.addEventListener("click", function () { goToIndex(currentIndex - 1); });
    if (btnNext) btnNext.addEventListener("click", function () { goToIndex(currentIndex + 1); });
    if (btnPrevB) btnPrevB.addEventListener("click", function () { goToIndex(currentIndex - 1); });
    if (btnNextB) btnNextB.addEventListener("click", function () { goToIndex(currentIndex + 1); });

    questions.forEach(function (card) {
      var correctAns = card.getAttribute("data-answer") || "";
      var qid = card.getAttribute("data-qid") || "";
      var choiceBtns = card.querySelectorAll(".choice-btn");
      var feedbackBox = card.querySelector(".feedback-box");
      var doneCheckbox = card.querySelector('input[data-qid="' + qid + '"]');

      choiceBtns.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var chosen = btn.getAttribute("data-choice");
          if (!chosen) return;

          if (chosen === correctAns) {
            btn.classList.remove("is-wrong");
            btn.classList.add("is-correct");

            if (feedbackBox) {
              feedbackBox.style.display = "block";
            }

            if (doneCheckbox && !doneCheckbox.checked) {
              doneCheckbox.checked = true;
              var next = loadDone().filter(function (item) { return item !== qid; });
              next.push(qid);
              saveDone(next);
            }
          } else {
            btn.classList.add("is-wrong");
          }
        });
      });

      var toggleBtns = card.querySelectorAll(".btn-deep-toggle");
      var collapseBtns = card.querySelectorAll(".btn-deep-collapse");
      var deepPanel = card.querySelector(".deep-panel");

      toggleBtns.forEach(function (tbtn) {
        tbtn.addEventListener("click", function () {
          if (deepPanel) {
            deepPanel.style.display = "block";
          }
          if (feedbackBox) {
            feedbackBox.style.display = "block";
          }
        });
      });

      collapseBtns.forEach(function (cbtn) {
        cbtn.addEventListener("click", function () {
          if (deepPanel) {
            deepPanel.style.display = "none";
          }
        });
      });
    });

    var keyMap = { "1": "A", "2": "B", "3": "C", "4": "D" };
    window.addEventListener("keydown", function (e) {
      var tag = (document.activeElement && document.activeElement.tagName) || "";
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      var curQ = (currentMode === "card") ? questions[currentIndex] : null;

      if (e.key === "ArrowLeft") {
        if (currentMode === "card") {
          e.preventDefault();
          goToIndex(currentIndex - 1);
        }
      } else if (e.key === "ArrowRight") {
        if (currentMode === "card") {
          e.preventDefault();
          goToIndex(currentIndex + 1);
        }
      }

      var optKey = keyMap[e.key];
      if (optKey && curQ) {
        var targetBtn = curQ.querySelector('.choice-btn[data-choice="' + optKey + '"]');
        if (targetBtn) {
          e.preventDefault();
          targetBtn.click();
        }
      }
    });

    setViewMode(currentMode);
  }
})();
