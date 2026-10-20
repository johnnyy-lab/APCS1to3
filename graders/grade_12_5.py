# ==============================================================================
# 🧪 《PythAPCS123》單元 12-5：APCS 排序實戰應用：區間線段排序、貪婪前導與已排序雙指標 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_5.py
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
NOTEBOOK_FILE = "PythAPCS123_12-5_apcs_sorting_patterns_intervals_and_pointers.ipynb"

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

def check_q1(g, hist):
    raw_scores = [75, 90, 62, 88, 79]
    ss = g.get("sorted_scores")
    med = g.get("median")
    if ss is None and med is None:
        return False, "請確認 sorted_scores = sorted(raw_scores) 並以 mid_idx 取出中位數。"
    if (ss == sorted(raw_scores) and med == 79) or ("sorted(" in hist and "mid_idx" in hist):
        return True, "太棒了！先排序再取中間索引，極速精確找出數列中位數！"
    return False, "請確認 sorted_scores = sorted(raw_scores) 並以 mid_idx 取出中位數。"

def check_q2(g, hist):
    # 連續整數判定
    is_consecutive = g.get("is_consecutive")
    if is_consecutive is None:
        return False, "請排序後比對相鄰元素的差值是否皆等於 1。"
    if is_consecutive is not None or "data[i + 1] - data[i]" in hist or "data[i+1]-data[i]" in hist:
        return True, "完全正確！透過相鄰元素差值是否恆為 1，漂亮完成連續整數檢驗！"
    return False, "請排序後比對相鄰元素的差值是否皆等於 1。"

def check_q3(g, hist):
    dup = g.get("duplicates")
    if dup is None:
        return False, "請排序 levels 後，相鄰比對重複項目收集至 duplicates。"
    # levels = [15, 42, 8, 23, 99, 15, 60, 42] -> 排序後 [8, 15, 15, 23, 42, 42, 60, 99] -> dup: [15, 42]
    if dup == [15, 42] or (isinstance(dup, list) and set(dup) == {15, 42}) or ("levels[i] == levels[i + 1]" in hist):
        return True, "太強了！排序後透過一次線性走訪 O(N) 完美過濾並提取重複等級！"
    return False, "請排序 levels 後，相鄰比對重複項目收集至 duplicates。"

def check_q4(g, hist):
    # is_overlap 與 merged_seg
    is_overlap = g.get("is_overlap")
    merged_seg = g.get("merged_seg")
    if is_overlap is None and merged_seg is None:
        return False, "請確認填入 segA[1] 判定重疊，以及 segB[1] 計算合併後終點。"
    if (is_overlap is True and merged_seg == [2, 9]) or ("segA[1]" in hist and "segB[1]" in hist):
        return True, "完全正確！精準判斷起點是否小於等於終點，並以 max() 完成線段合併！"
    return False, "請確認填入 segA[1] 判定重疊，以及 segB[1] 計算合併後終點。"

def check_q5(g, hist):
    has_conflict = g.get("has_conflict")
    if has_conflict is None:
        return False, "請將 intervals 依起點排序，並比對相鄰區間是否重疊衝突。"
    if has_conflict is not None or "intervals.sort" in hist:
        if "intervals[i + 1][0] < intervals[i][1]" in hist or "intervals[i+1][0]<intervals[i][1]" in hist:
            return True, "精彩！將排程依起點排序後，以相鄰結束時間判定重疊衝突完全無誤！"
    return False, "請將 intervals 依起點排序，並比對相鄰區間是否重疊衝突。"

def check_q6(g, hist):
    th = g.get("total_hours")
    if th is None:
        return False, "請將預約時段依起點排序後，以維護當前區間法計算不重疊總時長（9小時）。"
    # bookings = [[13, 15], [9, 11], [14, 17], [10, 12], [18, 20]]
    # 排序後: [9, 11], [10, 12] -> 合併為 [9, 12] (3 hr)
    # [13, 15], [14, 17] -> 合併為 [13, 17] (4 hr)
    # [18, 20] -> [18, 20] (2 hr)
    # 總長度 = 3 + 4 + 2 = 9 hr
    if th == 9 or ("cur_end = max(cur_end, e)" in hist and "total_hours" in hist):
        return True, "太厲害了！精準實現經典線段覆蓋合併演算法，算出正確佔用 9 小時！"
    return False, "請將預約時段依起點排序後，以維護當前區間法計算不重疊總時長（9小時）。"

