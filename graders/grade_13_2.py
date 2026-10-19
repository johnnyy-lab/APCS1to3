# ==============================================================================
# 🧪 《PythAPCS123》單元 13-2：語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_2.py
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
import keyword
# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_13-2_syntax_errors_and_traceback_decoding.ipynb"

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
    fn = g.get("diagnose_code_phase")
    if not callable(fn):
        return False, "尚未正確實作 diagnose_code_phase 或正常語法未回傳 'SYNTAX_OK'。"
    if callable(fn):
        try:
            r1 = fn("print('Hello Python')")
            r2 = fn("x = 10\ny = 20\nprint(x + y)")
            if r1 == "SYNTAX_OK" and r2 == "SYNTAX_OK":
                return True, "太棒了！合法 Python 程式碼皆精準判定為 SYNTAX_OK！"
        except Exception as e:
            return False, f"執行 diagnose_code_phase 時發生例外: {e}"
    if "SYNTAX_OK" in hist and "diagnose_code_phase" in hist:
        return True, "偵測到合法代碼檢驗通過記錄！"
    return False, "尚未正確實作 diagnose_code_phase 或正常語法未回傳 'SYNTAX_OK'。"

def check_q2(g, hist):
    fn = g.get("diagnose_code_phase")
    if not callable(fn):
        return False, "語法錯誤代碼未能正確回傳 'COMPILE_ERROR'。"
    if callable(fn):
        try:
            r1 = fn("if True\n    print(1)")
            r2 = fn("def foo(:")
            r3 = fn("123 = a")
            if r1 == "COMPILE_ERROR" and r2 == "COMPILE_ERROR" and r3 == "COMPILE_ERROR":
                return True, "太棒了！語法錯誤程式碼精準攔截並回傳 COMPILE_ERROR！"
        except Exception as e:
            return False, f"執行 diagnose_code_phase 時發生例外: {e}"
    if "COMPILE_ERROR" in hist and "diagnose_code_phase" in hist:
        return True, "偵測到語法錯誤攔截檢驗通過記錄！"
    return False, "語法錯誤代碼未能正確回傳 'COMPILE_ERROR'。"

def check_q3(g, hist):
    fn = g.get("is_brackets_balanced")
    if not callable(fn):
        return False, "尚未正確實作 is_brackets_balanced 或對稱括號未能回傳 True。"
    if callable(fn):
        try:
            c1 = fn("(a + b) * [c - d]")
            c2 = fn("{x: [1, (2 + 3)]}")
            c3 = fn("")
            c4 = fn("()[]{}")
            if c1 is True and c2 is True and c3 is True and c4 is True:
                return True, "太棒了！對稱與巢狀平衡括號皆精準判定為 True！"
        except Exception as e:
            return False, f"執行 is_brackets_balanced 時發生例外: {e}"
    if "is_brackets_balanced" in hist and "assert is_brackets_balanced" in hist:
        return True, "偵測到括號平衡檢驗通過記錄！"
    return False, "尚未正確實作 is_brackets_balanced 或對稱括號未能回傳 True。"

def check_q4(g, hist):
    fn = g.get("is_brackets_balanced")
    if not callable(fn):
        return False, "不平衡或交叉錯位括號未能正確判定為 False。"
    if callable(fn):
        try:
            c1 = fn("(a + b]")
            c2 = fn("((())")
            c3 = fn("][")
            c4 = fn("{[(])}")
            if c1 is False and c2 is False and c3 is False and c4 is False:
                return True, "太棒了！未閉合與交叉錯位之不平衡括號皆精準判定為 False！"
        except Exception as e:
            return False, f"執行 is_brackets_balanced 時發生例外: {e}"
    if "is_brackets_balanced" in hist:
        return True, "偵測到括號檢查邏輯！"
    return False, "不平衡或交叉錯位括號未能正確判定為 False。"

def check_q5(g, hist):
    fn = g.get("auto_fix_colons")
    if not callable(fn):
        return False, "尚未正確實作 auto_fix_colons 或末端缺少冒號未能自動補齊。"
    if callable(fn):
        try:
            res_if = fn("if x > 0")
            res_while = fn("    while True")
            res_def = fn("def my_func()")
            res_elif = fn("elif count == 0")
            res_else = fn("else")
            if (res_if.rstrip().endswith(":") and 
                res_while.rstrip().endswith(":") and 
                res_def.rstrip().endswith(":") and
                res_elif.rstrip().endswith(":") and
                res_else.rstrip().endswith(":")):
                return True, "太棒了！控制流程與函式宣告行末缺失冒號皆已自動補正！"
        except Exception as e:
            return False, f"執行 auto_fix_colons 時發生例外: {e}"
    if "auto_fix_colons" in hist:
        return True, "偵測到自動補冒號邏輯！"
    return False, "尚未正確實作 auto_fix_colons 或末端缺少冒號未能自動補齊。"

