# ==============================================================================
# 🧪 《PythAPCS123》單元 12-9：內建二分搜尋模組：bisect 與數值區間查詢應用 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_9.py
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
import bisect
# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_12-9_bisect_module_and_range_queries.ipynb"

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
    ip = g.get("insert_pos")
    if ip is None:
        return False, "請確認填入 import bisect 與 bisect.bisect(prms129, 35)。"
    if ip == 11 or ("bisect.bisect(prms129, 35)" in hist or "bisect.bisect_right(prms129, 35)" in hist):
        return True, "太棒了！正確引入 bisect 模組並精準計算出 35 應插入在索引 11！"
    return False, "請確認填入 import bisect 與 bisect.bisect(prms129, 35)。"

def check_q2(g, hist):
    pos129 = g.get("pos129")
    rd = g.get("raw_dt129")
    if pos129 is None and rd is None:
        return False, "請先對 raw_dt129 排序，再呼叫 bisect.bisect 找出插入索引。"
    if (pos129 == 2 and rd == [10, 20, 30, 40, 50]) or ("raw_dt129.sort()" in hist and "bisect.bisect" in hist):
        return True, "完全正確！排序後順利呼叫 bisect 找出數值 25 位於索引 2！"
    return False, "請先對 raw_dt129 排序，再呼叫 bisect.bisect 找出插入索引。"

def check_q3(g, hist):
    pmin = g.get("pos_min")
    pmax = g.get("pos_max")
    if pmin is None and pmax is None:
        return False, "請驗證 0.0 與 100.0 的插入位置 (應分別為 0 與 5)。"
    if (pmin == 0 and pmax == 5) or ("bisect.bisect(readings, 0.0)" in hist and "100.0" in hist):
        return True, "太強了！親自驗證 0.0 落在索引 0、100.0 落在 len(5)，邊界行為掌握透徹！"
    return False, "請驗證 0.0 與 100.0 的插入位置 (應分別為 0 與 5)。"

def check_q4(g, hist):
    is_found = g.get("is_found")
    idx129 = g.get("idx129")
    if is_found is None and idx129 is None:
        return False, "請確認填入 bisect.bisect_left 與相等比較符號 ==。"
    if (is_found is True and idx129 == 2) or ("bisect.bisect_left" in hist and "mmbr129[idx129] == query_id" in hist):
        return True, "完全正確！bisect_left 搭配相等比較 ==，安全精確檢驗存在性！"
    return False, "請確認填入 bisect.bisect_left 與相等比較符號 ==。"

def check_q5(g, hist):
    idx_pass = g.get("idx_pass")
    fld_cnt = g.get("fld_cnt")
    if idx_pass is None and fld_cnt is None:
        return False, "請使用 bisect_left(grds129, 60) 查詢第一個及格索引與不及格人數。"
    if (idx_pass == 1 and fld_cnt == 1) or ("bisect.bisect_left(grds129, 60)" in hist):
        return True, "精彩！bisect_left(60) 索引為 1，代表不及格人數恰好為 1 人，秒殺及格線！"
    return False, "請使用 bisect_left(grds129, 60) 查詢第一個及格索引與不及格人數。"

def check_q6(g, hist):
    func = g.get("get_fare")
    if func is None:
        return False, "請實作 get_fare(dist) 計算區間車資。"
    if callable(func):
        try:
            if func(28) == 35 and func(70) == 60 and func(10) == 15:
                return True, "太實用了！捷運計費函數實機測試完全正確，28km 收 35 元，70km 封頂 60 元！"
        except Exception:
            pass
    if "def get_fare" in hist and "bisect.bisect_left" in hist:
        return True, "計費邏輯正確，通過！"
    return False, "請實作 get_fare(dist) 計算區間車資。"

def check_q7(g, hist):
    lp = g.get("lst_pos")
    if lp is None:
        return False, "請填入 bisect.bisect_right 與 ub129 - 1 定位最後出現位置。"
    if lp == 4 or ("bisect.bisect_right" in hist and "ub129 - 1" in hist):
        return True, "完全正確！bisect_right 取得第一個嚴格大於位置後減 1，即為最後出現索引 4！"
    return False, "請填入 bisect.bisect_right 與 ub129 - 1 定位最後出現位置。"

def check_q8(g, hist):
    ub1 = g.get("ub1")
    if ub1 is None:
        return False, "請呼叫 bisect_right 查詢數值 15 的上界索引。"
    # arr129 = [5, 10, 15, 15, 15, 20, 25] -> bisect_right(arr129, 15) = 5
    if ub1 == 5 or ("bisect.bisect_right(arr129, 15)" in hist):
        return True, "太棒了！上界索引為 5，同時代表小於等於 15 的元素恰有 5 個！"
    return False, "請呼叫 bisect_right 查詢數值 15 的上界索引。"

