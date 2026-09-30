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
      { id: "sec1-2", title: "1.2 等號賦值與運算順序", available: true, url: "PythAPCS123_1-2_assignment_and_execution_order.html" },
      { id: "sec1-3", title: "1.3 多變數同時賦值與變數交換（Swap）", available: true, url: "PythAPCS123_1-3_multiple_assignment_and_swap.html" },
      { id: "sec1-4", title: "1.4 運算後賦值（複合賦值運算子）", available: true, url: "PythAPCS123_1-4_augmented_assignment_operators.html" },
      { id: "sec1-5", title: "1.5 單行多指令（分號）、註解（#）與長指令折行", available: true, url: "PythAPCS123_1-5_semicolon_and_comments.html" },
      { id: "sec1-6", title: "1.6 縮排規範與程式區塊", available: true, url: "PythAPCS123_1-6_indentation_and_code_blocks.html" }
    ]
  },
  {
    id: "ch2",
    title: "第二章 資料型態與數值 / 位元運算",
    sections: [
      { id: "sec2-1", title: "2.1 數值型態分類（整數與浮點數）", available: true, url: "PythAPCS123_2-1_numeric_types_int_and_float.html" },
      { id: "sec2-2", title: "2.2 整數基本算術運算與優先級", available: true, url: "PythAPCS123_2-2_integer_arithmetic_and_precedence.html" },
      { id: "sec2-3", title: "2.3 整數除法商數（//）與取餘數（%）", available: true, url: "PythAPCS123_2-3_integer_division_and_modulus.html" },
      { id: "sec2-4", title: "2.4 次方與開根號運算（**）", available: true, url: "PythAPCS123_2-4_power_and_square_root.html" },
      { id: "sec2-5", title: "2.5 浮點數除法（/）與精度限制", available: true, url: "PythAPCS123_2-5_float_division_and_precision_limits.html" },
      { id: "sec2-6", title: "2.6 進位制常數表示法（0b, 0x）", available: true, url: "PythAPCS123_2-6_number_bases_binary_and_hexadecimal.html" },
      { id: "sec2-7", title: "2.7 位元運算子與解題加速", available: true, url: "PythAPCS123_2-7_bitwise_operators_and_speedup.html" }
    ]
  },
  {
    id: "ch3",
    title: "第三章 型態轉換與內建數學函數",
    sections: [
      { id: "sec3-1", title: "3.1 數值與文字強制轉型（int, float, str）", available: true, url: "PythAPCS123_3-1_type_conversion_int_float_str.html" },
      { id: "sec3-2", title: "3.2 字元與 ASCII 互轉（ord, chr）", available: true, url: "PythAPCS123_3-2_character_and_ascii_ord_chr.html" },
      { id: "sec3-3", title: "3.3 極值比較函數（max, min）", available: true, url: "PythAPCS123_3-3_extremum_functions_max_min.html" },
      { id: "sec3-4", title: "3.4 絕對值計算（abs）", available: true, url: "PythAPCS123_3-4_absolute_value_abs.html" }
    ]
  },
  {
    id: "ch4",
    title: "第四章 標準輸出入（I/O）與測資處理技巧",
    sections: [
      { id: "sec4-1", title: "4.1 標準輸出 print() 基本語法", available: true, url: "PythAPCS123_4-1_standard_output_print.html" },
      { id: "sec4-2", title: "4.2 print() 分隔符號參數 sep", available: true, url: "PythAPCS123_4-2_print_separator_sep.html" },
      { id: "sec4-3", title: "4.3 print() 結尾符號參數 end", available: true, url: "PythAPCS123_4-3_print_end_parameter.html" },
      { id: "sec4-4", title: "4.4 變數與運算式綜合輸出", available: true, url: "PythAPCS123_4-4_variable_and_expression_output.html" },
      { id: "sec4-5", title: "4.5 標準輸入 input() 基本讀取", available: true, url: "PythAPCS123_4-5_standard_input_input.html" },
      { id: "sec4-6", title: "4.6 單行多數值切割與映射（split, map）", available: true, url: "PythAPCS123_4-6_single_line_multiple_inputs_split_map.html" },
      { id: "sec4-7", title: "4.7 連續多行固定筆數讀取", available: true, url: "PythAPCS123_4-7_multiline_fixed_inputs.html" }
    ]
  },
  {
    id: "ch5",
    title: "第五章 邏輯表示式、布林值與條件分支",
    sections: [
      { id: "sec5-1", title: "5.1 比較運算子與連續比較", available: true, url: "PythAPCS123_5-1_comparison_operators_and_chained_comparisons.html" },
      { id: "sec5-2", title: "5.2 邏輯運算子（and, or, not）", available: true, url: "PythAPCS123_5-2_logical_operators_and_or_not.html" },
      { id: "sec5-3", title: "5.3 布林型態（bool）與真假值規則", available: true, url: "PythAPCS123_5-3_boolean_type_and_truth_values.html" },
      { id: "sec5-4", title: "5.4 笛摩根定律的邏輯改寫", available: true, url: "PythAPCS123_5-4_demorgans_laws.html" },
      { id: "sec5-5", title: "5.5 分支控制結構（if, if-else, if-elif-else）", available: true, url: "PythAPCS123_5-5_branching_if_elif_else.html" },
      { id: "sec5-6", title: "5.6 巢狀 if 與短路求值（Short-circuit）", available: true, url: "PythAPCS123_5-6_nested_if_and_short_circuit.html" },
      { id: "sec5-7", title: "5.7 旗標變數（Flag）與狀態控制", available: true, url: "PythAPCS123_5-7_flag_variables_and_state_control.html" }
    ]
  },
  {
    id: "ch6",
    title: "第六章 迴圈結構與控制流程",
    sections: [
      { id: "sec6-1", title: "6.1 計數迴圈基礎與 range 函式全方位解析", available: true, url: "PythAPCS123_6-1_counting_loop_for_and_range.html" },
      { id: "sec6-2", title: "6.2 迴圈累加器、計數器與極值維護（資料縮減模式）", available: true, url: "PythAPCS123_6-2_loop_accumulators_and_counters.html" },
      { id: "sec6-3", title: "6.3 條件迴圈 while 的運作機制與經典數值演算法", available: true, url: "PythAPCS123_6-3_conditional_loop_while.html" },
      { id: "sec6-4", title: "6.4 迴圈流程跳轉控制（break, continue 與 for...else）", available: true, url: "PythAPCS123_6-4_loop_break_and_continue.html" },
      { id: "sec6-5", title: "6.5 雙重與多重巢狀迴圈（時鐘模型與維度展開）", available: true, url: "PythAPCS123_6-5_nested_loops_and_clock_model.html" },
      { id: "sec6-6", title: "6.6 幾何圖形與星號排版專題特訓（巢狀迴圈視覺化）", available: true, url: "PythAPCS123_6-6_geometric_patterns_and_asterisk_formatting.html" },
      { id: "sec6-7", title: "6.7 迴圈常見邏輯與控制變數陷阱排查", available: true, url: "PythAPCS123_6-7_loop_control_variable_pitfalls.html" },
      { id: "sec6-8", title: "6.8 APCS 考場迴圈輸入實戰模式：固定筆數、哨兵終止與未知行數（EOF）", available: true, url: "PythAPCS123_6-8_eof_and_input_streaming_patterns.html" }
    ]
  },
  {
    id: "ch7",
    title: "第七章 字串（String）特性與序列操作",
    sections: [
      { id: "sec7-1", title: "7.1 字串表示法與跳脫字元", available: true, url: "PythAPCS123_7-1_string_representation_and_escape_characters.html" },
      { id: "sec7-2", title: "7.2 字串序列操作（串接與重複）", available: true, url: "PythAPCS123_7-2_string_concatenation_and_repetition.html" },
      { id: "sec7-3", title: "7.3 格式化字串（f-string）與數值對齊", available: true, url: "PythAPCS123_7-3_fstring_formatting_and_alignment.html" },
      { id: "sec7-4", title: "7.4 字串索引、長度與走訪", available: true, url: "PythAPCS123_7-4_string_indexing_length_and_traversal.html" },
      { id: "sec7-5", title: "7.5 字串切片與反轉技巧（[::-1]）", available: true, url: "PythAPCS123_7-5_string_slicing_and_reversal.html" },
      { id: "sec7-6", title: "7.6 字串常用方法（split, count, in）", available: true, url: "PythAPCS123_7-6_common_string_methods.html" }
    ]
  },
  {
    id: "ch8",
    title: "第八章 一維串列（List）核心操作與列表生成式",
    sections: [
      { id: "sec8-1", title: "8.1 串列建立、正負索引與解包輸出（print(*a)）", available: true, url: "PythAPCS123_8-1_list_creation_indexing_and_unpacking.html" },
      { id: "sec8-2", title: "8.2 串列切片語法與切片賦值", available: true, url: "PythAPCS123_8-2_list_slicing_and_slice_assignment.html" },
      { id: "sec8-3", title: "8.3 串列常用內建方法（append, pop, insert 等）", available: true, url: "PythAPCS123_8-3_list_methods_append_pop_insert.html" },
      { id: "sec8-4", title: "8.4 串列統計與極值運算（sum, max, min, len）", available: true, url: "PythAPCS123_8-4_list_statistics_sum_max_min.html" },
      { id: "sec8-5", title: "8.5 串列走訪與成員查詢（for, index, in）", available: true, url: "PythAPCS123_8-5_list_traversal_and_membership.html" },
      { id: "sec8-6", title: "8.6 串列參照與淺拷貝（copy, [:]）", available: true, url: "PythAPCS123_8-6_list_reference_and_shallow_copy.html" },
      { id: "sec8-7", title: "8.7 列表生成式與動態輸入（List Comprehension）", available: true, url: "PythAPCS123_8-7_list_comprehension_and_dynamic_input.html" }
    ]
  },
  {
    id: "ch9",
    title: "第九章 二維陣列（2D Array / List of Lists）與網格模擬",
    sections: [
      { id: "sec9-1", title: "9.1 二維陣列概念與座標元素存取", available: true, url: "PythAPCS123_9-1_2d_array_concept_and_coordinate_access.html" },
      { id: "sec9-2", title: "9.2 二維陣列動態輸入讀取與解包輸出", available: true, url: "PythAPCS123_9-2_2d_array_dynamic_input_and_unpacking_output.html" },
      { id: "sec9-3", title: "9.3 二維陣列初始化與參照共用致命陷阱", available: true, url: "PythAPCS123_9-3_2d_array_initialization_and_reference_pitfall.html" },
      { id: "sec9-4", title: "9.4 二維網格雙重走訪與行列統計", available: true, url: "PythAPCS123_9-4_2d_array_traversal_and_row_col_statistics.html" },
      { id: "sec9-5", title: "9.5 二維方陣與特殊走訪：對角線與棋盤規律", available: true, url: "PythAPCS123_9-5_square_matrix_diagonals_and_patterns.html" },
      { id: "sec9-6", title: "9.6 矩陣幾何操作與逆推還原（APCS b266 專題）", available: true, url: "PythAPCS123_9-6_matrix_geometric_transformations_and_apcs_b266.html" },
      { id: "sec9-7", title: "9.7 二維網格導航：方向向量與相鄰探測（APCS e287 原型）", available: true, url: "PythAPCS123_9-7_grid_navigation_direction_vectors_and_apcs_e287.html" },
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
let isAnswerRevealed = true; // 追蹤當前頁主動預測答案是否已揭曉 (agytodo 3.2)
let currentSlideQuiz = null; // 當前頁二擇一預測題目 (agytodo 3.3)
let isQuizAnswered = false; // 當前頁預測題是否已作答 (agytodo 3.3)
let pinnedLineNum = null; // 鎖定釘選的程式碼行 (支援點選固定導引線與高亮 - agytodo 6.1, 6.2)
let animFrameId = null; // 導引線光斑流動 requestAnimationFrame ID

/* ==========================================================================
   3. 引擎初始化主入口 (initSlideEngine)
   ========================================================================== */
function initSlideEngine(config) {
  if (!config || !Array.isArray(config.slidesData)) {
    console.error("Slide Engine: 配置無效，slidesData 必須為陣列！", config);
    return;
  }

  
  // 自動從網址推導目前的章節 (統一更新，杜絕複製貼上忘記改 ID 的問題)
  const currentFilename = window.location.pathname.split('/').pop();
  let detectedSectionId = null;
  for (const ch of courseCurriculum) {
    const sec = ch.sections.find(s => s.url === currentFilename);
    if (sec) {
      detectedSectionId = sec.id;
      break;
    }
  }
  
  currentSectionId = detectedSectionId || config.sectionId || "sec1-1";

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
  updateFlowGuideTheme();
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

  currentSlide = index;
  pinnedLineNum = null;
  clearDataFlowSync();

  // Header 雙行
  const titleZh = document.getElementById('titleChinese');
  const titleEn = document.getElementById('titleEnglish');
  const breadcrumbCh = document.getElementById('breadcrumbChapter');
  const breadcrumbSec = document.getElementById('breadcrumbSection');

  if (titleZh) titleZh.textContent = slide.titleZh;
  if (titleEn) titleEn.textContent = slide.titleEn;
  if (breadcrumbCh) breadcrumbCh.textContent = slide.chapter;
  if (breadcrumbSec) breadcrumbSec.textContent = slide.section;

  // 瀏覽器分頁標題防禦：若 document.title 含有 {{ 或為空，自動依據課程單元資料修復
  if (!document.title || document.title.includes('{{')) {
    const curSec = courseCurriculum.flatMap(c => c.sections).find(s => s.id === currentSectionId);
    const unitTitle = curSec ? curSec.title : (slide.section || '單元教學');
    document.title = `${unitTitle} | APCS 教學投影片`;
  }

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
          <span class="dataflow-badge badge-code-out" id="code-badge-${line.num}" style="display:none;"></span>
          <div class="line-tooltip ${tooltipPositionClass}">
            <div class="tt-header">📌 第 ${line.num} 行代碼解析</div>
            <div class="tt-row"><span class="tt-tag">【白話含義】</span><span>${line.mean}</span></div>
            <div class="tt-row"><span class="tt-tag">【為何這樣寫】</span><span>${line.why}</span></div>
            ${line.alt && line.alt !== '此行無第二種寫法' && !line.alt.match(/^行 \d+。$/) ? `<div class="tt-row"><span class="tt-tag">【還可以怎麼寫】</span><span>${line.alt}</span></div>` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  // 頂部細緻進度線 (agytodo 5.2)
  const topbarProgress = document.getElementById('topbarProgressLine');
  if (topbarProgress) {
    const pct = ((index + 1) / activeSlidesData.length) * 100;
    topbarProgress.style.width = `${pct}%`;
  }

  // 執行結果 (純結果輸出，並支援主動預測遮罩與二擇一預測卡 - agytodo 3.2, 3.3)
  const outputViewport = document.getElementById('outputViewport');
  const predictionOverlay = document.getElementById('predictionOverlay');
  currentSlideQuiz = slide.predictQuiz || null;
  isQuizAnswered = false;
  const hasPrediction = !!slide.predict || !!slide.maskOutput || !!currentSlideQuiz;

  if (outputViewport) {
    outputViewport.innerHTML = formatOutputViewportContent(slide.output, slide);
    if (hasPrediction) {
      isAnswerRevealed = false;
      outputViewport.classList.add('blurred');
      if (predictionOverlay) {
        predictionOverlay.style.display = 'flex';
        if (currentSlideQuiz) {
          renderQuizCard(predictionOverlay, currentSlideQuiz);
        } else {
          renderSimplePredictionMask(predictionOverlay, slide.predict);
        }
      }
    } else {
      isAnswerRevealed = true;
      outputViewport.classList.remove('blurred');
      if (predictionOverlay) predictionOverlay.style.display = 'none';
    }
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
      const formattedText = (n.text || '').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      return `
        <li class="note-item" 
            onmouseenter='highlightLines(${linesJson})'
            onmouseleave='clearHighlightedLines()'
            onclick='onNoteClick(${linesJson})'>
          <span class="line-badge ${badgeClass}">${n.lineText || ''}</span>
          <div>${formattedText}</div>
        </li>
      `;
    }).join('');
  }

  // 記憶體狀態盒 (Memory State Widget - agytodo 2.1, 2.2, 2.6)
  const memoryStage = document.getElementById('memoryStage');
  const memoryBoxesContainer = document.getElementById('memoryBoxesContainer');
  if (memoryStage && memoryBoxesContainer) {
    if (Array.isArray(slide.memoryState) && slide.memoryState.length > 0) {
      memoryStage.style.display = 'block';
      memoryBoxesContainer.innerHTML = slide.memoryState.map(box => {
        const isDiff = box.diff ? 'diff-box' : '';
        const hasOverwrite = (box.prevVal !== undefined && box.prevVal !== null);
        let badgeHtml = '';
        if (box.badgeText) {
          const badgeClass = box.badgeClass || (box.action === 'swap' ? 'badge-swap' : (box.action === 'temp' ? 'badge-temp' : (hasOverwrite ? 'badge-overwrite' : 'badge-new')));
          badgeHtml = `<span class="${badgeClass}">${box.badgeText}</span>`;
        } else if (box.action === 'swap') {
          badgeHtml = '<span class="badge-swap">交換 Swap</span>';
        } else if (box.action === 'temp') {
          badgeHtml = '<span class="badge-temp">暫存 Temp</span>';
        } else if (hasOverwrite) {
          badgeHtml = '<span class="badge-overwrite">覆蓋 Overwrite</span>';
        } else if (box.diff) {
          badgeHtml = '<span class="badge-new">新放入</span>';
        }
        return `
          <div class="memory-box ${isDiff}" 
               data-var-name="${box.name}"
               onmouseenter="onMemoryBoxHover('${box.name}')"
               onmouseleave="onMemoryBoxLeave()"
               onclick="onMemoryBoxHover('${box.name}')"
               title="變數 ${box.name}：懸停或點擊以高亮程式碼參照行">
            <div class="memory-box-tag">${box.name}</div>
            <div class="memory-box-content">
              ${hasOverwrite ? `<span class="val-old">${box.prevVal}</span><span class="val-arrow">➔</span>` : ''}
              <span class="val-current">${box.val}</span>
            </div>
            ${badgeHtml}
          </div>
        `;
      }).join('');
    } else {
      memoryStage.style.display = 'none';
      memoryBoxesContainer.innerHTML = '';
    }
  }

  // 迴圈變數追蹤矩陣卡 (Trace Table Widget - agytodo 2.4)
  renderTraceTable(slide);

  // 雙向索引尺標卡 (Index Ruler Widget - agytodo 2.3)
  renderIndexRuler(slide);

  // 遞迴呼叫堆疊盒組件 (Call Stack Frame Widget - agytodo 2.5)
  renderCallStack(slide);

  // 單元通關徽章與 Colab 實戰卡片 (agytodo 5.3)
  const isLast = (index === activeSlidesData.length - 1);
  const completionCard = document.getElementById('completionCard');
  if (completionCard) {
    if (isLast) {
      completionCard.style.display = 'block';
      let colabTargetUrl = colabPracticeUrl;
      if (colabTargetUrl && !colabTargetUrl.startsWith('http')) {
        colabTargetUrl = `https://colab.research.google.com/github/johnnyy-lab/APCS1to3/blob/main/${colabTargetUrl.replace(/^\.\.\//, '')}`;
      }
      const customCard = slide.completionCard;
      const rawTitle = (customCard && customCard.badge) ? customCard.badge : '🏆 單元挑戰達成！滿分通關徽章';
      const badgeDesc = (customCard && customCard.summary) ? customCard.summary : `太棒了！您已全數完成本單元所有核心觀念與心智模型的微步進演練。<br>現在正是將觀念化為肌肉記憶的最佳時刻！`;
      const nextUnitHtml = (customCard && customCard.nextUnit) ? `<div class="completion-next-unit"><strong>👉 下一關預告</strong>：${customCard.nextUnit}</div>` : '';

      completionCard.innerHTML = `
        <div class="completion-badge-title">
          <span>${rawTitle}</span>
        </div>
        <div class="completion-badge-desc">
          ${badgeDesc}
        </div>
        <a class="btn-colab-launch" href="${colabTargetUrl || '#'}" target="_blank" rel="noopener noreferrer">
          <span>🚀 前往 Colab 動手練</span>
        </a>
        ${nextUnitHtml}
      `;
    } else {
      completionCard.style.display = 'none';
      completionCard.innerHTML = '';
    }
  }

  // 四階段學習路徑標記 (agytodo 5.1)
  const stageInfo = getSlideStage(slide, index, activeSlidesData.length);

  // 頁碼 (桌面端與行動端同步更新)
  const pageStr = `${index + 1} / ${activeSlidesData.length}`;
  const pageInd = document.getElementById('pageIndicator');
  if (pageInd) pageInd.textContent = pageStr;
  const dockPage = document.getElementById('dockPageIndicator');
  if (dockPage) {
    dockPage.innerHTML = `<span class="dock-stage-tag ${stageInfo.class}">${stageInfo.text}</span><span>${pageStr}</span>`;
  }

  // 微進度指示點 (Milestone Dots - agytodo 5.2) 與四階段標籤 (agytodo 5.1)
  const milestoneDots = document.getElementById('milestoneDots');
  if (milestoneDots) {
    let stageBadge = document.getElementById('stageBadge');
    if (!stageBadge && milestoneDots.parentNode) {
      stageBadge = document.createElement('span');
      stageBadge.id = 'stageBadge';
      milestoneDots.parentNode.insertBefore(stageBadge, milestoneDots);
    }
    if (stageBadge) {
      stageBadge.className = `stage-badge ${stageInfo.class}`;
      stageBadge.innerHTML = `<span class="stage-icon">${stageInfo.icon}</span> <span>${stageInfo.text}</span>`;
      stageBadge.title = `當前學習階段：${stageInfo.text} (${stageInfo.desc})`;
    }

    milestoneDots.innerHTML = activeSlidesData.map((s, i) => {
      let stateClass = 'pending';
      if (i < index) stateClass = 'completed';
      else if (i === index) stateClass = 'active';
      const dotStage = getSlideStage(s, i, activeSlidesData.length);
      return `<div class="milestone-dot ${stateClass}" 
                   title="第 ${i + 1} 頁 [${dotStage.text}]: ${s.titleZh || ''}" 
                   onclick="goToSlide(${i})"></div>`;
    }).join('');
  }

  // 按鈕狀態 (桌面端與行動端同步更新)
  const isFirst = (index === 0);
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  if (btnPrev) btnPrev.disabled = isFirst;
  if (btnNext) btnNext.disabled = isLast;

  const dockPrev = document.getElementById('dockBtnPrev');
  const dockNext = document.getElementById('dockBtnNext');
  if (dockPrev) dockPrev.disabled = isFirst;
  if (dockNext) dockNext.disabled = isLast;

  // 動態更新「下一頁」按鈕標籤（未揭曉顯示揭曉按鈕）
  if (!isAnswerRevealed) {
    if (btnNext) btnNext.innerHTML = '<span>👁️ 揭曉答案</span> <span class="key-badge">▶</span>';
    if (dockNext) dockNext.innerHTML = '<span>👁️ 揭曉</span><span>▶</span>';
  } else {
    if (btnNext) btnNext.innerHTML = '下一頁 <span class="key-badge">▶</span>';
    if (dockNext) dockNext.innerHTML = '<span>下一頁</span><span>▶</span>';
  }

  // 重置行解析條為預設狀態
  resetLineBar();
}

/* ==========================================================================
   7. 程式碼連動高亮、跨卡片數據流向導引與三維解析列 (agytodo 6.1, 6.2, 6.3)
   ========================================================================== */
function onLineHover(lineNum) {
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  const lineData = slide.codeLines.find(l => l.num === lineNum);
  if (lineData) {
    updateLineBar(lineData.num, lineData.mean, lineData.why, lineData.alt);
  }
  highlightMemoryBoxesForLines([lineNum]);

  // 🔗 跨卡片數據流向導引 (agytodo 6.1, 6.2)
  const mapping = getSlideOutputMapping(slide);
  const outIndices = mapping.codeToOutput[lineNum];
  if (outIndices && outIndices.length > 0) {
    triggerDataFlowSync(lineNum, outIndices[0], mapping.isErrorMap[lineNum]);
  } else if (pinnedLineNum === null) {
    clearDataFlowSync();
  }
}

function onLineLeave() {
  if (pinnedLineNum !== null) return; // 鎖定狀態下保留導引與高亮
  resetLineBar();
  clearHighlightedMemoryBoxes();
  clearHighlightedTraceRows();
  clearDataFlowSync();
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
    // 檢查是否有輸出映射行
    const mapping = getSlideOutputMapping(slide);
    for (const num of lineNums) {
      const outIndices = mapping.codeToOutput[num];
      if (outIndices && outIndices.length > 0) {
        triggerDataFlowSync(num, outIndices[0], mapping.isErrorMap[num]);
        break;
      }
    }
  }
  highlightMemoryBoxesForLines(lineNums);
  highlightTraceRowsForLines(lineNums);
}

