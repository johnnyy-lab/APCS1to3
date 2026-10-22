# ==============================================================================
# 🧪 《PythAPCS123》單元 6-8：EOF 與串流輸入模式 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_8.py
# 版權宣告：PythAPCS123 教材團隊版權所有
# ==============================================================================
#
# 🕵️‍♂️【給順藤摸瓜找到這裡的程式冒險者 —— 一封來自教材團隊的良心提醒信】
#
# 嗨！聰明的同學：
# 如果你有本事一路順著 Colab 的程式碼追查到 GitHub，並打開了這份評分腳本，
# 我們要真誠地為你喝采！這代表你具備敏銳的觀察力、駭客的探究精神，以及優異的程式直覺。
# 這種「打破砂鍋問到底、想搞懂系統底層怎麼運作」的好奇心，正是優秀工程師最珍貴的特質。
#
# 不過，請你暫時停下滾輪，聽老師一句良心建議：
# 既然你已經具備順利找到這裡的實力（這資質說不定早就有 APCS 實作 3 級分以上的水準了！😄），
# 直接看這份評分代碼裡的答案，對你的邏輯思維與未來的考場實戰毫無幫助——
# 因為在正式的 APCS 考場與真實世界的開發中，可沒有評分原始碼能讓你看喔！
#
# 程式設計最迷人的地方，在於親自思考、撞牆、除錯，直到測資全綠的那份無可取代的成就感。
#
# 何不現在就帥氣地關掉這個視窗，回到 Colab 筆記本，靠自己的雙手把每一題寫出來？
# 真正的程式大師，靠實力讓系統亮起綠燈！期待在未來的 APCS 考場與競賽舞台看見你的精彩表現！🚀
# ==============================================================================

import sys
import os
import json
import urllib.request
import urllib.parse
import unicodedata
from datetime import datetime, timezone, timedelta
import logging

# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_6-8_eof_and_input_streaming_patterns.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max。
    直接執行腳本時答案與評分器在同一個全域，呼叫內建會被遮蔽。"""
    total = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total


def _pad(text, width):
    """以顯示寬度為基準補齊空白，讓全形題名在終端也能對齊。"""
    gap = width - _disp_width(text)
    if gap > 0:
        return text + " " * gap
    return text


def _student_value(env, names):
    """各題學生實際值，截斷到 80 字元，方便分辨 7 與 7.0。"""
    parts = []
    for name in names:
        if name in env:
            parts.append(f"{name}={env.get(name)!r}")
        else:
            parts.append(f"{name}=缺")
    return ", ".join(parts)[:80]

def _student_env(env=None):
    """學員變數所在的命名空間。

    Cell B 隔離載入時讀 __STUDENT_ENV__。直接執行腳本，或測試把答案
    放在同一個全域時，改讀 globals()。"""
    if isinstance(env, dict):
        return env
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        return snapshot
    return globals()


def fetch_google_account_info(env=None):
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = _student_env(env)
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name


def auto_grade_unit_6_8(env=None):
    env = _student_env(env)
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info(env)

    # 3. 整合身分識別欄位（區分 Colab 雲端認證與本機免登入自評）
    is_colab = False
    try:
        import google.colab
        is_colab = True
    except ImportError:
        is_colab = False

    if google_email:
        final_email = google_email
        final_google_name = google_name if google_name else declared_name
        combined_display_name = f"{declared_name} (Google: {final_google_name})"
    elif not is_colab:
        final_email = "本機"
        final_google_name = "本機"
        combined_display_name = f"{declared_name} (本機)"
    else:
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未綁定 Google"
        final_google_name = "訪客"
        combined_display_name = declared_name

    tw_tz = timezone(timedelta(hours=8))
    timestamp_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 6-8-1 預知次數的輸入走訪 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-1", "填空題", "讀取首行 T 並走訪 T 次 (T, total_processed)", 4, ("total_processed",),
         lambda g: (
             (True, "預知筆數 T 與 for 迴圈結構填寫正確！")
             if (g.get("total_processed") == 3 or
                 (("range(T)" in history_clean or "range(int(simulated_first_line))" in history_clean) and
                  ("total_processed" in g or "total_processed" in history_str)))
             else (False, "請在 6-8-1 填空題空格填入 T 與正確的 range 走訪次數！")
         )),

        ("6-8-1", "練習題", "固定 N 筆加總與筆數統計 (total_sum = 100, count = 4)", 4, ("total_sum", "count"),
         lambda g: (
             (True, "固定 N 筆輸入與累加統計輸出正確！")
             if (g.get("total_sum") == 100 and g.get("count") in (2, 3, 4)) or
                (("total_sum" in g or "total_sum" in history_str) and
                 ("assert count == 4 and total_sum == 100" in history_str or
                  "assertcount==4andtotal_sum==100" in history_clean))
             else (False, "請撰寫 for 迴圈讀取 N 筆數值，計算 total_sum 與筆數 count！")
         )),

        ("6-8-1", "挑戰題", "櫃檯提款哨兵值 0 終止 (customer_count = 3, total_withdraw = 400)", 5, ("customer_count", "total_withdraw"),
         lambda g: (
             (True, "提款哨兵終止邏輯與金額結算完全正確！")
             if (g.get("customer_count") == 3 and g.get("total_withdraw") == 400) or
                (("customer_count" in g or "customer_count" in history_str) and
                 ("assert customer_count == 3 and total_withdraw == 400" in history_str or
                  "assertcustomer_count==3andtotal_withdraw==400" in history_clean))
             else (False, "請使用 while True 搭配哨兵值 0 判定退出，統計人數與總提款額！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-2 預知筆數標準走訪與底線慣例 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-2", "填空題", "底線 _ 慣例走訪 N 次 (for _ in range(N))", 4, (),
         lambda g: (
             (True, "底線 _ 慣用法與 range(N) 填寫正確！")
             if "for_inrange(N)" in history_clean or "for _ in range(N)" in history_str or "for _ in range(" in history_str
             else (False, "請在 6-8-2 填空題使用底線 _ 與 range(N) 走訪 N 輪！")
         )),

        ("6-8-2", "練習題", "N 筆成績統計及格人數與最高分 (pass_count = 2, max_score = 80)", 4, ("pass_count", "max_score"),
         lambda g: (
             (True, "N 筆成績及格計數與極值更新邏輯正確！")
             if (g.get("pass_count") == 2 and g.get("max_score") == 80) or
                (("pass_count" in g or "pass_count" in history_str) and
                 ("assert pass_count == 2 and max_score == 80" in history_str or
                  "assertpass_count==2andmax_score==80" in history_clean))
             else (False, "請撰寫 for 迴圈走訪 N 筆成績，統計 pass_count 與 max_score！")
         )),

        ("6-8-2", "挑戰題", "雙層巢狀多測資框架加總 (grand_total = 66)", 5, ("grand_total",),
         lambda g: (
             (True, "多組測資雙層 for 迴圈累加總和正確！")
             if g.get("grand_total") == 66 or
                (("grand_total" in g or "grand_total" in history_str) and
                 ("assert grand_total == 66" in history_str or "assertgrand_total==66" in history_clean))
             else (False, "請撰寫雙層 for 迴圈（外層 T、內層 N），計算全組別總和 grand_total！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-3 特殊哨兵值終止模式 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-3", "填空題", "while True 與哨兵 -1 煞車 (while True / break)", 4, (),
         lambda g: (
             (True, "while True 永動迴圈與哨兵 -1 煞車語法填寫正確！")
             if ("while True" in history_str or "whileTrue" in history_clean) and
                ("chk_num == -1" in history_str or "chk_num==-1" in history_clean or "val == -1" in history_str or "val==-1" in history_clean) and
                "break" in history_str
             else (False, "請在 6-8-3 填空題補齊 while True 與 chk_num == -1: break！")
         )),

        ("6-8-3", "練習題", "哨兵 0 終止體重累加與平均 (count = 3, avg_weight = 70)", 4, ("avg_weight", "total_weight", "count"),
         lambda g: (
             (True, "哨兵終止體重統計與平均值計算正確！")
             if (g.get("avg_weight") == 70 or g.get("total_weight") == 210 or
                 (g.get("count") == 3 and "weight" in history_clean) or
                 (("avg_weight" in g or "avg_weight" in history_str) and
                  ("assert count == 3 and avg_weight == 70" in history_str or
                   "assertcount==3andavg_weight==70" in history_clean)))
             else (False, "請使用 while 迴圈在遇到 0 時中斷，計算人數 count 與平均體重 avg_weight！")
         )),

        ("6-8-3", "挑戰題", "雙哨兵 (0, 0) 曼哈頓距離加總 (valid_points = 3, total_manhattan = 21)", 5, ("total_manhattan", "valid_points"),
         lambda g: (
             (True, "雙哨兵 (0, 0) 複合條件中斷與曼哈頓距離累加正確！")
             if (g.get("total_manhattan") == 21 or
                 (g.get("valid_points") == 3 and "manhattan" in history_clean) or
                 (("total_manhattan" in g or "total_manhattan" in history_str) and
                  ("assert valid_points == 3 and total_manhattan == 21" in history_str or
                   "assertvalid_points==3andtotal_manhattan==21" in history_clean)))
             else (False, "請檢查 x == 0 and y == 0 結束標記，並計算有效點曼哈頓距離總和！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-4 什麼是 EOF (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-4", "填空題", "Windows 與 Linux/Mac EOF 快捷鍵認知", 4, ("win_eof_key", "unix_eof_key"),
         lambda g: (
             (True, "EOF 系統快捷鍵觀念理解正確（Ctrl+Z / Ctrl+D）！")
             if ("z" in str(g.get("win_eof_key", "")).lower() and
                 "d" in str(g.get("unix_eof_key", "")).lower()) or
                ("win_eof_key" in history_clean and "unix_eof_key" in history_clean and
                 ("ctrl+z" in history_clean.lower() or "ctrl-z" in history_clean.lower()))
             else (False, "請填入 Windows (Ctrl+Z) 與 Unix (Ctrl+D) 的 EOF 模擬快捷鍵！")
         )),

        ("6-8-4", "練習題", "模擬 None 串流末端字串長度加總 (total_chars = 14)", 4, ("total_chars",),
         lambda g: (
             (True, "None 結尾偵測與字串長度累加正確！")
             if g.get("total_chars") == 14 or
                (("total_chars" in g or "total_chars" in history_str) and
                 ("assert total_chars == 14" in history_str or "asserttotal_chars==14" in history_clean))
             else (False, "請使用 while True 讀取字串，偵測到 None 時 break 並統計 total_chars！")
         )),

        ("6-8-4", "挑戰題", "逐行整數讀取至 EOF 總和與行數 (total_lines = 4, grand_sum = 120)", 5, ("grand_sum", "total_lines"),
         lambda g: (
             (True, "EOF 逐行整數統計行數與總和輸出完全正確！")
             if (g.get("grand_sum") == 120 or g.get("total_lines") == 4) or
                (("grand_sum" in g or "grand_sum" in history_str) and
                 ("assert total_lines == 4 and grand_sum == 120" in history_str or
                  "asserttotal_lines==4andgrand_sum==120" in history_clean))
             else (False, "請在讀取到 None 前累加整數至 grand_sum，並計算 total_lines！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-5 sys.stdin 自然走訪 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-5", "填空題", "sys.stdin 自然走訪語法 (for line in sys.stdin:)", 4, (),
         lambda g: (
             (True, "for line in sys.stdin 自然走訪語法填寫正確！")
             if "forlineinsys.stdin" in history_clean or "for line in sys.stdin" in history_str
             else (False, "請在 6-8-5 填空題填入走訪 sys.stdin 的 for 迴圈關鍵字！")
         )),

        ("6-8-5", "練習題", "自然迭代偶數平方和 (count = 2, even_sq_sum = 52)", 4, ("even_sq_sum", "count"),
         lambda g: (
             (True, "串流迭代偶數篩選與平方和統計輸出正確！")
             if g.get("even_sq_sum") == 52 or
                (g.get("count") == 2 and "even_sq_sum" in history_clean) or
                (("even_sq_sum" in g or "even_sq_sum" in history_str) and
                 ("assert count == 2 and even_sq_sum == 52" in history_str or
                  "assertcount==2andeven_sq_sum==52" in history_clean))
             else (False, "請走訪數列，篩選偶數累加平方和 even_sq_sum 與個數 count！")
         )),

        ("6-8-5", "挑戰題", "單行多值解包求矩形最大面積 (max_area = 16)", 4, ("max_area",),
         lambda g: (
             (True, "單行多值解包與極值面積比對完全正確！")
             if g.get("max_area") == 16 or
                (("max_area" in g or "max_area" in history_str) and
                 ("assert max_area == 16" in history_str or "assertmax_area==16" in history_clean))
             else (False, "請走訪每行字串，使用 map(int, line.split()) 解包並更新 max_area！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-6 while True + try-except EOFError (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-6", "填空題", "try-except 攔截 EOFError 骨架 (try: / except EOFError:)", 4, (),
         lambda g: (
             (True, "try-except EOFError 例外攔截語法填寫正確！")
             if ("try:" in history_str or "try" in history_str) and
                ("except EOFError" in history_str or "exceptEOFError" in history_clean)
             else (False, "請在 6-8-6 填空題補齊 try 與 except EOFError 關鍵字！")
         )),

        ("6-8-6", "練習題", "try-except 平方和連續累加 (sum_squares = 93)", 4, ("sum_squares",),
         lambda g: (
             (True, "例外攔截串流平方和計算正確！")
             if g.get("sum_squares") == 93 or
                (("sum_squares" in g or "sum_squares" in history_str) and
                 ("assert sum_squares == 93" in history_str or "assertsum_squares==93" in history_clean))
             else (False, "請使用 try-except 攔截 EOFError 並計算平方和 sum_squares！")
         )),

        ("6-8-6", "挑戰題", "EOF 氣溫極值更新與全距 (max_t = 31, min_t = 18, range_t = 13)", 4, ("max_t", "min_t", "range_t"),
         lambda g: (
             (True, "串流氣溫極值即時更新與全距計算正確！")
             if (g.get("max_t") == 31 and g.get("min_t") == 18 and g.get("range_t") == 13) or
                (("range_t" in g or "range_t" in history_str) and
                 ("assert max_t == 31 and min_t == 18 and range_t == 13" in history_str or
                  "assertmax_t==31andmin_t==18andrange_t==13" in history_clean))
             else (False, "請使用 try-except 在退出時計算 range_t = max_t - min_t！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-7 空間複雜度 O(1) 串流即時縮減心法 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-7", "填空題", "串流即時維護最小值 (min_val = 7)", 4, ("min_val",),
         lambda g: (
             (True, "最小值初值與即時比對更新填寫正確！")
             if g.get("min_val") == 7 or
                ("min_val" in history_clean and ("item_val < min_val" in history_str or "item_val<min_val" in history_clean or "data < min_val" in history_str or "data<min_val" in history_clean))
             else (False, "請在 6-8-7 填空題完成 min_val 初值與條件更新！")
         )),

        ("6-8-7", "練習題", "氣溫串流統計與全距 (count_t = 5, sum_t = 110, temp_range = 15)", 4, ("count_t", "sum_t", "temp_range"),
         lambda g: (
             (True, "空間 O(1) 氣溫串流統計與全距輸出正確！")
             if (g.get("count_t") == 5 and g.get("sum_t") == 110 and g.get("temp_range") == 15) or
                (("temp_range" in g or "temp_range" in history_str) and
                 ("assert count_t == 5 and sum_t == 110 and temp_range == 15" in history_str or
                  "assertcount_t==5andsum_t==110andtemp_range==15" in history_clean))
             else (False, "請以純純量維護總和、筆數、極值，並計算 temp_range！")
         )),

        ("6-8-7", "挑戰題", "串流及格率統計 (total_players = 6, pass_players = 4, pass_rate = 66)", 4, ("total_players", "pass_players", "pass_rate"),
         lambda g: (
             (True, "串流及格率整數百分比運算正確！")
             if (g.get("total_players") == 6 and g.get("pass_players") == 4 and g.get("pass_rate") == 66) or
                (("pass_rate" in g or "pass_rate" in history_str) and
                 ("assert total_players == 6 and pass_players == 4 and pass_rate == 66" in history_str or
                  "asserttotal_players==6andpass_players==4andpass_rate==66" in history_clean))
             else (False, "請統計 total_players 與 pass_players，計算 pass_rate = pass_players * 100 // total_players！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-8 單行多值拆解與 APCS 實戰總結 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-8", "填空題", "單行多值整數映射語法 (map(int, line_str.split()))", 4, ("total",),
         lambda g: (
             (True, "map 與 split 單行解包語法填寫正確！")
             if g.get("total") == 60 or
                ("map(int,line_str.split())" in history_clean or "map(int, line_str.split())" in history_str or "split()" in history_clean)
             else (False, "請在 6-8-8 填空題填入 map(int, line_str.split())！")
         )),

        ("6-8-8", "練習題", "連續兩行向量內積計算 (dot = 26)", 4, ("dot",),
         lambda g: (
             (True, "兩行向量解析與內積計算輸出正確！")
             if g.get("dot") == 26 or
                (("dot" in g or "dot" in history_str) and
                 ("assert dot == 26" in history_str or "assertdot==26" in history_clean))
             else (False, "請分別解包兩行座標，計算向量內積 dot = x1*x2 + y1*y2！")
         )),

        ("6-8-8", "挑戰題", "APCS 多組門檻過濾累加 (total_qualified = 4, all_groups_sum = 305)", 4, ("total_qualified", "all_groups_sum"),
         lambda g: (
             (True, "雙組測資合格門檻加總與計數完全正確！")
             if (g.get("total_qualified") == 4 and g.get("all_groups_sum") == 305) or
                (("all_groups_sum" in g or "all_groups_sum" in history_str) and
                 ("assert total_qualified == 4 and all_groups_sum == 305" in history_str or
                  "asserttotal_qualified==4andall_groups_sum==305" in history_clean))
             else (False, "請走訪雙組測資，統計高於門檻數字個數 total_qualified 與數值總和 all_groups_sum！")
         ))
    ]

    pass_count = 0
    item_results = []
    item_outputs = []

    for uid, qtype, name, pts, watch, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception:
            ok, msg = False, "執行檢驗時發生異常，請確認程式碼是否可正常執行"

        item_score = pts if ok else 0
        total_score += item_score
        if ok:
            pass_count += 1
            icon = "✅"
            status = f"通過 (+{pts}分)"
        else:
            icon = "❌"
            status = f"未通過 (0/{pts}分)"

        out_lines = [f"{icon} [{uid} {qtype}] {_pad(name, 44)} ➔ {status}"]
        if not ok:
            out_lines.append(f"   💡 提示：{msg}")
        item_outputs.append(out_lines)

        item_results.append({
            "uid": uid,
            "type": qtype,
            "name": name,
            "passed": ok,
            "score": item_score,
            "max_score": pts,
            "message": msg,
            "student_value": _student_value(env, watch)
        })

    if total_score >= 90:
        badge = '🏆【全章大滿貫榮譽徽章】串流與輸入處理大師！APCS 實作題破關神手！'
    elif total_score >= 80:
        badge = '🥇【優秀晉級徽章】對 EOF 與串流輸入已有相當敏銳的掌握度！'
    elif total_score >= 60:
        badge = '🥈【及格認證徽章】掌握基本輸入模式，多加練習即可更加熟練！'
    else:
        badge = '💡【尚在探索徽章】別氣餒！仔細觀察迴圈終止條件與 map 解包語法，再次挑戰吧！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-8：EOF 與串流輸入模式 —— 自動評分報告")
    print("=" * 72)
    print(f" 📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f" 🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)
    print(f" 👤 學員姓名：{declared_name}")
    print(f" 🆔 學號座號：{declared_id}")
    if google_email:
        print(f" 🔑 Google 帳號認證：{google_email}（暱稱：{final_google_name}）")
    elif not is_colab:
        print(f" 💻 執行環境：本機環境（免登入自評）")
    else:
        print(f" 📧 登記信箱：{final_email}")
    print(f" ⏰ 送交時間：{timestamp_str}")
    print("=" * 72)
    print(" 📝 題目作答細項檢驗：")
    for lines in item_outputs:
        for line in lines:
            print(line)
    print("=" * 72)

    # 試算表姓名、學號用學生輸入原值。暱稱與 email 在本機填「本機測試」。
    if google_email:
        sheet_google_name = google_name if google_name else declared_name
        sheet_google_email = google_email
    elif not is_colab:
        sheet_google_name = "本機測試"
        sheet_google_email = "本機測試"
    else:
        sheet_google_name = "未認證"
        sheet_google_email = "未認證"

    score_fingerprint = ",".join(
        f"{item['uid']}:{item['type']}:{'1' if item['passed'] else '0'}"
        for item in item_results
    )

    # --------------------------------------------------------------------------
    # 📡 雲端後台成績記錄（Google Apps Script 試算表 Webhook）
    # 欄位拆開送出。相同成績是否寫入由 Apps Script 判斷，這裡只讀回應。
    # 鐵律：絕不產生任何本地日誌暫存檔。
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "6-8",
        "unit_title": "EOF 與串流輸入模式",
        "declared_name": declared_name,
        "declared_id": declared_id,
        "google_name": sheet_google_name,
        "google_email": sheet_google_email,
        "student_name": declared_name,
        "student_id": declared_id,
        "name": declared_name,
        "id": declared_id,
        "student_email": sheet_google_email,
        "email": sheet_google_email,
        "timestamp": timestamp_str,
        "total_score": total_score,
        "max_score": max_score,
        "pass_count": pass_count,
        "total_count": len(test_cases),
        "badge": badge,
        "details": item_results,
        "grader_version": GRADER_VERSION,
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_6_8.py",
        "notebook_file": NOTEBOOK_FILE,
        "score_fingerprint": score_fingerprint
    }

    if LOG_WEBHOOK_URL:
        try:
            req_data = json.dumps(log_data, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_body = response.read().decode("utf-8", errors="replace").strip()
            status = ""
            if raw_body:
                try:
                    payload = json.loads(raw_body)
                    if isinstance(payload, dict):
                        status = str(payload.get("status", "")).strip().lower()
                except json.JSONDecodeError:
                    status = ""
            if status == "duplicate":
                print("📡 [雲端回報] 成績與上次相同，未重複登錄（本機成績仍有效）。\n")
            else:
                print("📡 [雲端回報] 成績已成功上傳並登錄至授課試算表！\n")
        except Exception:
            # 離線測試或連線逾時溫和提示，絕不噴出紅色例外
            if not is_colab:
                print("📡 [本機模式] 成績已於本機評分完成（雲端試算表未連線）。\n")
            else:
                print("📡 [離線模式] 暫時無法連線至雲端試算表，但本機評分已完成。\n")

    if total_score < 100:
        print("\n💡 小技巧：若有題目顯示 ❌ 未通過，請回到上方對應題目的儲存格修改程式碼，")
        print("   並務必重新點擊該題的『▶ 播放鍵』執行，再回來執行此評分儲存格就可以刷新成績與紀錄囉！")
        print("=" * 72)


# 執行評分
auto_grade_unit_6_8()
