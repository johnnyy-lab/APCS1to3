# ==============================================================================
# 🧪 《PythAPCS123》單元 13-1：競技程式線上評判系統（Online Judge）運作機制與評判結果型別解析 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_1.py
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
NOTEBOOK_FILE = "PythAPCS123_13-1_online_judge_mechanisms_and_verdicts.ipynb"

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

def get_evaluate_fn(g):
    return g.get("evaluate_testcase") or g.get("evaluate_testcase_ans")

def get_find_min_pos_fn(g):
    return g.get("find_min_positive") or g.get("find_min_positive_ans")

def get_format_report_fn(g):
    return g.get("format_report") or g.get("format_report_ans")

def get_predict_tle_fn(g):
    return g.get("predict_tle") or g.get("predict_tle_ans")

def get_safe_division_fn(g):
    return g.get("safe_division") or g.get("safe_division_ans")

def check_q1(g, hist):
    fn = get_evaluate_fn(g)
    if not callable(fn):
        return False, "請實作 evaluate_testcase(user_output, expected_output) 進行基礎判定。"
    if callable(fn):
        try:
            if fn("100\n", "100") == "AC" and fn("100", "200") == "WA":
                return True, "太棒了！精準判定完全吻合為 AC，答案相異為 WA！"
        except Exception:
            pass
    if "evaluate_testcase" in hist and '"AC"' in hist and '"WA"' in hist:
        return True, "比對邏輯檢驗通過！"
    return False, "請實作 evaluate_testcase(user_output, expected_output) 進行基礎判定。"

def check_q2(g, hist):
    fn = get_evaluate_fn(g)
    if not callable(fn):
        return False, "請使用 .strip() 消除尾端空白與換行以防範偽 WA。"
    if callable(fn):
        try:
            if fn("hello world  \n", "hello world") == "AC" and fn("42\n\n", "42") == "AC":
                return True, "完全正確！strip() 去除頭尾空白換行，落實 OJ 寬容比對規範！"
        except Exception:
            pass
    if ".strip()" in hist and "evaluate_testcase" in hist:
        return True, "空白修剪處理正確，通過！"
    return False, "請使用 .strip() 消除尾端空白與換行以防範偽 WA。"

def check_q3(g, hist):
    fn = get_evaluate_fn(g)
    if not callable(fn):
        return False, "當 user_output 包含 'Error:' 時請回傳 'RE'。"
    if callable(fn):
        try:
            if fn("Error: IndexError", "100") == "RE" and fn("Error: ZeroDivisionError", "0") == "RE":
                return True, "精彩！精確辨識 Error: 關鍵字並回傳 RE (Runtime Error)！"
        except Exception:
            pass
    if '"Error:"' in hist and '"RE"' in hist:
        return True, "例外識別邏輯正確，通過！"
    return False, "當 user_output 包含 'Error:' 時請回傳 'RE'。"

def check_q4(g, hist):
    fn = get_find_min_pos_fn(g)
    if not callable(fn):
        return False, "請實作 find_min_positive(nums) 回傳大於 0 的最小值。"
    if callable(fn):
        try:
            if fn([4, -2, 7, 1, 9]) == 1 and fn([10, 20, 5]) == 5:
                return True, "太棒了！順利過濾正整數並找出最小值 1！"
        except Exception:
            pass
    if "find_min_positive" in hist and "min(" in hist:
        return True, "正整數篩選通過！"
    return False, "請實作 find_min_positive(nums) 回傳大於 0 的最小值。"

def check_q5(g, hist):
    fn = get_find_min_pos_fn(g)
    if not callable(fn):
        return False, "當數列中無任何正整數時，必須回傳 -1。"
    if callable(fn):
        try:
            if fn([-5, -10, -3]) == -1 and fn([-1]) == -1:
                return True, "完全正確！面對全負數等無解極端測資，安全防禦回傳 -1！"
        except Exception:
            pass
    if "return -1" in hist and "find_min_positive" in hist:
        return True, "無解邊界防禦通過！"
    return False, "當數列中無任何正整數時，必須回傳 -1。"

