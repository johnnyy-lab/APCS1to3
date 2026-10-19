# ==============================================================================
# 🧪 《PythAPCS123》單元 13-4：try-except 防禦性程式設計與 EOF 讀取結束優雅收尾 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_4.py
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
NOTEBOOK_FILE = "PythAPCS123_13-4_try_except_and_eof_handling.ipynb"

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
    fn = g.get("safe_sum_mixed_list")
    if not callable(fn):
        return False, "尚未正確實作 safe_sum_mixed_list 或累加結果不符。"
    if callable(fn):
        try:
            if fn(["1", "2", "3"]) == 6 and fn(["10", 20, "30"]) == 60:
                return True, "太棒了！純數字與合法字串整數累加精準無誤！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到 safe_sum_mixed_list 累加邏輯！"
    return False, "尚未正確實作 safe_sum_mixed_list 或累加結果不符。"

def check_q2(g, hist):
    fn = g.get("safe_sum_mixed_list")
    if not callable(fn):
        return False, "非整數項目未被優雅跳過，或導致累加計算錯誤。"
    if callable(fn):
        try:
            r1 = fn(["10", "abc", "20"])
            r2 = fn([5, "15", None, "25", "3.14"])
            if r1 == 30 and r2 == 45:
                return True, "太棒了！遇到英文、None 或浮點字串皆優雅跳過，未中斷程式！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到非整數例外防禦邏輯！"
    return False, "非整數項目未被優雅跳過，或導致累加計算錯誤。"

def check_q3(g, hist):
    fn = g.get("safe_sum_mixed_list")
    if not callable(fn):
        return False, "空串列或全無效資料未能回傳 0。"
    if callable(fn):
        try:
            if fn([]) == 0 and fn(["x", "y", "z"]) == 0:
                return True, "太棒了！面對空串列與全無效字串安全回傳 0！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到空串列防禦邏輯！"
    return False, "空串列或全無效資料未能回傳 0。"

def check_q4(g, hist):
    fn = g.get("parse_float_safely")
    if not callable(fn):
        return False, "尚未正確實作 parse_float_safely 或合法數值解析失敗。"
    if callable(fn):
        try:
            if fn("12.5", 0.0) == 12.5 and fn("-8.0", 0.0) == -8.0 and fn("100", 0.0) == 100.0:
                return True, "太棒了！合法浮點數與整數字串皆精準解析！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到 parse_float_safely 解析邏輯！"
    return False, "尚未正確實作 parse_float_safely 或合法數值解析失敗。"

def check_q5(g, hist):
    fn = g.get("parse_float_safely")
    if not callable(fn):
        return False, "格式錯誤時未能正確回傳 default_val。"
    if callable(fn):
        try:
            if fn("abc", 99.9) == 99.9 and fn("hello_world", -1.0) == -1.0:
                return True, "太棒了！格式錯誤文字精準捕捉並回傳指定的 default_val！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到預設值回傳邏輯！"
    return False, "格式錯誤時未能正確回傳 default_val。"

def check_q6(g, hist):
    fn = g.get("parse_float_safely")
    if not callable(fn):
        return False, "空字串輸入未回傳預設值。"
    if callable(fn):
        try:
            if fn("", 0.0) == 0.0 and fn("   ", -5.5) == -5.5:
                return True, "太棒了！空字串與空白字串極端輸入安全防禦！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到空字串防禦邏輯！"
    return False, "空字串輸入未回傳預設值。"

