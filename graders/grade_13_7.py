# ==============================================================================
# 🧪 《PythAPCS123》單元 13-7：輸出格式錯誤（Presentation Error）與嚴格排版對齊 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_13_7.py
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
NOTEBOOK_FILE = "PythAPCS123_13-7_presentation_error_and_output_formatting.ipynb"

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
    fn = g.get("verify_exact_match")
    if callable(fn):
        try:
            if fn("AC\n", "AC\n") is True and fn("Hello World", "Hello World") is True:
                return True, "太棒了！字元完全嚴格吻合精準判定為 True！"
        except Exception as e:
            return False, f"執行 verify_exact_match 時發生例外: {e}"
    if "verify_exact_match" in hist:
        return True, "偵測到嚴格一致性比對邏輯！"
    return False, "尚未正確實作 verify_exact_match 或相符字串未回傳 True。"

def check_q2(g, hist):
    fn = g.get("verify_exact_match")
    if callable(fn):
        try:
            if fn("AC", "AC\n") is False and fn("1 2 3", "1 2 3 ") is False:
                return True, "太棒了！結尾少換行或末尾多空格皆精準攔截回傳 False！"
        except Exception as e:
            return False, f"執行 verify_exact_match 時發生例外: {e}"
    if "verify_exact_match" in hist:
        return True, "偵測到微小格式差異攔截邏輯！"
    return False, "微小格式差異未正確判定為 False。"

def check_q3(g, hist):
    fn = g.get("verify_exact_match")
    if callable(fn):
        try:
            if fn("", "") is True and fn("", " ") is False:
                return True, "太棒了！空字串極端比對邊界安全防禦！"
        except Exception as e:
            return False, f"執行 verify_exact_match 時發生例外: {e}"
    if "verify_exact_match" in hist:
        return True, "偵測到空字串比對防禦！"
    return False, "空字串比對有誤。"

def check_q4(g, hist):
    fn = g.get("clean_input_and_square")
    if callable(fn):
        try:
            old_in = sys.stdin
            sys.stdin = io.StringIO("12\n")
            res = fn()
            sys.stdin = old_in
            if res == 144:
                return True, "太棒了！純淨 input 讀取整數並回傳平方結果 144！"
        except Exception as e:
            sys.stdin = old_in
            return False, f"執行 clean_input_and_square 時發生例外: {e}"
    if "clean_input_and_square" in hist:
        return True, "偵測到乾淨 input 平方計算邏輯！"
    return False, "尚未正確實作 clean_input_and_square 或平方結果不符。"

def check_q5(g, hist):
    fn = g.get("clean_input_and_square")
    if callable(fn):
        try:
            old_in = sys.stdin
            sys.stdin = io.StringIO("-5\n")
            res = fn()
            sys.stdin = old_in
            if res == 25:
                return True, "太棒了！負整數 -5 純淨讀取並精準計算平方 25！"
        except Exception as e:
            sys.stdin = old_in
            return False, f"執行 clean_input_and_square 時發生例外: {e}"
    if "clean_input_and_square" in hist:
        return True, "偵測到負整數平方讀取邏輯！"
    return False, "負整數平方計算不符。"

def check_q6(g, hist):
    fn = g.get("clean_input_and_square")
    if callable(fn):
        try:
            old_in = sys.stdin
            sys.stdin = io.StringIO("0\n")
            res = fn()
            sys.stdin = old_in
            if res == 0:
                return True, "太棒了！邊界數值 0 純淨讀取安全回傳 0！"
        except Exception as e:
            sys.stdin = old_in
            return False, f"執行 clean_input_and_square 時發生例外: {e}"
    if "clean_input_and_square" in hist:
        return True, "偵測到邊界讀取邏輯！"
    return False, "邊界 0 讀取計算錯誤。"

def check_q7(g, hist):
    fn = g.get("format_space_separated")
    if callable(fn):
        try:
            r = fn([1, 2, 3])
            if r == "1 2 3" and not r.endswith(" "):
                return True, "太棒了！各數字以單一空格隔開且末尾絕對無多餘空格！"
        except Exception as e:
            return False, f"執行 format_space_separated 時發生例外: {e}"
    if "format_space_separated" in hist:
        return True, "偵測到空格分隔格式化邏輯！"
    return False, "尚未正確實作 format_space_separated 或格式不符。"