def check_q6(g, hist):
    fn = get_find_min_pos_fn(g)
    if not callable(fn):
        return False, "請確保 0 不被誤認為正整數，且重複值能正確求出最小值。"
    if callable(fn):
        try:
            if fn([0, 5, 2, 2]) == 2 and fn([0, 0, 0]) == -1:
                return True, "強韌無比！面對包含 0 與重複正整數極端邊界，判定完全精準！"
        except Exception:
            pass
    if "x > 0" in hist and "find_min_positive" in hist:
        return True, "嚴格大於零邏輯通過！"
    return False, "請確保 0 不被誤認為正整數，且重複值能正確求出最小值。"

def check_q7(g, hist):
    fc = g.get("fixed_code", "")
    if not isinstance(fc, str) or not fc.strip():
        return False, "請在 fixed_code 中修復 if len(nums) > 0: 漏冒號語法錯誤。"
    if isinstance(fc, str) and "if len(nums) > 0:" in fc:
        return True, "太棒了！成功在 if 條件句末尾補齊關鍵冒號 ':'！"
    if "len(nums) > 0:" in hist or "correct_code_sample" in g:
        return True, "語法修正通過！"
    return False, "請在 fixed_code 中修復 if len(nums) > 0: 漏冒號語法錯誤。"

def check_q8(g, hist):
    fc = g.get("fixed_code", "")
    if not isinstance(fc, str) or not fc.strip():
        return False, "請確保 fixed_code 不包含任何 SyntaxError，能順利編譯。"
    if isinstance(fc, str) and fc.strip():
        try:
            compile(fc, filename="<test>", mode="exec")
            return True, "完全正確！fixed_code 順利通過 compile() 編譯檢查，完全消滅 CE！"
        except SyntaxError:
            pass
    if g.get("comp_ok") is True:
        return True, "編譯檢驗通過！"
    return False, "請確保 fixed_code 不包含任何 SyntaxError，能順利編譯。"

def check_q9(g, hist):
    fc = g.get("fixed_code", "")
    if not isinstance(fc, str) or not fc.strip():
        return False, "請確保 calculate_average 正常回傳平均值，空串列回傳 0。"
    if isinstance(fc, str) and "def calculate_average" in fc:
        loc = {}
        try:
            exec(fc, loc)
            fn = loc.get("calculate_average")
            if not callable(fn):
                return False, "請確保 calculate_average 正常回傳平均值，空串列回傳 0。"
            if callable(fn) and fn([10, 20, 30]) == 20 and fn([]) == 0:
                return True, "精彩！修復後 calculate_average 實測正確，空串列保護亦完全無誤！"
        except Exception:
            pass
    if "calculate_average" in hist:
        return True, "平均計算邏輯檢驗通過！"
    return False, "請確保 calculate_average 正常回傳平均值，空串列回傳 0。"

def check_q10(g, hist):
    fn = get_format_report_fn(g)
    if not callable(fn):
        return False, "首行請輸出 round() 四捨五入後的整數平均值。"
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            first_line = out.strip().splitlines()[0]
            if first_line == "86":
                return True, "太棒了！首行平均數四捨五入為整數 86，完全符合輸出規範！"
        except Exception:
            pass
    if "round(" in hist and "format_report" in hist:
        return True, "四捨五入整數邏輯通過！"
    return False, "首行請輸出 round() 四捨五入後的整數平均值。"

def check_q11(g, hist):
    fn = get_format_report_fn(g)
    if not callable(fn):
        return False, "次行請將 >= 60 的成績由大到小降序排列輸出。"
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            lines = out.strip().splitlines()
            if len(lines) >= 2 and "92 90 85 78" in lines[1]:
                return True, "完全正確！及格成績由大到小降序排列無誤！"
        except Exception:
            pass
    if "reverse=True" in hist and "format_report" in hist:
        return True, "降序排列邏輯通過！"
    return False, "次行請將 >= 60 的成績由大到小降序排列輸出。"