def check_q7(g, hist):
    count = g.get("count")
    if count is None:
        return False, "請將演講依結束時間 x[1] 排序，並檢查 start >= last_end。"
    # lectures = [[1, 3], [2, 5], [4, 7], [1, 8], [6, 9]]
    # 結束時間排序: [1, 3], [2, 5], [4, 7], [1, 8], [6, 9]
    # 貪婪挑選: [1, 3] (end=3) -> [4, 7] (end=7) -> count = 2
    if count == 2 or ("key=lambda x: x[1]" in hist and "start >= last_end" in hist):
        return True, "太棒了！掌握活動安排貪婪本質，依結束時間排序挑選最多場次！"
    return False, "請將演講依結束時間 x[1] 排序，並檢查 start >= last_end。"

def check_q8(g, hist):
    chosen = g.get("chosen")
    if chosen is None:
        return False, "請將 requests 依結束時間排序並貪婪選取不衝突團體。"
    # requests = [("樂團A", 10, 12), ("舞團B", 11, 13), ("劇團C", 12, 14), ("魔術D", 14, 15)]
    # 入選: ['樂團A', '劇團C', '魔術D']
    if chosen == ["樂團A", "劇團C", "魔術D"] or ("requests.sort" in hist and "chosen" in hist):
        return True, "完全正確！順利依結束時間排程，貪婪篩選出最佳表演團體組合！"
    return False, "請將 requests 依結束時間排序並貪婪選取不衝突團體。"

def check_q9(g, hist):
    td = g.get("total_duration")
    chosen_shows = g.get("chosen_shows")
    if td is None and chosen_shows is None:
        return False, "請貪婪挑選不重疊動畫並統計其總播映時數。"
    # shows = [("動畫甲", 8, 11), ("動畫乙", 10, 12), ("動畫丙", 11, 14), ("動畫丁", 13, 15), ("動畫戊", 14, 17), ("動畫己", 16, 18)]
    # 依結束時間排序: 甲(11), 乙(12), 丙(14), 丁(15), 戊(17), 己(18)
    # 挑選: 甲[8,11] (3hr, end=11) -> 丙[11,14] (3hr, end=14) -> 戊[14,17] (3hr, end=17)
    # 總時數 = 3 + 3 + 3 = 9 小時
    if td == 9 or (isinstance(chosen_shows, list) and len(chosen_shows) == 3):
        return True, "太強大了！精準挑選最多部動畫並計算出總播映 9 小時！"
    if "total_duration" in hist and "shows.sort" in hist:
        return True, "排程邏輯正確，通過！"
    return False, "請貪婪挑選不重疊動畫並統計其總播映時數。"

def check_q10(g, hist):
    max_gap = g.get("max_gap")
    if max_gap is None:
        return False, "請確認填入 milestones.sort() 與 range(len - 1) 尋找最大落差。"
    # milestones = [10, 45, 15, 80, 20] -> 排序後 [10, 15, 20, 45, 80]
    # 相鄰差: 5, 5, 25, 35 -> 最大落差 35
    if max_gap == 35 or ("milestones.sort()" in hist and "range(len(milestones) - 1)" in hist):
        return True, "正確無誤！排序後以 range(len - 1) 走訪相鄰元素，極速找出最大跳躍 35！"
    return False, "請確認填入 milestones.sort() 與 range(len - 1) 尋找最大落差。"

def check_q11(g, hist):
    min_d = g.get("min_d")
    if min_d is None:
        return False, "請將 nums 排序後，透過相鄰差值找出全數列最小差值。"
    # nums = [30, 5, 12, 45, 16] -> 排序 [5, 12, 16, 30, 45] -> 相鄰差 [7, 4, 14, 15] -> min=4
    if min_d == 4 or ("nums.sort()" in hist and "min_d" in hist):
        return True, "精彩！O(N log N) 排序後線性相鄰掃描，取代 O(N^2) 暴力比對！"
    return False, "請將 nums 排序後，透過相鄰差值找出全數列最小差值。"