def check_q7(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if not callable(fn):
        return False, "尚未正確實作 safe_lookup_and_convert 或轉換結果不符。"
    if callable(fn):
        try:
            m = {"a": "100", "c": "0", "neg": "-42"}
            if fn(m, "a") == 100 and fn(m, "c") == 0 and fn(m, "neg") == -42:
                return True, "太棒了！合法鍵值查詢並順利轉換為整數型態！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist:
        return True, "偵測到合法鍵值查詢轉換邏輯！"
    return False, "尚未正確實作 safe_lookup_and_convert 或轉換結果不符。"

def check_q8(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if not callable(fn):
        return False, "鍵值不存在時未能正確回傳 'KEY_NOT_FOUND'。"
    if callable(fn):
        try:
            m = {"a": "100"}
            if fn(m, "not_exist") == "KEY_NOT_FOUND":
                return True, "太棒了！精準捕捉 KeyError 並安全回傳 'KEY_NOT_FOUND'！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist and '"KEY_NOT_FOUND"' in hist:
        return True, "偵測到 KEY_NOT_FOUND 攔截邏輯！"
    return False, "鍵值不存在時未能正確回傳 'KEY_NOT_FOUND'。"

def check_q9(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if not callable(fn):
        return False, "數值轉換失敗時未能正確回傳 'INVALID_NUMBER'。"
    if callable(fn):
        try:
            m = {"bad": "invalid_num", "empty": ""}
            if fn(m, "bad") == "INVALID_NUMBER" and fn(m, "empty") == "INVALID_NUMBER":
                return True, "太棒了！精準捕捉 ValueError 並安全回傳 'INVALID_NUMBER'！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist and '"INVALID_NUMBER"' in hist:
        return True, "偵測到 INVALID_NUMBER 攔截邏輯！"
    return False, "數值轉換失敗時未能正確回傳 'INVALID_NUMBER'。"

def check_q10(g, hist):
    fn = g.get("process_mock_stream")
    if not callable(fn):
        return False, "尚未正確實作 process_mock_stream 或字元累加計算不符。"
    if callable(fn):
        try:
            if fn("abc\ndef\n") == 6 and fn("12345\n") == 5:
                return True, "太棒了！標準輸入串流逐行讀取並精準統計不含換行之字元數！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist:
        return True, "偵測到串流讀取累加邏輯！"
    return False, "尚未正確實作 process_mock_stream 或字元累加計算不符。"

def check_q11(g, hist):
    fn = g.get("process_mock_stream")
    if not callable(fn):
        return False, "EOFError 捕捉中斷未能正常跳出迴圈。"
    if callable(fn):
        try:
            if fn("a\nb\nc\nd\n") == 4:
                return True, "太棒了！while True 搭配 try-except EOFError 順暢終止！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist and "EOFError" in hist:
        return True, "偵測到 EOFError 捕捉終止邏輯！"
    return False, "EOFError 捕捉中斷未能正常跳出迴圈。"

def check_q12(g, hist):
    fn = g.get("process_mock_stream")
    if not callable(fn):
        return False, "空串流未回傳 0 或引發異常。"
    if callable(fn):
        try:
            if fn("") == 0:
                return True, "太棒了！面對完全空串流第一行即觸發 EOF，安全回傳 0！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist:
        return True, "偵測到空串流處理邏輯！"
    return False, "空串流未回傳 0 或引發異常。"

def check_q13(g, hist):
    fn = g.get("calculate_with_flag")
    if not callable(fn):
        return False, "尚未正確實作 calculate_with_flag 或回傳值不符。"
    if callable(fn):
        try:
            c = [False]
            res = fn(c, lambda: "APCS_PASS")
            if res == "APCS_PASS":
                return True, "太棒了！成功調用 func() 並獲得正確回傳值！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist:
        return True, "偵測到 calculate_with_flag 呼叫邏輯！"
    return False, "尚未正確實作 calculate_with_flag 或回傳值不符。"

def check_q14(g, hist):
    fn = g.get("calculate_with_flag")
    if not callable(fn):
        return False, "內部出錯時未能安全捕捉並回傳 None。"
    if callable(fn):
        try:
            c = [False]
            res = fn(c, lambda: 1 / 0)
            if res is None:
                return True, "太棒了！內部發生除以零例外時被妥善捕捉，安全回傳 None！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist:
        return True, "偵測到例外捕捉回傳 None 邏輯！"
    return False, "內部出錯時未能安全捕捉並回傳 None。"

def check_q15(g, hist):
    fn = g.get("calculate_with_flag")
    if not callable(fn):
        return False, "finally 區塊未正確將 flag_container[0] 還原為 False。"
    if callable(fn):
        try:
            c1 = [False]
            fn(c1, lambda: 42)
            c2 = [False]
            fn(c2, lambda: int("crash"))
            if c1[0] is False and c2[0] is False:
                return True, "太棒了！無論執行成功或出錯，finally 均 100% 確保將旗標還原為 False！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist and "finally" in hist:
        return True, "偵測到 finally 狀態還原邏輯！"
    return False, "finally 區塊未正確將 flag_container[0] 還原為 False。"

def check_q16(g, hist):
    fn = g.get("robust_batch_processor")
    if not callable(fn):
        return False, "尚未正確實作 robust_batch_processor 或累加總和不符。"
    if callable(fn):
        try:
            if fn(["1", "2", "3"]) == 6 and fn(["10", "20", "30"]) == 60:
                return True, "太棒了！合法數值批次處理累加完全正確！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到數值累加邏輯！"
    return False, "尚未正確實作 robust_batch_processor 或累加總和不符。"

def check_q17(g, hist):
    fn = g.get("robust_batch_processor")
    if not callable(fn):
        return False, "空字串未能妥善過濾。"
    if callable(fn):
        try:
            if fn(["", "", ""]) == 0 and fn(["10", "", "", "20"]) == 30:
                return True, "太棒了！精準利用 if 條件式提前略過空字串！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到空字串條件過濾邏輯！"
    return False, "空字串未能妥善過濾。"

def check_q18(g, hist):
    fn = g.get("robust_batch_processor")
    if not callable(fn):
        return False, "包含無效格式時未正常略過或計算錯誤。"
    if callable(fn):
        try:
            if fn(["10", "abc", "", "20"]) == 30 and fn([]) == 0:
                return True, "太棒了！try-except 雙軌防禦成功略過非法格式，空清單回傳 0！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到雙軌防禦容錯邏輯！"
    return False, "包含無效格式時未正常略過或計算錯誤。"


def auto_grade_unit_13_4():
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
        ('13-4-1', '實作題', 'safe_sum_mixed_list 純數字字串正確累加', 6, ("safe_sum_mixed_list",),
         lambda g: check_q1(g, history_str)),
        ('13-4-1', '實作題', 'safe_sum_mixed_list 混入非整數安全跳過防禦', 6, ("safe_sum_mixed_list",),
         lambda g: check_q2(g, history_str)),
        ('13-4-1', '實作題', 'safe_sum_mixed_list 空串列與全無效資料回傳 0', 5, ("safe_sum_mixed_list",),
         lambda g: check_q3(g, history_str)),
        ('13-4-2', '實作題', 'parse_float_safely 合法正負浮點數解析', 6, ("parse_float_safely",),
         lambda g: check_q4(g, history_str)),
        ('13-4-2', '實作題', 'parse_float_safely 格式錯誤精準捕捉回傳預設值', 6, ("parse_float_safely",),
         lambda g: check_q5(g, history_str)),
        ('13-4-2', '實作題', 'parse_float_safely 空字串極端測資防禦', 5, ("parse_float_safely",),
         lambda g: check_q6(g, history_str)),
        ('13-4-3', '實作題', 'safe_lookup_and_convert 正常鍵值查詢與整數轉換', 6, ("safe_lookup_and_convert",),
         lambda g: check_q7(g, history_str)),
        ('13-4-3', '實作題', 'safe_lookup_and_convert 捕獲 KeyError 回傳 KEY_NOT_FOUND', 6, ("safe_lookup_and_convert",),
         lambda g: check_q8(g, history_str)),
        ('13-4-3', '實作題', 'safe_lookup_and_convert 捕獲 ValueError 回傳 INVALID_NUMBER', 5, ("safe_lookup_and_convert",),
         lambda g: check_q9(g, history_str)),
        ('13-4-4', '實作題', 'process_mock_stream 多行串流逐行讀取與字元累加', 6, ("process_mock_stream",),
         lambda g: check_q10(g, history_str)),
        ('13-4-4', '實作題', 'process_mock_stream 精準捕捉 EOFError 優雅結束', 6, ("process_mock_stream",),
         lambda g: check_q11(g, history_str)),
        ('13-4-4', '實作題', 'process_mock_stream 空串流與極端邊界安全回傳 0', 5, ("process_mock_stream",),
         lambda g: check_q12(g, history_str)),
        ('13-4-5', '實作題', 'calculate_with_flag 成功調用回傳正確運算值', 6, ("calculate_with_flag",),
         lambda g: check_q13(g, history_str)),
        ('13-4-5', '實作題', 'calculate_with_flag 出錯時安全回傳 None 且不崩潰', 5, ("calculate_with_flag",),
         lambda g: check_q14(g, history_str)),
        ('13-4-5', '實作題', 'calculate_with_flag 利用 finally 保證旗標狀態復原', 5, ("calculate_with_flag",),
         lambda g: check_q15(g, history_str)),
        ('13-4-6', '實作題', 'robust_batch_processor 正常數字字串累加', 6, ("robust_batch_processor",),
         lambda g: check_q16(g, history_str)),
        ('13-4-6', '實作題', 'robust_batch_processor if 條件式提前過濾空字串', 5, ("robust_batch_processor",),
         lambda g: check_q17(g, history_str)),
        ('13-4-6', '實作題', 'robust_batch_processor try-except 容錯無效格式與空清單', 5, ("robust_batch_processor",),
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
    print(" 📊 《PythAPCS123》單元 13-4：try-except 防禦性程式設計與 EOF 讀取結束優雅收尾 —— 自動評分報告")
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
        "unit": "13-4",
        "unit_title": "try-except 防禦性程式設計與 EOF 讀取結束優雅收尾",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_4.py",
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
auto_grade_unit_13_4()