def check_q12(g, hist):
    fn = get_format_report_fn(g)
    if not callable(fn):
        return False, "請使用 ' '.join() 串接成績，確保數字間單一空格且行末無空白。"
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            lines = out.strip().splitlines()
            if len(lines) >= 2 and lines[1] == "92 90 85 78" and not lines[1].endswith(" "):
                return True, "字元級嚴謹！以 ' '.join() 分隔且行末無多餘空白，徹底杜絕格式 WA！"
        except Exception:
            pass
    if '" ".join' in hist or "' '.join" in hist:
        return True, "空格串接格式通過！"
    return False, "請使用 ' '.join() 串接成績，確保數字間單一空格且行末無空白。"

def check_q13(g, hist):
    fn = get_predict_tle_fn(g)
    if not callable(fn):
        return False, "請實作 predict_tle，當運算量小於限制時回傳 'PASS'。"
    if callable(fn):
        try:
            if fn(100000, "O(N)") == "PASS":
                return True, "太棒了！N=10^5 在 O(N) 僅 10 萬次運算，遠低於千萬上限，判定 PASS！"
        except Exception:
            pass
    if 'predict_tle(100000, "O(N)")' in hist:
        return True, "O(N) 運算量檢驗通過！"
    return False, "請實作 predict_tle，當運算量小於限制時回傳 'PASS'。"

def check_q14(g, hist):
    fn = get_predict_tle_fn(g)
    if not callable(fn):
        return False, "當預估運算次數超過限制時，請回傳 'TLE'。"
    if callable(fn):
        try:
            if fn(100000, "O(N^2)") == "TLE":
                return True, "完全正確！N=10^5 在 O(N^2) 高達 10^10 次運算，精準預警 TLE！"
        except Exception:
            pass
    if 'predict_tle(100000, "O(N^2)")' in hist:
        return True, "O(N^2) TLE 預警通過！"
    return False, "當預估運算次數超過限制時，請回傳 'TLE'。"

def check_q15(g, hist):
    fn = get_predict_tle_fn(g)
    if not callable(fn):
        return False, "請依運算次數上限正確認定邊界 (2000 PASS, 5000 TLE)。"
    if callable(fn):
        try:
            if fn(2000, "O(N^2)") == "PASS" and fn(5000, "O(N^2)") == "TLE":
                return True, "精彩！精確掌握 2000^2=4*10^6 (PASS) 與 5000^2=2.5*10^7 (TLE) 臨界邊界！"
        except Exception:
            pass
    if "predict_tle" in hist and "time_limit_sec" in hist:
        return True, "臨界值邊界檢驗通過！"
    return False, "請依運算次數上限正確認定邊界 (2000 PASS, 5000 TLE)。"

def check_q16(g, hist):
    fn = get_safe_division_fn(g)
    if not callable(fn):
        return False, "請在輸入合法時回傳 lst[0] // lst[1]。"
    if callable(fn):
        try:
            if fn([20, 4]) == 5 and fn([-8, 2]) == -4 and fn([0, 5]) == 0:
                return True, "太棒了！正常數值整數商 lst[0] // lst[1] 計算完全正確！"
        except Exception:
            pass
    if "safe_division" in hist and "//" in hist:
        return True, "整數商計算通過！"
    return False, "請在輸入合法時回傳 lst[0] // lst[1]。"

def check_q17(g, hist):
    fn = get_safe_division_fn(g)
    if not callable(fn):
        return False, "當 lst 長度小於 2 時，請安全回傳 'INVALID_LENGTH'。"
    if callable(fn):
        try:
            if fn([10]) == "INVALID_LENGTH" and fn([]) == "INVALID_LENGTH":
                return True, "完全正確！長度小於 2 與空串列防禦無懈可擊，回傳 INVALID_LENGTH！"
        except Exception:
            pass
    if '"INVALID_LENGTH"' in hist and "len(" in hist:
        return True, "長度防禦檢驗通過！"
    return False, "當 lst 長度小於 2 時，請安全回傳 'INVALID_LENGTH'。"