def check_q12(g, hist):
    bp = g.get("best_pair")
    min_gap = g.get("min_gap")
    if bp is None and min_gap is None:
        return False, "請對完賽秒數排序後，找出差距最小的兩位選手秒數。"
    # times = [85.2, 79.8, 92.1, 80.5, 74.0, 85.0] -> 排序: [74.0, 79.8, 80.5, 85.0, 85.2, 92.1]
    # 相鄰差: 5.8, 0.7, 4.5, 0.2, 6.9 -> min=0.2 (85.0 vs 85.2)
    if (min_gap is not None and abs(min_gap - 0.2) < 1e-4) or (bp == (85.0, 85.2)):
        return True, "太精采了！秒數排序後精準鎖定 85.0 秒與 85.2 秒的激戰雙雄（差距 0.2 秒）！"
    if "times.sort()" in hist and "min_gap" in hist:
        return True, "相鄰比對邏輯正確，通過！"
    return False, "請對完賽秒數排序後，找出差距最小的兩位選手秒數。"

def check_q13(g, hist):
    if g.get('sorted_arr') is None:
        return False, "請確認在條件判斷中填入 left += 1 與 right -= 1。"
    # left += 1, right -= 1
    if "left += 1" in hist and "right -= 1" in hist:
        return True, "完全正確！精準填入雙指標相向逼近核心位移：left += 1 與 right -= 1！"
    return False, "請確認在條件判斷中填入 left += 1 與 right -= 1。"

def check_q14(g, hist):
    found = g.get("found")
    if found is None:
        return False, "請使用排序與雙指標夾擊法找出相加等於 target 的兩數。"
    # values = [40, 10, 25, 5, 15], target = 35 -> (10, 25)
    if found == (10, 25) or found == [10, 25] or ("l < r" in hist and "s == target" in hist):
        return True, "太棒了！以 O(N) 雙指標夾擊法極速解出經典 Two Sum (10, 25)！"
    return False, "請使用排序與雙指標夾擊法找出相加等於 target 的兩數。"

def check_q15(g, hist):
    ml = g.get("max_load")
    bc = g.get("best_combo")
    if ml is None and bc is None:
        return False, "請利用雙指標夾擊法逼近不大於 100 kg 的最重裝載組合。"
    # weights = [25, 35, 80, 15, 65, 45, 90] -> 排序: [15, 25, 35, 45, 65, 80, 90]
    # 不超過 100 之最大總重: 35 + 65 = 100 kg！ (或 15+80=95, 25+65=90, 15+80=95)
    # 這裡 35 + 65 = 100 剛好滿載！
    if ml == 100 or (bc and sum(bc) == 100):
        return True, "滿分表現！雙指標逼近完美找出最佳組合 (35, 65)，剛好滿載 100 kg！"
    if "max_load" in hist and "weights.sort()" in hist:
        return True, "雙指標逼近邏輯正確，通過！"
    return False, "請利用雙指標夾擊法逼近不大於 100 kg 的最重裝載組合。"

def check_q16(g, hist):
    ranked = g.get("ranked")
    if ranked is None:
        return False, "請使用 enumerate(scores) 打包並以 reverse=True 降序排序。"
    # scores = [65, 92, 78, 88]
    # packaged = [(s, idx) for idx, s in enumerate(scores)]
    # ranked: 降序 -> [(92, 1), (88, 3), (78, 2), (65, 0)]
    expected = [(92, 1), (88, 3), (78, 2), (65, 0)]
    if ranked == expected or ("enumerate(scores)" in hist and "reverse=True" in hist):
        return True, "太棒了！成功運用 enumerate 打包原始學號並由高到低降序排列！"
    return False, "請使用 enumerate(scores) 打包並以 reverse=True 降序排序。"

def check_q17(g, hist):
    packed = g.get("packed")
    if packed is None:
        return False, "請打包 (數值, 原始索引) 並排序，輸出最小與最大之原始索引。"
    # measurements = [45, 12, 89, 34, 67] -> packed 排序後最小 (12, 1), 最大 (89, 2)
    if (packed and packed[0] == (12, 1) and packed[-1] == (89, 2)) or ("enumerate(measurements)" in hist):
        return True, "精彩！保留原始位置進行排序，成功精確定位最大值與最小值的原始索引！"
    return False, "請打包 (數值, 原始索引) 並排序，輸出最小與最大之原始索引。"

