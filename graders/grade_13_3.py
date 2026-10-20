# ==============================================================================
# 🧪 《PythAPCS123》單元 13-3：執行時期錯誤（Runtime Error, RE）常見排行榜與崩潰防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_3.py
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
NOTEBOOK_FILE = "PythAPCS123_13-3_runtime_errors_ranking_and_defense.ipynb"

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
    fn = g.get("safe_execute_and_diagnose")
    if not callable(fn):
        return False, "尚未正確實作 safe_execute_and_diagnose 或正常回傳值不符。"
    if callable(fn):
        try:
            r1 = fn(lambda x: x + 10, 5)
            r2 = fn(lambda a, b: a * b, 3, 4)
            if r1 == ("SUCCESS", 15) and r2 == ("SUCCESS", 12):
                return True, "太棒了！安全執行成功且精準回傳 ('SUCCESS', 運算結果)！"
        except Exception as e:
            return False, f"執行 safe_execute_and_diagnose 時發生例外: {e}"
    if "safe_execute_and_diagnose" in hist and '"SUCCESS"' in hist:
        return True, "偵測到安全診斷成功執行記錄！"
    return False, "尚未正確實作 safe_execute_and_diagnose 或正常回傳值不符。"

def check_q2(g, hist):
    fn = g.get("safe_execute_and_diagnose")
    if not callable(fn):
        return False, "發生崩潰時未能正確回傳 ('RE', 例外型別)。"
    if callable(fn):
        try:
            r1 = fn(lambda a, b: a / b, 10, 0)
            r2 = fn(lambda lst, i: lst[i], [1, 2], 99)
            r3 = fn(lambda s: int(s), "not_a_number")
            if (r1 == ("RE", "ZeroDivisionError") and 
                r2 == ("RE", "IndexError") and 
                r3 == ("RE", "ValueError")):
                return True, "太棒了！中途例外精準捕獲並回傳 ('RE', 例外型別名稱)！"
        except Exception as e:
            return False, f"執行 safe_execute_and_diagnose 時發生例外: {e}"
    if "safe_execute_and_diagnose" in hist and '"RE"' in hist:
        return True, "偵測到例外捕獲與診斷邏輯！"
    return False, "發生崩潰時未能正確回傳 ('RE', 例外型別)。"

def check_q3(g, hist):
    fn = g.get("safe_get")
    if not callable(fn):
        return False, "尚未正確實作 safe_get 或正負邊界未妥善處理。"
    if callable(fn):
        try:
            lst = [10, 20, 30]
            if (fn(lst, 0) == 10 and 
                fn(lst, 2) == 30 and 
                fn(lst, 3) is None and 
                fn(lst, -1) == 30 and 
                fn(lst, -4, 999) == 999 and 
                fn([], 0, "EMPTY") == "EMPTY"):
                return True, "太棒了！正負索引與越界預設值防禦皆 100% 正確！"
        except Exception as e:
            return False, f"執行 safe_get 時發生例外: {e}"
    if "safe_get" in hist:
        return True, "偵測到 safe_get 越界防禦邏輯！"
    return False, "尚未正確實作 safe_get 或正負邊界未妥善處理。"

def check_q4(g, hist):
    fn = g.get("safe_adjacent_diffs")
    if not callable(fn):
        return False, "尚未正確實作 safe_adjacent_diffs 或邊界防守不完善。"
    if callable(fn):
        try:
            r1 = fn([10, 20, 35])
            r2 = fn([5])
            r3 = fn([])
            if r1 == [10, 15] and r2 == [] and r3 == []:
                return True, "太棒了！相鄰差值計算準確且長度不足 2 時安全回傳空串列！"
        except Exception as e:
            return False, f"執行 safe_adjacent_diffs 時發生例外: {e}"
    if "safe_adjacent_diffs" in hist:
        return True, "偵測到相鄰差值安全計算邏輯！"
    return False, "尚未正確實作 safe_adjacent_diffs 或邊界防守不完善。"

def check_q5(g, hist):
    fn = g.get("safe_parse_int")
    if not callable(fn):
        return False, "尚未正確實作 safe_parse_int 或非法字串未回傳 default。"
    if callable(fn):
        try:
            c1 = fn("100") == 100
            c2 = fn("  -50  ") == -50
            c3 = fn("3.99") == 3
            c4 = fn("invalid", 0) == 0
            c5 = fn("", -999) == -999
            if c1 and c2 and c3 and c4 and c5:
                return True, "太棒了！整數、空白字串、浮點字串與非法輸入剖析完全正確！"
        except Exception as e:
            return False, f"執行 safe_parse_int 時發生例外: {e}"
    if "safe_parse_int" in hist:
        return True, "偵測到 safe_parse_int 數值防禦邏輯！"
    return False, "尚未正確實作 safe_parse_int 或非法字串未回傳 default。"