def check_q6(g, hist):
    fn = g.get("auto_fix_colons")
    if not callable(fn):
        return False, "已有冒號或一般陳述式未保持原貌。"
    if callable(fn):
        try:
            res_already = fn("if x > 0:")
            res_stmt = fn("x = 10")
            res_print = fn("    print('hello')")
            if res_already == "if x > 0:" and res_stmt == "x = 10" and res_print == "    print('hello')":
                return True, "太棒了！既有冒號與一般表達式保持原貌，無重複補正之副作用！"
        except Exception as e:
            return False, f"執行 auto_fix_colons 時發生例外: {e}"
    if "auto_fix_colons" in hist:
        return True, "偵測到無副作用防禦邏輯！"
    return False, "已有冒號或一般陳述式未保持原貌。"

def check_q7(g, hist):
    fn = g.get("safe_quote_string")
    if not callable(fn):
        return False, "尚未正確實作 safe_quote_string 或包覆後字串無法正確 eval() 解碼。"
    if callable(fn):
        try:
            t1 = "Hello 'World'"
            q1 = fn(t1)
            t2 = 'Hello "World"'
            q2 = fn(t2)
            if eval(q1) == t1 and eval(q2) == t2:
                return True, "太棒了！單/雙引號衝突動態切換包覆，eval() 解析 100% 吻合！"
        except Exception as e:
            return False, f"執行 safe_quote_string 時發生例外: {e}"
    if "safe_quote_string" in hist:
        return True, "偵測到安全引號包覆邏輯！"
    return False, "尚未正確實作 safe_quote_string 或包覆後字串無法正確 eval() 解碼。"

def check_q8(g, hist):
    fn = g.get("safe_quote_string")
    if not callable(fn):
        return False, "同時含單雙引號時未能採用三引號安全包覆或 eval() 結果相異。"
    if callable(fn):
        try:
            t_both = 'He said "It\'s fine"'
            q_both = fn(t_both)
            if eval(q_both) == t_both and (q_both.startswith('"""') or q_both.startswith("'''")):
                return True, "太棒了！同時包含單雙引號時成功啟動三引號防禦機制！"
        except Exception as e:
            return False, f"執行 safe_quote_string 時發生例外: {e}"
    if "safe_quote_string" in hist:
        return True, "偵測到三引號安全防禦邏輯！"
    return False, "同時含單雙引號時未能採用三引號安全包覆或 eval() 結果相異。"

def check_q9(g, hist):
    fn = g.get("fill_empty_blocks_with_pass")
    if not callable(fn):
        return False, "尚未正確實作 fill_empty_blocks_with_pass 或修復後未插入 pass。"
    if callable(fn):
        try:
            code = "if x > 0:\nprint(x)"
            fixed = fn(code)
            if "pass" in fixed:
                compile(fixed, "<test_q9>", "exec")
                return True, "太棒了！空區塊成功自動插入 pass 並順利通過編譯！"
        except Exception as e:
            return False, f"執行 fill_empty_blocks_with_pass 時發生例外: {e}"
    if "fill_empty_blocks_with_pass" in hist:
        return True, "偵測到自動填補 pass 邏輯！"
    return False, "尚未正確實作 fill_empty_blocks_with_pass 或修復後未插入 pass。"

def check_q10(g, hist):
    fn = g.get("fill_empty_blocks_with_pass")
    if not callable(fn):
        return False, "包含既有陳述式之區塊修復後編譯失敗。"
    if callable(fn):
        try:
            code = "def foo():\n    if True:\n        pass\n    return 42"
            fixed = fn(code)
            compile(fixed, "<test_q10>", "exec")
            return True, "太棒了！既有合法巢狀結構完整保留且維持合法編譯！"
        except Exception as e:
            return False, f"執行 fill_empty_blocks_with_pass 時發生例外: {e}"
    if "fill_empty_blocks_with_pass" in hist:
        return True, "偵測到合法結構保持邏輯！"
    return False, "包含既有陳述式之區塊修復後編譯失敗。"

def check_q11(g, hist):
    fn = g.get("deep_sanitize_code")
    if not callable(fn):
        return False, "尚未正確實作 deep_sanitize_code 或未能完全消除全形標點。"
    if callable(fn):
        try:
            code = "for　i　in range(5)：\n　　print(i，i+1)"
            cleaned = fn(code)
            if '\u3000' not in cleaned and '：' not in cleaned and '，' not in cleaned:
                if ":" in cleaned and "," in cleaned and " " in cleaned:
                    return True, "太棒了！全形空白、全形冒號與全形逗號全數精準淨化！"
        except Exception as e:
            return False, f"執行 deep_sanitize_code 時發生例外: {e}"
    if "deep_sanitize_code" in hist:
        return True, "偵測到全形字元淨化邏輯！"
    return False, "尚未正確實作 deep_sanitize_code 或未能完全消除全形標點。"

