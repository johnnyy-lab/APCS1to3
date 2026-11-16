/* 全真模擬試卷。目前只有一份。
   成績與作答只寫 pyth_apcs_reading_exam_v1。
   不讀、不寫 pyth_apcs_reading_done、pyth_apcs_completed_units、pyth_apcs_last_visited。
   深淺色沿用 pyth_apcs_theme。
   題目頁沒有答案。READING_EXAM_KEY 要等交卷才載入 reading-answers.js。 */
(function () {
  var THEME_KEY = "pyth_apcs_theme";
  var STORE_KEY = "pyth_apcs_reading_exam_v1";
  var DURATION = 90 * 60 * 1000;
  var LETTERS = ["A", "B", "C", "D"];

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

  var app = document.getElementById("examApp");
  if (!app) return;

  var gate = document.getElementById("examGate");
  var run = document.getElementById("examRun");
  var scoreBox = document.getElementById("examScore");
  var clock = document.getElementById("examClock");
  var progress = document.getElementById("examProgress");
  var questions = Array.prototype.slice.call(document.querySelectorAll(".exam-q"));
  var navButtons = Array.prototype.slice.call(document.querySelectorAll(".qnav-btn"));
  var state = null;
  var submitting = false;

  function show(el, on) {
    if (!el) return;
    if (on) el.removeAttribute("hidden");
    else el.setAttribute("hidden", "");
  }

  function pad(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function clockText(ms) {
    if (ms < 0) ms = 0;
    var total = Math.ceil(ms / 1000);
    return pad(Math.floor(total / 60)) + ":" + pad(total % 60);
  }

  function qids() {
    return questions.map(function (q) { return q.id; });
  }

  function validLetter(letter) {
    return LETTERS.indexOf(letter) >= 0;
  }

  function loadState() {
    try {
      var raw = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      if (!raw || typeof raw.startedAt !== "number" || !isFinite(raw.startedAt)) return null;
      var answers = {};
      var ids = qids();
      if (raw.answers && typeof raw.answers === "object") {
        ids.forEach(function (id) {
          if (validLetter(raw.answers[id])) answers[id] = raw.answers[id];
        });
      }
      var cursor = raw.cursor;
      if (typeof cursor !== "number" || cursor < 0 || cursor >= questions.length) cursor = 0;
      return {
        startedAt: raw.startedAt,
        submittedAt: typeof raw.submittedAt === "number" ? raw.submittedAt : null,
        timedOut: !!raw.timedOut,
        cursor: cursor,
        answers: answers
      };
    } catch (e) {
      return null;
    }
  }

  function save() {
    if (!state) return;
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function remain() {
    return state.startedAt + DURATION - Date.now();
  }

  function paintClock() {
    var left = remain();
    if (left < 0) left = 0;
    clock.textContent = clockText(left);
    clock.classList.toggle("is-danger", left <= 60 * 1000);
    clock.classList.toggle("is-warn", left > 60 * 1000 && left <= 5 * 60 * 1000);
  }

  function paintPicks() {
    var answered = 0;
    questions.forEach(function (card, i) {
      var picked = state.answers[card.id] || "";
      if (picked) answered += 1;
      card.querySelectorAll(".choice-btn").forEach(function (btn) {
        var on = btn.getAttribute("data-letter") === picked;
        btn.classList.toggle("is-picked", on);
        btn.setAttribute("aria-checked", on ? "true" : "false");
      });
      if (navButtons[i]) navButtons[i].classList.toggle("is-answered", !!picked);
    });
    progress.textContent = "已作答 " + answered + " / " + questions.length;
  }

  function showQuestion(index) {
    if (index < 0) index = 0;
    if (index >= questions.length) index = questions.length - 1;
    state.cursor = index;
    questions.forEach(function (card, i) {
      card.classList.toggle("is-active", i === index);
    });
    navButtons.forEach(function (btn, i) {
      var on = i === index;
      btn.classList.toggle("is-current", on);
      if (on) btn.setAttribute("aria-current", "true");
      else btn.removeAttribute("aria-current");
    });
    var prev = document.getElementById("btnPrev");
    var next = document.getElementById("btnNext");
    if (prev) prev.disabled = index === 0;
    if (next) next.disabled = index === questions.length - 1;
    save();
  }

  function pick(qid, letter) {
    if (!state || state.submittedAt || submitting) return;
    if (!validLetter(letter)) return;
    state.answers[qid] = letter;
    paintPicks();
    save();
  }

  function blankCount() {
    var n = 0;
    qids().forEach(function (id) {
      if (!state.answers[id]) n += 1;
    });
    return n;
  }

  function enterAnswering() {
    show(gate, false);
    show(scoreBox, false);
    show(run, true);
    run.classList.remove("is-review");
    run.classList.add("is-answering");
    paintPicks();
    showQuestion(state.cursor || 0);
    paintClock();
  }

  function band(score) {
    if (score >= 90) return "五級";
    if (score >= 70) return "四級";
    if (score >= 50) return "三級";
    if (score >= 30) return "二級";
    return "一級";
  }

  function loadKey(done, fail) {
    if (window.READING_EXAM_KEY && window.READING_EXAM_KEY.length === questions.length) {
      done();
      return;
    }
    var script = document.createElement("script");
    script.src = "reading-answers.js";
    script.onload = function () {
      if (!window.READING_EXAM_KEY || window.READING_EXAM_KEY.length !== questions.length) {
        fail();
        return;
      }
      done();
    };
    script.onerror = fail;
    document.body.appendChild(script);
  }

  function renderScore() {
    var key = window.READING_EXAM_KEY;
    var correct = 0;
    questions.forEach(function (card, i) {
      var want = key[i];
      var got = state.answers[card.id] || "";
      var right = got === want;
      if (right) correct += 1;
      card.querySelectorAll(".choice-btn").forEach(function (btn) {
        var letter = btn.getAttribute("data-letter");
        btn.disabled = true;
        btn.classList.remove("is-picked");
        btn.classList.toggle("is-correct", letter === want);
        btn.classList.toggle("is-wrong", !!got && letter === got && letter !== want);
      });
      var line = card.querySelector(".exam-result");
      if (!line) {
        line = document.createElement("p");
        line.className = "exam-result";
        card.appendChild(line);
      }
      line.textContent = right
        ? "這題答對。答案是 (" + want + ")。"
        : (got
          ? "這題答錯。你選 (" + got + ")，答案是 (" + want + ")。"
          : "這題未作答，算錯。答案是 (" + want + ")。");
      if (navButtons[i]) {
        navButtons[i].classList.remove("is-current", "is-answered");
        navButtons[i].classList.toggle("is-right", right);
        navButtons[i].classList.toggle("is-miss", !right);
      }
    });

    var score = Math.round(correct / questions.length * 100);
    var used = state.submittedAt - state.startedAt;
    if (used < 0) used = 0;
    if (used > DURATION) used = DURATION;
    show(gate, false);
    show(run, true);
    show(scoreBox, true);
    run.classList.remove("is-answering");
    run.classList.add("is-review");
    questions.forEach(function (card) { card.classList.remove("is-active"); });

    scoreBox.innerHTML = "";
    var kicker = document.createElement("p");
    kicker.className = "kicker";
    kicker.textContent = "成績";
    var title = document.createElement("h1");
    title.textContent = "答對 " + correct + " / " + questions.length + " 題";
    var num = document.createElement("p");
    num.className = "score-num";
    num.textContent = score + " 分";
    var grade = document.createElement("p");
    grade.textContent = "級分：" + band(score);
    var fine = document.createElement("p");
    fine.className = "fine";
    fine.textContent = "這 " + score + " 分是本站換算：四捨五入（答對題數 ÷ 30 × 100）。官方沒有公布每一題幾分。級分用這個分數去套：90～100 五級、70～89 四級、50～69 三級、30～49 二級、0～29 一級。";
    var meta = document.createElement("p");
    meta.textContent = "用時 " + clockText(used) + (state.timedOut ? "。時間到，尚未作答的題目算錯。" : "。");
    var actions = document.createElement("div");
    actions.className = "score-actions";
    var keyLink = document.createElement("a");
    keyLink.className = "btn-go read";
    keyLink.href = "reading-key.html";
    keyLink.textContent = "看全部解析";
    var again = document.createElement("button");
    again.type = "button";
    again.className = "btn-go read";
    again.id = "btnRetake";
    again.textContent = "再考一次";
    again.addEventListener("click", retake);
    actions.appendChild(keyLink);
    actions.appendChild(again);
    scoreBox.appendChild(kicker);
    scoreBox.appendChild(title);
    scoreBox.appendChild(num);
    scoreBox.appendChild(grade);
    scoreBox.appendChild(fine);
    scoreBox.appendChild(meta);
    scoreBox.appendChild(actions);
    window.scrollTo(0, 0);
  }

  function failScore() {
    submitting = false;
    show(scoreBox, true);
    scoreBox.textContent = "成績暫時算不出來。請重新整理這頁，再按一次交卷。";
  }

  function submit(force) {
    if (!state || state.submittedAt || submitting) return;
    var blanks = blankCount();
    if (!force && blanks > 0) {
      var ok = window.confirm("還有 " + blanks + " 題空白。空白算錯。要交卷嗎？");
      if (!ok) {
        if (remain() <= 0) submit(true);
        return;
      }
    }
    submitting = true;
    if (remain() <= 0) state.timedOut = true;
    state.submittedAt = Date.now();
    save();
    show(gate, false);
    show(run, true);
    loadKey(function () {
      renderScore();
    }, failScore);
  }

  function retake() {
    var ok = window.confirm("再考一次會清掉這一份的作答與成績。全真模擬試卷目前只有一份，題目仍是這 30 題。");
    if (!ok) return;
    try {
      localStorage.removeItem(STORE_KEY);
    } catch (e) {}
    window.location.reload();
  }

  document.getElementById("btnStart").addEventListener("click", function () {
    if (state && state.submittedAt) return;
    if (state && !state.submittedAt) {
      enterAnswering();
      return;
    }
    state = {
      startedAt: Date.now(),
      submittedAt: null,
      timedOut: false,
      cursor: 0,
      answers: {}
    };
    save();
    enterAnswering();
  });

  document.getElementById("btnSubmit").addEventListener("click", function () {
    submit(false);
  });

  document.getElementById("btnPrev").addEventListener("click", function () {
    if (!state || state.submittedAt) return;
    showQuestion(state.cursor - 1);
  });

  document.getElementById("btnNext").addEventListener("click", function () {
    if (!state || state.submittedAt) return;
    showQuestion(state.cursor + 1);
  });

  navButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (!state) return;
      var index = Number(btn.getAttribute("data-n")) - 1;
      if (state.submittedAt) {
        var card = questions[index];
        if (card) card.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
      showQuestion(index);
    });
  });

  questions.forEach(function (card) {
    card.querySelectorAll(".choice-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        pick(card.id, btn.getAttribute("data-letter"));
      });
    });
  });

  window.addEventListener("keydown", function (e) {
    if (!state || state.submittedAt) return;
    if (!run.classList.contains("is-answering")) return;
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    var map = { "1": "A", "2": "B", "3": "C", "4": "D" };
    if (map[e.key]) {
      e.preventDefault();
      pick(questions[state.cursor].id, map[e.key]);
      return;
    }
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      showQuestion(state.cursor - 1);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      showQuestion(state.cursor + 1);
    }
  });

  setInterval(function () {
    if (!state || state.submittedAt) return;
    if (remain() <= 0) {
      submit(true);
      return;
    }
    paintClock();
  }, 200);

  state = loadState();
  if (state && state.submittedAt) {
    show(gate, false);
    loadKey(function () {
      renderScore();
    }, failScore);
  } else if (state) {
    if (remain() <= 0) {
      state.timedOut = true;
      submit(true);
    } else {
      enterAnswering();
    }
  }
})();
