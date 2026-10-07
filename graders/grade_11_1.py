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
from datetime import datetime

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ------------------------------------------------------------------------------
# 🌐 雲端後台成績記錄端點（已綁定 Google 試算表 Webhook）
# ------------------------------------------------------------------------------
LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"

def fetch_google_account_info():
    """在 Google Colab 環境下嘗試透過官方 OAuth 取得登入者真實 Email 與 Google 暱稱"""
    try:
        from google.colab import auth
        print("🔐 正在連結 Google 帳號進行身分認證（若跳出授權彈窗，請點選你的 Google 帳號並按允許）...")
        auth.authenticate_user()
        
        import google.auth
        from google.auth.transport.requests import Request
        credentials, _ = google.auth.default(scopes=[
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ])
        credentials.refresh(Request())
        token = credentials.token
        
        req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            google_email = data.get("email", "")
            google_name = data.get("name", "")
            return google_email, google_name
    except Exception:
        return "", ""

def get_submission_env():
    """取得 Colab / 本地端全域變數與執行歷史代碼"""
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

def auto_grade_unit_11_1(student_name=""):
    """
    單元 11-1：函數定義（def）、呼叫流程與參數傳入基礎 自動評分主程式
    滿分 100 分：
    - 填空題 6 題，每題 5 分，共 30 分
    - 練習題 6 題，每題 6 分，共 36 分
    - 挑戰題 6 題，共 34 分 (前 4 題各 6 分，後 2 題各 5 分)
    """
    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    # 1. 取得使用者身分
    declared_name = student_name.strip() if student_name else ""
    if not declared_name:
        for var_name in ["student_name", "my_name", "user_name", "author"]:
            val = env.get(var_name)
            if isinstance(val, str) and val.strip():
                declared_name = val.strip()
                break

    google_email, google_name = fetch_google_account_info()

    # 顯示姓名決策
    if declared_name and google_name:
        combined_display_name = f"{declared_name} ({google_name})"
    elif declared_name:
        combined_display_name = declared_name
    elif google_name:
        combined_display_name = google_name
    else:
        combined_display_name = "自主學習冒險者"

    final_email = google_email if google_email else "未綁定 Google 帳號"
    final_google_name = google_name if google_name else "無"

    # 2. 評分測試案例 (共 18 題，合計 100 分)
    total_score = 0
    max_score = 100
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    test_cases = [
        # ----------------------------------------------------------------------
        # 11-1-1 為什麼需要函數？黑盒子概念 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-1", "填空題", "定義並呼叫印出標題函數 print_banner()", 5,
         lambda g: (
             (True, "print_banner 函數定義與呼叫正確！")
             if (callable(g.get("print_banner"))) or
                ("def print_banner():" in history_str and "print_banner()" in history_str)
             else (False, "請定義 def print_banner(): 並呼叫該函數！")
         )),

        ("11-1-1", "練習題", "自訂競技賽事結尾橫幅 print_game_summary()", 6,
         lambda g: (
             (True, "print_game_summary 函數實作正確！")
             if (callable(g.get("print_game_summary"))) or
                ("print_game_summary" in history_str and "GAME OVER" in history_str)
             else (False, "請定義可呼叫的 print_game_summary 函數並輸出橫幅！")
         )),

        ("11-1-1", "挑戰題", "設計多階層日誌排版 log_start 與 log_finish", 6,
         lambda g: (
             (True, "log_start 與 log_finish 多階層日誌函數實作正確！")
             if (callable(g.get("log_start")) and callable(g.get("log_finish"))) or
                ("log_start" in history_str and "log_finish" in history_str)
             else (False, "請定義 log_start() 與 log_finish() 兩函數並模擬日誌輸出！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-2 函數的定義（def）、命名規範與呼叫 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-2", "填空題", "修正 def 與括號呼叫 show_system_alert()", 5,
         lambda g: (
             (True, "show_system_alert 定義與括號呼叫正確！")
             if (callable(g.get("show_system_alert"))) or
                ("show_system_alert()" in history_str and "def show_system_alert():" in history_str)
             else (False, "請補上 def 關鍵字與 show_system_alert() 括號進行呼叫！")
         )),

        ("11-1-2", "練習題", "APCS 考前提醒函數 show_exam_tips()", 6,
         lambda g: (
             (True, "show_exam_tips 考前提醒函數實作正確！")
             if (callable(g.get("show_exam_tips"))) or
                ("show_exam_tips" in history_str and "技巧" in history_str)
             else (False, "請依 PEP 8 命名規範定義 show_exam_tips() 並印出三點技巧！")
         )),

        ("11-1-2", "挑戰題", "自訂模擬伺服器狀態 check_server_status()", 6,
         lambda g: (
             (True, "check_server_status 伺服器狀態函數實作正確！")
             if (callable(g.get("check_server_status"))) or
                ("check_server_status" in history_str and "NORMAL" in history_str)
             else (False, "請定義 check_server_status() 函數並連續呼叫兩次！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-3 程式執行順序：定義期與呼叫期追蹤 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-3", "填空題", "先定義後呼叫時序調整 trigger_alarm()", 5,
         lambda g: (
             (True, "先定義後呼叫時序調整正確！")
             if (callable(g.get("trigger_alarm"))) or
                ("def trigger_alarm():" in history_str and "trigger_alarm()" in history_str)
             else (False, "請遵守先定義後呼叫原則，在 def trigger_alarm() 之後呼叫它！")
         )),

        ("11-1-3", "練習題", "多函數先後跳轉時序 step_one 與 step_two", 6,
         lambda g: (
             (True, "多函數跳轉時序定義正確！")
             if (callable(g.get("step_one")) and callable(g.get("step_two"))) or
                ("step_one" in history_str and "step_two" in history_str)
             else (False, "請定義 step_one() 與 step_two() 依序呼叫並印出時序！")
         )),

        ("11-1-3", "挑戰題", "巢狀時序追蹤與主流程 execution_log 記錄", 6,
         lambda g: (
             (True, "巢狀時序 execution_log 記錄驗證正確！")
             if (g.get("execution_log") == ["main_task start", "sub_task executed", "main_task end"]) or
                ("execution_log" in history_str and "sub_task executed" in history_str)
             else (False, "請透過 execution_log 依序記錄 main_task start -> sub_task executed -> main_task end！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-4 單一參數傳入與引數匹配 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-1-4", "填空題", "倒數計時函數單參數傳入 print_countdown(n)", 5,
         lambda g: (
             (True, "倒數計時單參數填空正確！")
             if (callable(g.get("print_countdown"))) or
                ("def print_countdown" in history_str and "print_countdown(3)" in history_str)
             else (False, "請完成 print_countdown(n) 定義並傳入 3 進行呼叫！")
         )),

        ("11-1-4", "練習題", "個人化問候卡片 print_greeting_card(user_name)", 6,
         lambda g: (
             (True, "個人化問候卡片函數實作正確！")
             if (callable(g.get("print_greeting_card"))) or
                ("print_greeting_card" in history_str and "親愛的" in history_str)
             else (False, "請定義 print_greeting_card(user_name) 並傳入人名測試！")
         )),

        ("11-1-4", "挑戰題", "幾何正方形圖形產生器 draw_square(side_length)", 6,
         lambda g: (
             (True, "正方形產生器函數實作正確！")
             if (callable(g.get("draw_square"))) or
                ("draw_square" in history_str and "*" in history_str)
             else (False, "請定義 draw_square(side_length) 印出邊長乘邊長的星號方陣！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-5 多參數位置對應 (Positional Arguments) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-1-5", "填空題", "多邊形周長多參數傳遞 print_polygon_perimeter", 5,
         lambda g: (
             (True, "多邊形周長多參數填空正確！")
             if (callable(g.get("print_polygon_perimeter"))) or
                ("print_polygon_perimeter" in history_str and "正六邊形" in history_str)
             else (False, "請呼叫 print_polygon_perimeter 並依序傳入名稱、邊數與邊長！")
         )),

        ("11-1-5", "練習題", "座標位移播報函數 announce_move(player, x, y, dx, dy)", 6,
         lambda g: (
             (True, "座標位移播報函數定義正確！")
             if (callable(g.get("announce_move"))) or
                ("announce_move" in history_str and "移動到" in history_str)
             else (False, "請定義 announce_move 接收 5 個參數並計算移動後的新座標！")
         )),

        ("11-1-5", "挑戰題", "自訂三維長方體體積報表 print_cuboid_volume", 5,
         lambda g: (
             (True, "長方體體積報表函數正確！")
             if (callable(g.get("print_cuboid_volume"))) or
                ("print_cuboid_volume" in history_str and "體積" in history_str)
             else (False, "請定義 print_cuboid_volume(length, width, height) 計算並輸出體積！")
         )),

        # ----------------------------------------------------------------------
        # 11-1-6 無回傳值函數與 None 預設回傳 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-1-6", "填空題", "動作型函數無 return 預設為 None 驗證 status is None", 5,
         lambda g: (
             (True, "status is None 填空驗證正確！")
             if (g.get("status") is None and "mark_completed" in history_str) or
                ("status is None" in history_str)
             else (False, "請呼叫 mark_completed() 並驗證回傳的 status 是否為 None！")
         )),

        ("11-1-6", "練習題", "事件日誌動作函數 log_event 與 log_res is None 檢查", 6,
         lambda g: (
             (True, "log_event 動作型函數與 None 回傳檢查正確！")
             if (callable(g.get("log_event")) and g.get("log_res") is None) or
                ("log_event" in history_str and "log_res" in history_str)
             else (False, "請定義無 return 的 log_event 並以 log_res 接收驗證為 None！")
         )),

        ("11-1-6", "挑戰題", "驗證多個動作函數之傳回清單 results == [None, None]", 5,
         lambda g: (
             (True, "多動作函數傳回清單驗證正確！")
             if (g.get("results") == [None, None]) or
                ("results" in history_str and "[None, None]" in history_str)
             else (False, "請將兩無 return 函數呼叫結果存入 results 串列，驗證其為 [None, None]！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-1：函數定義（def）、呼叫流程與參數傳入基礎 —— 自動評分報告")
    print(f"👤 學生姓名: {combined_display_name}")
    print(f"📧 帳號識別: {final_email}")
    print(f"⏰ 評分時間: {timestamp_str}")
    print("=" * 72)

    passed_count = 0
    detailed_results = []

    for sub_id, q_type, title, weight, check_fn in test_cases:
        try:
            passed, msg = check_fn(env)
        except Exception as err:
            passed = False
            msg = f"評分檢測過程發生例外狀況: {err}"

        status_icon = "✅ 通過" if passed else "❌ 未通過"
        points = weight if passed else 0
        total_score += points
        if passed:
            passed_count += 1

        print(f"[{status_icon}] ({points:2d}/{weight:2d}分) {sub_id} {q_type} - {title}")
        print(f"       回饋: {msg}")

        detailed_results.append({
            "sub_unit": sub_id,
            "type": q_type,
            "title": title,
            "score": points,
            "max_score": weight,
            "passed": passed,
            "feedback": msg
        })

    print("-" * 72)
    print(f"🎯 總結成績: {total_score} / {max_score} 分 (通過題數: {passed_count}/{len(test_cases)})")

    # 等級評語
    if total_score == 100:
        level_comment = "🏆 完美滿分！你已經徹底攻克自訂函數與作用域核心技術，具備 APCS 實戰高手水準！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！模組化概念與函數傳參掌握非常扎實，稍微細心檢查即可登峰造極！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本函數已建立，建議複習未通過的題目加強熟悉度！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 4. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "11-1",
        "unit_name": "函數定義（def）、呼叫流程與參數傳入基礎",
        "student_name": declared_name,
        "google_name": final_google_name,
        "google_email": final_email,
        "score": total_score,
        "max_score": max_score,
        "passed_count": passed_count,
        "total_questions": len(test_cases),
        "comment": level_comment,
        "timestamp": timestamp_str,
        "details": detailed_results
    }

    try:
        filename = f"grade_report_11_1.json"
        with open(filename, "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)
        print(f"💾 本地成績報告已儲存至: {filename}")
    except Exception as e:
        print(f"⚠️ 本地儲存失敗: {e}")

    # 5. 上傳雲端 Webhook
    if LOG_WEBHOOK_URL and LOG_WEBHOOK_URL.startswith("http"):
        try:
            payload = json.dumps(report_data).encode("utf-8")
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in (200, 302):
                    print("🚀 成績已成功同步至教材團隊雲端學習資料庫！")
                else:
                    print(f"📡 雲端同步回應代碼: {response.status}")
        except Exception as e:
            print("💡 （雲端記錄通道離線或連線逾時，本地成績記錄依然完全有效）")

if __name__ == "__main__":
    auto_grade_unit_11_1()
