# ==============================================================================
# 🧪 《PythAPCS123》單元 6-7：迴圈控制變數的常見天坑與除錯防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_7.py
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
NOTEBOOK_FILE = "PythAPCS123_6-7_loop_control_variable_pitfalls.ipynb"

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


def auto_grade_unit_6_7(env=None):
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
    history_clean_all = history_clean.replace("\n", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 6-7-1 迴圈變數篡改天坑（Loop Variable Tampering） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-7-1", "填空題", "替換手動竄改為正確煞車 (i == 4: break)", 4, ("last_seen",),
         lambda g: (
             (True, "中斷關鍵字 break 填寫正確，停機最後記錄為 4！")
             if (g.get("last_seen") == 4 or "break" in history_str) and
                ("i==4" in history_clean or "i == 4" in history_str)
             else (False, "請在 6-7-1 填空題空格填入正確煞車關鍵字 break！")
         )),

        ("6-7-1", "練習題", "棋盤彈簧跳步模擬 (total_steps = 8/7)", 4, ("total_steps",),
         lambda g: (
             (True, "while 自由步進彈簧跳躍模擬輸出正確！")
             if (g.get("total_steps") in [8, 7] or
                 (("total_steps" in g or "total_steps" in history_str) and
                  ("pos += 3" in history_str or "pos+=3" in history_clean)))
             else (False, "請撰寫 while 迴圈實現踩到彈簧跳步，統計 total_steps！")
         )),

        ("6-7-1", "挑戰題", "機器人動態能量損耗走訪 (final_x = 12, steps = 6)", 5, ("final_x", "steps", "energy"),
         lambda g: (
             (True, "能量消耗與步進前進雙重模擬 (x=12, steps=6) 成功！")
             if (((g.get("final_x") == 12) and g.get("steps") == 6) or
                 (("energy" in g or "energy" in history_str) and
                  ("final_x += 2" in history_str or "x += 2" in history_str or "energy -= 2" in history_str)))
             else (False, "請使用 while energy > 0 模擬奇偶能量消耗，得出 x=12, steps=6！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-2 差一錯誤（Off-by-One Error）與邊界防空轉 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-7-2", "填空題", "折返跑倒數點名 10 次 (range(10, 0, -1))", 4, ("count_runs",),
         lambda g: (
             (True, "負步進折返跑邊界 range(10, 0, -1) 填寫正確！")
             if (g.get("count_runs") == 10 or "range(10,0,-1)" in history_clean or "range(10, 0, -1)" in history_str)
             else (False, "請在 6-7-2 填空題填入起點 10、終點 0 與步進 -1！")
         )),

        ("6-7-2", "練習題", "閉區間端點偶數和 (even_sum = 28/10)", 4, ("even_sum",),
         lambda g: (
             (True, "包含端點 high + 1 區間偶數和輸出正確！")
             if (g.get("even_sum") in [28, 10] or
                 (("even_sum" in g or "even_sum" in history_str) and
                  ("high + 1" in history_str or "high+1" in history_clean)))
             else (False, "請走訪 range(low, high + 1) 計算閉區間偶數和！")
         )),

        ("6-7-2", "挑戰題", "包含端點負步進降溫 (non_negative_count = 3)", 5, ("non_negative_count",),
         lambda g: (
             (True, "包含端點 -5 降溫走訪與非負次數 (3 次) 驗證成功！")
             if (g.get("non_negative_count") == 3 or
                 (("non_negative_count" in g or "non_negative_count" in history_str) and
                  ("range(5," in history_clean and "-2)" in history_clean)))
             else (False, "請走訪 5 到 -5（步進 -2），統計非負溫度次數為 3 次！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-3 迴圈變數外溢與作用域幽靈（Leaked Loop Variables） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-7-3", "填空題", "外顯獨立變數承接搜尋結果 (target_found = candidate, break)", 4, ("target_found",),
         lambda g: (
             (True, "獨立變數承接與 break 終止填寫正確！")
             if (g.get("target_found") == 37 or ("target_found" in history_str and "break" in history_str) or
                 ("result" in history_str and "break" in history_str))
             else (False, "請在 6-7-3 填空題填入 result = val 並立刻 break！")
         )),

        ("6-7-3", "練習題", "空迴圈防禦與預設值守護 (answer = 51/-1)", 4, ("answer",),
         lambda g: (
             (True, "空區間預設值安全防護輸出正確！")
             if (g.get("answer") in [51, -1] or
                 (("answer" in g or "answer" in history_str) and
                  ("answer = -1" in history_str or "answer=-1" in history_clean)))
             else (False, "請預設 answer = -1，若找到 > 50 則更新並 break！")
         )),

        ("6-7-3", "挑戰題", "質數因數安全提取 (is_prime = True, factor_found = 0)", 5, ("is_prime", "factor_found"),
         lambda g: (
             (True, "質數檢驗因數安全提取與旗標維護成功！")
             if ((g.get("is_prime") is True and g.get("factor_found") == 0) or
                 (("factor_found" in g or "factor_found" in history_str) and
                  ("is_prime" in g or "is_prime" in history_str)))
             else (False, "請以迴圈檢查 n = 29，質數維持 factor_found = 0！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-4 while 忘記步進或步進邏輯死結（Infinite Loop） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-7-4", "填空題", "補齊電量扣除步進 (battery -= 2)", 4, (),
         lambda g: (
             (True, "while 步進更新指令 battery -= 2 填寫正確！")
             if ("battery-=2" in history_clean or "battery -= 2" in history_str)
             else (False, "請在 6-7-4 填空題填入電量扣除指令 battery -= 2！")
         )),

        ("6-7-4", "練習題", "對數折半縮小安全計數 (halves = 4)", 4, ("halves",),
         lambda g: (
             (True, "數值必定折半縮小安全計數輸出正確！")
             if (g.get("halves") == 4 or
                 (("halves" in g or "halves" in history_str) and
                  ("N //= 2" in history_str or "N//=2" in history_clean)))
             else (False, "請在 while N > 1 中 N //= 2 並累加 halves 次數！")
         )),

        ("6-7-4", "挑戰題", "考拉茲猜想抵達 1 的步數 (n=12 時 step_count = 9)", 5, ("step_count",),
         lambda g: (
             (True, "考拉茲 3n+1 步數統計 (9 步) 成功！")
             if (g.get("step_count") == 9 or
                 (("step_count" in g or "step_count" in history_str) and
                  ("3 * collatz_n + 1" in history_str or "3*collatz_n+1" in history_clean or "3 * n + 1" in history_str or "3*n+1" in history_clean)))
             else (False, "請以 while 迴圈模擬考拉茲猜想，n = 12 抵達 1 為 9 步！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-5 巢狀迴圈變數同名遮蔽（Variable Shadowing） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-7-5", "填空題", "內層變數修正為獨立 col (for col in range(4))", 4, ("total_stars",),
         lambda g: (
             (True, "內層計數器獨立命名 col 填寫正確，12 顆星無誤！")
             if (g.get("total_stars") == 12 or "forcolinrange" in history_clean)
             else (False, "請在 6-7-5 填空題將內層變數修正為 col！")
         )),

        ("6-7-5", "練習題", "獨立變數二維座標偶數和計數 (even_cells = 5/3)", 4, ("even_cells",),
         lambda g: (
             (True, "雙層獨立命名 r, c 與偶數和座標統計正確！")
             if (g.get("even_cells") in [5, 3] or
                 (("even_cells" in g or "even_cells" in history_str) and
                  ("(r + c) % 2 == 0" in history_str or "(r+c)%2==0" in history_clean)))
             else (False, "請使用獨立變數 r 與 c，統計 (r + c) % 2 == 0 的格子數！")
         )),

        ("6-7-5", "挑戰題", "三重獨立變數立體座標點 (match_points = 8)", 4, ("match_points",),
         lambda g: (
             (True, "三重獨立變數 x, y, z 體積走訪 (8 點) 成功！")
             if (g.get("match_points") == 8 or
                 (("match_points" in g or "match_points" in history_str) and
                  ("(x_pos + y_pos + z_pos) % 3 == 0" in history_str or "(x_pos+y_pos+z_pos)%3==0" in history_clean or "(x + y + z) % 3 == 0" in history_str or "(x+y+z)%3==0" in history_clean)))
             else (False, "請使用 x, y, z 三重迴圈，統計 (x + y + z) % 3 == 0 為 8 點！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-6 累加器與旗標「忘了歸零」狀態污染（State Leakage） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-7-6", "填空題", "每回合外層開始前歸零 (total = 0)", 4, (),
         lambda g: (
             (True, "每回合累加器事前歸零 total = 0 填寫正確！")
             if ("total = 0" in history_str or "total=0" in history_clean)
             else (False, "請在 6-7-6 填空題空格填入歸零指令 total = 0！")
         )),

        ("6-7-6", "練習題", "每列偶數獨立歸零統計 (last_row_even)", 4, ("last_row_even",),
         lambda g: (
             (True, "雙重迴圈每列獨立歸零與末列偶數統計正確！")
             if (("last_row_even" in g or "last_row_even" in history_str) and
                 ("row_even_count = 0" in history_str or "row_even_count=0" in history_clean) and
                 (g.get("last_row_even") in (1, 3) or "last_row_even" in g))
             else (False, "請在每列外層迴圈開頭將 row_even_count 歸零，並記錄末列偶數個數 last_row_even！")
         )),

        ("6-7-6", "挑戰題", "多回合質數檢驗旗標獨立歸零 (prime_total = 1)", 4, ("prime_total",),
         lambda g: (
             (True, "多回合獨立重設 is_prime 旗標 (質數個數 1) 成功！")
             if (g.get("prime_total") == 1 or
                 (("prime_total" in g or "prime_total" in history_str) and
                  ("is_prime = True" in history_str or "is_prime=True" in history_clean)))
             else (False, "請每回合將 is_prime 重設為 True，統計質數總數為 1！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-7 while 條件邏輯反轉與變數未同步（Desynchronization） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-7-7", "填空題", "因數連續除盡條件與縮小 (num_val % 2 == 0, num_val // 2)", 4, (),
         lambda g: (
             (True, "因數連續整除條件 num_val % 2 == 0 與縮半填寫正確！")
             if (("num_val%2" in history_clean or "n%2" in history_clean) and ("num_val//2" in history_clean or "num_val //= 2" in history_str or "n//2" in history_clean or "n //= 2" in history_str))
             else (False, "請在 6-7-7 填空題填入 num_val % 2 以及縮小 num_val // 2！")
         )),

        ("6-7-7", "練習題", "高度序列高峰點計數 (peak_count = 5/3)", 4, ("peak_count",),
         lambda g: (
             (True, "序列高度點精準受檢高峰點統計輸出正確！")
             if (g.get("peak_count") in [5, 3] or
                 (("peak_count" in g or "peak_count" in history_str) and
                  ("height > 5" in history_str or "height>5" in history_clean)))
             else (False, "請走訪 i 檢查 height = (i * 7) % 11 > 5 的高峰點！")
         )),

        ("6-7-7", "挑戰題", "連續減法模擬取餘數 (sub_times = 5, remainder = 3)", 4, ("sub_times", "remainder"),
         lambda g: (
             (True, "連續減法模擬商數 (5) 與餘數 (3) 成功！")
             if ((g.get("sub_times") == 5 and (g.get("remainder") == 3 or g.get("dividend") == 3)) or
                 (("sub_times" in g or "sub_times" in history_str) and
                  ("dividend -= divisor" in history_str or "dividend-=divisor" in history_clean or "a -= b" in history_str or "a-=b" in history_clean)))
             else (False, "請以 while a >= b 模擬 38 除以 7，求得商 5 餘 3！")
         )),

        # ----------------------------------------------------------------------
        # 6-7-8 APCS 考場四問自我檢核 SOP (共 12 分)
        # ----------------------------------------------------------------------
        ("6-7-8", "填空題", "考場四問修正歸零與包含端點 (odd_count = 0, range(1, 6))", 4, (),
         lambda g: (
             (True, "考場四問歸零與正確邊界 range(1, 6) 填寫正確！")
             if ("odd_count=0" in history_clean or "odd_count = 0" in history_str) and
                ("range(1,6)" in history_clean or "range(1, 6)" in history_str or "5+1" in history_clean)
             else (False, "請在 6-7-8 填空題填入 odd_count = 0 與邊界 6！")
         )),

        ("6-7-8", "練習題", "區間最大偶數倒序搜尋 (max_even = 18/-1)", 4, ("max_even",),
         lambda g: (
             (True, "包含端點 B 倒序搜尋最大偶數輸出正確！")
             if (g.get("max_even") in [18, -1] or
                 (("max_even" in g or "max_even" in history_str) and
                  ("max_even = num" in history_str or "max_even=num" in history_clean)))
             else (False, "請倒序搜尋 [A, B] 區間最大偶數，找到即 break！")
         )),

        ("6-7-8", "挑戰題", "二維方陣 0 出現頻率無死角檢核 (zero_freq = 0)", 4, ("zero_freq",),
         lambda g: (
             (True, "二維方陣 (r*c)%5 等於 0 頻率精確檢核 (0 次) 成功！")
             if (g.get("zero_freq") == 0 or
                 (("zero_freq" in g or "zero_freq" in history_str) and
                  ("(r * c) % 5" in history_str or "(r*c)%5" in history_clean)))
             else (False, "請在 4x4 方陣統計 (r*c)%5 == 0 出現次數，結果必為 0！")
         )),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通迴圈控制變數避坑指南，考場四問與狀態隔離無懈可擊！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，差一錯誤防禦與變數外溢隔離思維嚴密！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調狀態歸零或步進更新！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-7：迴圈控制變數的常見天坑與除錯防禦 —— 自動評分報告")
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
        "unit": "6-7",
        "unit_title": "迴圈控制變數的常見天坑與除錯防禦",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_6_7.py",
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
auto_grade_unit_6_7()
