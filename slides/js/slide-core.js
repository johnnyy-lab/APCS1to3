/**
 * APCS123 教學投影片全域核心引擎 (slide-core.js)
 * 版本: v2.5.0
 * 適用單元: 全書 15 章 / 118 節教學投影片
 * 規範參照: slide_generation_rules.md, agytodo.md (項目 0.1, 0.2, 0.3)
 */

/* ==========================================================================
   1. 全書 15 章與 118 節完整資料目錄 (依據 PythAPCS123_python_syntax_outline.md)
   ========================================================================== */
const courseCurriculum = [
  {
    id: "ch1",
    title: "第一章 變數、賦值與基本語法慣例",
    sections: [
      { id: "sec1-1", title: "1.1 變數命名規則與記憶體參照概念", available: true, url: "PythAPCS123_1-1_variable_naming_and_memory.html" },
      { id: "sec1-2", title: "1.2 等號賦值與運算順序", available: false, url: "PythAPCS123_1-2_assignment_and_execution_order.html" },
      { id: "sec1-3", title: "1.3 多變數同時賦值與變數交換（Swap）", available: false, url: "PythAPCS123_1-3_multiple_assignment_and_swap.html" },
      { id: "sec1-4", title: "1.4 運算後賦值（複合賦值運算子）", available: false, url: "PythAPCS123_1-4_augmented_assignment_operators.html" },
      { id: "sec1-5", title: "1.5 單行多指令（分號）、註解（#）與長指令折行", available: false, url: "PythAPCS123_1-5_semicolon_and_comments.html" },
      { id: "sec1-6", title: "1.6 縮排規範與程式區塊", available: false, url: "PythAPCS123_1-6_indentation_and_code_blocks.html" }
    ]
  },
  {
    id: "ch2",
    title: "第二章 資料型態與數值 / 位元運算",
    sections: [
      { id: "sec2-1", title: "2.1 數值型態分類（整數與浮點數）", available: false },
      { id: "sec2-2", title: "2.2 整數基本算術運算與優先級", available: false },
      { id: "sec2-3", title: "2.3 整數除法商數（//）與取餘數（%）", available: false },
      { id: "sec2-4", title: "2.4 次方與開根號運算（**）", available: false },
      { id: "sec2-5", title: "2.5 浮點數除法（/）與精度限制", available: false },
      { id: "sec2-6", title: "2.6 進位制常數表示法（0b, 0x）", available: false },
      { id: "sec2-7", title: "2.7 位元運算子與解題加速", available: false }
    ]
  },
  {
    id: "ch3",
    title: "第三章 型態轉換與內建數學函數",
    sections: [
      { id: "sec3-1", title: "3.1 數值與文字強制轉型（int, float, str）", available: false },
      { id: "sec3-2", title: "3.2 字元與 ASCII 互轉（ord, chr）", available: false },
      { id: "sec3-3", title: "3.3 極值比較函數（max, min）", available: false },
      { id: "sec3-4", title: "3.4 絕對值計算（abs）", available: false }
    ]
  },
  {
    id: "ch4",
    title: "第四章 標準輸出入（I/O）與測資處理技巧",
    sections: [
      { id: "sec4-1", title: "4.1 標準輸出 print() 基本語法", available: false },
      { id: "sec4-2", title: "4.2 print() 分隔符號參數 sep", available: false },
      { id: "sec4-3", title: "4.3 print() 結尾符號參數 end", available: false },
      { id: "sec4-4", title: "4.4 變數與運算式綜合輸出", available: false },
      { id: "sec4-5", title: "4.5 標準輸入 input() 基本讀取", available: false },
      { id: "sec4-6", title: "4.6 單行多數值切割與映射（split, map）", available: false },
      { id: "sec4-7", title: "4.7 連續多行固定筆數讀取", available: false }
    ]
  },
  {
    id: "ch5",
    title: "第五章 邏輯表示式、布林值與條件分支",
    sections: [
      { id: "sec5-1", title: "5.1 比較運算子與連續比較", available: false },
      { id: "sec5-2", title: "5.2 邏輯運算子（and, or, not）", available: false },
      { id: "sec5-3", title: "5.3 布林型態（bool）與真假值規則", available: false },
      { id: "sec5-4", title: "5.4 笛摩根定律的邏輯改寫", available: false },
      { id: "sec5-5", title: "5.5 分支控制結構（if, if-else, if-elif-else）", available: false },
      { id: "sec5-6", title: "5.6 巢狀 if 與短路求值（Short-circuit）", available: false },
      { id: "sec5-7", title: "5.7 旗標變數（Flag）與狀態控制", available: false }
    ]
  },
  {
    id: "ch6",
    title: "第六章 迴圈結構與控制流程",
    sections: [
      { id: "sec6-1", title: "6.1 計數迴圈基礎與 range 函式全方位解析", available: false },
      { id: "sec6-2", title: "6.2 迴圈累加器、計數器與極值維護（資料縮減模式）", available: false },
      { id: "sec6-3", title: "6.3 條件迴圈 while 的運作機制與經典數值演算法", available: false },
      { id: "sec6-4", title: "6.4 迴圈流程跳轉控制（break, continue 與 for...else）", available: false },
      { id: "sec6-5", title: "6.5 雙重與多重巢狀迴圈（時鐘模型與維度展開）", available: false },
      { id: "sec6-6", title: "6.6 幾何圖形與星號排版專題特訓（巢狀迴圈視覺化）", available: false },
      { id: "sec6-7", title: "6.7 迴圈常見邏輯與控制變數陷阱排查", available: false },
      { id: "sec6-8", title: "6.8 APCS 考場迴圈輸入實戰模式：固定筆數、哨兵終止與未知行數（EOF）", available: false }
    ]
  },
  {
    id: "ch7",
    title: "第七章 字串（String）特性與序列操作",
    sections: [
      { id: "sec7-1", title: "7.1 字串表示法與跳脫字元", available: false },
      { id: "sec7-2", title: "7.2 字串序列操作（串接與重複）", available: false },
      { id: "sec7-3", title: "7.3 格式化字串（f-string）與數值對齊", available: false },
      { id: "sec7-4", title: "7.4 字串索引、長度與走訪", available: false },
      { id: "sec7-5", title: "7.5 字串切片與反轉技巧（[::-1]）", available: false },
      { id: "sec7-6", title: "7.6 字串常用方法（split, count, in）", available: false }
    ]
  },
  {
    id: "ch8",
    title: "第八章 一維串列（List）核心操作與列表生成式",
    sections: [
      { id: "sec8-1", title: "8.1 串列建立、正負索引與解包輸出（print(*a)）", available: false },
      { id: "sec8-2", title: "8.2 串列切片語法與切片賦值", available: false },
      { id: "sec8-3", title: "8.3 串列常用內建方法（append, pop, insert 等）", available: false },
      { id: "sec8-4", title: "8.4 串列統計與極值運算（sum, max, min, len）", available: false },
      { id: "sec8-5", title: "8.5 串列走訪與成員查詢（for, index, in）", available: false },
      { id: "sec8-6", title: "8.6 串列參照與淺拷貝（copy, [:]）", available: false },
      { id: "sec8-7", title: "8.7 列表生成式與動態輸入（List Comprehension）", available: false }
    ]
  },
  {
    id: "ch9",
    title: "第九章 二維陣列（2D Array / List of Lists）與網格模擬",
    sections: [
      { id: "sec9-1", title: "9.1 二維陣列概念與座標元素存取", available: false },
      { id: "sec9-2", title: "9.2 二維陣列動態輸入讀取與解包輸出", available: false },
      { id: "sec9-3", title: "9.3 二維陣列初始化與參照共用致命陷阱", available: false },
      { id: "sec9-4", title: "9.4 二維網格雙重走訪與行列統計", available: false },
      { id: "sec9-5", title: "9.5 二維方陣與特殊走訪：對角線與棋盤規律", available: false },
      { id: "sec9-6", title: "9.6 矩陣幾何操作與逆推還原（APCS b266 專題）", available: false },
      { id: "sec9-7", title: "9.7 二維網格導航：方向向量與相鄰探測（APCS e287 原型）", available: false },
      { id: "sec9-8", title: "9.8 網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題）", available: false },
      { id: "sec9-9", title: "9.9 網格邊界安全墊（Padding）與模擬題型（APCS f313 原型）", available: false }
    ]
  },
  {
    id: "ch10",
    title: "第十章 雜湊容器：字典（Dict）與集合（Set）",
    sections: [
      { id: "sec10-1", title: "10.1 序對（Tuple）不可變特性與應用場景", available: false },
      { id: "sec10-2", title: "10.2 序對高階應用與 Hashable 鍵值要求", available: false },
      { id: "sec10-3", title: "10.3 字典概念、建立與基本存取", available: false },
      { id: "sec10-4", title: "10.4 字典常用方法與走訪技巧", available: false },
      { id: "sec10-5", title: "10.5 APCS 字典解題模式：頻率統計與映射加速", available: false },
      { id: "sec10-6", title: "10.6 集合建立、去重與成員查詢", available: false },
      { id: "sec10-7", title: "10.7 集合運算子與文氏圖模式", available: false },
      { id: "sec10-8", title: "10.8 雜湊容器綜合實戰：空間換取時間的極速思維", available: false }
    ]
  },
  {
    id: "ch11",
    title: "第十一章 函式模組化與遞迴思維",
    sections: [
      { id: "sec11-1", title: "11.1 自訂函式基礎：定義、呼叫流程與參數傳遞", available: false },
      { id: "sec11-2", title: "11.2 回傳值 return 與守衛子句（Guard Clauses）", available: false },
      { id: "sec11-3", title: "11.3 參數傳遞機制與副作用（可變 vs 不可變物件）", available: false },
      { id: "sec11-4", title: "11.4 變數作用域：區域變數與遮蔽現象（Shadowing）", available: false },
      { id: "sec11-5", title: "11.5 全域變數 global 關鍵字與除錯陷阱", available: false },
      { id: "sec11-6", title: "11.6 線性遞迴與呼叫堆疊（Call Stack）視覺化", available: false },
      { id: "sec11-7", title: "11.7 樹狀遞迴與經典數論問題（輾轉相除法、費氏數列）", available: false },
      { id: "sec11-8", title: "11.8 模組化解題戰略：頂層抽象與輔助函式設計", available: false }
    ]
  },
  {
    id: "ch12",
    title: "第十二章 排序（Sort）與二分搜尋（Binary Search）",
    sections: [
      { id: "sec12-1", title: "12.1 原地排序 list.sort() 與新創排序 sorted()", available: false },
      { id: "sec12-2", title: "12.2 反向排序 reverse=True 與字典序規則", available: false },
      { id: "sec12-3", title: "12.3 自訂排序鍵值 key：具名函式提取", available: false },
      { id: "sec12-4", title: "12.4 匿名函式 lambda 與多條件複合排序", available: false },
      { id: "sec12-5", title: "12.5 APCS 排序實戰應用：區間線段排序與雙指標", available: false },
      { id: "sec12-6", title: "12.6 線性搜尋與 index() 例外防範", available: false },
      { id: "sec12-7", title: "12.7 二分搜尋法手刻演算法一：猜數字模型與精確匹配", available: false },
      { id: "sec12-8", title: "12.8 二分搜尋法手刻演算法二：邊界二分搜尋（Lower/Upper Bound）", available: false },
      { id: "sec12-9", title: "12.9 內建二分搜尋模組：bisect 與數值區間查詢", available: false }
    ]
  },
  {
    id: "ch13",
    title: "第十三章 程式除錯（Debug）與異常處理",
    sections: [
      { id: "sec13-1", title: "13.1 競技程式線上評判系統（OJ）運作機制與評判型別", available: false },
      { id: "sec13-2", title: "13.2 語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法", available: false },
      { id: "sec13-3", title: "13.3 執行時期錯誤（RE）常見排行榜與崩潰防禦", available: false },
      { id: "sec13-4", title: "13.4 例外捕捉語法：try ... except 架構與未知長度輸入處理", available: false },
      { id: "sec13-5", title: "13.5 語意錯誤（Logic Error）與常見邏輯盲點排查（WA 防範）", available: false },
      { id: "sec13-6", title: "13.6 時間超限（TLE）診斷：運算量估算與隱形效能坑洞", available: false },
      { id: "sec13-7", title: "13.7 輸出格式防禦與對齊心法（Presentation WA 防範）", available: false },
      { id: "sec13-8", title: "13.8 考場系統化除錯戰略：錯誤重現、二分隔離與送出前 SOP", available: false }
    ]
  },
  {
    id: "ch14",
    title: "第十四章 APCS 實作真題特訓（初級題）",
    sections: [
      { id: "sec14-1", title: "14.1 c294. 三角形辨別（APCS 2016-10 舊版第 1 題）", available: false },
      { id: "sec14-2", title: "14.2 c290. 秘密差（APCS 2017-03 舊版第 1 題）", available: false },
      { id: "sec14-3", title: "14.3 c461. 邏輯運算子（APCS 2017-10 舊版第 1 題）", available: false },
      { id: "sec14-4", title: "14.4 e286. 籃球比賽（APCS 2019-06 舊版第 1 題）", available: false },
      { id: "sec14-5", title: "14.5 f579. 購物車（APCS 2020-07 舊版第 1 題）", available: false },
      { id: "sec14-6", title: "14.6 f312. 人力分配（APCS 2020-10 舊版第 1 題）", available: false },
      { id: "sec14-7", title: "14.7 f605. 購買力（APCS 2021-01 舊版第 1 題）", available: false },
      { id: "sec14-8", title: "14.8 g275. 七言對聯（官方初級範例第 1 題）", available: false },
      { id: "sec14-9", title: "14.9 g595. 修補圍籬（APCS 2021-11 舊版第 1 題）", available: false },
      { id: "sec14-10", title: "14.10 m931. 遊戲選角（官方初級範例第 3 題）", available: false },
      { id: "sec14-11", title: "14.11 o711. 裝飲料（官方初級範例第 2 題）", available: false }
    ]
  },
  {
    id: "ch15",
    title: "第十五章 APCS 實作真題特訓（中級題）",
    sections: [
      { id: "sec15-1", title: "15.1 c295. 最大和（APCS 2016-10 舊版第 2 題）", available: false },
      { id: "sec15-2", title: "15.2 c291. 小群體（APCS 2017-03 舊版第 2 題）", available: false },
      { id: "sec15-3", title: "15.3 e287. 機器人的路徑（APCS 2019-06 舊版第 2 題）", available: false },
      { id: "sec15-4", title: "15.4 b266. 矩陣轉換（APCS 2016-03 舊版第 2 題）", available: false },
      { id: "sec15-5", title: "15.5 f313. 人口遷移（APCS 2020-10 舊版第 2 題）", available: false },
      { id: "sec15-6", title: "15.6 f606. 流量（APCS 2021-01 舊版第 2 題）", available: false },
      { id: "sec15-7", title: "15.7 f580. 骰子（APCS 2020-07 舊版第 2 題）", available: false },
      { id: "sec15-8", title: "15.8 c462. 交錯字串（APCS 2017-10 舊版第 2 題）", available: false },
      { id: "sec15-9", title: "15.9 g276. 魔王迷宮（APCS 2021-09 舊版第 2 題）", available: false },
      { id: "sec15-10", title: "15.10 g596. 動線安排（APCS 2021-11 舊版第 2 題）", available: false },
      { id: "sec15-11", title: "15.11 k732. 特殊位置（官方中級範例第 1 題）", available: false },
      { id: "sec15-12", title: "15.12 o712. 蒐集寶石（官方中級範例第 2 題）", available: false },
      { id: "sec15-13", title: "15.13 i400. 字串解碼（官方中級範例第 3 題）", available: false }
    ]
  }
];

