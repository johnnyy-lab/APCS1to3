# ==============================================================================
# 🧪 《PythAPCS123》單元 13-8：系統化除錯法與考場送出前自主檢核清單（Checklist） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_8.py
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
import io
# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_13-8_systematic_debugging_and_pre_submission_checklist.ipynb"

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
    fn = g.get("reverse_sublist")
    if not callable(fn):
        return False, "尚未正確實作 reverse_sublist 或反轉結果不符。"
    if callable(fn):
        try:
            r = fn([1, 2, 3, 4, 5], 1, 3)
            if r == [1, 4, 3, 2, 5]:
                return True, "太棒了！指定子區間精準反轉且前後綴完整保留！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到區間反轉邏輯！"
    return False, "尚未正確實作 reverse_sublist 或反轉結果不符。"

def check_q2(g, hist):
    fn = g.get("reverse_sublist")
    if not callable(fn):
        return False, "全區間或單元素反轉失敗。"
    if callable(fn):
        try:
            r1 = fn([1, 2, 3], 0, 2)
            r2 = fn([10], 0, 0)
            if r1 == [3, 2, 1] and r2 == [10]:
                return True, "太棒了！全區間反轉與單元素微型測資驗證無誤！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到微型邊界反轉邏輯！"
    return False, "全區間或單元素反轉失敗。"

def check_q3(g, hist):
    fn = g.get("reverse_sublist")
    if not callable(fn):
        return False, "兩元素反轉不符。"
    if callable(fn):
        try:
            if fn([1, 2], 0, 1) == [2, 1]:
                return True, "太棒了！兩元素邊界反轉正確無誤！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到兩元素反轉！"
    return False, "兩元素反轉不符。"

def check_q4(g, hist):
    fn = g.get("safe_pipeline_executor")
    if not callable(fn):
        return False, "尚未正確實作 safe_pipeline_executor 或平均值不符。"
    if callable(fn):
        try:
            if fn(["10", "20", "30"]) == 20.0:
                return True, "太棒了！字串轉整數並精準計算浮點平均值 20.0！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到管線平均計算邏輯！"
    return False, "尚未正確實作 safe_pipeline_executor 或平均值不符。"

def check_q5(g, hist):
    fn = g.get("safe_pipeline_executor")
    if not callable(fn):
        return False, "非數字字串過濾有誤。"
    if callable(fn):
        try:
            if fn(["5", "invalid", "15"]) == 10.0:
                return True, "太棒了！自動過濾非數字文字，維持正常數據運算！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到非數字安全過濾邏輯！"
    return False, "非數字字串過濾有誤。"

def check_q6(g, hist):
    fn = g.get("safe_pipeline_executor")
    if not callable(fn):
        return False, "空資料未回傳 0.0。"
    if callable(fn):
        try:
            if fn([]) == 0.0 and fn(["abc", "xyz"]) == 0.0:
                return True, "太棒了！空串列與全無效字串安全回傳 0.0，杜絕除以零崩潰！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到空資料防禦邏輯！"
    return False, "空資料未回傳 0.0。"

def check_q7(g, hist):
    fn = g.get("binary_search_with_logs")
    if not callable(fn):
        return False, "尚未正確實作 binary_search_with_logs 或索引不符。"
    if callable(fn):
        try:
            pos, logs = fn([1, 3, 5, 7, 9], 7)
            if pos == 3:
                return True, "太棒了！二分搜尋正確定位目標值索引 3！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist:
        return True, "偵測到二分搜尋回傳邏輯！"
    return False, "尚未正確實作 binary_search_with_logs 或索引不符。"

def check_q8(g, hist):
    fn = g.get("binary_search_with_logs")
    if not callable(fn):
        return False, "日誌歷程格式不符或未包含 [DEBUG]。"
    if callable(fn):
        try:
            _, logs = fn([1, 3, 5, 7, 9], 7)
            if len(logs) >= 1 and logs[0].startswith("[DEBUG]") and "num=" in logs[0]:
                return True, "太棒了！搜尋歷程正確記錄 [DEBUG] 標籤且包含變數細節！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist and "[DEBUG]" in hist:
        return True, "偵測到 [DEBUG] 日誌格式邏輯！"
    return False, "日誌歷程格式不符或未包含 [DEBUG]。"