def check_q6(g, hist):
    fn = g.get("safe_find_index")
    if not callable(fn):
        return False, "尚未正確實作 safe_find_index 或查無元素時未回傳 -1。"
    if callable(fn):
        try:
            r1 = fn(["apple", "banana"], "banana")
            r2 = fn(["apple", "banana"], "cherry")
            r3 = fn([], "apple")
            if r1 == 1 and r2 == -1 and r3 == -1:
                return True, "太棒了！元素存在回傳正確索引，不存在安全回傳 -1！"
        except Exception as e:
            return False, f"執行 safe_find_index 時發生例外: {e}"
    if "safe_find_index" in hist:
        return True, "偵測到 safe_find_index 查找邏輯！"
    return False, "尚未正確實作 safe_find_index 或查無元素時未回傳 -1。"

def check_q7(g, hist):
    fn = g.get("safe_count_frequencies")
    if not callable(fn):
        return False, "尚未正確實作 safe_count_frequencies 或空清單處理有誤。"
    if callable(fn):
        try:
            r1 = fn(["a", "b", "a", "c", "b", "a"])
            r2 = fn([])
            if r1 == {"a": 3, "b": 2, "c": 1} and r2 == {}:
                return True, "太棒了！字頻統計安全累加，完全免疫 KeyError！"
        except Exception as e:
            return False, f"執行 safe_count_frequencies 時發生例外: {e}"
    if "safe_count_frequencies" in hist:
        return True, "偵測到字頻統計安全邏輯！"
    return False, "尚未正確實作 safe_count_frequencies 或空清單處理有誤。"

def check_q8(g, hist):
    fn = g.get("safe_query_user")
    if not callable(fn):
        return False, "尚未正確實作 safe_query_user 或預設值防禦未生效。"
    if callable(fn):
        try:
            db = {"alice": "manager", "bob": "staff"}
            if (fn(db, "alice") == "manager" and 
                fn(db, "nobody") == "guest" and 
                fn(db, "nobody", "anon") == "anon"):
                return True, "太棒了！字典安全查詢與自訂預設值防禦 100% 正確！"
        except Exception as e:
            return False, f"執行 safe_query_user 時發生例外: {e}"
    if "safe_query_user" in hist:
        return True, "偵測到 safe_query_user 字典防禦邏輯！"
    return False, "尚未正確實作 safe_query_user 或預設值防禦未生效。"

def check_q9(g, hist):
    fn = g.get("safe_divide")
    if not callable(fn):
        return False, "尚未正確實作 safe_divide 或分母為零時未回傳 default。"
    if callable(fn):
        try:
            if (fn(15, 3) == 5.0 and 
                fn(10, 0) == 0.0 and 
                fn(10, 0, -1.0) == -1.0):
                return True, "太棒了！安全除法正常運算與除以零 default 防禦完全正確！"
        except Exception as e:
            return False, f"執行 safe_divide 時發生例外: {e}"
    if "safe_divide" in hist:
        return True, "偵測到 safe_divide 除法守門員！"
    return False, "尚未正確實作 safe_divide 或分母為零時未回傳 default。"

def check_q10(g, hist):
    fn = g.get("safe_modulo")
    if not callable(fn):
        return False, "尚未正確實作 safe_modulo 或模除零未回傳 default。"
    if callable(fn):
        try:
            if (fn(17, 5) == 2 and 
                fn(10, 0) == -1 and 
                fn(10, 0, 999) == 999):
                return True, "太棒了！安全模除正常運算與除數為零 default 防禦完全正確！"
        except Exception as e:
            return False, f"執行 safe_modulo 時發生例外: {e}"
    if "safe_modulo" in hist:
        return True, "偵測到 safe_modulo 模除防禦邏輯！"
    return False, "尚未正確實作 safe_modulo 或模除零未回傳 default。"

def check_q11(g, hist):
    fn = g.get("safe_format_key_value")
    if not callable(fn):
        return False, "尚未正確實作 safe_format_key_value 或 NoneType 格式化失敗。"
    if callable(fn):
        try:
            if (fn("age", 18) == "age = 18" and 
                fn("flag", True) == "flag = True" and 
                fn("item", None) == "item = None"):
                return True, "太棒了！數字、布林與 None 等異質型態字串拼接安全格式化！"
        except Exception as e:
            return False, f"執行 safe_format_key_value 時發生例外: {e}"
    if "safe_format_key_value" in hist:
        return True, "偵測到 safe_format_key_value 安全格式化邏輯！"
    return False, "尚未正確實作 safe_format_key_value 或 NoneType 格式化失敗。"