/* ==========================================================================
   2. 引擎全域運行狀態 (Slide Engine State)
   ========================================================================== */
let currentSlide = 0;
let isIdleTheme = false;
let currentSectionId = "sec1-1";
let activeSlidesData = [];
let colabPracticeUrl = "";

/* ==========================================================================
   3. 引擎初始化主入口 (initSlideEngine)
   ========================================================================== */
function initSlideEngine(config) {
  if (!config || !Array.isArray(config.slidesData)) {
    console.error("Slide Engine: 配置無效，slidesData 必須為陣列！", config);
    return;
  }

  currentSectionId = config.sectionId || "sec1-1";
  activeSlidesData = config.slidesData;
  colabPracticeUrl = config.colabUrl || "";

  // 1. 初始化主題
  initThemeFromSession();

  // 2. 初始化課程導航下拉選單
  initCurriculumSelects();

  // 3. 綁定手勢與鍵盤事件
  setupEventListeners();

  // 4. 初次渲染第 1 張投影片
  currentSlide = 0;
  renderSlide(0);
}

/* ==========================================================================
   4. 主題切換與 Session 持久化
   ========================================================================== */
function initThemeFromSession() {
  const savedTheme = sessionStorage.getItem('apcs_slide_theme');
  if (savedTheme === 'idle') {
    setTheme(true);
  } else {
    setTheme(false); // 預設 Colab 深色風格
  }
}