function clearHighlightedLines() {
  if (pinnedLineNum !== null) return;
  document.querySelectorAll('.code-line.linked-highlight').forEach(el => {
    el.classList.remove('linked-highlight');
  });
  clearHighlightedMemoryBoxes();
  clearHighlightedTraceRows();
  clearDataFlowSync();
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
      ${alt && alt !== '此行無第二種寫法' && !alt.match(/^行 \d+。$/) ? `<span class="bar-badge badge-alt" style="margin-left:8px;">還可怎麼寫</span><span>${alt}</span>` : ''}
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
  if (pinnedLineNum === lineNum) {
    pinnedLineNum = null;
    clearHighlightedLines();
    clearDataFlowSync();
    resetLineBar();
    return;
  }
  pinnedLineNum = lineNum;
  document.querySelectorAll('.code-line.linked-highlight').forEach(el => el.classList.remove('linked-highlight'));
  const el = document.getElementById(`code-line-${lineNum}`);
  if (el) el.classList.add('linked-highlight');
  onLineHover(lineNum);
}

function onNoteClick(lineNums) {
  highlightLines(lineNums);
}

// 🔗 變數引用微高亮與連動呼應 (agytodo 6.3)
function highlightMemoryBoxesForLines(lineNums) {
  clearHighlightedMemoryBoxes();
  if (!Array.isArray(lineNums) || lineNums.length === 0) return;
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  if (!Array.isArray(slide.memoryState) || slide.memoryState.length === 0) return;

  const targetVars = new Set();
  lineNums.forEach(num => {
    const line = slide.codeLines.find(l => l.num === num);
    if (!line) return;
    if (Array.isArray(line.vars)) {
      line.vars.forEach(v => targetVars.add(v));
    } else {
      slide.memoryState.forEach(box => {
        const regex = new RegExp(`(^|[^a-zA-Z0-9_])${box.name}([^a-zA-Z0-9_]|$)`);
        const plainText = (line.html || '').replace(/<[^>]+>/g, ' ');
        if (regex.test(plainText)) {
          targetVars.add(box.name);
        }
      });
    }
  });

  targetVars.forEach(varName => {
    const boxEls = document.querySelectorAll(`.memory-box[data-var-name="${varName}"]`);
    boxEls.forEach(el => el.classList.add('var-referenced'));
  });
}

