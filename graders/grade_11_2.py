# ==============================================================================
# 🧪 《PythAPCS123》單元 11-2：函數回傳值（return）、多值回傳與衛語句提早結束 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_2.py
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

def auto_grade_unit_11_2(student_name=""):
    """
    單元 11-2：函數回傳值（return）、多值回傳與衛語句提早結束 自動評分主程式
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
        # 11-2-1 return 關鍵字：交接計算結果 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-2-1", "填空題", "梯形面積函數 calc_trapezoid_area 與 return area", 5,
         lambda g: (
             (True, "梯形面積 return 填空正確！")
             if (callable(g.get("calc_trapezoid_area")) and g.get("calc_trapezoid_area")(4, 6, 5) == 25.0) or
                (g.get("result") == 25.0) or
                ("return area" in history_str)
             else (False, "請在 calc_trapezoid_area 內使用 return area 回傳計算結果！")
         )),

        ("11-2-1", "練習題", "曼哈頓距離計算函數 calc_manhattan_dist(x1, y1, x2, y2)", 6,
         lambda g: (
             (True, "曼哈頓距離計算函數實作正確！")
             if (callable(g.get("calc_manhattan_dist")) and
                 g.get("calc_manhattan_dist")(0, 0, 3, 4) == 7 and
                 g.get("calc_manhattan_dist")(2, -5, -1, 3) == 11) or
                ("calc_manhattan_dist" in history_str and "abs(" in history_str)
             else (False, "請實作 calc_manhattan_dist 並回傳兩點間曼哈頓距離！")
         )),

        ("11-2-1", "挑戰題", "連續鏈式呼叫計算立方表面積 calc_cube_surface_area", 6,
         lambda g: (
             (True, "立方體表面積鏈式計算正確！")
             if (callable(g.get("calc_cube_surface_area")) and g.get("calc_cube_surface_area")(3) == 54) or
                (g.get("ans") == 54) or
                ("calc_square_area" in history_str and "calc_cube_surface_area" in history_str)
             else (False, "請串接 calc_square_area 與 calc_cube_surface_area 計算邊長 3 的立方體表面積 54！")
         )),

        # ----------------------------------------------------------------------
        # 11-2-2 世紀迷思剖析：return vs print (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-2-2", "填空題", "破解世紀迷思：以 return max(num_list) 替換 print", 5,
         lambda g: (
             (True, "破解迷思 return max 填空正確！")
             if (callable(g.get("get_max_element")) and g.get("get_max_element")([45, 12, 89, 33]) == 89) or
                (g.get("is_passed") is True) or
                ("return max(" in history_str)
             else (False, "請將 print 改為 return 回傳最大值，使外部可正確進行條件比較！")
         )),

        ("11-2-2", "練習題", "字串清理與長度檢驗器 get_cleaned_length(raw_text)", 6,
         lambda g: (
             (True, "字串去除空白與長度檢驗器實作正確！")
             if (callable(g.get("get_cleaned_length")) and
                 g.get("get_cleaned_length")("  APCS Exam  ") == 9 and
                 g.get("get_cleaned_length")("Python") == 6) or
                ("get_cleaned_length" in history_str and "strip()" in history_str)
             else (False, "請定義 get_cleaned_length 使用 strip() 並回傳 len() 長度！")
         )),

        ("11-2-2", "挑戰題", "多步驟成績轉換管道 apply_curve 與 check_pass_status", 6,
         lambda g: (
             (True, "多步驟成績轉換管道實作正確！")
             if (callable(g.get("apply_curve")) and callable(g.get("check_pass_status")) and
                 g.get("check_pass_status")(g.get("apply_curve")(55)) == "PASS") or
                (g.get("final_status") == "PASS")
             else (False, "請定義 apply_curve 與 check_pass_status 串接調分與及格判定！")
         )),

        # ----------------------------------------------------------------------
        # 11-2-3 衛語句（Guard Clauses）：提早 return 攔截 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-2-3", "填空題", "票價衛語句攔截非法年齡 return -1", 5,
         lambda g: (
             (True, "票價衛語句防禦填空正確！")
             if (callable(g.get("calc_ticket_price")) and
                 g.get("calc_ticket_price")(-5) == -1 and
                 g.get("calc_ticket_price")(70) == 100) or
                ("return -1" in history_str and "age < 0" in history_str)
             else (False, "請在 calc_ticket_price 內使用衛語句對非法年齡提早 return -1！")
         )),

        ("11-2-3", "練習題", "網格座標合法性防守檢查 get_grid_value_safe", 6,
         lambda g: (
             (True, "網格座標安全越界防守檢查正確！")
             if (callable(g.get("get_grid_value_safe")) and
                 g.get("get_grid_value_safe")([[10, 20], [30, 40]], 0, 1) == 20 and
                 g.get("get_grid_value_safe")([[10, 20], [30, 40]], 2, 0) == -1) or
                ("get_grid_value_safe" in history_str and "return -1" in history_str)
             else (False, "請定義 get_grid_value_safe 以衛語句攔截越界座標並回傳 -1！")
         )),

        ("11-2-3", "挑戰題", "會員折價券多重守衛檢驗 calc_coupon_discount", 6,
         lambda g: (
             (True, "多重折價券衛語句防禦正確！")
             if (callable(g.get("calc_coupon_discount")) and
                 g.get("calc_coupon_discount")(500, "SAVE50") == 50 and
                 g.get("calc_coupon_discount")(800, "SAVE100") == 0 and
                 g.get("calc_coupon_discount")(1200, "SAVE100") == 100) or
                ("calc_coupon_discount" in history_str and "SAVE100" in history_str)
             else (False, "請實作 calc_coupon_discount 衛語句依序過濾消費金額、代碼與門檻！")
         )),

        # ----------------------------------------------------------------------
        # 11-2-4 多條件分支回傳完整性 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-2-4", "填空題", "正負零三向分類器 get_number_sign 完整分支 return", 5,
         lambda g: (
             (True, "三向分類器分支 return 填空正確！")
             if (callable(g.get("get_number_sign")) and
                 g.get("get_number_sign")(42) == "POSITIVE" and
                 g.get("get_number_sign")(-5) == "NEGATIVE" and
                 g.get("get_number_sign")(0) == "ZERO") or
                ("return \"NEGATIVE\"" in history_str or "return 'NEGATIVE'" in history_str)
             else (False, "請補齊 get_number_sign 分支回傳 \"NEGATIVE\" 與 \"ZERO\"！")
         )),

        ("11-2-4", "練習題", "APCS 題號分類評等 get_apcs_level(score)", 6,
         lambda g: (
             (True, "APCS 評等覆蓋分類函數正確！")
             if (callable(g.get("get_apcs_level")) and
                 g.get("get_apcs_level")(350) == "Level 4" and
                 g.get("get_apcs_level")(200) == "Level 3" and
                 g.get("get_apcs_level")(150) == "Level 2" and
                 g.get("get_apcs_level")(40) == "Level 1") or
                ("get_apcs_level" in history_str and "Level 4" in history_str)
             else (False, "請實作 get_apcs_level 完整覆蓋 Level 1 到 Level 4 四種分支！")
         )),

        ("11-2-4", "挑戰題", "剪刀石頭布勝負判定器 rps_game(player1, player2)", 6,
         lambda g: (
             (True, "剪刀石頭布判定器實作正確！")
             if (callable(g.get("rps_game")) and
                 g.get("rps_game")("R", "R") == "TIE" and
                 g.get("rps_game")("R", "S") == "PLAYER 1" and
                 g.get("rps_game")("S", "R") == "PLAYER 2") or
                ("rps_game" in history_str and "TIE" in history_str)
             else (False, "請定義 rps_game 回傳 TIE、PLAYER 1 或 PLAYER 2 完整判定勝負！")
         )),

        # ----------------------------------------------------------------------
        # 11-2-5 函數多值回傳與呼叫端解包 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-2-5", "填空題", "整數除法與餘數雙回傳 custom_divmod(a, b)", 5,
         lambda g: (
             (True, "custom_divmod 多值回傳填空正確！")
             if (callable(g.get("custom_divmod")) and g.get("custom_divmod")(17, 5) == (3, 2)) or
                (g.get("q") == 3 and g.get("r") == 2) or
                ("return quotient, remainder" in history_str or "returnquotient,remainder" in history_clean)
             else (False, "請在 custom_divmod 回傳 quotient, remainder 並解包給 q, r！")
         )),

        ("11-2-5", "練習題", "二維座標位移計算 move_coordinate(x, y, dx, dy)", 6,
         lambda g: (
             (True, "座標位移雙值回傳函數正確！")
             if (callable(g.get("move_coordinate")) and
                 g.get("move_coordinate")(10, 20, 3, -5) == (13, 15)) or
                ("move_coordinate" in history_str and "return new_x, new_y" in history_str)
             else (False, "請實作 move_coordinate 同時回傳 new_x, new_y！")
         )),

        ("11-2-5", "挑戰題", "多項目統計解包並求全距 analyze_prices", 5,
         lambda g: (
             (True, "價格分析三值回傳與解包正確！")
             if (callable(g.get("analyze_prices")) and
                 g.get("analyze_prices")([199, 450, 120, 880, 310]) == (120, 880, 760)) or
                (g.get("price_range") == 760) or
                ("analyze_prices" in history_str and "hi - lo" in history_str)
             else (False, "請實作 analyze_prices 回傳最低價、最高價與全距三項指標！")
         )),

        # ----------------------------------------------------------------------
        # 11-2-6 函數回傳布林值：Predicate Functions (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-2-6", "填空題", "三角形合法性布林判定 is_valid_triangle", 5,
         lambda g: (
             (True, "三角形合法性判定填空正確！")
             if (callable(g.get("is_valid_triangle")) and
                 g.get("is_valid_triangle")(3, 4, 5) is True and
                 g.get("is_valid_triangle")(1, 2, 3) is False) or
                ("a + c > b" in history_str and "b + c > a" in history_str)
             else (False, "請補齊 is_valid_triangle 中三組兩邊和大於第三邊的條件！")
         )),

        ("11-2-6", "練習題", "六的倍數判定函數 is_multiple_of_six(n)", 6,
         lambda g: (
             (True, "六的倍數布林判定函數實作正確！")
             if (callable(g.get("is_multiple_of_six")) and
                 g.get("is_multiple_of_six")(18) is True and
                 g.get("is_multiple_of_six")(9) is False and
                 g.get("is_multiple_of_six")(20) is False) or
                ("is_multiple_of_six" in history_str and "% 2 == 0" in history_str)
             else (False, "請定義 is_multiple_of_six 回傳 n % 2 == 0 and n % 3 == 0！")
         )),

        ("11-2-6", "挑戰題", "迴文字串與數值全能判定器 is_palindrome(val)", 5,
         lambda g: (
             (True, "全能迴文判定函數實作正確！")
             if (callable(g.get("is_palindrome")) and
                 g.get("is_palindrome")(12321) is True and
                 g.get("is_palindrome")("radar") is True and
                 g.get("is_palindrome")(12345) is False) or
                ("is_palindrome" in history_str and "[::-1]" in history_str)
             else (False, "請定義 is_palindrome 將輸入轉為字串並比較 s == s[::-1]！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-2：函數回傳值（return）、多值回傳與衛語句提早結束 —— 自動評分報告")
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
        "unit_id": "11-2",
        "unit_name": "函數回傳值（return）、多值回傳與衛語句提早結束",
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
        filename = f"grade_report_11_2.json"
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
    auto_grade_unit_11_2()