def check_q9(g, hist):
    start_pos = g.get("start_idx")
    e = g.get("end_idx")
    if start_pos is None and e is None:
        return False, "請利用 bisect_left 與 bisect_right 定位數值 50 的出現區間。"
    # exp_rcrd = [10, 20, 20, 35, 50, 50, 50, 80] -> 50: [4, 6]
    if (start_pos == 4 and e == 6) or ("bisect_left" in hist and "bisect_right" in hist):
        return True, "精彩！雙向夾擊精準定位數值 50 之完整區間 [4, 6]！"
    return False, "請利用 bisect_left 與 bisect_right 定位數值 50 的出現區間。"

def check_q10(g, hist):
    cnt129 = g.get("cnt129")
    if cnt129 is None:
        return False, "請填入 bisect_left(ns129, 20) 與 bisect_right(ns129, 40)。"
    # ns129 = [5, 12, 20, 25, 30, 40, 45, 60] -> [20, 40] 內有 20, 25, 30, 40 共 4 個
    if cnt129 == 4 or ("r129 - l129" in hist and "bisect_left" in hist and "bisect_right" in hist):
        return True, "完全正確！左閉右閉區間以 bisect_right(40) - bisect_left(20) 秒算個數 4！"
    return False, "請填入 bisect_left(ns129, 20) 與 bisect_right(ns129, 40)。"

def check_q11(g, hist):
    rng_cnts = g.get("rng_cnts")
    if rng_cnts is None:
        return False, "請以 bisect_right - bisect_left 計算各區間人數清單。"
    # qrs = [(160, 170), (150, 150), (190, 200)] -> [3, 1, 0]
    if rng_cnts == [3, 1, 0] or ("count_in_range" in hist):
        return True, "太棒了！批次查詢多組身高區間人數 [3, 1, 0] 完全無誤！"
    return False, "請以 bisect_right - bisect_left 計算各區間人數清單。"

def check_q12(g, hist):
    qc = g.get("qlfd_cnt")
    qs = g.get("qlfd_sum")
    if qc is None and qs is None:
        return False, "請計算符合區間資格的訂單筆數 (5) 與總金額 (5590)。"
    # orders = [120, 450, 500, 890, 1200, 1500, 1500, 2300, 3100]
    # [500, 1500] 內: 500, 890, 1200, 1500, 1500 共 5 筆，總和 = 5590 元
    if (qc == 5 and qs == 5590) or ("sum(orders[l1:r3])" in hist and "r3 - l1" in hist):
        return True, "太厲害了！不僅以雙界算出 5 筆合資格訂單，更以切片累加出總金額 5590 元！"
    return False, "請計算符合區間資格的訂單筆數 (5) 與總金額 (5590)。"

def check_q13(g, hist):
    bi = g.get("brck_idx")
    if bi is None:
        return False, "請呼叫 bisect.bisect 取得稅率級距索引。"
    # tax_brkt = [50, 120], income = 80 -> idx129 = 1 ("12%")
    if bi == 1 or ("bisect.bisect(tax_brkt, income)" in hist):
        return True, "完全正確！年所得 80 萬精確對應級距 1（稅率 12%），免寫繁複 if-elif！"
    return False, "請呼叫 bisect.bisect 取得稅率級距索引。"

def check_q14(g, hist):
    func = g.get("get_rank")
    if func is None:
        return False, "請實作 get_rank(points) 函數，回傳對應段位名稱。"
    if callable(func):
        try:
            if func(2500) == "黃金" and func(800) == "青銅" and func(3500) == "鑽石":
                return True, "太神了！段位查表函數實機測試全數吻合，2500 分晉升黃金，800 分為青銅！"
        except Exception:
            pass
    if "def get_rank" in hist and "bisect.bisect_right" in hist:
        return True, "段位查表邏輯正確，通過！"
    return False, "請實作 get_rank(points) 函數，回傳對應段位名稱。"

def check_q15(g, hist):
    func = g.get("calc_final_bill")
    if func is None:
        return False, "請實作 calc_final_bill(amount) 計算折後實付金額。"
    if callable(func):
        try:
            if func(2500) == 2250 and func(6000) == 4200 and func(500) == 500:
                return True, "精彩絕倫！滿額折扣查表計算實測完全正確，2500 元折為 2250 元，6000 元折為 4200 元！"
        except Exception:
            pass
    if "def calc_final_bill" in hist and "bisect" in hist:
        return True, "折扣計算邏輯通過！"
    return False, "請實作 calc_final_bill(amount) 計算折後實付金額。"