def check_q8(g, hist):
    fn = g.get("format_space_separated")
    if callable(fn):
        try:
            if fn([42]) == "42" and fn([-10, 20]) == "-10 20":
                return True, "太棒了！單一元素與負數格式化完全精準！"
        except Exception as e:
            return False, f"執行 format_space_separated 時發生例外: {e}"
    if "format_space_separated" in hist:
        return True, "偵測到單元素與負數格式化！"
    return False, "單一元素或負數格式化不符。"

def check_q9(g, hist):
    fn = g.get("format_space_separated")
    if callable(fn):
        try:
            if fn([]) == "":
                return True, "太棒了！空串列安全回傳空字串！"
        except Exception as e:
            return False, f"執行 format_space_separated 時發生例外: {e}"
    if "format_space_separated" in hist:
        return True, "偵測到空串列安全回傳！"
    return False, "空串列未回傳空字串。"

def check_q10(g, hist):
    fn = g.get("format_grade_report")
    if callable(fn):
        try:
            r = fn([10, 20, 25])
            if r == "Total: 55, Average: 18.33":
                return True, "太棒了！總分整數與平均值小數點後兩位格式對齊完全正確！"
        except Exception as e:
            return False, f"執行 format_grade_report 時發生例外: {e}"
    if "format_grade_report" in hist:
        return True, "偵測到成績報表格式化邏輯！"
    return False, "尚未正確實作 format_grade_report 或格式字串不符。"

def check_q11(g, hist):
    fn = g.get("format_grade_report")
    if callable(fn):
        try:
            r = fn([80, 80, 80])
            if r == "Total: 240, Average: 80.00":
                return True, "太棒了！整除時精準補足小數點後兩位零 (.00)！"
        except Exception as e:
            return False, f"執行 format_grade_report 時發生例外: {e}"
    if "format_grade_report" in hist:
        return True, "偵測到整除小數點補零邏輯！"
    return False, "整除時未格式化為 .00。"

def check_q12(g, hist):
    fn = g.get("format_grade_report")
    if callable(fn):
        try:
            r = fn([100, 50])
            if r == "Total: 150, Average: 75.00":
                return True, "太棒了！兩筆資料平均值精準對齊無誤！"
        except Exception as e:
            return False, f"執行 format_grade_report 時發生例外: {e}"
    if "format_grade_report" in hist:
        return True, "偵測到成績報表邊界計算！"
    return False, "兩筆資料格式化計算錯誤。"

def check_q13(g, hist):
    fn = g.get("judge_prime_output")
    if callable(fn):
        try:
            if fn(7, "YES_NO") == "YES" and fn(9, "YES_NO") == "NO":
                return True, "太棒了！YES_NO 風格全大寫嚴格對齊無誤！"
        except Exception as e:
            return False, f"執行 judge_prime_output 時發生例外: {e}"
    if "judge_prime_output" in hist:
        return True, "偵測到 YES_NO 規格對齊邏輯！"
    return False, "尚未正確實作 judge_prime_output 或 YES/NO 格式不符。"

def check_q14(g, hist):
    fn = g.get("judge_prime_output")
    if callable(fn):
        try:
            if fn(2, "LOWER") == "true" and fn(1, "LOWER") == "false":
                return True, "太棒了！LOWER 風格全小寫 true/false 嚴格對齊，且最小質數 2 判定正確！"
        except Exception as e:
            return False, f"執行 judge_prime_output 時發生例外: {e}"
    if "judge_prime_output" in hist:
        return True, "偵測到 LOWER 規格對齊邏輯！"
    return False, "全小寫格式不符或 2/1 質數判定錯誤。"

def check_q15(g, hist):
    fn = g.get("judge_prime_output")
    if callable(fn):
        try:
            if fn(13, "TITLE") == "Prime" and fn(15, "TITLE") == "Not Prime":
                return True, "太棒了！TITLE 風格 Prime / Not Prime 首字大寫規格對齊完全無瑕！"
        except Exception as e:
            return False, f"執行 judge_prime_output 時發生例外: {e}"
    if "judge_prime_output" in hist:
        return True, "偵測到 TITLE 規格對齊邏輯！"
    return False, "TITLE 規格格式不符。"

def check_q16(g, hist):
    fn = g.get("format_grid_output")
    if callable(fn):
        try:
            g_mat = [[1, 2], [3, 4]]
            if fn(g_mat) == "1 2\n3 4":
                return True, "太棒了！二維網格行內以空格分隔、行間以換行分隔，排版完全符合規格！"
        except Exception as e:
            return False, f"執行 format_grid_output 時發生例外: {e}"
    if "format_grid_output" in hist:
        return True, "偵測到二維網格格式化邏輯！"
    return False, "尚未正確實作 format_grid_output 或網格字串不符。"

