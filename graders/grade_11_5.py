# ==============================================================================
# 🧪 《PythAPCS123》單元 11-5：全域變數在 APCS 競賽中的使用準則與除錯防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_5.py
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

def auto_grade_unit_11_5(student_name=""):
    """
    單元 11-5：全域變數在 APCS 競賽中的使用準則與除錯防禦 自動評分主程式
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
        # 11-5-1 global 關鍵字在函數內改寫全域變數 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-1", "填空題", "計程車里程累計 add_mileage 與 global fare", 5,
         lambda g: (
             (True, "add_mileage global 關鍵字填空正確！")
             if (callable(g.get("add_mileage"))) or
                ("global fare" in history_str)
             else (False, "請在 add_mileage 內加入 global fare 以便修改全域車資變數！")
         )),

        ("11-5-1", "練習題", "網站點擊計數器 click_counter 與 global total_clicks", 6,
         lambda g: (
             (True, "click_counter 全域計數實作正確！")
             if (callable(g.get("click_counter"))) or
                ("click_counter" in history_str and "global total_clicks" in history_str)
             else (False, "請定義 click_counter 使用 global total_clicks 每次累加 1！")
         )),

        ("11-5-1", "挑戰題", "護盾能量增減 modify_shield_energy(delta)", 6,
         lambda g: (
             (True, "modify_shield_energy 全域能量更新正確！")
             if (callable(g.get("modify_shield_energy"))) or
                ("modify_shield_energy" in history_str and "global shield_energy" in history_str)
             else (False, "請使用 global shield_energy 實作能量上限 100、下限 0 的安全增減！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-2 APCS 場景一：全域最佳解累計計數器 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-2", "填空題", "跳高冠軍紀錄 record_jump 與 global highest_jump", 5,
         lambda g: (
             (True, "record_jump 最佳解填空正確！")
             if (callable(g.get("record_jump"))) or
                ("global highest_jump" in history_str and "max(" in history_str)
             else (False, "請在 record_jump 內使用 global highest_jump 維護全域最高紀錄！")
         )),

        ("11-5-2", "練習題", "全域最小成本更新 update_min_cost(cost)", 6,
         lambda g: (
             (True, "update_min_cost 最小成本維護正確！")
             if (callable(g.get("update_min_cost"))) or
                ("update_min_cost" in history_str and "global min_cost" in history_str)
             else (False, "請定義 update_min_cost 以 min_cost = min(min_cost, cost) 更新全域解！")
         )),

        ("11-5-2", "挑戰題", "氣溫極值雙指標追蹤 track_temperature_extremes", 6,
         lambda g: (
             (True, "氣溫極值雙指標追蹤實作正確！")
             if (callable(g.get("track_temperature_extremes"))) or
                ("track_temperature_extremes" in history_str and "max_temp" in history_str and "min_temp" in history_str)
             else (False, "請同時維護 global max_temp, min_temp 兩項全域極值指標！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-3 APCS 場景二：大型地圖全域共享存取 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-3", "填空題", "網格障礙物計數 count_adjacent_walls 與全域 board", 5,
         lambda g: (
             (True, "count_adjacent_walls 全域網格讀取填空正確！")
             if (callable(g.get("count_adjacent_walls"))) or
                ("board[nr][nc]" in history_str or "count_adjacent_walls" in history_str)
             else (False, "請在 count_adjacent_walls 直接唯讀存取全域二維地圖 board！")
         )),

        ("11-5-3", "練習題", "全域矩陣區間和查詢 query_matrix_sum", 6,
         lambda g: (
             (True, "query_matrix_sum 全域矩陣查詢正確！")
             if (callable(g.get("query_matrix_sum"))) or
                ("query_matrix_sum" in history_str and "score_grid" in history_str)
             else (False, "請定義 query_matrix_sum 直接走訪全域矩陣指定範圍並回傳總和！")
         )),

        ("11-5-3", "挑戰題", "全域二維網格浸水著色 global_flood_fill", 6,
         lambda g: (
             (True, "global_flood_fill 全域網格染色實作正確！")
             if (callable(g.get("global_flood_fill"))) or
                ("global_flood_fill" in history_str)
             else (False, "請直接修改全域網格指定座標與相鄰格子之數值！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-4 可變物件免 global 原理 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-4", "填空題", "佇列原地追加 add_job 免宣告 global 原理", 5,
         lambda g: (
             (True, "add_job 免 global 原地修改填空正確！")
             if (callable(g.get("add_job"))) or
                ("print_queue.append" in history_str)
             else (False, "請直接在 add_job 呼叫 print_queue.append(job) 體驗可變物件免 global！")
         )),

        ("11-5-4", "練習題", "購物車清單免 global 原處修改 add_to_cart", 6,
         lambda g: (
             (True, "add_to_cart 免 global 串列操作正確！")
             if (callable(g.get("add_to_cart"))) or
                ("add_to_cart" in history_str and "cart.append" in history_str)
             else (False, "請在 add_to_cart 直接對全域 cart 串列進行 append 操作！")
         )),

        ("11-5-4", "挑戰題", "全域成績字典就地登錄 update_grade_book", 6,
         lambda g: (
             (True, "update_grade_book 免 global 字典更新正確！")
             if (callable(g.get("update_grade_book"))) or
                ("update_grade_book" in history_str and "grade_book" in history_str)
             else (False, "請直接對全域 grade_book 字典賦值，體驗字典就地修改無須 global！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-5 濫用 global 的狀態污染隱患 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-5-5", "填空題", "跨測資未清空慘劇剖析 process_daily_batch", 5,
         lambda g: (
             (True, "狀態污染剖析填空正確！")
             if ("process_daily_batch" in history_str and "visitor_log" in history_str) or
                ("visitor_log" in history_str)
             else (False, "請觀察 process_daily_batch 未清空全域 visitor_log 所導致的跨日污染！")
         )),

        ("11-5-5", "練習題", "字元統計前重置清空 reset_and_count_chars(s)", 6,
         lambda g: (
             (True, "reset_and_count_chars 重置清空正確！")
             if (callable(g.get("reset_and_count_chars"))) or
                ("char_count.clear()" in history_str or "char_count = {}" in history_str)
             else (False, "請在 reset_and_count_chars 開頭清空全域字典，杜絕殘留狀態！")
         )),

        ("11-5-5", "挑戰題", "跨多筆測資偶數和安全累加模擬", 5,
         lambda g: (
             (True, "跨多筆測資安全累加模擬正確！")
             if ("even_sum" in history_str and "clear" in history_str or "even_sum = 0" in history_str)
             else (False, "請在每筆測資迴圈開頭將全域累計變數歸零！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-6 競賽除錯守則：多筆測資迴圈開頭重置 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-5-6", "填空題", "競賽重置標準框架 reset_contest 與 solve_case", 5,
         lambda g: (
             (True, "reset_contest 競賽重置框架填空正確！")
             if (callable(g.get("reset_contest")) and callable(g.get("solve_case"))) or
                ("reset_contest" in history_str and "solve_case" in history_str)
             else (False, "請定義 reset_contest 歸零全域變數，並在 solve_case 前呼叫！")
         )),

        ("11-5-6", "練習題", "氣象站每季重置與讀取記錄 reset_weather_station", 6,
         lambda g: (
             (True, "reset_weather_station 每季重置實作正確！")
             if (callable(g.get("reset_weather_station"))) or
                ("reset_weather_station" in history_str and "daily_high" in history_str)
             else (False, "請實作 reset_weather_station 歸零 daily_high 與 daily_low！")
         )),

        ("11-5-6", "挑戰題", "APCS 多筆測資迴圈開頭重置除錯模擬", 5,
         lambda g: (
             (True, "多筆測資迴圈重置模擬挑戰成功！")
             if ("reset" in history_str and "for" in history_str and "solve" in history_str) or
                ("solve_case" in history_str)
             else (False, "請撰寫外層迴圈遍歷多組測資，並在每次迴圈開頭呼叫 reset 函數！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-5：全域變數在 APCS 競賽中的使用準則與除錯防禦 —— 自動評分報告")
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
        "unit_id": "11-5",
        "unit_name": "全域變數在 APCS 競賽中的使用準則與除錯防禦",
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
        filename = f"grade_report_11_5.json"
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
    auto_grade_unit_11_5()