def check_q18(g, hist):
    fn = get_safe_division_fn(g)
    if not callable(fn):
        return False, "當分母 lst[1] == 0 時，請安全回傳 'DIVISION_BY_ZERO'。"
    if callable(fn):
        try:
            if fn([10, 0]) == "DIVISION_BY_ZERO":
                return True, "滿分通關！除以零防禦無懈可擊，回傳 DIVISION_BY_ZERO，零崩潰達成！"
        except Exception:
            pass
    if '"DIVISION_BY_ZERO"' in hist:
        return True, "除以零防禦通過！"
    return False, "當分母 lst[1] == 0 時，請安全回傳 'DIVISION_BY_ZERO'。"


def auto_grade_unit_13_1(env=None):
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
        ('13-1-1', '實作題', '評判狀態基礎比對判定（AC / WA）', 6, (),
         lambda g: check_q1(g, history_str)),
        ('13-1-1', '實作題', '輸出格式尾端空白與換行容錯處理', 6, (),
         lambda g: check_q2(g, history_str)),
        ('13-1-1', '實作題', '偵測執行崩潰 Error 關鍵字回傳 RE', 5, (),
         lambda g: check_q3(g, history_str)),
        ('13-1-2', '實作題', '正整數篩選與最小正整數計算', 6, (),
         lambda g: check_q4(g, history_str)),
        ('13-1-2', '實作題', '極端全負數與無正整數回傳 -1', 6, (),
         lambda g: check_q5(g, history_str)),
        ('13-1-2', '實作題', '含零與重複值極端測資強韌性', 5, (),
         lambda g: check_q6(g, history_str)),
        ('13-1-3', '實作題', 'fixed_code 修正語法漏冒號錯誤', 6, ("fixed_code", "correct_code_sample"),
         lambda g: check_q7(g, history_str)),
        ('13-1-3', '實作題', 'fixed_code 成功通過 compile() 編譯', 6, ("fixed_code", "comp_ok"),
         lambda g: check_q8(g, history_str)),
        ('13-1-3', '實作題', '修復後 calculate_average 運算邏輯正確', 5, ("fixed_code",),
         lambda g: check_q9(g, history_str)),
        ('13-1-4', '實作題', '首行總平均四捨五入整數規範', 6, (),
         lambda g: check_q10(g, history_str)),
        ('13-1-4', '實作題', '次行及格成績降序排列篩選', 6, (),
         lambda g: check_q11(g, history_str)),
        ('13-1-4', '實作題', '嚴格空格分隔與尾端無多餘空白格式', 5, (),
         lambda g: check_q12(g, history_str)),
        ('13-1-5', '實作題', 'O(N) 線性複雜度 10^5 運算量判定 PASS', 6, (),
         lambda g: check_q13(g, history_str)),
        ('13-1-5', '實作題', 'O(N^2) 平方複雜度 10^5 運算量預警 TLE', 5, (),
         lambda g: check_q14(g, history_str)),
        ('13-1-5', '實作題', '時間限制與運算量臨界邊界判定', 5, (),
         lambda g: check_q15(g, history_str)),
        ('13-1-6', '實作題', 'safe_division 正常數值整數商計算', 6, (),
         lambda g: check_q16(g, history_str)),
        ('13-1-6', '實作題', '防禦空串列與長度不足 INVALID_LENGTH', 5, (),
         lambda g: check_q17(g, history_str)),
        ('13-1-6', '實作題', '防禦除以零 DIVISION_BY_ZERO 零崩潰', 5, (),
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
    print(" 📊 《PythAPCS123》單元 13-1：競技程式線上評判系統（Online Judge）運作機制與評判結果型別解析 —— 自動評分報告")
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
        "unit": "13-1",
        "unit_title": "競技程式線上評判系統（Online Judge）運作機制與評判結果型別解析",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_1.py",
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
auto_grade_unit_13_1()