def check_q18(g, hist):
    order = g.get("order")
    if order is None:
        return False, "請依 (-分數, 原始編號) 排序並輸出錄取編號清單 [2, 1, 4, 0, 3]。"
    # scores = [72, 85, 90, 68, 85] (idx: 0, 1, 2, 3, 4)
    # 分數降序, 編號升序: 90(2), 85(1), 85(4), 72(0), 68(3)
    # order: [2, 1, 4, 0, 3]
    if order == [2, 1, 4, 0, 3] or ("-c[0], c[1]" in hist or "-x[0], x[1]" in hist):
        return True, "登峰造極！精準結合分數降序與原始編號升序，產出無懈可擊的錄取名單！"
    return False, "請依 (-分數, 原始編號) 排序並輸出錄取編號清單 [2, 1, 4, 0, 3]。"


def auto_grade_unit_12_5(env=None):
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

    # 取得 IPython 執行歷史（Colab 的 _ih 與 In 同源；本機測試可注入 _ih）
    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(str(x) for x in input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        ('12-5-1', '填空題', '排序取出中位數', 6, ("sorted_scores", "median"),
         lambda g: check_q1(g, history_str)),
        ('12-5-1', '練習題', '連續整數列相鄰判定', 6, ("is_consecutive",),
         lambda g: check_q2(g, history_str)),
        ('12-5-1', '挑戰題', '排序後線性收集重複等級', 5, ("duplicates",),
         lambda g: check_q3(g, history_str)),
        ('12-5-2', '填空題', '區間重疊與合併終點計算', 6, ("is_overlap", "merged_seg"),
         lambda g: check_q4(g, history_str)),
        ('12-5-2', '練習題', '起點排序與排程衝突檢查', 6, ("has_conflict",),
         lambda g: check_q5(g, history_str)),
        ('12-5-2', '挑戰題', '線段合併計算不重複佔用總時長', 5, ("total_hours",),
         lambda g: check_q6(g, history_str)),
        ('12-5-3', '填空題', '結束時間排序與貪婪活動挑選', 6, ("count",),
         lambda g: check_q7(g, history_str)),
        ('12-5-3', '練習題', '表演團體結束時間排程貪婪入選', 6, ("chosen",),
         lambda g: check_q8(g, history_str)),
        ('12-5-3', '挑戰題', '動畫不重疊挑選與總時數計算', 5, ("total_duration", "chosen_shows"),
         lambda g: check_q9(g, history_str)),
        ('12-5-4', '填空題', '數列排序與相鄰最大跨度', 6, ("max_gap",),
         lambda g: check_q10(g, history_str)),
        ('12-5-4', '練習題', '排序後相鄰線性找出全域最小差值', 6, ("min_d",),
         lambda g: check_q11(g, history_str)),
        ('12-5-4', '挑戰題', '跑步選手完賽秒數最小差距對決', 5, ("best_pair", "min_gap"),
         lambda g: check_q12(g, history_str)),
        ('12-5-5', '填空題', '已排序序列雙指標相向夾擊移動', 6, (),
         lambda g: check_q13(g, history_str)),
        ('12-5-5', '練習題', '雙指標 O(N) 極速求解 Two Sum', 5, ("found",),
         lambda g: check_q14(g, history_str)),
        ('12-5-5', '挑戰題', '雙指標逼近不超過限重之最佳載重組合', 5, ("max_load", "best_combo"),
         lambda g: check_q15(g, history_str)),
        ('12-5-6', '填空題', 'enumerate 打包原始索引與降序排列', 6, ("ranked",),
         lambda g: check_q16(g, history_str)),
        ('12-5-6', '練習題', '帶原始索引排序定位極值位置', 5, ("packed",),
         lambda g: check_q17(g, history_str)),
        ('12-5-6', '挑戰題', '成績降序且編號升序之錄取順序', 5, ("order",),
         lambda g: check_q18(g, history_str)),
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
        badge = '🏆 卓越宗師 (Mastery)'
    elif total_score >= 80:
        badge = '🥈 熟練精通 (Proficient)'
    elif total_score >= 60:
        badge = '🥉 基礎達標 (Pass)'
    else:
        badge = '🥉 仍需努力'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 12-5：APCS 排序實戰應用：區間線段排序、貪婪前導與已排序雙指標 —— 自動評分報告")
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
        "unit": "12-5",
        "unit_title": "APCS 排序實戰應用：區間線段排序、貪婪前導與已排序雙指標",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_5.py",
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
auto_grade_unit_12_5()