function clearHighlightedMemoryBoxes() {
  document.querySelectorAll('.memory-box.var-referenced').forEach(el => {
    el.classList.remove('var-referenced');
  });
}

function onMemoryBoxHover(varName) {
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  if (!Array.isArray(slide.codeLines)) return;
  const regex = new RegExp(`(^|[^a-zA-Z0-9_])${varName}([^a-zA-Z0-9_]|$)`);
  const matchedNums = [];
  slide.codeLines.forEach(l => {
    if (Array.isArray(l.vars) && l.vars.includes(varName)) {
      matchedNums.push(l.num);
    } else {
      const plainText = (l.html || '').replace(/<[^>]+>/g, ' ');
      if (regex.test(plainText)) {
        matchedNums.push(l.num);
      }
    }
  });
  if (matchedNums.length > 0) {
    highlightLines(matchedNums);
    const boxEl = document.querySelector(`.memory-box[data-var-name="${varName}"]`);
    if (boxEl) boxEl.classList.add('var-referenced');
  }
}

function onMemoryBoxLeave() {
  if (pinnedLineNum !== null) return;
  clearHighlightedLines();
  clearHighlightedMemoryBoxes();
  clearHighlightedTraceRows();
}

/* ==========================================================================
   7.4.5 迴圈變數追蹤矩陣卡引擎（Trace Table Widget - agytodo 2.4）
   ========================================================================== */

/**
 * 動態渲染迴圈變數追蹤矩陣卡 (Trace Table)
 * @param {Object} slide 當前投影片物件
 */