def check_q16(g, hist):
    lt = g.get("live_temps")
    if lt is None:
        return False, "請呼叫 bisect.insort(live_temps, new_rdng)。"
    # live_temps = [18.5, 20.2, 22.0, 25.5], new_rdng = 21.4 -> [18.5, 20.2, 21.4, 22.0, 25.5]
    if lt == [18.5, 20.2, 21.4, 22.0, 25.5] or ("bisect.insort" in hist and "live_temps" in hist):
        return True, "完全正確！bisect.insort 動態有序插入 21.4，維護單調序列絲滑無縫！"
    return False, "請呼叫 bisect.insort(live_temps, new_rdng)。"

def check_q17(g, hist):
    tasks = g.get("tasks")
    if tasks is None:
        return False, "請使用 bisect.insort 依序插入任務至 tasks 清單。"
    if tasks == [1, 2, 3, 4, 5, 7, 8] or ("bisect.insort(tasks" in hist):
        return True, "太棒了！動態依序插入新任務，維持任務緊急度清單 [1, 2, 3, 4, 5, 7, 8]！"
    return False, "請使用 bisect.insort 依序插入任務至 tasks 清單。"

def check_q18(g, hist):
    strm = g.get("strm")
    if strm is None:
        return False, "請使用 bisect.insort 依序插入串流數據並計算中位數。"
    if strm == [10, 20, 30, 40, 50] or ("bisect.insort(strm" in hist and "mid_val" in hist):
        return True, "滿分通關！動態中位數監控器實作大獲全勝，全單元與第十二章全體通關！"
    return False, "請使用 bisect.insort 依序插入串流數據並計算中位數。"


def auto_grade_unit_12_9(env=None):
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
        ('12-9-1', '填空題', 'import bisect 引入與插入位置查詢', 6, ("insert_pos",),
         lambda g: check_q1(g, history_str)),
        ('12-9-1', '練習題', '先排序後呼叫 bisect 找出目標插入點', 6, ("pos129", "raw_dt129"),
         lambda g: check_q2(g, history_str)),
        ('12-9-1', '挑戰題', '極小極大兩極端值在 0 與 len 之邊界表現', 5, ("pos_min", "pos_max"),
         lambda g: check_q3(g, history_str)),
        ('12-9-2', '填空題', 'bisect_left 下界查詢與相等驗證', 6, ("is_found", "idx129"),
         lambda g: check_q4(g, history_str)),
        ('12-9-2', '練習題', '及格線門檻索引與不及格人數秒算', 6, ("idx_pass", "fld_cnt"),
         lambda g: check_q5(g, history_str)),
        ('12-9-2', '挑戰題', '里程計費門檻查表與封頂設計', 5, ("get_fare",),
         lambda g: check_q6(g, history_str)),
        ('12-9-3', '填空題', 'bisect_right 上界查詢與最後出現位置 ub129 - 1', 6, ("lst_pos",),
         lambda g: check_q7(g, history_str)),
        ('12-9-3', '練習題', '上界索引與小於等於目標之元素統計', 6, ("ub1",),
         lambda g: check_q8(g, history_str)),
        ('12-9-3', '挑戰題', '雙界結合一次定位重複元素之 [start, end] 區間', 5, ("start_idx", "end_idx"),
         lambda g: check_q9(g, history_str)),
        ('12-9-4', '填空題', '雙界相減 r129 - l129 秒算區間元素總數', 6, ("cnt129",),
         lambda g: check_q10(g, history_str)),
        ('12-9-4', '練習題', '批次多組區間範圍人數極速查詢', 6, ("rng_cnts",),
         lambda g: check_q11(g, history_str)),
        ('12-9-4', '挑戰題', '折價券資格訂單筆數與切片總金額計算', 5, ("qlfd_cnt", "qlfd_sum"),
         lambda g: check_q12(g, history_str)),
        ('12-9-5', '填空題', '所得稅率級距查表免寫多重分支', 6, ("brck_idx",),
         lambda g: check_q13(g, history_str)),
        ('12-9-5', '練習題', '遊戲積分段位名稱極速查表', 5, ("get_rank",),
         lambda g: check_q14(g, history_str)),
        ('12-9-5', '挑戰題', '購物消費滿額階梯折扣查表實付金額', 5, ("calc_final_bill",),
         lambda g: check_q15(g, history_str)),
        ('12-9-6', '填空題', 'bisect.insort 動態有序插入新測量值', 6, ("live_temps",),
         lambda g: check_q16(g, history_str)),
        ('12-9-6', '練習題', '維護即時緊急度待辦任務有序清單', 5, ("tasks",),
         lambda g: check_q17(g, history_str)),
        ('12-9-6', '挑戰題', '動態串流數據中位數 (Running Median) 監控', 5, ("strm",),
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
    print(" 📊 《PythAPCS123》單元 12-9：內建二分搜尋模組：bisect 與數值區間查詢應用 —— 自動評分報告")
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
        "unit": "12-9",
        "unit_title": "內建二分搜尋模組：bisect 與數值區間查詢應用",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_9.py",
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
auto_grade_unit_12_9()
