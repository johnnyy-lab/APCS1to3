# ==============================================================================
# 🧪 《PythAPCS123》單元 5-1：比較運算子與連續比較 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_1.py
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
NOTEBOOK_FILE = "PythAPCS123_5-1_comparison_operators_and_chained_comparisons.ipynb"

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


def auto_grade_unit_5_1(env=None):
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

    test_cases = [
        # ----------------------------------------------------------------------
        # 5-1-1 數值大小比較——大於（>）、小於（<）、大於等於（>=）、小於等於（<=） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-1-1", "填空題", "圖書館借閱與逾期檢驗 (is_books_valid, has_overdue)", 6, ("is_books_valid", "has_overdue"),
         lambda g: (
             (True, "比較運算子填寫正確：is_books_valid=True 且 has_overdue=True！")
             if (g.get("is_books_valid") is True and g.get("has_overdue") is True) or
                ("books <= 10" in history_str.replace(" ", "") and "overdue_days > 0" in history_str.replace(" ", ""))
             else (
                 (False, "is_books_valid 判斷未通過：8 本不超過 10 本應為 True，請確認是否填入 <= 10！")
                 if (g.get("is_books_valid") is False)
                 else (
                     (False, "has_overdue 判斷未通過：逾期 3 天大於 0 天應為 True，請確認是否填入 > 0！")
                     if (g.get("has_overdue") is False)
                     else (False, "請在 5-1-1 填空題填入 <= 與 > 並點擊播放鍵 ▶ 執行！")
                 )
             )
         )),

        ("5-1-1", "練習題", "水庫水情預警系統 (current_level >= 150 與 < 80)", 8, ("current_level",),
         lambda g: (
             (True, "水庫防汛與抗旱雙重門檻比較正確！")
             if ((">= 150" in history_str or ">= flood" in history_str or ">=150" in history_str.replace(" ", "")) and
                 ("< 80" in history_str or "< drought" in history_str or "<80" in history_str.replace(" ", ""))) or
                ("current_level" in g and (
                    g.get("current_level") >= 150 if isinstance(g.get("current_level"), (int, float)) and g.get("current_level") >= 150 else True
                ) and (">= 150" in history_str or "< 80" in history_str))
             else (False, "請讀入 current_level，並分別判斷 current_level >= 150 與 current_level < 80 輸出兩行布林值！")
         )),

        ("5-1-1", "挑戰題", "包裹重量規格檢驗 (w1 <= 20, w2 <= 20)", 6, ("w1", "w2"),
         lambda g: (
             (True, "兩件包裹重量上限 20 公斤比對成功！")
             if ("<= 20" in history_str or "<=20" in history_str.replace(" ", "")) or
                (all(k in g for k in ["w1", "w2"]) and (g.get("w1") <= 20 or g.get("w2") <= 20)) or
                ("w1" in g and "w2" in g)
             else (False, "請以單行 split 讀入整數 w1 與 w2，並分別檢驗 w1 <= 20 與 w2 <= 20 輸出結果！")
         )),

        # ----------------------------------------------------------------------
        # 5-1-2 嚴格相等與不相等——雙等號（==）與驚嘆號等號（!=） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-1-2", "填空題", "門禁通行驗證與實名登記 (is_auth_success, needs_registration)", 6, ("is_auth_success", "needs_registration"),
         lambda g: (
             (True, "金鑰與訪客代碼驗證正確：is_auth_success=True 且 needs_registration=True！")
             if (g.get("is_auth_success") is True and g.get("needs_registration") is True) or
                ("user_key == system_key" in history_str.replace(" ", "") and "visitor_code != 0" in history_str.replace(" ", ""))
             else (False, "請在 5-1-2 填空題填入雙等號 == 與不等於 != 並點擊播放鍵 ▶ 執行！")
         )),

        ("5-1-2", "練習題", "數字密碼對碰遊戲 (guess == target, guess != target)", 8, ("target", "guess"),
         lambda g: (
             (True, "數字密碼相等（==）與不相等（!=）判定正確！")
             if (("guess == target" in history_str.replace(" ", "") or "target == guess" in history_str.replace(" ", "")) and
                 ("guess != target" in history_str.replace(" ", "") or "target != guess" in history_str.replace(" ", ""))) or
                (("==" in history_str and "!=" in history_str) and ("target" in g or "guess" in g))
             else (False, "請依序讀入 target 與 guess，並印出 guess == target 與 guess != target！")
         )),

        ("5-1-2", "挑戰題", "擲骰子對子判定 (d1 == d2)", 6, ("d1", "d2"),
         lambda g: (
             (True, "骰子對子比對成功：d1 == d2 判斷完成！")
             if ("d1 == d2" in history_str.replace(" ", "") or "d2 == d1" in history_str.replace(" ", "")) or
                ("d1" in g and "d2" in g and "==" in history_str) or
                ("==" in history_str and "split" in history_str)
             else (False, "請單行讀入 d1 與 d2，並以 d1 == d2 判斷點數是否完全相同！")
         )),

        # ----------------------------------------------------------------------
        # 5-1-3 運算式與運算優先級——先算術運算，再進行大小比較 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-1-3", "填空題", "矩形與正方形面積大比拼 (square_area, is_rect_larger)", 6, ("rect_area", "square_area", "is_rect_larger"),
         lambda g: (
             (True, "幾何面積與運算優先級正確：square_area=49 且 is_rect_larger=True！")
             if (g.get("rect_area") == 60 and g.get("square_area") == 49 and g.get("is_rect_larger") is True) or
                (("side ** 2" in history_str or "side**2" in history_str or "side * side" in history_str) and
                 ("rect_area > square_area" in history_str.replace(" ", "")))
             else (False, "正方形面積應填入 side ** 2（49），且判斷長方形面積是否大於正方形面積（>）！")
         )),

        ("5-1-3", "練習題", "促銷優惠方案試算 (方案 A 9折 vs 方案 B 買三送一)", 8, ("price", "quantity"),
         lambda g: (
             (True, "促銷方案 A 與方案 B 算術計算與價格比較正確！")
             if (("// 10" in history_str or "//10" in history_str or "* 9 // 10" in history_str) and
                 ("// 4" in history_str or "//4" in history_str) and
                 ("<" in history_str or "plan_a" in history_str)) or
                ("price" in g and "quantity" in g and "<" in history_str)
             else (False, "請計算方案 A（9折）與方案 B（買三送一）金額，並比較方案 A 是否更便宜（<）！")
         )),

        ("5-1-3", "挑戰題", "畢氏定理直角三角形驗證 (side_a**2 + side_b**2 == side_c**2)", 6, ("side_a", "side_b", "side_c"),
         lambda g: (
             (True, "畢氏定理直角三角形平方和比對成功！")
             if ("side_a**2 + side_b**2 == side_c**2" in history_str.replace(" ", "") or
                 "side_a*side_a + side_b*side_b == side_c*side_c" in history_str.replace(" ", "") or
                 ("side_a" in g and "side_b" in g and "side_c" in g and "**2" in history_str and "==" in history_str)) or
                ("**" in history_str and "==" in history_str and "split" in history_str)
             else (False, "請單行讀入三個整數 side_a, side_b, side_c，並驗證畢氏定理 side_a**2 + side_b**2 == side_c**2！")
         )),

        # ----------------------------------------------------------------------
        # 5-1-4 文字字串的比較——字典序（Lexicographical Order）與大小寫 ASCII (共 20 分)
        # ----------------------------------------------------------------------
        ("5-1-4", "填空題", "字典排序檢驗員 (is_same=False, is_earlier=True)", 6, ("is_same", "is_earlier"),
         lambda g: (
             (True, "字串比較填空正確：is_same=False 且 is_earlier=True！")
             if (g.get("is_same") is False and g.get("is_earlier") is True) or
                ("word1 == word2" in history_str.replace(" ", "") and "word1 < word2" in history_str.replace(" ", ""))
             else (False, "word1 與 word2 不相等（== 結果為 False），且 banana 在 cat 前面（< 結果為 True）！")
         )),

        ("5-1-4", "練習題", "帳號名稱大小寫與字典序比對 (account1, account2)", 8, ("account1", "account2"),
         lambda g: (
             (True, "帳號雙重比對正確：相等判定（==）與字典序比對（<）完成！")
             if (("account1 == account2" in history_str.replace(" ", "") or "account1==account2" in history_str.replace(" ", "")) and
                 ("account1 < account2" in history_str.replace(" ", "") or "account1<account2" in history_str.replace(" ", ""))) or
                ("account1" in g and "account2" in g and "==" in history_str and "<" in history_str)
             else (False, "請讀入兩行帳號字串 account1 與 account2，並依序輸出是否相等（==）及字典序大小（<）！")
         )),

        ("5-1-4", "挑戰題", "學生英文名單依序排列檢定 (name1 < name2 < name3)", 6, ("name1", "name2", "name3"),
         lambda g: (
             (True, "三位學生英文姓名連續字典序比對成功！")
             if ("name1 < name2 < name3" in history_str.replace(" ", "") or
                 "name1<name2<name3" in history_str.replace(" ", "") or
                 ("name1 < name2" in history_str.replace(" ", "") and "name2 < name3" in history_str.replace(" ", ""))) or
                ("name1" in g and "name2" in g and "name3" in g and "<" in history_str)
             else (False, "請單行讀入三個英文名字，並以連續比較式 name1 < name2 < name3 檢驗是否依字典序排好！")
         )),

        # ----------------------------------------------------------------------
        # 5-1-5 Python 獨家黑科技——連續比較式（Chained Comparisons） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-1-5", "填空題", "智慧恆溫溫室系統 (is_ideal_temp)", 6, ("is_ideal_temp",),
         lambda g: (
             (True, "連續比較式閉區間填寫正確：is_ideal_temp=True (20 <= 25 <= 28)！")
             if (g.get("is_ideal_temp") is True) and
                ("20 <= current_temp <= 28" in history_str.replace(" ", "") or "20<=current_temp<=28" in history_str.replace(" ", "") or "<=" in history_str)
             else (False, "請在空格填入 <= 完成 20 <= current_temp <= 28 雙向閉區間檢驗！")
         )),

        ("5-1-5", "練習題", "數值落在開區間內檢驗 (10 < num < 50)", 8, ("num",),
         lambda g: (
             (True, "連續比較式開區間 10 < num < 50 判斷正確！")
             if ("10 < num < 50" in history_str.replace(" ", "") or "10<num<50" in history_str.replace(" ", "")) or
                ("num" in g and ("10 < num" in history_str or "num < 50" in history_str or "10<num" in history_str.replace(" ", "")))
             else (False, "請讀入整數 num，並使用 Python 連續比較式 10 < num < 50 輸出檢驗結果！")
         )),

        ("5-1-5", "挑戰題", "嚴格遞增三數序列檢定 (num1 < num2 < num3)", 6, ("num1", "num2", "num3"),
         lambda g: (
             (True, "嚴格遞增三數連續比較式 num1 < num2 < num3 判斷成功！")
             if ("num1 < num2 < num3" in history_str.replace(" ", "") or "num1<num2<num3" in history_str.replace(" ", "")) or
                (all(k in g for k in ["num1", "num2", "num3"]) and ("num1 < num2 < num3" in history_str.replace(" ", "") or ("num1 < num2" in history_str and "num2 < num3" in history_str)))
             else (False, "請單行讀入三個整數 num1, num2, num3，並使用連續比較式 num1 < num2 < num3 輸出判斷結果！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通比較運算子與連續比較式，真假判斷明察秋毫！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，數值大小、字串字典序與連續比較邏輯精湛！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-1：比較運算子與連續比較 —— 自動評分報告")
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
        "unit": "5-1",
        "unit_title": "比較運算子與連續比較",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_5_1.py",
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
auto_grade_unit_5_1()
