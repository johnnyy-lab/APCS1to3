# ==============================================================================
# 🧪 《PythAPCS123》單元 11-1：函數定義（def）、呼叫流程與參數傳入基礎 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_1.py
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
NOTEBOOK_FILE = "PythAPCS123_11-1_function_definition_and_call_process.ipynb"

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

def get_submission_env():
    """取得學員全域與執行歷史。Cell B 隔離載入時優先讀 __STUDENT_ENV__。"""
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        history_cells = snapshot.get("_ih", snapshot.get("In", []))
        if not isinstance(history_cells, list):
            history_cells = []
        return snapshot, history_cells
    try:
        import IPython
        ipython_inst = IPython.get_ipython()
        if ipython_inst is not None:
            user_ns = ipython_inst.user_ns
            history_cells = getattr(ipython_inst, 'user_ns', {}).get('_ih', [])
            return user_ns, history_cells
    except Exception:
        pass
    
    # 備用機制：若不在 IPython 環境，從呼叫棧主模組獲取
    try:
        import __main__
        return __main__.__dict__, []
    except Exception:
        return {}, []


def auto_grade_unit_11_1(env=None):
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

    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 11-1-1 為什麼需要函數？黑盒子概念 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-1", "填空題", "定義並呼叫印出標題函數 print_banner()", 5, ("print_banner",),
         lambda g: (
             (True, "print_banner 函數定義與呼叫正確！")
             if (callable(g.get("print_banner"))) or
                ("def print_banner():" in history_str and "print_banner()" in history_str)
             else (False, "請定義 def print_banner(): 並呼叫該函數！")
         )),

        ("11-1-1", "練習題", "自訂競技賽事結尾橫幅 print_game_summary()", 6, ("print_game_summary",),
         lambda g: (
             (True, "print_game_summary 函數實作正確！")
             if (callable(g.get("print_game_summary"))) or
                ("print_game_summary" in history_str and "GAME OVER" in history_str)
             else (False, "請定義可呼叫的 print_game_summary 函數並輸出橫幅！")
         )),

        ("11-1-1", "挑戰題", "設計多階層日誌排版 log_start 與 log_finish", 6, ("log_start", "log_finish"),
         lambda g: (
             (True, "log_start 與 log_finish 多階層日誌函數實作正確！")
             if (callable(g.get("log_start")) and callable(g.get("log_finish"))) or
                ("log_start" in history_str and "log_finish" in history_str)
             else (False, "請定義 log_start() 與 log_finish() 兩函數並模擬日誌輸出！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-2 函數的定義（def）、命名規範與呼叫 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-2", "填空題", "修正 def 與括號呼叫 show_system_alert()", 5, ("show_system_alert",),
         lambda g: (
             (True, "show_system_alert 定義與括號呼叫正確！")
             if (callable(g.get("show_system_alert"))) or
                ("show_system_alert()" in history_str and "def show_system_alert():" in history_str)
             else (False, "請補上 def 關鍵字與 show_system_alert() 括號進行呼叫！")
         )),

        ("11-1-2", "練習題", "APCS 考前提醒函數 show_exam_tips()", 6, ("show_exam_tips",),
         lambda g: (
             (True, "show_exam_tips 考前提醒函數實作正確！")
             if (callable(g.get("show_exam_tips"))) or
                ("show_exam_tips" in history_str and "技巧" in history_str)
             else (False, "請依 PEP 8 命名規範定義 show_exam_tips() 並印出三點技巧！")
         )),

        ("11-1-2", "挑戰題", "自訂模擬伺服器狀態 check_server_status()", 6, ("check_server_status",),
         lambda g: (
             (True, "check_server_status 伺服器狀態函數實作正確！")
             if (callable(g.get("check_server_status"))) or
                ("check_server_status" in history_str and "NORMAL" in history_str)
             else (False, "請定義 check_server_status() 函數並連續呼叫兩次！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-3 程式執行順序：定義期與呼叫期追蹤 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-3", "填空題", "先定義後呼叫時序調整 trigger_alarm()", 5, ("trigger_alarm",),
         lambda g: (
             (True, "先定義後呼叫時序調整正確！")
             if (callable(g.get("trigger_alarm"))) or
                ("def trigger_alarm():" in history_str and "trigger_alarm()" in history_str)
             else (False, "請遵守先定義後呼叫原則，在 def trigger_alarm() 之後呼叫它！")
         )),

        ("11-1-3", "練習題", "多函數先後跳轉時序 step_one 與 step_two", 6, ("step_one", "step_two"),
         lambda g: (
             (True, "多函數跳轉時序定義正確！")
             if (callable(g.get("step_one")) and callable(g.get("step_two"))) or
                ("step_one" in history_str and "step_two" in history_str)
             else (False, "請定義 step_one() 與 step_two() 依序呼叫並印出時序！")
         )),

        ("11-1-3", "挑戰題", "巢狀時序追蹤與主流程 execution_log 記錄", 6, ("execution_log",),
         lambda g: (
             (True, "巢狀時序 execution_log 記錄驗證正確！")
             if (g.get("execution_log") == ["main_task start", "sub_task executed", "main_task end"]) or
                ("execution_log" in history_str and "sub_task executed" in history_str)
             else (False, "請透過 execution_log 依序記錄 main_task start -> sub_task executed -> main_task end！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-4 單一參數傳入與引數匹配 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-4", "填空題", "倒數計時函數單參數傳入 print_countdown(n)", 5, ("print_countdown",),
         lambda g: (
             (True, "倒數計時單參數填空正確！")
             if (callable(g.get("print_countdown"))) or
                ("def print_countdown" in history_str and "print_countdown(3)" in history_str)
             else (False, "請完成 print_countdown(n) 定義並傳入 3 進行呼叫！")
         )),

        ("11-1-4", "練習題", "個人化問候卡片 print_greeting_card(user_name)", 6, ("print_greeting_card",),
         lambda g: (
             (True, "個人化問候卡片函數實作正確！")
             if (callable(g.get("print_greeting_card"))) or
                ("print_greeting_card" in history_str and "親愛的" in history_str)
             else (False, "請定義 print_greeting_card(user_name) 並傳入人名測試！")
         )),

        ("11-1-4", "挑戰題", "幾何正方形圖形產生器 draw_square(side_length)", 6, ("draw_square",),
         lambda g: (
             (True, "正方形產生器函數實作正確！")
             if (callable(g.get("draw_square"))) or
                ("draw_square" in history_str and "*" in history_str)
             else (False, "請定義 draw_square(side_length) 印出邊長乘邊長的星號方陣！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-5 多參數位置對應 (Positional Arguments) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-1-5", "填空題", "多邊形周長多參數傳遞 print_polygon_perimeter", 5, ("print_polygon_perimeter",),
         lambda g: (
             (True, "多邊形周長多參數填空正確！")
             if (callable(g.get("print_polygon_perimeter"))) or
                ("print_polygon_perimeter" in history_str and "正六邊形" in history_str)
             else (False, "請呼叫 print_polygon_perimeter 並依序傳入名稱、邊數與邊長！")
         )),

        ("11-1-5", "練習題", "座標位移播報函數 announce_move(player, x, y, dx, dy)", 6, ("announce_move",),
         lambda g: (
             (True, "座標位移播報函數定義正確！")
             if (callable(g.get("announce_move"))) or
                ("announce_move" in history_str and "移動到" in history_str)
             else (False, "請定義 announce_move 接收 5 個參數並計算移動後的新座標！")
         )),

        ("11-1-5", "挑戰題", "自訂三維長方體體積報表 print_cuboid_volume", 5, ("print_cuboid_volume",),
         lambda g: (
             (True, "長方體體積報表函數正確！")
             if (callable(g.get("print_cuboid_volume"))) or
                ("print_cuboid_volume" in history_str and "體積" in history_str)
             else (False, "請定義 print_cuboid_volume(length, width, height) 計算並輸出體積！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-6 無回傳值函數與 None 預設回傳 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-1-6", "填空題", "動作型函數無 return 預設為 None 驗證 status is None", 5, ("status",),
         lambda g: (
             (True, "status is None 填空驗證正確！")
             if (g.get("status") is None and "mark_completed" in history_str) or
                ("status is None" in history_str)
             else (False, "請呼叫 mark_completed() 並驗證回傳的 status 是否為 None！")
         )),

        ("11-1-6", "練習題", "事件日誌動作函數 log_event 與 log_res is None 檢查", 6, ("log_event", "log_res"),
         lambda g: (
             (True, "log_event 動作型函數與 None 回傳檢查正確！")
             if (callable(g.get("log_event")) and g.get("log_res") is None) or
                ("log_event" in history_str and "log_res" in history_str)
             else (False, "請定義無 return 的 log_event 並以 log_res 接收驗證為 None！")
         )),

        ("11-1-6", "挑戰題", "驗證多個動作函數之傳回清單 results == [None, None]", 5, ("results",),
         lambda g: (
             (True, "多動作函數傳回清單驗證正確！")
             if (g.get("results") == [None, None]) or
                ("results" in history_str and "[None, None]" in history_str)
             else (False, "請將兩無 return 函數呼叫結果存入 results 串列，驗證其為 [None, None]！")
         ))
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
        badge = '🏆 完美滿分！你已經徹底攻克自訂函數與作用域核心技術，具備 APCS 實戰高手水準！'
    elif total_score >= 80:
        badge = '🌟 優秀！模組化概念與函數傳參掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本函數已建立，建議複習未通過的題目加強熟悉度！'
    else:
        badge = '💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 11-1：函數定義（def）、呼叫流程與參數傳入基礎 —— 自動評分報告")
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
        "unit": "11-1",
        "unit_title": "函數定義（def）、呼叫流程與參數傳入基礎",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_1.py",
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
auto_grade_unit_11_1()