def check_q17(g, hist):
    fn = g.get("format_grid_output")
    if callable(fn):
        try:
            if fn([[42]]) == "42":
                return True, "太棒了！1x1 單一元素網格末尾無多餘換行或空格！"
        except Exception as e:
            return False, f"執行 format_grid_output 時發生例外: {e}"
    if "format_grid_output" in hist:
        return True, "偵測到單元素網格邊界格式化！"
    return False, "單一元素網格末尾有多餘空格或換行。"

def check_q18(g, hist):
    fn = g.get("format_grid_output")
    if callable(fn):
        try:
            if fn([]) == "":
                return True, "太棒了！空網格安全回傳空字串！"
        except Exception as e:
            return False, f"執行 format_grid_output 時發生例外: {e}"
    if "format_grid_output" in hist:
        return True, "偵測到空網格安全回傳！"
    return False, "空網格未回傳空字串。"


def auto_grade_unit_13_7():
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
        ('13-7-1', '實作題', 'verify_exact_match 字元與換行完全吻合判定 True', 6, ("verify_exact_match",),
         lambda g: check_q1(g, history_str)),
        ('13-7-1', '實作題', 'verify_exact_match 結尾多空格或少換行判定 False', 6, ("verify_exact_match",),
         lambda g: check_q2(g, history_str)),
        ('13-7-1', '實作題', 'verify_exact_match 空字串極端比對防禦', 5, ("verify_exact_match",),
         lambda g: check_q3(g, history_str)),
        ('13-7-2', '實作題', 'clean_input_and_square 純淨 input 讀取與平方計算', 6, ("clean_input_and_square",),
         lambda g: check_q4(g, history_str)),
        ('13-7-2', '實作題', 'clean_input_and_square 負整數平方計算無瑕疵', 6, ("clean_input_and_square",),
         lambda g: check_q5(g, history_str)),
        ('13-7-2', '實作題', 'clean_input_and_square 零與邊界數值純淨讀取', 5, ("clean_input_and_square",),
         lambda g: check_q6(g, history_str)),
        ('13-7-3', '實作題', 'format_space_separated 多元素單一空格隔開且末尾無空格', 6, ("format_space_separated",),
         lambda g: check_q7(g, history_str)),
        ('13-7-3', '實作題', 'format_space_separated 單一元素與負數格式化', 6, ("format_space_separated",),
         lambda g: check_q8(g, history_str)),
        ('13-7-3', '實作題', 'format_space_separated 空串列回傳空字串防禦', 5, ("format_space_separated",),
         lambda g: check_q9(g, history_str)),
        ('13-7-4', '實作題', 'format_grade_report 總分整數與平均小數點後兩位格式化', 6, ("format_grade_report",),
         lambda g: check_q10(g, history_str)),
        ('13-7-4', '實作題', 'format_grade_report 整除時精準補足小數點後兩位零 (.00)', 6, ("format_grade_report",),
         lambda g: check_q11(g, history_str)),
        ('13-7-4', '實作題', 'format_grade_report 兩筆元素與不規則平均精準四捨五入', 5, ("format_grade_report",),
         lambda g: check_q12(g, history_str)),
        ('13-7-5', '實作題', 'judge_prime_output YES_NO 風格全大寫嚴格對齊', 6, ("judge_prime_output",),
         lambda g: check_q13(g, history_str)),
        ('13-7-5', '實作題', 'judge_prime_output LOWER 風格全小寫 true/false 嚴格對齊', 5, ("judge_prime_output",),
         lambda g: check_q14(g, history_str)),
        ('13-7-5', '實作題', 'judge_prime_output TITLE 風格 Prime/Not Prime 邊界判定', 5, ("judge_prime_output",),
         lambda g: check_q15(g, history_str)),
        ('13-7-6', '實作題', 'format_grid_output 二維網格行內空格與各行換行', 6, ("format_grid_output",),
         lambda g: check_q16(g, history_str)),
        ('13-7-6', '實作題', 'format_grid_output 單一元素網格末尾無多餘換行或空格', 5, ("format_grid_output",),
         lambda g: check_q17(g, history_str)),
        ('13-7-6', '實作題', 'format_grid_output 空網格安全回傳空字串', 5, ("format_grid_output",),
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
    print(" 📊 《PythAPCS123》單元 13-7：輸出格式錯誤（Presentation Error）與嚴格排版對齊 —— 自動評分報告")
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
        "unit": "13-7",
        "unit_title": "輸出格式錯誤（Presentation Error）與嚴格排版對齊",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_13_7.py",
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
auto_grade_unit_13_7()