function setTheme(toIdle) {
  isIdleTheme = toIdle;
  const body = document.body;
  const btn = document.getElementById('btnThemeToggle');
  const pill = document.getElementById('themePill');
  const dockIcon = document.getElementById('dockThemeIcon');

  if (isIdleTheme) {
    body.classList.add('idle-theme');
    if (btn) btn.textContent = "切換為 Colab 深色風格";
    if (pill) pill.textContent = "IDLE 考場風格 (白底黑字)";
    if (dockIcon) dockIcon.textContent = "💻 深色";
    sessionStorage.setItem('apcs_slide_theme', 'idle');
  } else {
    body.classList.remove('idle-theme');
    if (btn) btn.textContent = "切換為 IDLE 考場風格";
    if (pill) pill.textContent = "Colab 深色風格";
    if (dockIcon) dockIcon.textContent = "🏛️ 考場";
    sessionStorage.setItem('apcs_slide_theme', 'colab');
  }
}

function toggleTheme() {
  setTheme(!isIdleTheme);
}

/* ==========================================================================
   5. 課程下拉式選單與導航控制
   ========================================================================== */
function initCurriculumSelects() {
  const chSelect = document.getElementById('chapterSelect');
  if (!chSelect) return;
  chSelect.innerHTML = '';

  let matchedChapterId = 'ch1';

  courseCurriculum.forEach(ch => {
    const opt = document.createElement('option');
    opt.value = ch.id;
    opt.textContent = ch.title;
    chSelect.appendChild(opt);

    if (ch.sections.some(s => s.id === currentSectionId)) {
      matchedChapterId = ch.id;
    }
  });

  chSelect.value = matchedChapterId;
  populateSections(matchedChapterId);
}