def check_q9(g, hist):
    fn = g.get("binary_search_with_logs")
    if not callable(fn):
        return False, "查無目標時未回傳 -1。"
    if callable(fn):
        try:
            pos_nf, logs_nf = fn([1, 2, 3], 99)
            if pos_nf == -1 and len(logs_nf) >= 1:
                return True, "太棒了！查無目標時安全回傳 -1 與完整搜尋日誌！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist:
        return True, "偵測到查無目標防禦！"
    return False, "查無目標時未回傳 -1。"

def check_q10(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if not callable(fn):
        return False, "尚未正確實作 divide_and_assert_invariant 或商餘不符。"
    if callable(fn):
        try:
            if fn(10, 3) == (3, 1) and fn(29, 6) == (4, 5):
                return True, "太棒了！整數除法商與餘數計算精準，滿足除法不變量！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist:
        return True, "偵測到商餘計算邏輯！"
    return False, "尚未正確實作 divide_and_assert_invariant 或商餘不符。"

def check_q11(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if not callable(fn):
        return False, "整除或負數除法斷言失敗。"
    if callable(fn):
        try:
            if fn(20, 5) == (4, 0) and fn(-15, 4) == (-4, 1):
                return True, "太棒了！整除情境與負數除法商餘計算均正確斷言通過！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist:
        return True, "偵測到整除斷言通過！"
    return False, "整除或負數除法斷言失敗。"

def check_q12(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if not callable(fn):
        return False, "除數為 0 時未能引爆 AssertionError。"
    if callable(fn):
        try:
            threw = False
            try:
                fn(10, 0)
            except AssertionError:
                threw = True
            except Exception:
                pass
            if threw:
                return True, "太棒了！除數為 0 時精準由 assert 攔截觸發 AssertionError！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist and "assert" in hist:
        return True, "偵測到除以零斷言邏輯！"
    return False, "除數為 0 時未能引爆 AssertionError。"

def check_q13(g, hist):
    fn = g.get("find_top_two")
    if not callable(fn):
        return False, "尚未正確實作 find_top_two 或回傳值不符。"
    if callable(fn):
        try:
            if fn([1, 2, 3, 4]) == (4, 3) and fn([10, 5, 20, 15]) == (20, 15):
                return True, "太棒了！正整數串列前兩大不重複值查找完全精準！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到前兩大極值查找邏輯！"
    return False, "尚未正確實作 find_top_two 或回傳值不符。"

def check_q14(g, hist):
    fn = g.get("find_top_two")
    if not callable(fn):
        return False, "全負數輸入查找失敗。"
    if callable(fn):
        try:
            if fn([-5, -1, -10]) == (-1, -5) and fn([-5, -10, -3]) == (-3, -5):
                return True, "太棒了！全負數極端測資前兩大負數查找完全正確！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到全負數極值查找邏輯！"
    return False, "全負數輸入查找失敗。"

def check_q15(g, hist):
    fn = g.get("find_top_two")
    if not callable(fn):
        return False, "元素不足或全相同時未回傳 None。"
    if callable(fn):
        try:
            if fn([7, 7, 7]) is None and fn([99]) is None and fn([]) is None:
                return True, "太棒了！全相同數字、單一元素與空串列安全回傳 None！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到無解安全回傳 None 邏輯！"
    return False, "元素不足或全相同時未回傳 None。"

def check_q16(g, hist):
    fn = g.get("apcs_standard_solution")
    if not callable(fn):
        return False, "尚未正確實作 apcs_standard_solution 或輸出不符。"
    if callable(fn):
        try:
            test_in = "4\n3 6 9 12\n"
            expc138 = "12\n4\n"
            if fn(test_in) == expc138:
                return True, "太棒了！標準兩行輸出最大整數與能被 3 整除之個數完全正確！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到 APCS 標準解題輸出邏輯！"
    return False, "尚未正確實作 apcs_standard_solution 或輸出不符。"

def check_q17(g, hist):
    fn = g.get("apcs_standard_solution")
    if not callable(fn):
        return False, "全負數測資輸出結果不符。"
    if callable(fn):
        try:
            test_neg = "3\n-9 -3 -6\n"
            expc_neg = "-3\n3\n"
            if fn(test_neg) == expc_neg:
                return True, "太棒了！全負數測資最大值 -3 與整除個數 3 格式對齊完全無瑕！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到全負數標準輸出邏輯！"
    return False, "全負數測資輸出結果不符。"

def check_q18(g, hist):
    fn = g.get("apcs_standard_solution")
    if not callable(fn):
        return False, "輸出內容包含多餘行數或污染文字。"
    if callable(fn):
        try:
            test_mix = "5\n10 15 20 33 7\n"
            out = fn(test_mix)
            lines = out.strip().split("\n")
            if len(lines) == 2 and lines[0] == "33" and lines[1] == "2":
                return True, "太棒了！純淨標準輸出，無任何提示文字或 debug print 污染！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到純淨標準輸出檢查！"
    return False, "輸出內容包含多餘行數或污染文字。"


def auto_grade_unit_13_8(env=None):
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
        ('13-8-1', '實作題', 'reverse_sublist 指定區間反轉且前後綴保持', 6, ("reverse_sublist",),
         lambda g: check_q1(g, history_str)),
        ('13-8-1', '實作題', 'reverse_sublist 全區間與單元素微型測資驗證', 6, ("reverse_sublist",),
         lambda g: check_q2(g, history_str)),
        ('13-8-1', '實作題', 'reverse_sublist 兩元素邊界反轉正確無誤', 5, ("reverse_sublist",),
         lambda g: check_q3(g, history_str)),
        ('13-8-2', '實作題', 'safe_pipeline_executor 正常數值過濾與平均計算', 6, ("safe_pipeline_executor",),
         lambda g: check_q4(g, history_str)),
        ('13-8-2', '實作題', 'safe_pipeline_executor 混入非數字安全過濾防禦', 6, ("safe_pipeline_executor",),
         lambda g: check_q5(g, history_str)),
        ('13-8-2', '實作題', 'safe_pipeline_executor 空資料安全回傳 0.0 防禦除零', 5, ("safe_pipeline_executor",),
         lambda g: check_q6(g, history_str)),
        ('13-8-3', '實作題', 'binary_search_with_logs 二分搜尋正確回傳目標索引', 6, ("binary_search_with_logs",),
         lambda g: check_q7(g, history_str)),
        ('13-8-3', '實作題', 'binary_search_with_logs 歷程完整包含 [DEBUG] 標籤日誌', 6, ("binary_search_with_logs",),
         lambda g: check_q8(g, history_str)),
        ('13-8-3', '實作題', 'binary_search_with_logs 查無目標回傳 -1 與日誌', 5, ("binary_search_with_logs",),
         lambda g: check_q9(g, history_str)),
        ('13-8-4', '實作題', 'divide_and_assert_invariant 商餘計算滿足除法不變量', 6, ("divide_and_assert_invariant",),
         lambda g: check_q10(g, history_str)),
        ('13-8-4', '實作題', 'divide_and_assert_invariant 整除餘數為 0 斷言驗證', 6, ("divide_and_assert_invariant",),
         lambda g: check_q11(g, history_str)),
        ('13-8-4', '實作題', 'divide_and_assert_invariant 除數為 0 觸發 AssertionError', 5, ("divide_and_assert_invariant",),
         lambda g: check_q12(g, history_str)),
        ('13-8-5', '實作題', 'find_top_two 正整數串列前兩大不重複值查找', 6, ("find_top_two",),
         lambda g: check_q13(g, history_str)),
        ('13-8-5', '實作題', 'find_top_two 全負數極端測資前兩大負數查找', 5, ("find_top_two",),
         lambda g: check_q14(g, history_str)),
        ('13-8-5', '實作題', 'find_top_two 全相同或元素不足安全回傳 None', 5, ("find_top_two",),
         lambda g: check_q15(g, history_str)),
        ('13-8-6', '實作題', 'apcs_standard_solution 最大值與 3 的倍數個數計算', 6, ("apcs_standard_solution",),
         lambda g: check_q16(g, history_str)),
        ('13-8-6', '實作題', 'apcs_standard_solution 全負數輸入精確對齊換行格式', 5, ("apcs_standard_solution",),
         lambda g: check_q17(g, history_str)),
        ('13-8-6', '實作題', 'apcs_standard_solution 純淨標準 I/O 無殘留提示與除錯', 5, ("apcs_standard_solution",),
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
    print(" 📊 《PythAPCS123》單元 13-8：系統化除錯法與考場送出前自主檢核清單（Checklist） —— 自動評分報告")
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
        "unit": "13-8",
        "unit_title": "系統化除錯法與考場送出前自主檢核清單（Checklist）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_8.py",
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
auto_grade_unit_13_8()