def check_q12(g, hist):
    fn = g.get("safe_sort_numbers")
    if not callable(fn):
        return False, "尚未正確實作 safe_sort_numbers 或污染了原始串列。"
    if callable(fn):
        try:
            orig = [9, 3, 7]
            res = fn(orig)
            if res == [3, 7, 9] and orig == [9, 3, 7] and res is not orig:
                return True, "太棒了！回傳新排序串列且原始串列內容完整保留未受污染！"
        except Exception as e:
            return False, f"執行 safe_sort_numbers 時發生例外: {e}"
    if "safe_sort_numbers" in hist:
        return True, "偵測到 safe_sort_numbers 排序防禦邏輯！"
    return False, "尚未正確實作 safe_sort_numbers 或污染了原始串列。"

def check_q13(g, hist):
    fn = g.get("safe_factorial")
    if not callable(fn):
        return False, "尚未正確實作 safe_factorial 或面對大數引發例外。"
    if callable(fn):
        try:
            c1 = fn(0) == 1
            c2 = fn(1) == 1
            c3 = fn(6) == 720
            c4 = fn(1200) > 0 # 大數測試不引發 RecursionError
            if c1 and c2 and c3 and c4:
                return True, "太棒了！大數階乘使用迭代演算法抗爆棧，RecursionError 徹底歸零！"
        except Exception as e:
            return False, f"執行 safe_factorial 時發生例外: {e}"
    if "safe_factorial" in hist:
        return True, "偵測到迭代階乘防禦邏輯！"
    return False, "尚未正確實作 safe_factorial 或面對大數引發例外。"

def check_q14(g, hist):
    fn = g.get("safe_fibonacci")
    if not callable(fn):
        return False, "尚未正確實作 safe_fibonacci 或大數計算有誤。"
    if callable(fn):
        try:
            c1 = fn(0) == 0
            c2 = fn(1) == 1
            c3 = fn(7) == 13
            c4 = fn(100) == 354224848179261915075
            if c1 and c2 and c3 and c4:
                return True, "太棒了！費氏數列常數空間迭代實作，杜絕堆疊溢出與超時！"
        except Exception as e:
            return False, f"執行 safe_fibonacci 時發生例外: {e}"
    if "safe_fibonacci" in hist:
        return True, "偵測到迭代費氏數列防禦邏輯！"
    return False, "尚未正確實作 safe_fibonacci 或大數計算有誤。"

def check_q15(g, hist):
    fn = g.get("safe_append_or_concat")
    if not callable(fn):
        return False, "尚未正確實作 safe_append_or_concat 或不支援型態未回傳 None。"
    if callable(fn):
        try:
            l = [10, 20]
            r1 = fn(l, 30)
            r2 = fn("Hello", " World")
            r3 = fn("Num: ", 42)
            r4 = fn({"a": 1}, "b")
            if r1 == [10, 20, 30] and r2 == "Hello World" and r3 == "Num: 42" and r4 is None:
                return True, "太棒了！型態相容分支判斷完全正確，徹底免疫 AttributeError！"
        except Exception as e:
            return False, f"執行 safe_append_or_concat 時發生例外: {e}"
    if "safe_append_or_concat" in hist:
        return True, "偵測到型態相容處理邏輯！"
    return False, "尚未正確實作 safe_append_or_concat 或不支援型態未回傳 None。"

def check_q16(g, hist):
    fn = g.get("safe_accumulator")
    if not callable(fn):
        return False, "尚未正確實作 safe_accumulator。"
    if callable(fn):
        try:
            r1 = fn([1, 2, 3, 4], 0)
            r2 = fn([], 100)
            if r1 == 10 and r2 == 100:
                return True, "太棒了！純區域變數累加計算準確，完全杜絕 UnboundLocalError 作用域陷阱！"
        except Exception as e:
            return False, f"執行 safe_accumulator 時發生例外: {e}"
    if "safe_accumulator" in hist:
        return True, "偵測到安全累加器邏輯！"
    return False, "尚未正確實作 safe_accumulator。"

def check_q17(g, hist):
    fn = g.get("bulletproof_data_pipeline")
    if not callable(fn):
        return False, "尚未正確實作 bulletproof_data_pipeline 或清洗指標結果不符。"
    if callable(fn):
        try:
            dirty_data = [
                "A,15,80",
                "B,16,90",
                "C,invalid,100",
                "D,15,invalid",
                "E,15",
                "   ",
                "F,17,100"
            ]
            res = fn(dirty_data)
            if (isinstance(res, dict) and 
                res.get("valid_count") == 3 and 
                res.get("average_score") == 90.0 and 
                res.get("max_score") == 100):
                return True, "太棒了！髒資料清洗完整防禦 IndexError 與 ValueError，各項指標完全精準！"
        except Exception as e:
            return False, f"執行 bulletproof_data_pipeline 時發生例外: {e}"
    if "bulletproof_data_pipeline" in hist:
        return True, "偵測到綜合強固資料管線邏輯！"
    return False, "尚未正確實作 bulletproof_data_pipeline 或清洗指標結果不符。"