function renderTraceTable(slide) {
  let traceStage = document.getElementById('traceTableStage');
  // 自動掛載防禦：若 HTML 檔中無 traceTableStage，自動在 notes 區塊內動態插入
  if (!traceStage) {
    const memoryStage = document.getElementById('memoryStage');
    const notesContainer = memoryStage ? memoryStage.parentNode : (document.querySelector('.card-notes > div') || document.querySelector('.card-notes'));
    if (!notesContainer) return;
    traceStage = document.createElement('div');
    traceStage.className = 'trace-table-stage';
    traceStage.id = 'traceTableStage';
    traceStage.style.display = 'none';
    traceStage.innerHTML = `
      <div class="trace-table-header">
        <span class="trace-table-title" id="traceTableTitle">📊 迴圈變數追蹤矩陣 (Trace Table)</span>
        <span class="trace-table-hint" id="traceTableHint">變數與條件動態追蹤</span>
      </div>
      <div class="trace-table-wrap" id="traceTableWrap"></div>
    `;
    if (memoryStage && memoryStage.nextSibling) {
      notesContainer.insertBefore(traceStage, memoryStage.nextSibling);
    } else {
      const completionCard = document.getElementById('completionCard');
      if (completionCard) {
        notesContainer.insertBefore(traceStage, completionCard);
      } else {
        notesContainer.appendChild(traceStage);
      }
    }
  }

  const traceTableTitle = document.getElementById('traceTableTitle');
  const traceTableHint = document.getElementById('traceTableHint');
  const traceTableWrap = document.getElementById('traceTableWrap');
  if (!traceTableWrap) return;

  // 若無 traceTable 資料或表頭為空，隱藏舞台並清空
  if (!slide || !slide.traceTable || !Array.isArray(slide.traceTable.headers) || slide.traceTable.headers.length === 0) {
    traceStage.style.display = 'none';
    traceTableWrap.innerHTML = '';
    return;
  }

  const tt = slide.traceTable;
  traceStage.style.display = 'block';

  if (traceTableTitle) {
    traceTableTitle.textContent = tt.title || '📊 迴圈變數追蹤矩陣 (Trace Table)';
  }
  if (traceTableHint) {
    traceTableHint.textContent = tt.hint || '每一圈變數動態變化';
  }

  const headers = tt.headers || [];
  const rows = Array.isArray(tt.rows) ? tt.rows : [];
  const activeRowIdx = (typeof tt.activeRow === 'number') ? tt.activeRow : ((typeof tt.activeRowIndex === 'number') ? tt.activeRowIndex : -1);

  const thHtml = headers.map(h => `<th>${h}</th>`).join('');

  const rowsHtml = rows.map((rowItem, rIndex) => {
    // 支援 row 為物件或單純陣列
    const isObj = (typeof rowItem === 'object' && rowItem !== null && !Array.isArray(rowItem));
    const values = isObj ? (rowItem.values || rowItem.cells || []) : (Array.isArray(rowItem) ? rowItem : []);
    const isRowActive = isObj ? (rowItem.active === true || rIndex === activeRowIdx) : (rIndex === activeRowIdx);
    const isRowDone = isObj ? (rowItem.done === true || (activeRowIdx > -1 && rIndex < activeRowIdx)) : (activeRowIdx > -1 && rIndex < activeRowIdx);

    let rowClass = 'trace-row';
    if (isRowActive) rowClass += ' trace-row-active';
    else if (isRowDone) rowClass += ' trace-row-done';

    // 狀態徽章
    let badgeHtml = '';
    if (isObj && rowItem.badge) {
      let bClass = rowItem.badgeClass || (isRowActive ? 'trace-badge-active' : (rowItem.status === 'break' ? 'trace-badge-break' : (rowItem.status === 'continue' ? 'trace-badge-continue' : (rowItem.status === 'exit' ? 'trace-badge-exit' : 'trace-badge-done'))));
      badgeHtml = `<span class="trace-badge ${bClass}">${rowItem.badge}</span>`;
    } else if (isRowActive && tt.showActiveBadge !== false) {
      badgeHtml = `<span class="trace-badge trace-badge-active">當前圈</span>`;
    }

    // 關聯程式碼行號
    let hoverEvents = '';
    let codeLinesAttr = '';
    let clickableClass = '';
    const codeLines = isObj ? (Array.isArray(rowItem.codeLines) ? rowItem.codeLines : (typeof rowItem.codeLine === 'number' ? [rowItem.codeLine] : null)) : null;
    if (codeLines && codeLines.length > 0) {
      clickableClass = ' trace-row-clickable';
      const lineNumsJson = JSON.stringify(codeLines);
      hoverEvents = `
        onmouseenter="onTraceRowHover(${lineNumsJson})"
        onmouseleave="onTraceRowLeave()"
        onclick="togglePinTraceRow(${lineNumsJson}, event)"
      `;
      codeLinesAttr = `data-code-lines="${codeLines.join(',')}" title="點擊鎖定或懸停高亮關聯程式碼行 [${codeLines.join(', ')}]"`;
    }

    const badgeCol = (isObj && typeof rowItem.badgeCol === 'number') ? rowItem.badgeCol : 0;

    const cellsHtml = values.map((val, cIndex) => {
      const isDiff = isObj && Array.isArray(rowItem.diffCols) && rowItem.diffCols.includes(cIndex);
      const diffClass = isDiff ? 'trace-cell-diff' : '';
      let cellContent = val;
      if (cIndex === badgeCol && badgeHtml) {
        cellContent = `<div class="trace-cell-inner"><span>${val}</span>${badgeHtml}</div>`;
      }
      return `<td class="${diffClass}">${cellContent}</td>`;
    }).join('');

    return `
      <tr class="${rowClass}${clickableClass}" id="trace-row-${rIndex}" ${codeLinesAttr} ${hoverEvents}>
        ${cellsHtml}
      </tr>
    `;
  }).join('');

  traceTableWrap.innerHTML = `
    <table class="trace-table" aria-label="迴圈變數追蹤表">
      <thead>
        <tr>${thHtml}</tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
}

/**
 * 依據程式碼行號反向微高亮追蹤表列
 */
function highlightTraceRowsForLines(lineNums) {
  if (!Array.isArray(lineNums) || lineNums.length === 0) return;
  clearHighlightedTraceRows();
  const rows = document.querySelectorAll('.trace-row[data-code-lines]');
  rows.forEach(row => {
    const rawLines = row.getAttribute('data-code-lines');
    if (!rawLines) return;
    const rowLines = rawLines.split(',').map(s => parseInt(s.trim(), 10));
    const hasOverlap = lineNums.some(num => rowLines.includes(num));
    if (hasOverlap) {
      row.classList.add('trace-row-highlighted');
    }
  });
}

/**
 * 清除所有追蹤表反向高亮
 */
function clearHighlightedTraceRows() {
  document.querySelectorAll('.trace-row.trace-row-highlighted').forEach(el => {
    el.classList.remove('trace-row-highlighted');
  });
}

/**
 * 滑鼠懸停追蹤表列時高亮程式碼行
 */
function onTraceRowHover(lineNums) {
  if (!Array.isArray(lineNums) || lineNums.length === 0) return;
  highlightLines(lineNums);
}

/**
 * 滑鼠離開追蹤表列時恢復
 */
function onTraceRowLeave() {
  if (pinnedLineNum !== null) return;
  clearHighlightedLines();
  clearHighlightedMemoryBoxes();
  clearHighlightedTraceRows();
}

/**
 * 點選追蹤表列切換鎖定關聯程式碼行
 */
function togglePinTraceRow(lineNums, event) {
  if (event) event.stopPropagation();
  if (!Array.isArray(lineNums) || lineNums.length === 0) return;
  onLineClick(lineNums[0]);
}

// 暴露全域事件處理函式以供 inline HTML 呼叫
window.renderTraceTable = renderTraceTable;
window.onTraceRowHover = onTraceRowHover;
window.onTraceRowLeave = onTraceRowLeave;
window.togglePinTraceRow = togglePinTraceRow;
window.highlightTraceRowsForLines = highlightTraceRowsForLines;
window.clearHighlightedTraceRows = clearHighlightedTraceRows;

/* ==========================================================================
   7.4 雙向索引尺標卡渲染引擎 (Index Ruler Widget - agytodo 2.3)
   ========================================================================== */

/**
 * 動態渲染字串/串列雙向索引尺標卡
 * slide.indexRuler 資料格式：
 * {
 *   title: "字串 s = \"PYTHON\" 的雙向索引",
 *   hint: "點選欄位可高亮對應索引",
 *   items: ["P","Y","T","H","O","N"],    // 字串字元或串列元素
 *   activeIndex: 2,                       // 當前高亮欄位（optional）
 *   diffIndices: [0, 5],                  // 特別標記欄位（optional）
 *   showLegend: true                      // 是否顯示圖例
 * }
 */
function renderIndexRuler(slide) {
  let rulerStage = document.getElementById('indexRulerStage');

  // 自動掛載：若 HTML 無此容器，自動插入在 traceTableStage 之後或 completionCard 之前
  if (!rulerStage) {
    const traceStage = document.getElementById('traceTableStage');
    const notesContainer = traceStage
      ? traceStage.parentNode
      : (document.querySelector('.card-notes > div') || document.querySelector('.card-notes'));
    if (!notesContainer) return;

    rulerStage = document.createElement('div');
    rulerStage.className = 'index-ruler-stage';
    rulerStage.id = 'indexRulerStage';
    rulerStage.style.display = 'none';
    rulerStage.innerHTML = `
      <div class="index-ruler-header">
        <span class="index-ruler-title" id="indexRulerTitle">📐 雙向索引尺標</span>
        <span class="index-ruler-hint" id="indexRulerHint">正向 0~N-1 · 負向 -1~-N</span>
      </div>
      <div class="index-ruler-cells" id="indexRulerCells"></div>
      <div class="index-ruler-legend" id="indexRulerLegend" style="display:none">
        <div class="ruler-legend-item"><div class="ruler-legend-dot pos"></div>正向索引</div>
        <div class="ruler-legend-item"><div class="ruler-legend-dot val"></div>字元/元素</div>
        <div class="ruler-legend-item"><div class="ruler-legend-dot neg"></div>負向索引</div>
      </div>
    `;

    const completionCard = document.getElementById('completionCard');
    if (traceStage && traceStage.nextSibling) {
      notesContainer.insertBefore(rulerStage, traceStage.nextSibling);
    } else if (completionCard) {
      notesContainer.insertBefore(rulerStage, completionCard);
    } else {
      notesContainer.appendChild(rulerStage);
    }
  }

  const rulerTitle = document.getElementById('indexRulerTitle');
  const rulerHint = document.getElementById('indexRulerHint');
  const rulerCells = document.getElementById('indexRulerCells');
  const rulerLegend = document.getElementById('indexRulerLegend');

  // 若無資料，隱藏並清空
  if (!slide || !slide.indexRuler || !Array.isArray(slide.indexRuler.items) || slide.indexRuler.items.length === 0) {
    rulerStage.style.display = 'none';
    if (rulerCells) rulerCells.innerHTML = '';
    return;
  }

  const ir = slide.indexRuler;
  const items = ir.items;
  const n = items.length;
  const activeIndex = (typeof ir.activeIndex === 'number') ? ir.activeIndex : -1;
  const diffIndices = Array.isArray(ir.diffIndices) ? ir.diffIndices : [];

  rulerStage.style.display = 'block';

  if (rulerTitle) rulerTitle.textContent = ir.title || '📐 雙向索引尺標';
  if (rulerHint) rulerHint.textContent = ir.hint || `字串/串列長度：${n}，點選欄位高亮對應索引`;

  if (rulerLegend) {
    rulerLegend.style.display = (ir.showLegend !== false) ? 'flex' : 'none';
  }

  // 生成欄位 HTML：每個欄位包含 [正向索引, 元素, 負向索引]
  const columnsHtml = items.map((item, i) => {
    const posIdx = i;
    const negIdx = i - n;
    const isActive = (i === activeIndex);
    const isDiff = diffIndices.includes(i);
    const colClass = `ruler-column${isActive ? ' ruler-col-active' : ''}${isDiff ? ' ruler-col-diff' : ''}`;
    const clickHandler = `onRulerColumnClick(${i})`;

    // 顯示字串時用引號包圍
    let displayVal = item;
    if (typeof item === 'string' && item.length === 1) {
      displayVal = `'${item}'`;
    } else if (typeof item === 'string' && item.length > 1) {
      displayVal = item;
    }

    return `
      <div class="${colClass}" data-index="${i}" onclick="${clickHandler}" title="正向索引: ${posIdx}  負向索引: ${negIdx}  元素: ${item}">
        <div class="ruler-cell-pos">${posIdx}</div>
        <div class="ruler-cell-value">${displayVal}</div>
        <div class="ruler-cell-neg">${negIdx}</div>
      </div>
    `;
  }).join('');

  if (rulerCells) {
    rulerCells.innerHTML = `<div class="ruler-row" style="display:flex;flex-direction:row;gap:2px;">${columnsHtml}</div>`;
  }
}

/**
 * 點選尺標欄位時切換高亮
 */
function onRulerColumnClick(idx) {
  const allCols = document.querySelectorAll('.ruler-column');
  const clickedCol = document.querySelector(`.ruler-column[data-index="${idx}"]`);
  if (!clickedCol) return;

  // 若已高亮則取消，否則切換到該欄
  if (clickedCol.classList.contains('ruler-col-active')) {
    allCols.forEach(c => c.classList.remove('ruler-col-active'));
  } else {
    allCols.forEach(c => c.classList.remove('ruler-col-active'));
    clickedCol.classList.add('ruler-col-active');
  }
}

window.renderIndexRuler = renderIndexRuler;
window.onRulerColumnClick = onRulerColumnClick;

/* ==========================================================================
   7.5 遞迴呼叫堆疊盒渲染引擎 (Call Stack Frame Widget - agytodo 2.5)
   ========================================================================== */

/**
 * 動態渲染遞迴呼叫堆疊盒
 * slide.callStack 資料格式：
 * {
 *   title: "呼叫堆疊（Call Stack）",
 *   hint: "最新呼叫在最上方",
 *   frames: [                             // 由底部到頂部順序
 *     {
 *       name: "factorial",               // 函式名
 *       args: "(n=5)",                   // 參數（帶括號的完整字串）
 *       vars: [                          // 區域變數（optional）
 *         { name: "n", val: "5" },
 *         { name: "result", val: "?" }
 *       ],
 *       returnVal: "120",                // 已回傳的值（optional）
 *       status: "active"|"push"|"pop"|"base"|"done",
 *       badge: "執行中",                 // 徽章文字（optional）
 *       depth: 0                         // 巢狀深度（optional）
 *     }
 *   ],
 *   maxDepth: 5                          // 最大深度限制展示（optional）
 * }
 */
function renderCallStack(slide) {
  let callStackStage = document.getElementById('callStackStage');

  // 自動掛載
  if (!callStackStage) {
    const rulerStage = document.getElementById('indexRulerStage');
    const traceStage = document.getElementById('traceTableStage');
    const anchor = rulerStage || traceStage;
    const notesContainer = anchor
      ? anchor.parentNode
      : (document.querySelector('.card-notes > div') || document.querySelector('.card-notes'));
    if (!notesContainer) return;

    callStackStage = document.createElement('div');
    callStackStage.className = 'call-stack-stage';
    callStackStage.id = 'callStackStage';
    callStackStage.style.display = 'none';
    callStackStage.innerHTML = `
      <div class="call-stack-header">
        <span class="call-stack-title" id="callStackTitle">📞 呼叫堆疊 (Call Stack)</span>
        <span class="call-stack-hint" id="callStackHint">最新呼叫在最上方</span>
      </div>
      <div class="call-stack-frames" id="callStackFrames"></div>
      <div class="call-stack-depth-bar" id="callStackDepthBar" style="display:none">
        <span class="call-stack-depth-label">呼叫深度：</span>
        <div class="call-stack-depth-dots" id="callStackDepthDots"></div>
      </div>
    `;

    const completionCard = document.getElementById('completionCard');
    if (anchor && anchor.nextSibling) {
      notesContainer.insertBefore(callStackStage, anchor.nextSibling);
    } else if (completionCard) {
      notesContainer.insertBefore(callStackStage, completionCard);
    } else {
      notesContainer.appendChild(callStackStage);
    }
  }

  const callStackTitle = document.getElementById('callStackTitle');
  const callStackHint = document.getElementById('callStackHint');
  const callStackFrames = document.getElementById('callStackFrames');
  const callStackDepthBar = document.getElementById('callStackDepthBar');
  const callStackDepthDots = document.getElementById('callStackDepthDots');

  // 若無資料，隱藏並清空
  if (!slide || !slide.callStack || !Array.isArray(slide.callStack.frames) || slide.callStack.frames.length === 0) {
    callStackStage.style.display = 'none';
    if (callStackFrames) callStackFrames.innerHTML = '';
    return;
  }

  const cs = slide.callStack;
  const frames = cs.frames;

  callStackStage.style.display = 'block';

  if (callStackTitle) callStackTitle.textContent = cs.title || '📞 呼叫堆疊 (Call Stack)';
  if (callStackHint) callStackHint.textContent = cs.hint || '最新呼叫在最上方';

  // 渲染框架列表
  const framesHtml = frames.map((frame, fi) => {
    const status = frame.status || 'active';
    let frameClass = 'stack-frame';
    if (status === 'active') frameClass += ' frame-active';
    else if (status === 'pop') frameClass += ' frame-popping';
    else if (status === 'base') frameClass += ' frame-base';
    else if (status === 'done') frameClass += ' frame-done';

    // 徽章
    let badgeHtml = '';
    let badgeClass = 'stack-badge ';
    if (frame.badge) {
      if (status === 'active') badgeClass += 'stack-badge-active';
      else if (status === 'push') badgeClass += 'stack-badge-push';
      else if (status === 'pop') badgeClass += 'stack-badge-pop';
      else if (status === 'base') badgeClass += 'stack-badge-base';
      else badgeClass += 'stack-badge-done';
      badgeHtml = `<span class="${badgeClass}">${frame.badge}</span>`;
    }

    // 區域變數
    let varsHtml = '';
    if (Array.isArray(frame.vars) && frame.vars.length > 0) {
      const varItems = frame.vars.map(v =>
        `<span class="stack-frame-var">
          <span class="stack-frame-var-name">${v.name}</span>
          <span class="stack-frame-var-eq"> = </span>
          <span class="stack-frame-var-val">${v.val}</span>
        </span>`
      ).join('');
      varsHtml = `<div class="stack-frame-vars">${varItems}</div>`;
    }

    // 回傳值
    let returnHtml = '';
    if (frame.returnVal !== undefined && frame.returnVal !== null) {
      returnHtml = `
        <div class="stack-frame-return">
          <span class="stack-frame-return-arrow">↩ return</span>
          <span class="stack-frame-return-val">${frame.returnVal}</span>
        </div>`;
    }

    const depth = typeof frame.depth === 'number' ? frame.depth : fi;
    const marginLeft = Math.min(depth * 8, 48);

    return `
      <div class="${frameClass}" data-frame-index="${fi}" style="margin-left:${marginLeft}px">
        <div class="stack-frame-header">
          <span class="stack-frame-name">${frame.name || 'func'}</span>
          <span class="stack-frame-args">${frame.args || ''}</span>
          ${badgeHtml}
        </div>
        ${varsHtml}
        ${returnHtml}
      </div>
    `;
  }).join('');

  if (callStackFrames) {
    callStackFrames.innerHTML = framesHtml.length > 0
      ? framesHtml
      : '<div class="call-stack-empty">堆疊為空</div>';
  }

  // 深度指示點
  const totalDepth = frames.length;
  const maxDots = cs.maxDepth || Math.max(totalDepth, 1);
  if (callStackDepthBar && totalDepth > 0) {
    callStackDepthBar.style.display = 'flex';
    if (callStackDepthDots) {
      callStackDepthDots.innerHTML = Array.from({ length: maxDots }, (_, i) =>
        `<div class="call-stack-depth-dot ${i < totalDepth ? 'active' : ''}" title="深度 ${i + 1}"></div>`
      ).join('');
    }
  } else if (callStackDepthBar) {
    callStackDepthBar.style.display = 'none';
  }
}

window.renderCallStack = renderCallStack;



/* ==========================================================================
   7.5 數據流向同步引擎（Data Flow Sync Engine - agytodo 6.1, 6.2）
   ========================================================================== */

/**
 * 智慧推導程式碼行與終端機輸出行之間的因果對映
 */
function getSlideOutputMapping(slide) {
  if (!slide || !Array.isArray(slide.codeLines)) {
    return { codeToOutput: {}, outputToCode: {}, isErrorMap: {} };
  }

  // 1. 若 slide 顯式指定 outputMapping，以顯式設定優先
  if (slide.outputMapping) {
    const codeToOutput = {};
    const outputToCode = {};
    const isErrorMap = {};
    Object.keys(slide.outputMapping).forEach(cKey => {
      const cNum = Number(cKey);
      const o = slide.outputMapping[cKey];
      const oArr = Array.isArray(o) ? o : [o];
      codeToOutput[cNum] = oArr;
      oArr.forEach(outIdx => {
        if (!outputToCode[outIdx]) outputToCode[outIdx] = [];
        outputToCode[outIdx].push(cNum);
      });
    });
    return { codeToOutput, outputToCode, isErrorMap };
  }

  const codeToOutput = {};
  const outputToCode = {};
  const isErrorMap = {};

  if (!slide.output || String(slide.output).includes('output-empty')) {
    return { codeToOutput, outputToCode, isErrorMap };
  }

  const outputStr = String(slide.output);
  const isErrorOutput = outputStr.includes('output-error') || /Error:|Exception:/.test(outputStr);

  if (isErrorOutput) {
    const errLine = slide.codeLines.find(l => l.error === true) || slide.codeLines[slide.codeLines.length - 1];
    if (errLine) {
      codeToOutput[errLine.num] = [1];
      outputToCode[1] = [errLine.num];
      isErrorMap[errLine.num] = true;
    }
    return { codeToOutput, outputToCode, isErrorMap };
  }

  // 正常輸出：找出所有包含 print() 函式呼叫的行
  const printLines = [];
  slide.codeLines.forEach(l => {
    const hasPrint = /\bprint\s*\(/.test(l.html || '') ||
                     (l.html && (l.html.includes('token-func') || l.html.includes('token-builtin')) && /print/.test(l.html)) ||
                     (l.mean && l.mean.includes('print('));
    if (hasPrint) {
      printLines.push(l.num);
    }
  });

  const outputLineCount = outputStr.split('\n').length;

  if (printLines.length === 0) {
    const diffLine = slide.codeLines.find(l => l.diff) || slide.codeLines[slide.codeLines.length - 1];
    if (diffLine) {
      codeToOutput[diffLine.num] = [1];
      outputToCode[1] = [diffLine.num];
    }
  } else if (printLines.length === 1) {
    const allOuts = [];
    for (let i = 1; i <= outputLineCount; i++) allOuts.push(i);
    codeToOutput[printLines[0]] = allOuts;
    allOuts.forEach(idx => {
      outputToCode[idx] = [printLines[0]];
    });
  } else if (printLines.length === outputLineCount) {
    printLines.forEach((cNum, idx) => {
      const outIdx = idx + 1;
      codeToOutput[cNum] = [outIdx];
      outputToCode[outIdx] = [cNum];
    });
  } else {
    printLines.forEach((cNum, idx) => {
      const outIdx = Math.min(idx + 1, outputLineCount);
      if (!codeToOutput[cNum]) codeToOutput[cNum] = [];
      codeToOutput[cNum].push(outIdx);
      if (!outputToCode[outIdx]) outputToCode[outIdx] = [];
      outputToCode[outIdx].push(cNum);
    });
  }

  return { codeToOutput, outputToCode, isErrorMap };
}

/**
 * 格式化終端機輸出內容，自動將多行文字包裹為支援雙向互動之 output-line
 */
function formatOutputViewportContent(rawOutput, slide) {
  if (!rawOutput) {
    return '<span class="output-empty">（無終端輸出）</span>';
  }
  const str = String(rawOutput);
  if (str.includes('output-empty')) {
    return str;
  }
  if (str.includes('output-error')) {
    return `
      <div class="output-line output-line-error" id="output-line-1" data-out-idx="1"
           onmouseenter="onOutputLineHover(1)"
           onmouseleave="onOutputLineLeave()"
           onclick="onOutputLineClick(1)">
        <span class="output-line-text">${str}</span>
        <span class="dataflow-badge badge-output-src badge-err" id="output-badge-1" style="display: none;"></span>
      </div>
    `;
  }

  const lines = str.split('\n');
  return lines.map((lineContent, i) => {
    const idx = i + 1;
    return `
      <div class="output-line" id="output-line-${idx}" data-out-idx="${idx}"
           onmouseenter="onOutputLineHover(${idx})"
           onmouseleave="onOutputLineLeave()"
           onclick="onOutputLineClick(${idx})">
        <span class="output-line-text">${lineContent || '&nbsp;'}</span>
        <span class="dataflow-badge badge-output-src" id="output-badge-${idx}" style="display: none;"></span>
      </div>
    `;
  }).join('');
}

/**
 * 終端機輸出行懸停互動（反向連動程式碼與導引線）
 */
function onOutputLineHover(outIdx) {
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  const mapping = getSlideOutputMapping(slide);
  const codeNums = mapping.outputToCode[outIdx];
  if (codeNums && codeNums.length > 0) {
    const cNum = codeNums[0];
    highlightLines(codeNums);
    triggerDataFlowSync(cNum, outIdx, mapping.isErrorMap[cNum]);
  } else {
    const outEl = document.getElementById(`output-line-${outIdx}`);
    if (outEl) outEl.classList.add('output-focused');
  }
}

function onOutputLineLeave() {
  if (pinnedLineNum !== null) return;
  clearHighlightedLines();
  clearDataFlowSync();
}

function onOutputLineClick(outIdx) {
  if (!activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  const mapping = getSlideOutputMapping(slide);
  const codeNums = mapping.outputToCode[outIdx];
  if (codeNums && codeNums.length > 0) {
    onLineClick(codeNums[0]);
  }
}

/**
 * 確保畫布中具備 SVG 導引線 DOM 容器
 */
function ensureFlowGuideSvg() {
  let svg = document.getElementById('flowGuideSvg');
  if (!svg) {
    const stage = document.getElementById('slideStage');
    if (!stage) return null;
    svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'flow-guide-svg');
    svg.setAttribute('id', 'flowGuideSvg');
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML = `
      <defs>
        <linearGradient id="flowLineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.95" />
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="1" />
        </linearGradient>
        <linearGradient id="flowLineGradErr" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f43f5e" stop-opacity="0.95" />
          <stop offset="100%" stop-color="#e11d48" stop-opacity="1" />
        </linearGradient>
        <marker id="flowArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#06b6d4" />
        </marker>
        <marker id="flowArrowErr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f43f5e" />
        </marker>
        <marker id="flowArrowIdle" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#000000" />
        </marker>
      </defs>
      <path id="flowGuidePath" class="flow-guide-path" d="" />
      <circle id="flowGuideStartDot" class="flow-guide-start-dot" r="4" cx="-999" cy="-999" />
      <circle id="flowGuideDot" class="flow-guide-dot" r="4.5" cx="-999" cy="-999" />
    `;
    stage.appendChild(svg);
  }
  return svg;
}

/**
 * 6.1 桌機版：計算並繪製跨卡片平滑貝茲導引線與流動光斑
 */
function drawFlowGuide(codeLineNum, outputLineIdx, isError) {
  if (window.innerWidth <= 1024) return;

  const stage = document.getElementById('slideStage');
  const codeLineEl = document.getElementById(`code-line-${codeLineNum}`);
  let outputEl = document.getElementById(`output-line-${outputLineIdx}`);
  if (!outputEl) {
    outputEl = document.getElementById('outputViewport');
  }

  ensureFlowGuideSvg();
  const path = document.getElementById('flowGuidePath');
  const startDot = document.getElementById('flowGuideStartDot');
  const pulseDot = document.getElementById('flowGuideDot');

  if (!stage || !codeLineEl || !outputEl || !path) return;

  const stageRect = stage.getBoundingClientRect();
  const codeRect = codeLineEl.getBoundingClientRect();
  const outRect = outputEl.getBoundingClientRect();

  if (codeRect.width === 0 || outRect.width === 0 || stageRect.width === 0) return;

  // 起點 (程式碼行右側偏內)
  const x1 = (codeRect.right - stageRect.left) - 16;
  const y1 = (codeRect.top - stageRect.top) + (codeRect.height / 2);

  // 終點 (終端機輸出列右側偏內)
  const x2 = (outRect.right - stageRect.left) - 16;
  const y2 = (outRect.top - stageRect.top) + (outRect.height / 2);

  // 弧度控制：向右外弧凸出至卡片與筆記區的間隙 (gap)
  const dy = Math.abs(y2 - y1);
  const bulge = Math.max(32, Math.min(65, dy * 0.35));

  const cp1x = x1 + bulge;
  const cp1y = y1;
  const cp2x = x2 + bulge;
  const cp2y = y2;

  const d = `M ${x1} ${y1} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`;
  path.setAttribute('d', d);

  const isIdle = document.body.classList.contains('idle-theme');
  if (isError) {
    path.classList.add('error-guide');
    path.setAttribute('marker-end', isIdle ? 'url(#flowArrowIdle)' : 'url(#flowArrowErr)');
  } else {
    path.classList.remove('error-guide');
    path.setAttribute('marker-end', isIdle ? 'url(#flowArrowIdle)' : 'url(#flowArrow)');
  }
  path.classList.add('active');

  if (startDot) {
    startDot.setAttribute('cx', x1);
    startDot.setAttribute('cy', y1);
    startDot.classList.add('active');
    if (isError) startDot.classList.add('error-dot');
    else startDot.classList.remove('error-dot');
  }

  animatePulseDot(path, pulseDot, isError);
}

/**
 * 沿著 SVG 貝茲曲線流動的光斑動畫
 */
function animatePulseDot(pathEl, dotEl, isError) {
  if (!pathEl || !dotEl) return;
  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
    animFrameId = null;
  }

  let totalLen = 0;
  try {
    totalLen = pathEl.getTotalLength();
  } catch (err) {
    return;
  }
  if (totalLen <= 0) return;

  dotEl.classList.add('active');
  if (isError) dotEl.classList.add('error-dot');
  else dotEl.classList.remove('error-dot');

  const duration = 1200; // 1.2 秒循環一次
  let startTime = null;

  function step(timestamp) {
    if (!startTime) startTime = timestamp;
    const elapsed = (timestamp - startTime) % duration;
    const progress = elapsed / duration;
    try {
      const pt = pathEl.getPointAtLength(progress * totalLen);
      dotEl.setAttribute('cx', pt.x);
      dotEl.setAttribute('cy', pt.y);
    } catch (e) {}

    if (pathEl.classList.contains('active')) {
      animFrameId = requestAnimationFrame(step);
    }
  }
  animFrameId = requestAnimationFrame(step);
}

function clearFlowGuide() {
  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
    animFrameId = null;
  }
  const path = document.getElementById('flowGuidePath');
  if (path) {
    path.classList.remove('active');
    path.setAttribute('d', '');
  }
  const startDot = document.getElementById('flowGuideStartDot');
  if (startDot) startDot.classList.remove('active');
  const pulseDot = document.getElementById('flowGuideDot');
  if (pulseDot) {
    pulseDot.classList.remove('active');
    pulseDot.setAttribute('cx', -999);
    pulseDot.setAttribute('cy', -999);
  }
}

/**
 * 觸發數據流向同步（桌機導引線 + 行動端同色呼吸脈衝）
 */
function triggerDataFlowSync(codeLineNum, outputLineIdx, isError) {
  const isMobile = (window.innerWidth <= 1024);

  const codeEl = document.getElementById(`code-line-${codeLineNum}`);
  const outEl = document.getElementById(`output-line-${outputLineIdx}`) || document.getElementById('outputViewport');
  const codeBadge = document.getElementById(`code-badge-${codeLineNum}`);
  const outBadge = document.getElementById(`output-badge-${outputLineIdx}`);

  // 聚焦終端輸出文字行
  if (outEl) {
    outEl.classList.add('output-focused');
  }

  if (isMobile) {
    // 6.2 行動端同色呼吸外框與索引標籤
    if (codeEl) {
      codeEl.classList.add('pulse-active-code');
      if (codeBadge) {
        codeBadge.textContent = isError ? '💥 報錯來源' : `➔ 輸出 #${outputLineIdx}`;
        codeBadge.style.display = 'inline-flex';
        codeBadge.className = `dataflow-badge badge-code-out ${isError ? 'badge-err' : ''}`;
      }
    }
    if (outEl) {
      outEl.classList.add('pulse-active-output');
      if (outBadge) {
        outBadge.textContent = isError ? `行 ${codeLineNum} 觸發` : `來自 行 ${codeLineNum}`;
        outBadge.style.display = 'inline-flex';
        outBadge.className = `dataflow-badge badge-output-src ${isError ? 'badge-err' : ''}`;
      }
    }
  } else {
    // 6.1 桌機版跨卡片 SVG 導引線
    drawFlowGuide(codeLineNum, outputLineIdx, isError);
  }
}