function populateSections(chapterId) {
  const secSelect = document.getElementById('sectionSelect');
  if (!secSelect) return;
  secSelect.innerHTML = '';
  const chapter = courseCurriculum.find(c => c.id === chapterId);
  if (!chapter) return;

  chapter.sections.forEach(sec => {
    const opt = document.createElement('option');
    opt.value = sec.id;
    opt.textContent = (sec.available ? '✅ ' : '⏳ ') + sec.title;
    secSelect.appendChild(opt);
  });

  if (chapter.sections.some(s => s.id === currentSectionId)) {
    secSelect.value = currentSectionId;
  } else if (chapter.sections.length > 0) {
    secSelect.value = chapter.sections[0].id;
  }

  handleSectionSelection(secSelect.value);
}

function onChapterChange() {
  const chapterId = document.getElementById('chapterSelect').value;
  populateSections(chapterId);
}

function onSectionChange() {
  const sectionId = document.getElementById('sectionSelect').value;
  handleSectionSelection(sectionId);
}

function handleSectionSelection(sectionId) {
  const slideHeader = document.getElementById('slideHeader');
  const slideBody = document.getElementById('slideBody');
  const constructionStage = document.getElementById('constructionStage');
  const deckActions = document.getElementById('deckActions');
  const mobileDock = document.getElementById('mobileBottomDock');

  if (sectionId === currentSectionId) {
    if (slideHeader) slideHeader.style.display = '';
    if (slideBody) slideBody.style.display = '';
    if (constructionStage) constructionStage.style.display = 'none';
    if (deckActions) deckActions.style.visibility = 'visible';
    if (mobileDock) mobileDock.style.display = '';

    currentSlide = 0;
    renderSlide(0);
  } else {
    // 檢查是否有現成網頁可直接跳轉
    let targetSection = null;
    for (const ch of courseCurriculum) {
      targetSection = ch.sections.find(s => s.id === sectionId);
      if (targetSection) break;
    }

    if (targetSection && targetSection.available && targetSection.url) {
      location.href = targetSection.url;
      return;
    }

    // 尚未開放之施工中頁面
    if (slideHeader) slideHeader.style.display = 'none';
    if (slideBody) slideBody.style.display = 'none';
    if (constructionStage) constructionStage.style.display = 'flex';
    if (deckActions) deckActions.style.visibility = 'hidden';
    if (mobileDock) mobileDock.style.display = 'none';

    const targetTitle = targetSection ? targetSection.title : '指定單元';
    const targetEl = document.getElementById('constructionTarget');
    if (targetEl) targetEl.textContent = targetTitle;
  }
}