def check_q12(g, hist):
    fn = g.get("deep_sanitize_code")
    if not callable(fn):
        return False, "全形引號或圓括號未完全消除，或淨化後代碼無法編譯。"
    if callable(fn):
        try:
            code = "if x == 10:\n    print（“PASS”，x）"
            cleaned = fn(code)
            if '（' not in cleaned and '）' not in cleaned and '“' not in cleaned and '”' not in cleaned:
                compile("x = 10\n" + cleaned, "<test_q12>", "exec")
                return True, "太棒了！全形引號與圓括號全數淨化且通過實機編譯驗證！"
        except Exception as e:
            return False, f"執行 deep_sanitize_code 時發生例外: {e}"
    if "deep_sanitize_code" in hist:
        return True, "偵測到全形標點淨化與編譯邏輯！"
    return False, "全形引號或圓括號未完全消除，或淨化後代碼無法編譯。"

def check_q13(g, hist):
    fn = g.get("convert_c_increment_to_python")
    if not callable(fn):
        return False, "尚未正確實作 convert_c_increment_to_python 或 i++ 轉譯結果不正確。"
    if callable(fn):
        try:
            r1 = fn("i++")
            r2 = fn("    counter++")
            if r1.strip() == "i += 1" and r2 == "    counter += 1":
                return True, "太棒了！自增運算子 i++ 精準轉譯為 Python i += 1 且縮排完整！"
        except Exception as e:
            return False, f"執行 convert_c_increment_to_python 時發生例外: {e}"
    if "convert_c_increment_to_python" in hist:
        return True, "偵測到自增運算子轉譯邏輯！"
    return False, "尚未正確實作 convert_c_increment_to_python 或 i++ 轉譯結果不正確。"

def check_q14(g, hist):
    fn = g.get("convert_c_increment_to_python")
    if not callable(fn):
        return False, "自減運算子未轉譯或一般語法行被異常修改。"
    if callable(fn):
        try:
            r1 = fn("idx--")
            r2 = fn("        step--")
            r3 = fn("x = 10")
            if r1.strip() == "idx -= 1" and r2 == "        step -= 1" and r3 == "x = 10":
                return True, "太棒了！自減運算子 i-- 成功轉譯為 -= 1，且一般賦值不受影響！"
        except Exception as e:
            return False, f"執行 convert_c_increment_to_python 時發生例外: {e}"
    if "convert_c_increment_to_python" in hist:
        return True, "偵測到自減轉譯與非自減行保護邏輯！"
    return False, "自減運算子未轉譯或一般語法行被異常修改。"

def check_q15(g, hist):
    fn = g.get("is_safe_identifier")
    if not callable(fn):
        return False, "尚未正確實作 is_safe_identifier 或合規命名未能回傳 True。"
    if callable(fn):
        try:
            v1 = fn("score")
            v2 = fn("_total_sum")
            v3 = fn("student_id_99")
            if v1 is True and v2 is True and v3 is True:
                return True, "太棒了！合規英文、底線與混合命名皆正確判定為安全識別字！"
        except Exception as e:
            return False, f"執行 is_safe_identifier 時發生例外: {e}"
    if "is_safe_identifier" in hist:
        return True, "偵測到安全識別字驗證邏輯！"
    return False, "尚未正確實作 is_safe_identifier 或合規命名未能回傳 True。"

def check_q16(g, hist):
    fn = g.get("is_safe_identifier")
    if not callable(fn):
        return False, "Python 關鍵字或非法識別字未能正確判定為 False。"
    if callable(fn):
        try:
            f1 = fn("class")
            f2 = fn("def")
            f3 = fn("for")
            f4 = fn("123abc")
            f5 = fn("my-score")
            if f1 is False and f2 is False and f3 is False and f4 is False and f5 is False:
                return True, "太棒了！Python 保留關鍵字與非法符號開頭皆精準攔截拒絕！"
        except Exception as e:
            return False, f"執行 is_safe_identifier 時發生例外: {e}"
    if "is_safe_identifier" in hist:
        return True, "偵測到保留字攔截邏輯！"
    return False, "Python 關鍵字或非法識別字未能正確判定為 False。"

def check_q17(g, hist):
    fn = g.get("fix_all_syntax_errors")
    if not callable(fn):
        return False, "尚未正確實作 fix_all_syntax_errors 或未能成功修復全形字元與自增。"
    if callable(fn):
        try:
            broken = "while　i < 10：\n　　i++"
            fixed = fn(broken)
            if "i++" not in fixed and "i += 1" in fixed and "：" not in fixed and "\u3000" not in fixed:
                return True, "太棒了！綜合修復器成功粉碎全形冒號、全形空白與 i++ 語法缺陷！"
        except Exception as e:
            return False, f"執行 fix_all_syntax_errors 時發生例外: {e}"
    if "fix_all_syntax_errors" in hist:
        return True, "偵測到綜合語法修復器邏輯！"
    return False, "尚未正確實作 fix_all_syntax_errors 或未能成功修復全形字元與自增。"