def check_q18(g, hist):
    fn = g.get("bulletproof_data_pipeline")
    if not callable(fn):
        return False, "面對空資料或全無效資料時引發例外或回傳值不符。"
    if callable(fn):
        try:
            r_empty = fn([])
            r_trash = fn(["garbage", ",,,", "a,b,c"])
            expected = {"valid_count": 0, "average_score": 0.0, "max_score": 0}
            if r_empty == expected and r_trash == expected:
                return True, "太棒了！空串列與全垃圾輸入極端測試安全防禦，絕不觸發 ZeroDivisionError！"
        except Exception as e:
            return False, f"執行 bulletproof_data_pipeline 時發生例外: {e}"
    if "bulletproof_data_pipeline" in hist:
        return True, "偵測到空輸入防禦邏輯！"
    return False, "面對空資料或全無效資料時引發例外或回傳值不符。"


def auto_grade_unit_13_3(env=None):
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
        ('13-3-1', '實作題', "安全執行成功回傳 ('SUCCESS', res)", 6, ("safe_execute_and_diagnose",),
         lambda g: check_q1(g, history_str)),
        ('13-3-1', '實作題', "精準捕獲中途例外回傳 ('RE', 例外型別)", 6, ("safe_execute_and_diagnose",),
         lambda g: check_q2(g, history_str)),
        ('13-3-2', '實作題', 'safe_get 支援正負索引與越界 default 防禦', 6, ("safe_get",),
         lambda g: check_q3(g, history_str)),
        ('13-3-2', '實作題', 'safe_adjacent_diffs 相鄰差值與邊界安全防禦', 6, ("safe_adjacent_diffs",),
         lambda g: check_q4(g, history_str)),
        ('13-3-3', '實作題', 'safe_parse_int 整數/浮點字串安全剖析', 6, ("safe_parse_int",),
         lambda g: check_q5(g, history_str)),
        ('13-3-3', '實作題', 'safe_find_index 元素索引查找與安全回傳 -1', 6, ("safe_find_index",),
         lambda g: check_q6(g, history_str)),
        ('13-3-4', '實作題', 'safe_count_frequencies 字頻統計抗 KeyError', 6, ("safe_count_frequencies",),
         lambda g: check_q7(g, history_str)),
        ('13-3-4', '實作題', 'safe_query_user 字典安全查詢與預設值防禦', 6, ("safe_query_user",),
         lambda g: check_q8(g, history_str)),
        ('13-3-5', '實作題', 'safe_divide 正常除法與除以零安全回傳', 6, ("safe_divide",),
         lambda g: check_q9(g, history_str)),
        ('13-3-5', '實作題', 'safe_modulo 正常取模與模除零安全防禦', 6, ("safe_modulo",),
         lambda g: check_q10(g, history_str)),
        ('13-3-6', '實作題', 'safe_format_key_value 異質型態安全字串格式化', 5, ("safe_format_key_value",),
         lambda g: check_q11(g, history_str)),
        ('13-3-6', '實作題', 'safe_sort_numbers 升序排序且不污染原串列', 5, ("safe_sort_numbers",),
         lambda g: check_q12(g, history_str)),
        ('13-3-7', '實作題', 'safe_factorial 大數階乘迭代實作抗爆棧', 5, ("safe_factorial",),
         lambda g: check_q13(g, history_str)),
        ('13-3-7', '實作題', 'safe_fibonacci 費氏數列迭代防禦堆疊溢出', 5, ("safe_fibonacci",),
         lambda g: check_q14(g, history_str)),
        ('13-3-8', '實作題', 'safe_append_or_concat 串列與字串型態分支防禦', 5, ("safe_append_or_concat",),
         lambda g: check_q15(g, history_str)),
        ('13-3-8', '實作題', 'safe_accumulator 純區域變數累加杜絕作用域污染', 5, ("safe_accumulator",),
         lambda g: check_q16(g, history_str)),
        ('13-3-9', '實作題', 'bulletproof_data_pipeline 髒資料清洗與指標計算', 5, ("bulletproof_data_pipeline",),
         lambda g: check_q17(g, history_str)),
        ('13-3-9', '實作題', 'bulletproof_data_pipeline 空輸入與全垃圾極端防禦', 5, ("bulletproof_data_pipeline",),
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
    print(" 📊 《PythAPCS123》單元 13-3：執行時期錯誤（Runtime Error, RE）常見排行榜與崩潰防禦 —— 自動評分報告")
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
        "unit": "13-3",
        "unit_title": "執行時期錯誤（Runtime Error, RE）常見排行榜與崩潰防禦",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_3.py",
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
auto_grade_unit_13_3()
