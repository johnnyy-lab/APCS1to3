# ==============================================================================
# 🧪 《PythAPCS123》單元 13-5：邏輯錯誤（Logic Error）排查與常見 WA 陷阱拆解 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_5.py
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
NOTEBOOK_FILE = "PythAPCS123_13-5_logic_errors_and_wa_pitfalls.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max，
    評分器與學員程式共用同一個全域，呼叫內建會被學員變數遮蔽。"""
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

def fetch_google_account_info():
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = globals()
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name

def extract_notebook_history():
    hist_text = ""
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip and hasattr(ip, "user_ns"):
            In = ip.user_ns.get("In", [])
            hist_text = "\n".join(In)
    except Exception:
        pass
    return hist_text

def check_q1(g, hist):
    fn = g.get("diagnose_wa_discrepancy")
    if callable(fn):
        try:
            r1 = fn("42", "42")
            r2 = fn("Line1\nLine2", "Line1\nLine2 ")
            if r1 == ("AC", "Accepted") and r2 == ("AC", "Accepted"):
                return True, "太棒了！完全吻合或尾端空格容錯皆判定為 AC！"
        except Exception as e:
            return False, f"執行 diagnose_wa_discrepancy 時發生例外: {e}"
    if "diagnose_wa_discrepancy" in hist and '"AC"' in hist:
        return True, "偵測到 AC 診斷判定邏輯！"
    return False, "尚未正確實作 diagnose_wa_discrepancy 或相符輸出未回傳 AC。"

def check_q2(g, hist):
    fn = g.get("diagnose_wa_discrepancy")
    if callable(fn):
        try:
            r1 = fn("100", "99")
            r2 = fn("A\nB\nC", "A\nB")
            if r1[0] == "WA" and "Line 1" in r1[1] and r2[0] == "WA" and "Line 3" in r2[1]:
                return True, "太棒了！精準定位第一個相異行號與內容細節！"
        except Exception as e:
            return False, f"執行 diagnose_wa_discrepancy 時發生例外: {e}"
    if "diagnose_wa_discrepancy" in hist and '"WA"' in hist:
        return True, "偵測到 WA 診斷判定邏輯！"
    return False, "相異輸出未能回傳正確 WA 行號與資訊。"

def check_q3(g, hist):
    fn = g.get("interval_stats")
    if callable(fn):
        try:
            r1 = fn(1, 5)
            r2 = fn(10, 10)
            r3 = fn(-3, 3)
            if r1 == (5, 15) and r2 == (1, 10) and r3 == (7, 0):
                return True, "太棒了！閉區間元素個數與總和計算完全杜絕差一錯誤！"
        except Exception as e:
            return False, f"執行 interval_stats 時發生例外: {e}"
    if "interval_stats" in hist:
        return True, "偵測到 interval_stats 閉區間統計邏輯！"
    return False, "尚未正確實作 interval_stats 或區間計算有誤。"

def check_q4(g, hist):
    fn = g.get("safe_binary_search")
    if callable(fn):
        try:
            if (fn([5], 5) is True and 
                fn([5], 6) is False and 
                fn([], 1) is False and 
                fn([1, 3, 5, 7, 9], 9) is True):
                return True, "太棒了！二分搜尋在單元素、空陣列與邊界完全不漏判！"
        except Exception as e:
            return False, f"執行 safe_binary_search 時發生例外: {e}"
    if "safe_binary_search" in hist:
        return True, "偵測到 safe_binary_search 二分搜尋邏輯！"
    return False, "尚未正確實作 safe_binary_search 或邊界搜尋有誤。"

def check_q5(g, hist):
    fn = g.get("safe_midpoint")
    if callable(fn):
        try:
            if fn(10, 20) == 15 and fn(0, 8) == 4 and fn(-10, 10) == 0:
                return True, "太棒了！中點計算括號完全正確，無優先級運算偏差！"
        except Exception as e:
            return False, f"執行 safe_midpoint 時發生例外: {e}"
    if "safe_midpoint" in hist:
        return True, "偵測到 safe_midpoint 中點計算邏輯！"
    return False, "尚未正確實作 safe_midpoint。"

def check_q6(g, hist):
    fn = g.get("is_even_bitwise")
    if callable(fn):
        try:
            if (fn(4) is True and 
                fn(7) is False and 
                fn(0) is True and 
                fn(-2) is True and 
                fn(-3) is False):
                return True, "太棒了！位元運算與等號優先級括號精準結合！"
        except Exception as e:
            return False, f"執行 is_even_bitwise 時發生例外: {e}"
    if "is_even_bitwise" in hist:
        return True, "偵測到 is_even_bitwise 偶數判斷邏輯！"
    return False, "尚未正確實作 is_even_bitwise 或正負奇偶判斷不符。"

def check_q7(g, hist):
    fn = g.get("safe_float_equal")
    if callable(fn):
        try:
            if (fn(0.1 + 0.2, 0.3) is True and 
                fn(1.00000000001, 1.0) is True and 
                fn(1.05, 1.0) is False):
                return True, "太棒了！浮點數微小誤差容許比對守門員精準防禦！"
        except Exception as e:
            return False, f"執行 safe_float_equal 時發生例外: {e}"
    if "safe_float_equal" in hist:
        return True, "偵測到 safe_float_equal 浮點比對邏輯！"
    return False, "尚未正確實作 safe_float_equal 或比對結果不符。"

def check_q8(g, hist):
    fn = g.get("truncate_towards_zero_divide")
    if callable(fn):
        try:
            if (fn(7, 2) == 3 and 
                fn(-7, 2) == -3 and 
                fn(10, -3) == -3 and 
                fn(-10, -3) == 3):
                return True, "太棒了！正負數向零截斷除法實作精確無誤！"
        except Exception as e:
            return False, f"執行 truncate_towards_zero_divide 時發生例外: {e}"
    if "truncate_towards_zero_divide" in hist:
        return True, "偵測到向零截斷除法邏輯！"
    return False, "尚未正確實作 truncate_towards_zero_divide 或向零截斷偏差。"

def check_q9(g, hist):
    fn = g.get("create_independent_matrix")
    if callable(fn):
        try:
            m = fn(3, 4, 0)
            m[1][2] = 5
            if m[0] == [0, 0, 0, 0] and m[1] == [0, 0, 5, 0] and m[2] == [0, 0, 0, 0]:
                return True, "太棒了！二維矩陣列與列完全獨立，徹底粉碎淺拷貝幽靈！"
        except Exception as e:
            return False, f"執行 create_independent_matrix 時發生例外: {e}"
    if "create_independent_matrix" in hist:
        return True, "偵測到獨立矩陣建立邏輯！"
    return False, "尚未正確實作 create_independent_matrix 或列與列存在共享參考。"

def check_q10(g, hist):
    fn = g.get("safe_append_copy")
    if callable(fn):
        try:
            src = ["a", "b"]
            res = fn(src, "c")
            if res == ["a", "b", "c"] and src == ["a", "b"] and res is not src:
                return True, "太棒了！無副作用追加新元素，原始串列 100% 未受污染！"
        except Exception as e:
            return False, f"執行 safe_append_copy 時發生例外: {e}"
    if "safe_append_copy" in hist:
        return True, "偵測到無副作用複本邏輯！"
    return False, "尚未正確實作 safe_append_copy 或原始串列被修改。"

def check_q11(g, hist):
    fn = g.get("matrix_diagonal_sums")
    if callable(fn):
        try:
            m1 = [[1, 2], [3, 4]]
            if fn(m1) == (5, 5):
                return True, "太棒了！主次對角線計算完全正確且變數命名無遮蔽！"
        except Exception as e:
            return False, f"執行 matrix_diagonal_sums 時發生例外: {e}"
    if "matrix_diagonal_sums" in hist:
        return True, "偵測到對角線計算邏輯！"
    return False, "尚未正確實作 matrix_diagonal_sums 或對角線加總不符。"

def check_q12(g, hist):
    fn = g.get("matrix_diagonal_sums")
    if callable(fn):
        try:
            m2 = [[2, 0, 0], [0, 3, 0], [0, 0, 4]]
            if fn(m2) == (9, 3):
                return True, "太棒了！3x3 矩陣中心元素次對角線重複計數與邊界加總無誤！"
        except Exception as e:
            return False, f"執行 matrix_diagonal_sums 時發生例外: {e}"
    if "matrix_diagonal_sums" in hist:
        return True, "偵測到 3x3 矩陣對角線驗算！"
    return False, "3x3 矩陣對角線總和計算錯誤。"

def check_q13(g, hist):
    fn = g.get("process_testcases_cleanly")
    if callable(fn):
        try:
            data = [[60, 40, 70], [50, 51], [10, 20]]
            if fn(data) == [130, 51, 0]:
                return True, "太棒了！每筆測資獨立重設狀態，徹底根絕跨測資污染！"
        except Exception as e:
            return False, f"執行 process_testcases_cleanly 時發生例外: {e}"
    if "process_testcases_cleanly" in hist:
        return True, "偵測到乾淨多測資處理邏輯！"
    return False, "尚未正確實作 process_testcases_cleanly 或存在狀態殘留。"

def check_q14(g, hist):
    fn = g.get("process_testcases_cleanly")
    if callable(fn):
        try:
            if fn([[], [100]]) == [0, 100] and fn([[55], [55], [55]]) == [55, 55, 55]:
                return True, "太棒了！空測資與重複單元素測資完全隔離精準計算！"
        except Exception as e:
            return False, f"執行 process_testcases_cleanly 時發生例外: {e}"
    if "process_testcases_cleanly" in hist:
        return True, "偵測到邊界測資獨立隔離邏輯！"
    return False, "空測資或重複測資處理不符。"

def check_q15(g, hist):
    fn = g.get("find_min_max_difference")
    if callable(fn):
        try:
            if fn([-10, -5, -20]) == 15 and fn([-7, 8]) == 15:
                return True, "太棒了！全負數測資極值差計算精確，擺脫預設為 0 之盲點！"
        except Exception as e:
            return False, f"執行 find_min_max_difference 時發生例外: {e}"
    if "find_min_max_difference" in hist:
        return True, "偵測到全負數極值差防禦邏輯！"
    return False, "尚未正確實作 find_min_max_difference 或全負數差值計算錯誤。"

def check_q16(g, hist):
    fn = g.get("find_min_max_difference")
    if callable(fn):
        try:
            if fn([-100]) == 0 and fn([5, 5, 5]) == 0:
                return True, "太棒了！單一元素與全相同元素差值安全回傳 0！"
        except Exception as e:
            return False, f"執行 find_min_max_difference 時發生例外: {e}"
    if "find_min_max_difference" in hist:
        return True, "偵測到單元素與重複值極值防禦！"
    return False, "單一元素或全相同串列未能回傳 0。"

def check_q17(g, hist):
    fn = g.get("stress_test_validator")
    if callable(fn):
        try:
            f_s = lambda lst: max(lst) if lst else None
            f_f_good = lambda lst: sorted(lst)[-1] if lst else None
            res = fn(f_s, f_f_good, [[1, 5, 2], [-5, -1], [10]])
            if res == ("AC", 3):
                return True, "太棒了！對拍測資全數吻合時精準報告 ('AC', 測資數)！"
        except Exception as e:
            return False, f"執行 stress_test_validator 時發生例外: {e}"
    if "stress_test_validator" in hist and '"AC"' in hist:
        return True, "偵測到對拍 AC 驗證邏輯！"
    return False, "尚未正確實作 stress_test_validator 或全相符未回傳 AC。"

def check_q18(g, hist):
    fn = g.get("stress_test_validator")
    if callable(fn):
        try:
            f_s = lambda lst: max(lst) if lst else None
            f_f_bad = lambda lst: lst[0] if lst else None
            res = fn(f_s, f_f_bad, [[10, 20]])
            if (isinstance(res, tuple) and 
                res[0] == "WA" and 
                res[1] == [10, 20] and 
                res[2] == 20 and 
                res[3] == 10):
                return True, "太棒了！對拍中途出現相異時立刻終止並回傳反例與兩者答案！"
        except Exception as e:
            return False, f"執行 stress_test_validator 時發生例外: {e}"
    if "stress_test_validator" in hist and '"WA"' in hist:
        return True, "偵測到對拍 WA 抓反例邏輯！"
    return False, "對拍出錯時未能回傳正確反例與答案元組。"


def auto_grade_unit_13_5():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info()

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
        ('13-5-1', '實作題', 'diagnose_wa_discrepancy 完全相符回傳 AC', 6, ("diagnose_wa_discrepancy",),
         lambda g: check_q1(g, history_str)),
        ('13-5-1', '實作題', 'diagnose_wa_discrepancy 揪出首個差異行與內容', 6, ("diagnose_wa_discrepancy",),
         lambda g: check_q2(g, history_str)),
        ('13-5-2', '實作題', 'interval_stats 閉區間長度與總和精準計算', 6, ("interval_stats",),
         lambda g: check_q3(g, history_str)),
        ('13-5-2', '實作題', 'safe_binary_search 二分搜尋涵蓋單元素邊界', 6, ("safe_binary_search",),
         lambda g: check_q4(g, history_str)),
        ('13-5-3', '實作題', 'safe_midpoint 中點運算正確優先級防偏', 6, ("safe_midpoint",),
         lambda g: check_q5(g, history_str)),
        ('13-5-3', '實作題', 'is_even_bitwise 位元運算與等號優先級防護', 6, ("is_even_bitwise",),
         lambda g: check_q6(g, history_str)),
        ('13-5-4', '實作題', 'safe_float_equal 浮點數微小誤差容許比對', 6, ("safe_float_equal",),
         lambda g: check_q7(g, history_str)),
        ('13-5-4', '實作題', 'truncate_towards_zero_divide 正負向零截斷整除', 6, ("truncate_towards_zero_divide",),
         lambda g: check_q8(g, history_str)),
        ('13-5-5', '實作題', 'create_independent_matrix 建立完全獨立二維矩陣', 6, ("create_independent_matrix",),
         lambda g: check_q9(g, history_str)),
        ('13-5-5', '實作題', 'safe_append_copy 無副作用複本追加', 6, ("safe_append_copy",),
         lambda g: check_q10(g, history_str)),
        ('13-5-6', '實作題', 'matrix_diagonal_sums 主次對角線計算', 5, ("matrix_diagonal_sums",),
         lambda g: check_q11(g, history_str)),
        ('13-5-6', '實作題', 'matrix_diagonal_sums 方陣大小邊界與零元素計算', 5, ("matrix_diagonal_sums",),
         lambda g: check_q12(g, history_str)),
        ('13-5-7', '實作題', 'process_testcases_cleanly 多測資獨立乾淨加總', 5, ("process_testcases_cleanly",),
         lambda g: check_q13(g, history_str)),
        ('13-5-7', '實作題', 'process_testcases_cleanly 空測資與邊界狀態隔離', 5, ("process_testcases_cleanly",),
         lambda g: check_q14(g, history_str)),
        ('13-5-8', '實作題', 'find_min_max_difference 全負數測資極值差計算', 5, ("find_min_max_difference",),
         lambda g: check_q15(g, history_str)),
        ('13-5-8', '實作題', 'find_min_max_difference 單一元素與重複值回傳 0', 5, ("find_min_max_difference",),
         lambda g: check_q16(g, history_str)),
        ('13-5-9', '實作題', 'stress_test_validator 對拍全數通過判定 AC', 5, ("stress_test_validator",),
         lambda g: check_q17(g, history_str)),
        ('13-5-9', '實作題', 'stress_test_validator 揪出相異反例精準報告 WA', 5, ("stress_test_validator",),
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
    print(" 📊 《PythAPCS123》單元 13-5：邏輯錯誤（Logic Error）排查與常見 WA 陷阱拆解 —— 自動評分報告")
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
        "unit": "13-5",
        "unit_title": "邏輯錯誤（Logic Error）排查與常見 WA 陷阱拆解",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_5.py",
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
auto_grade_unit_13_5()