function clearDataFlowSync() {
  clearFlowGuide();
  document.querySelectorAll('.pulse-active-code').forEach(el => el.classList.remove('pulse-active-code'));
  document.querySelectorAll('.pulse-active-output').forEach(el => el.classList.remove('pulse-active-output'));
  document.querySelectorAll('.output-focused').forEach(el => el.classList.remove('output-focused'));
  document.querySelectorAll('.dataflow-badge').forEach(el => {
    el.style.display = 'none';
    el.textContent = '';
  });
}

function updateFlowGuideTheme() {
  const path = document.getElementById('flowGuidePath');
  if (!path || !path.classList.contains('active')) return;
  const isIdle = document.body.classList.contains('idle-theme');
  const isError = path.classList.contains('error-guide');
  if (isError) {
    path.setAttribute('marker-end', isIdle ? 'url(#flowArrowIdle)' : 'url(#flowArrowErr)');
  } else {
    path.setAttribute('marker-end', isIdle ? 'url(#flowArrowIdle)' : 'url(#flowArrow)');
  }
}

function updateActiveFlowGuide() {
  if (pinnedLineNum === null || !activeSlidesData[currentSlide]) return;
  const slide = activeSlidesData[currentSlide];
  const mapping = getSlideOutputMapping(slide);
  const outIndices = mapping.codeToOutput[pinnedLineNum];
  if (outIndices && outIndices.length > 0) {
    drawFlowGuide(pinnedLineNum, outIndices[0], mapping.isErrorMap[pinnedLineNum]);
  }
}


