# ==============================================================================
# 🧪 《PythAPCS123》單元 9-6：矩陣幾何操作與逆推還原（APCS b266 專題） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_6.py
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
NOTEBOOK_FILE = "PythAPCS123_9-6_matrix_geometric_transformations_and_apcs_b266.ipynb"

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


def auto_grade_unit_9_6(env=None):
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

    test_cases = [
        # ----------------------------------------------------------------------
        # 9-6-1 矩陣水平翻轉 (Horizontal Flip) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-6-1", "填空題", "水平翻轉切片 row[::-1]", 5, (),
         lambda g: (
             (True, "水平翻轉 row[::-1] 填空正確！")
             if ("row[::-1]" in history_clean)
             else (False, "請在 9-6-1 填空題填入 row[::-1]！")
         )),

        ("9-6-1", "練習題", "讀入網格並輸出水平翻轉後成果", 6, (),
         lambda g: (
             (True, "水平翻轉與解包輸出正確！")
             if ("[row[::-1] for row in gd27]" in history_str or "row[::-1]" in history_clean) and "print" in history_str
             else (False, "請將讀入的網格水平翻轉並印出！")
         )),

        ("9-6-1", "挑戰題", "兩次水平翻轉等同還原驗證", 5, (),
         lambda g: (
             (True, "兩次翻轉還原驗證正確！")
             if ("== gd28" in history_str or "==" in history_str) and "row[::-1]" in history_clean
             else (False, "請驗證兩次水平翻轉後是否與原始網格完全相同！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-2 矩陣垂直翻轉 (Vertical Flip) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-2", "填空題", "垂直翻轉切片 matrix[::-1]", 5, (),
         lambda g: (
             (True, "垂直翻轉 matrix[::-1] 填空正確！")
             if ("matrix[::-1]" in history_clean or "brd096[::-1]" in history_clean)
             else (False, "請在 9-6-2 填空題填入 matrix[::-1]！")
         )),

        ("9-6-2", "練習題", "垂直翻轉矩陣並解包輸出", 6, (),
         lambda g: (
             (True, "垂直翻轉操作與輸出正確！")
             if ("::-1" in history_str and "print" in history_str)
             else (False, "請使用 gd29[::-1] 進行垂直翻轉並解包印出每一列！")
         )),

        ("9-6-2", "挑戰題", "垂直翻轉後再水平翻轉 (旋轉 180 度)", 6, (),
         lambda g: (
             (True, "水平垂直雙重翻轉正確！")
             if ("::-1" in history_str and "row[::-1]" in history_clean)
             else (False, "請依序執行垂直翻轉與水平翻轉！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-3 矩陣轉置操作 (Transpose) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-3", "填空題", "二維轉置列表生成式 origin[r][c]", 5, (),
         lambda g: (
             (True, "轉置生成式填空正確！")
             if ("origin[r][c]" in history_clean or "matrix[r][c]" in history_clean) and ("for r in range(R18)" in history_str)
             else (False, "請在 9-6-3 填空題填入 origin[r][c] 完成轉置！")
         )),

        ("9-6-3", "練習題", "非方陣轉置與尺寸互換 (R, C 變為 C, R)", 6, (),
         lambda g: (
             (True, "非方陣轉置與尺寸轉換正確！")
             if ("for c in range(C)" in history_str and "for r in range(R)" in history_str) or "zip(*gd31)" in history_str
             else (False, "請將 R x C 矩陣轉置為 C x R 矩陣並輸出！")
         )),

        ("9-6-3", "挑戰題", "連續兩次轉置恢復原貌", 6, (),
         lambda g: (
             (True, "二次轉置恢復驗證正確！")
             if ("transpose" in history_str or "T" in history_str or "==" in history_str)
             else (False, "請驗證轉置兩次後矩陣恢復原始樣貌！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-4 矩陣旋轉 90 度 (Rotate 90) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-4", "填空題", "順時針 90 度旋轉 (轉置後每列水平翻轉)", 5, (),
         lambda g: (
             (True, "順時針 90 度旋轉填空正確！")
             if ("row[::-1]" in history_clean or "matrix[R19 - 1 - r][c]" in history_clean)
             else (False, "請在 9-6-4 填空題完成順時針 90 度旋轉！")
         )),

        ("9-6-4", "練習題", "實作逆時針 90 度旋轉", 6, (),
         lambda g: (
             (True, "逆時針 90 度旋轉實作正確！")
             if ("rotate" in history_str or "90" in history_str) and ("::-1" in history_str)
             else (False, "請實作逆時針旋轉 90 度（水平翻轉後轉置）！")
         )),

        ("9-6-4", "挑戰題", "連轉四次 360 度恢復初始", 6, (),
         lambda g: (
             (True, "360 度四次旋轉循環驗證正確！")
             if ("range(4)" in history_str or "4" in history_str) and "==" in history_str
             else (False, "請連續旋轉 4 次驗證是否完全回到原陣列！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-5 連續操作與變數尺寸動態追蹤 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-5", "填空題", "動態追蹤列數 curr_R = len(mat)", 5, (),
         lambda g: (
             (True, "動態尺寸追蹤填空正確！")
             if ("len(mat)" in history_clean or "len(grid)" in history_clean)
             else (False, "請在 9-6-5 填空題填入 len(mat)！")
         )),

        ("9-6-5", "練習題", "執行操作序列 [0, 1] 並印出最終網格", 6, (),
         lambda g: (
             (True, "操作指令分流執行正確！")
             if ("cmd == 0" in history_str or "cmd == 1" in history_str or "op == 0" in history_str or "op == 1" in history_str)
             else (False, "請依操作序列依序執行翻轉與旋轉！")
         )),

        ("9-6-5", "挑戰題", "動態追蹤多步操作之網格行列尺寸變化", 6, (),
         lambda g: (
             (True, "動態維度追蹤正確！")
             if ("len(" in history_str and "print" in history_str)
             else (False, "請在每次操作後即時更新並輸出網格的新維度 R 與 C！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-6 APCS b266 矩陣轉換：逆操作還原心法 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-6-6", "填空題", "逆操作順序 ops096[::-1]", 5, (),
         lambda g: (
             (True, "逆操作反轉 ops096[::-1] 填空正確！")
             if ("ops096[::-1]" in history_clean or "reversed(ops096)" in history_str)
             else (False, "請在 9-6-6 填空題填入 ops096[::-1] 將操作序列倒轉！")
         )),

        ("9-6-6", "練習題", "APCS b266 單組測資逆推還原原型", 6, (),
         lambda g: (
             (True, "APCS b266 逆推還原正確！")
             if ("ops1[::-1]" in history_clean or "reversed(" in history_str) and ("print(*row)" in history_str)
             else (False, "請依照 APCS b266 規格逆序執行操作還原原始矩陣！")
         )),

        ("9-6-6", "挑戰題", "APCS b266 多組測資 while True 逆推終極通關", 5, (),
         lambda g: (
             (True, "APCS b266 完整多測資框架正確！")
             if ("while True:" in history_str or "try:" in history_str or "EOFError" in history_str)
             else (False, "請以 while True 搭配 try-except 完成 APCS b266 多測資逆推！")
         ))    ]

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
        badge = '🏆 完美滿分！你已經徹底攻克二維陣列核心技術，具備 APCS 實戰高手水準！'
    elif total_score >= 80:
        badge = '🌟 優秀！觀念掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本概念已建立，建議複習未通過的題目加強熟悉度！'
    else:
        badge = '💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 9-6：矩陣幾何操作與逆推還原（APCS b266 專題） —— 自動評分報告")
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
        "unit": "9-6",
        "unit_title": "矩陣幾何操作與逆推還原（APCS b266 專題）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_9_6.py",
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
auto_grade_unit_9_6()