function returnToDemoUnit() {
  let matchedChapterId = 'ch1';
  for (const ch of courseCurriculum) {
    if (ch.sections.some(s => s.id === currentSectionId)) {
      matchedChapterId = ch.id;
      break;
    }
  }

  const chSelect = document.getElementById('chapterSelect');
  if (chSelect) chSelect.value = matchedChapterId;
  populateSections(matchedChapterId);

  const secSelect = document.getElementById('sectionSelect');
  if (secSelect) secSelect.value = currentSectionId;
  handleSectionSelection(currentSectionId);
}

/* ==========================================================================
   6. 投影片核心渲染器 (Slide Renderer)
   ========================================================================== */
function renderSlide(index) {
  if (!activeSlidesData || activeSlidesData.length === 0) return;
  const slide = activeSlidesData[index];
  if (!slide) return;

  // Header 雙行
  const titleZh = document.getElementById('titleChinese');
  const titleEn = document.getElementById('titleEnglish');
  const breadcrumbCh = document.getElementById('breadcrumbChapter');
  const breadcrumbSec = document.getElementById('breadcrumbSection');

  if (titleZh) titleZh.textContent = slide.titleZh;
  if (titleEn) titleEn.textContent = slide.titleEn;
  if (breadcrumbCh) breadcrumbCh.textContent = slide.chapter;
  if (breadcrumbSec) breadcrumbSec.textContent = slide.section;

  // 教學程式碼與懸停提示（行號 <= 2 向下展開避免切邊，支援手機/平板點選）
  const codeViewport = document.getElementById('codeViewport');
  if (codeViewport && Array.isArray(slide.codeLines)) {
    codeViewport.innerHTML = slide.codeLines.map(line => {
      const diffClass = line.diff ? 'diff-highlight' : (line.error ? 'error-highlight' : '');
      const tooltipPositionClass = (line.num <= 2) ? 'tooltip-down' : 'tooltip-up';
      return `
        <div class="code-line ${diffClass}" id="code-line-${line.num}"
             onmouseenter="onLineHover(${line.num})"
             onmouseleave="onLineLeave()"
             onclick="onLineClick(${line.num})">
          <span class="line-num">${line.num}</span>
          <span class="line-content">${line.html}</span>
          <div class="line-tooltip ${tooltipPositionClass}">
            <div class="tt-header">📌 第 ${line.num} 行代碼解析</div>
            <div class="tt-row"><span class="tt-tag">【白話含義】</span><span>${line.mean}</span></div>
            <div class="tt-row"><span class="tt-tag">【為何這樣寫】</span><span>${line.why}</span></div>
            <div class="tt-row"><span class="tt-tag">【還可以怎麼寫】</span><span>${line.alt}</span></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // 執行結果 (純結果輸出，無終端機提示符號)
  const outputViewport = document.getElementById('outputViewport');
  if (outputViewport) {
    outputViewport.innerHTML = slide.output || '<span class="output-empty">（無終端輸出）</span>';
  }

  // 重點說明 (支援滑鼠移入與手機點擊時，聯動高亮對應程式碼行)
  const notesList = document.getElementById('notesList');
  if (notesList && Array.isArray(slide.notes)) {
    notesList.innerHTML = slide.notes.map(n => {
      let badgeClass = '';
      if (n.type === 'error') badgeClass = 'error-badge';
      else if (n.type === 'concept') badgeClass = 'concept-badge';
      else if (n.type === 'radar') badgeClass = 'radar-badge';
      else if (n.type === 'mnemonic') badgeClass = 'mnemonic-badge';
      else if (n.type === 'wa') badgeClass = 'wa-badge';
      else if (n.type) badgeClass = `${n.type}-badge`;
      const linesJson = JSON.stringify(n.lines || []);
      return `
        <li class="note-item" 
            onmouseenter='highlightLines(${linesJson})'
            onmouseleave='clearHighlightedLines()'
            onclick='onNoteClick(${linesJson})'>
          <span class="line-badge ${badgeClass}">${n.lineText || ''}</span>
          <div>${n.text}</div>
        </li>
      `;
    }).join('');
  }

  // 頁碼 (桌面端與行動端同步更新)
  const pageStr = `${index + 1} / ${activeSlidesData.length}`;
  const pageInd = document.getElementById('pageIndicator');
  if (pageInd) pageInd.textContent = pageStr;
  const dockPage = document.getElementById('dockPageIndicator');
  if (dockPage) dockPage.textContent = pageStr;

  // 按鈕狀態 (桌面端與行動端同步更新)
  const isFirst = (index === 0);
  const isLast = (index === activeSlidesData.length - 1);
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  if (btnPrev) btnPrev.disabled = isFirst;
  if (btnNext) btnNext.disabled = isLast;

  const dockPrev = document.getElementById('dockBtnPrev');
  const dockNext = document.getElementById('dockBtnNext');
  if (dockPrev) dockPrev.disabled = isFirst;
  if (dockNext) dockNext.disabled = isLast;

  // 重置行解析條為預設狀態
  resetLineBar();
}

/* ==========================================================================
   7. 程式碼連動高亮與三維解析列
   ========================================================================== */
function onLineHover(lineNum) {
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  const lineData = slide.codeLines.find(l => l.num === lineNum);
  if (lineData) {
    updateLineBar(lineData.num, lineData.mean, lineData.why, lineData.alt);
  }
}

function onLineLeave() {
  resetLineBar();
}

function highlightLines(lineNums) {
  clearHighlightedLines();
  if (!Array.isArray(lineNums)) return;
  lineNums.forEach(num => {
    const el = document.getElementById(`code-line-${num}`);
    if (el) el.classList.add('linked-highlight');
  });

  if (lineNums.length > 0 && activeSlidesData[currentSlide]) {
    const slide = activeSlidesData[currentSlide];
    const firstLine = slide.codeLines.find(l => l.num === lineNums[0]);
    if (firstLine) {
      updateLineBar(firstLine.num, firstLine.mean, firstLine.why, firstLine.alt);
    }
  }
}

function clearHighlightedLines() {
  document.querySelectorAll('.code-line.linked-highlight').forEach(el => {
    el.classList.remove('linked-highlight');
  });
  resetLineBar();
}

function updateLineBar(num, mean, why, alt) {
  const bar = document.getElementById('codeLineBar');
  if (!bar) return;
  bar.innerHTML = `
    <div class="bar-row">
      <span class="bar-badge badge-mean">第 ${num} 行含義</span>
      <span>${mean}</span>
    </div>
    <div class="bar-row">
      <span class="bar-badge badge-why">為何這樣寫</span>
      <span>${why}</span>
      <span class="bar-badge badge-alt" style="margin-left:8px;">還可怎麼寫</span>
      <span>${alt}</span>
    </div>
  `;
}

function resetLineBar() {
  const bar = document.getElementById('codeLineBar');
  if (!bar) return;
  bar.innerHTML = `
    <div class="bar-row" style="color: #94a3b8;">
      <span>💡 <strong>三維解析列：</strong>滑鼠懸停於任一行或右側重點，可即時探索【白話含義】、【為何這樣寫】與【還可以怎麼寫】。</span>
    </div>
  `;
}

function onLineClick(lineNum) {
  clearHighlightedLines();
  const el = document.getElementById(`code-line-${lineNum}`);
  if (el) el.classList.add('linked-highlight');
  onLineHover(lineNum);
}

function onNoteClick(lineNums) {
  highlightLines(lineNums);
}

/* ==========================================================================
   8. 翻頁與全螢幕操作
   ========================================================================== */
function prevSlide() {
  if (currentSlide > 0) {
    currentSlide--;
    renderSlide(currentSlide);
  }
}

function nextSlide() {
  if (currentSlide < activeSlidesData.length - 1) {
    currentSlide++;
    renderSlide(currentSlide);
  }
}

function toggleFullscreen() {
  const elem = document.getElementById('slideStage');
  if (!elem) return;
  try {
    if (!document.fullscreenElement) {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
      } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  } catch (err) {
    console.warn('全螢幕切換受限:', err);
  }
}

/* ==========================================================================
   9. 手勢與鍵盤監聽設定
   ========================================================================== */
function setupEventListeners() {
  // 手機與平板觸控左右滑動 (Swipe Left / Swipe Right)
  let touchStartX = 0;
  let touchStartY = 0;
  let touchEndX = 0;
  let touchEndY = 0;

  const stageEl = document.getElementById('slideStage');
  if (stageEl) {
    stageEl.addEventListener('touchstart', (e) => {
      if (!e.changedTouches || e.changedTouches.length === 0) return;
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    stageEl.addEventListener('touchend', (e) => {
      if (!e.changedTouches || e.changedTouches.length === 0) return;
      touchEndX = e.changedTouches[0].screenX;
      touchEndY = e.changedTouches[0].screenY;
      
      const dx = touchEndX - touchStartX;
      const dy = touchEndY - touchStartY;
      // 橫向位移大於 45px，且橫向位移大於縱向位移的 1.2 倍（防止上下滾動時誤觸）
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        if (dx < 0) {
          nextSlide(); // 向左滑動 -> 下一張
        } else {
          prevSlide(); // 向右滑動 -> 上一張
        }
      }
    }, { passive: true });
  }

  // 鍵盤切換支援
  window.addEventListener('keydown', (e) => {
    const secSelect = document.getElementById('sectionSelect');
    if (secSelect && secSelect.value !== currentSectionId) return;

    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      prevSlide();
    } else if (e.key === 'f' || e.key === 'F') {
      toggleFullscreen();
    } else if (e.key === 't' || e.key === 'T') {
      toggleTheme();
    }
  });
}