def check_q18(g, hist):
    fn = g.get("fix_all_syntax_errors")
    if not callable(fn):
        return False, "if 單等號未修正或綜合修復後程式碼無法通過編譯。"
    if callable(fn):
        try:
            broken = "if　val = 5：\n　　pass\ni++"
            fixed = fn(broken)
            if "==" in fixed and "pass" in fixed:
                compile("val = 5\ni = 0\n" + fixed, "<test_q18>", "exec")
                return True, "太棒了！if 條件單等號成功修復為雙等號，並通過 compile() 實機驗證！"
        except Exception as e:
            return False, f"執行 fix_all_syntax_errors 時發生例外: {e}"
    if "fix_all_syntax_errors" in hist:
        return True, "偵測到綜合修復與實機編譯驗證！"
    return False, "if 單等號未修正或綜合修復後程式碼無法通過編譯。"


def auto_grade_unit_13_2():
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
        ('13-2-1', '實作題', '合法 Python 語法回傳 SYNTAX_OK', 6, ("diagnose_code_phase",),
         lambda g: check_q1(g, history_str)),
        ('13-2-1', '實作題', '語法錯誤精準捕獲回傳 COMPILE_ERROR', 6, ("diagnose_code_phase",),
         lambda g: check_q2(g, history_str)),
        ('13-2-2', '實作題', '括號堆疊對稱匹配平衡檢驗（True）', 6, ("is_brackets_balanced",),
         lambda g: check_q3(g, history_str)),
        ('13-2-2', '實作題', '單邊未閉合與交叉錯位括號檢驗（False）', 6, ("is_brackets_balanced",),
         lambda g: check_q4(g, history_str)),
        ('13-2-3', '實作題', '區塊控制關鍵字尾端缺失冒號自動補正', 6, ("auto_fix_colons",),
         lambda g: check_q5(g, history_str)),
        ('13-2-3', '實作題', '已具備冒號與一般陳述式無副作用保持', 6, ("auto_fix_colons",),
         lambda g: check_q6(g, history_str)),
        ('13-2-4', '實作題', '單雙引號衝突動態安全包覆與 eval 解析', 6, ("safe_quote_string",),
         lambda g: check_q7(g, history_str)),
        ('13-2-4', '實作題', '同時含單雙引號之三引號包覆防禦機制', 6, ("safe_quote_string",),
         lambda g: check_q8(g, history_str)),
        ('13-2-5', '實作題', '未縮排空區塊自動插入 pass 防禦', 6, ("fill_empty_blocks_with_pass",),
         lambda g: check_q9(g, history_str)),
        ('13-2-5', '實作題', '修正後程式碼合法通過 compile() 編譯', 6, ("fill_empty_blocks_with_pass",),
         lambda g: check_q10(g, history_str)),
        ('13-2-6', '實作題', '全形空白、全形冒號與逗號深度淨化', 5, ("deep_sanitize_code",),
         lambda g: check_q11(g, history_str)),
        ('13-2-6', '實作題', '全形中文引號與圓括號淨化並通過編譯', 5, ("deep_sanitize_code",),
         lambda g: check_q12(g, history_str)),
        ('13-2-7', '實作題', 'C 風格自增運算子 i++ 轉譯為 Python i += 1', 5, ("convert_c_increment_to_python",),
         lambda g: check_q13(g, history_str)),
        ('13-2-7', '實作題', 'C 風格自減運算子 i-- 轉譯並完整保留縮排', 5, ("convert_c_increment_to_python",),
         lambda g: check_q14(g, history_str)),
        ('13-2-8', '實作題', '合法識別字雙重檢驗（底線、變數名）', 5, ("is_safe_identifier",),
         lambda g: check_q15(g, history_str)),
        ('13-2-8', '實作題', 'Python 關鍵字與非法開頭排除防禦', 5, ("is_safe_identifier",),
         lambda g: check_q16(g, history_str)),
        ('13-2-9', '實作題', '綜合語法修復：全形字元淨化與運算子轉譯', 5, ("fix_all_syntax_errors",),
         lambda g: check_q17(g, history_str)),
        ('13-2-9', '實作題', '綜合語法修復：條件單等號修復與實機編譯', 5, ("fix_all_syntax_errors",),
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
    print(" 📊 《PythAPCS123》單元 13-2：語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法 —— 自動評分報告")
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
        "unit": "13-2",
        "unit_title": "語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_2.py",
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
auto_grade_unit_13_2()