// 🪜 四階段學習路徑判定 (agytodo 5.1)
function getSlideStage(slide, index, total) {
  if (!slide) return { text: '① 觀念初探', icon: '💡', class: 'stage-concept', desc: '建立心智模型' };
  if (slide.stage) {
    const s = String(slide.stage).trim();
    if (s.includes('1') || s.includes('①') || s === 'concept') {
      return { text: '① 觀念初探', icon: '💡', class: 'stage-concept', desc: '建立心智模型' };
    }
    if (s.includes('2') || s.includes('②') || s === 'syntax') {
      return { text: '② 語法鐵律', icon: '⚖️', class: 'stage-syntax', desc: '核心語法規範' };
    }
    if (s.includes('3') || s.includes('③') || s === 'trap') {
      return { text: '③ 考場地雷', icon: '💥', class: 'stage-trap', desc: '避開爆零天坑' };
    }
    if (s.includes('4') || s.includes('④') || s === 'practice') {
      return { text: '④ 綜合驗收', icon: '🏆', class: 'stage-practice', desc: '實戰驗收閉環' };
    }
    return { text: s, icon: '📌', class: 'stage-custom', desc: s };
  }

  // 自動依據投影片屬性智能判定
  if (index === total - 1) {
    return { text: '④ 綜合驗收', icon: '🏆', class: 'stage-practice', desc: '實戰驗收閉環' };
  }
  const hasError = Array.isArray(slide.codeLines) && slide.codeLines.some(l => l.error);
  const hasTrapNote = Array.isArray(slide.notes) && slide.notes.some(n => n.type === 'wa' || n.type === 'error');
  const isErrorOutput = typeof slide.output === 'string' && (slide.output.includes('Error') || slide.output.includes('Exception'));
  if (hasError || hasTrapNote || isErrorOutput) {
    return { text: '③ 考場地雷', icon: '💥', class: 'stage-trap', desc: '避開爆零天坑' };
  }
  const quarter = Math.max(2, Math.floor(total * 0.25));
  if (index < quarter) {
    return { text: '① 觀念初探', icon: '💡', class: 'stage-concept', desc: '建立心智模型' };
  }
  return { text: '② 語法鐵律', icon: '⚖️', class: 'stage-syntax', desc: '核心語法規範' };
}

/* ==========================================================================
   8. 翻頁、主動預測揭曉與二擇一互動操作 (agytodo 3.2, 3.3, 5.2)
   ========================================================================== */
function escapeHtml(str) {
  if (typeof str !== 'string') return String(str ?? '');
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderSimplePredictionMask(overlayEl, predictText) {
  let badgeText = '🧠 點擊揭曉預測答案';
  if (typeof predictText === 'string' && predictText.trim() !== '') {
    badgeText = `🧠 預測思考：${predictText}`;
  }
  overlayEl.innerHTML = `
    <div class="prediction-simple-wrap" onclick="revealPrediction(event)">
      <div class="prediction-badge">${escapeHtml(badgeText)}</div>
      <div class="prediction-hint">或按鍵盤 ▶ / 點擊「揭曉答案」解鎖</div>
    </div>
  `;
}

function renderQuizCard(overlayEl, quiz) {
  const opt0 = quiz.options && quiz.options[0];
  const opt1 = quiz.options && quiz.options[1];
  const opt0Text = typeof opt0 === 'object' ? (opt0.text || '') : String(opt0 || '選項 A');
  const opt1Text = typeof opt1 === 'object' ? (opt1.text || '') : String(opt1 || '選項 B');
  const opt0Tag = (typeof opt0 === 'object' && opt0.label) ? opt0.label : 'A';
  const opt1Tag = (typeof opt1 === 'object' && opt1.label) ? opt1.label : 'B';
  const question = quiz.question || '預測思考：執行此處代碼後，終端機將產生何種結果？';

  overlayEl.innerHTML = `
    <div class="prediction-quiz-card" onclick="event.stopPropagation()">
      <div class="quiz-card-header">
        <span class="quiz-card-badge">🧠 APCS 考場秒問秒答（二擇一預測）</span>
        <span class="quiz-card-hint">可按 <kbd>A</kbd> / <kbd>B</kbd> 或點選</span>
      </div>
      <div class="quiz-question">${escapeHtml(question)}</div>
      <div class="quiz-options-grid">
        <button type="button" class="quiz-option-btn" id="quizOpt0" onclick="handleQuizOption(0, event)">
          <span class="quiz-opt-tag">${escapeHtml(opt0Tag)}</span>
          <span class="quiz-opt-text">${escapeHtml(opt0Text)}</span>
          <span class="quiz-opt-status-icon"></span>
        </button>
        <button type="button" class="quiz-option-btn" id="quizOpt1" onclick="handleQuizOption(1, event)">
          <span class="quiz-opt-tag">${escapeHtml(opt1Tag)}</span>
          <span class="quiz-opt-text">${escapeHtml(opt1Text)}</span>
          <span class="quiz-opt-status-icon"></span>
        </button>
      </div>
      <div class="quiz-feedback-box" id="quizFeedbackBox" style="display: none;">
        <div class="quiz-feedback-status" id="quizFeedbackStatus"></div>
        <div class="quiz-feedback-explanation" id="quizFeedbackExp"></div>
        <div class="quiz-feedback-actions">
          <button type="button" class="quiz-action-btn secondary" onclick="dismissPredictionOverlay(event)">
            <span>查看原始輸出 ▾</span>
          </button>
          <button type="button" class="quiz-action-btn primary" onclick="nextSlide()">
            <span>下一頁 ▶</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

function handleQuizOption(choiceIndex, event) {
  if (event) event.stopPropagation();
  if (isQuizAnswered || !currentSlideQuiz) return;
  isQuizAnswered = true;
  isAnswerRevealed = true;

  const btn0 = document.getElementById('quizOpt0');
  const btn1 = document.getElementById('quizOpt1');
  const feedbackBox = document.getElementById('quizFeedbackBox');
  const feedbackStatus = document.getElementById('quizFeedbackStatus');
  const feedbackExp = document.getElementById('quizFeedbackExp');
  const outputViewport = document.getElementById('outputViewport');

  const correctIndex = Number(currentSlideQuiz.correct || 0);
  const isCorrect = (choiceIndex === correctIndex);

  // 解除終端輸出模糊，方便對照
  if (outputViewport) outputViewport.classList.remove('blurred');

  // 更新導航與 Dock 按鈕為「下一頁」
  const btnNext = document.getElementById('btnNext');
  if (btnNext) btnNext.innerHTML = '下一頁 <span class="key-badge">▶</span>';
  const dockNext = document.getElementById('dockBtnNext');
  if (dockNext) dockNext.innerHTML = '<span>下一頁</span><span>▶</span>';

  // 設置選項按鈕動態樣式
  if (choiceIndex === 0) {
    if (isCorrect) {
      if (btn0) {
        btn0.classList.add('quiz-opt-correct');
        const icon = btn0.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✓ 正確';
      }
      if (btn1) btn1.classList.add('quiz-opt-dimmed');
    } else {
      if (btn0) {
        btn0.classList.add('quiz-opt-wrong');
        const icon = btn0.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✗ 踩雷';
      }
      if (btn1) {
        btn1.classList.add('quiz-opt-correct');
        const icon = btn1.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✓ 正解';
      }
    }
  } else {
    if (isCorrect) {
      if (btn1) {
        btn1.classList.add('quiz-opt-correct');
        const icon = btn1.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✓ 正確';
      }
      if (btn0) btn0.classList.add('quiz-opt-dimmed');
    } else {
      if (btn1) {
        btn1.classList.add('quiz-opt-wrong');
        const icon = btn1.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✗ 踩雷';
      }
      if (btn0) {
        btn0.classList.add('quiz-opt-correct');
        const icon = btn0.querySelector('.quiz-opt-status-icon');
        if (icon) icon.innerHTML = '✓ 正解';
      }
    }
  }

  // 鎖定選項避免重複點選
  if (btn0) btn0.setAttribute('disabled', 'true');
  if (btn1) btn1.setAttribute('disabled', 'true');

  // 展開考場解析與反饋
  if (feedbackBox) {
    feedbackBox.style.display = 'block';
    if (feedbackStatus) {
      if (isCorrect) {
        feedbackStatus.className = 'quiz-feedback-status correct';
        feedbackStatus.innerHTML = '🎉 預測命中！觀念完全正確！';
      } else {
        feedbackStatus.className = 'quiz-feedback-status wrong';
        feedbackStatus.innerHTML = '⚠️ 考場常見盲點！踩到陷阱囉！';
      }
    }
    if (feedbackExp) {
      const exp = currentSlideQuiz.explanation || (isCorrect ? '太棒了，邏輯思維非常清晰！' : '請參考上述正解與下方終端機輸出。');
      feedbackExp.innerHTML = `<span class="quiz-exp-label">【考場解析】</span>${escapeHtml(exp)}`;
    }
  }
}

function dismissPredictionOverlay(event) {
  if (event) event.stopPropagation();
  const overlay = document.getElementById('predictionOverlay');
  if (overlay) overlay.style.display = 'none';
  const outViewport = document.getElementById('outputViewport');
  if (outViewport) outViewport.classList.remove('blurred');
  isAnswerRevealed = true;
}

function revealPrediction(event) {
  if (event && event.target && event.target.closest && (event.target.closest('.quiz-option-btn') || event.target.closest('.quiz-action-btn'))) {
    return;
  }

  // 若當前有未作答的二擇一預測卡：第一下自動標示正解並展開解析 (agytodo 3.2, 3.3)
  if (currentSlideQuiz && !isQuizAnswered) {
    isQuizAnswered = true;
    isAnswerRevealed = true;

    const correctIndex = Number(currentSlideQuiz.correct || 0);
    const btn0 = document.getElementById('quizOpt0');
    const btn1 = document.getElementById('quizOpt1');
    const feedbackBox = document.getElementById('quizFeedbackBox');
    const feedbackStatus = document.getElementById('quizFeedbackStatus');
    const feedbackExp = document.getElementById('quizFeedbackExp');
    const outputViewport = document.getElementById('outputViewport');

    if (outputViewport) outputViewport.classList.remove('blurred');

    const correctBtn = correctIndex === 0 ? btn0 : btn1;
    const otherBtn = correctIndex === 0 ? btn1 : btn0;

    if (correctBtn) {
      correctBtn.classList.add('quiz-opt-correct');
      const icon = correctBtn.querySelector('.quiz-opt-status-icon');
      if (icon) icon.innerHTML = '✓ 正解';
    }
    if (otherBtn) otherBtn.classList.add('quiz-opt-dimmed');

    if (btn0) btn0.setAttribute('disabled', 'true');
    if (btn1) btn1.setAttribute('disabled', 'true');

    if (feedbackBox) {
      feedbackBox.style.display = 'block';
      if (feedbackStatus) {
        feedbackStatus.className = 'quiz-feedback-status revealed';
        feedbackStatus.innerHTML = '💡 考場正解與觀念揭曉：';
      }
      if (feedbackExp) {
        const exp = currentSlideQuiz.explanation || '請參考上述正解與下方終端機輸出。';
        feedbackExp.innerHTML = `<span class="quiz-exp-label">【考場解析】</span>${escapeHtml(exp)}`;
      }
    }

    const btnNext = document.getElementById('btnNext');
    if (btnNext) btnNext.innerHTML = '下一頁 <span class="key-badge">▶</span>';
    const dockNext = document.getElementById('dockBtnNext');
    if (dockNext) dockNext.innerHTML = '<span>下一頁</span><span>▶</span>';
    return;
  }

  // 若已作答或為單純遮罩：直接隱藏 overlay 顯示原始終端機輸出
  isAnswerRevealed = true;
  const overlay = document.getElementById('predictionOverlay');
  if (overlay) overlay.style.display = 'none';
  const outViewport = document.getElementById('outputViewport');
  if (outViewport) outViewport.classList.remove('blurred');

  const btnNext = document.getElementById('btnNext');
  if (btnNext) btnNext.innerHTML = '下一頁 <span class="key-badge">▶</span>';
  const dockNext = document.getElementById('dockBtnNext');
  if (dockNext) dockNext.innerHTML = '<span>下一頁</span><span>▶</span>';
}

function prevSlide() {
  if (currentSlide > 0) {
    currentSlide--;
    renderSlide(currentSlide);
  }
}

function nextSlide() {
  // 若當前頁有預測遮罩且尚未揭曉答案：第 1 下平滑揭曉答案 (agytodo 3.2)
  if (!isAnswerRevealed) {
    revealPrediction();
    return;
  }

  // 第 2 下或無遮罩時：正常切換至下一頁
  if (currentSlide < activeSlidesData.length - 1) {
    currentSlide++;
    renderSlide(currentSlide);
  }
}

function goToSlide(targetIndex) {
  if (targetIndex >= 0 && targetIndex < activeSlidesData.length) {
    currentSlide = targetIndex;
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
  // 初始化 SVG 跨卡片導引線畫布 (agytodo 6.1)
  ensureFlowGuideSvg();

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

  // 點擊空白處解除程式碼行釘選鎖定 (agytodo 6.1, 6.2)
  window.addEventListener('click', (e) => {
    if (pinnedLineNum !== null) {
      if (!e.target.closest('.code-line') && !e.target.closest('.output-line') && !e.target.closest('.note-item')) {
        pinnedLineNum = null;
        clearHighlightedLines();
        clearDataFlowSync();
        resetLineBar();
      }
    }
  });

  // 視窗尺寸改變時重置或重算導引線座標
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 1024) {
      clearFlowGuide();
    } else if (pinnedLineNum !== null) {
      updateActiveFlowGuide();
    }
  });

  // 程式碼視窗滾動時連動重算導引線
  const codeVp = document.getElementById('codeViewport');
  if (codeVp) {
    codeVp.addEventListener('scroll', () => {
      if (pinnedLineNum !== null && window.innerWidth > 1024) {
        updateActiveFlowGuide();
      }
    }, { passive: true });
  }

  // 鍵盤切換支援
  window.addEventListener('keydown', (e) => {
    const secSelect = document.getElementById('sectionSelect');
    if (secSelect && secSelect.value !== currentSectionId) return;

    // 二擇一預測卡快捷鍵 (A / B 或 1 / 2) - agytodo 3.3
    if (currentSlideQuiz && !isQuizAnswered) {
      if (e.key === 'a' || e.key === 'A' || e.key === '1') {
        handleQuizOption(0, e);
        return;
      }
      if (e.key === 'b' || e.key === 'B' || e.key === '2') {
        handleQuizOption(1, e);
        return;
      }
    }

    if (e.key === 'Escape') {
      if (pinnedLineNum !== null) {
        pinnedLineNum = null;
        clearHighlightedLines();
        clearDataFlowSync();
        resetLineBar();
      }
    } else if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
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

