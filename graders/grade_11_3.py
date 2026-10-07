# ==============================================================================
# 🧪 《PythAPCS123》單元 11-3：參數傳遞機制與副作用防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_3.py
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

def auto_grade_unit_11_3(student_name=""):
    """
    單元 11-3：參數傳遞機制與副作用防禦 自動評分主程式
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
        # 11-3-1 不可變物件傳遞與外部接收 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-1", "填空題", "調薪函數不可變數值傳遞 give_raise 與 return", 5,
         lambda g: (
             (True, "give_raise 填空正確！")
             if (callable(g.get("give_raise")) and g.get("give_raise")(40000, 5000) == 45000) or
                (g.get("current_salary") == 45000) or
                ("return new_salary" in history_str or "give_raise(current_salary" in history_str)
             else (False, "請在 give_raise 內 return new_salary 並在主程式接收回傳值！")
         )),

        ("11-3-1", "練習題", "商品折扣計算 apply_discount(price, rate)", 6,
         lambda g: (
             (True, "apply_discount 折扣計算實作正確！")
             if (callable(g.get("apply_discount")) and
                 g.get("apply_discount")(1000, 0.8) == 800 and
                 g.get("apply_discount")(250, 0.75) == 187) or
                ("apply_discount" in history_str and "int(" in history_str)
             else (False, "請定義 apply_discount 計算 int(price * rate) 並回傳折後價！")
         )),

        ("11-3-1", "挑戰題", "安全字串加密 caesar_shift(text, shift)", 6,
         lambda g: (
             (True, "凱薩位移加密函數實作正確！")
             if (callable(g.get("caesar_shift")) and
                 g.get("caesar_shift")("ABC", 3) == "DEF" and
                 g.get("caesar_shift")("XYZ", 3) == "ABC") or
                ("caesar_shift" in history_str and "ord(" in history_str and "chr(" in history_str)
             else (False, "請實作 caesar_shift 回傳全新位移字串且原字串不受影響！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-2 可變物件傳遞：串列與字典原地修改 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-2", "填空題", "活動簽到簿原地追加 check_in 與 append", 5,
         lambda g: (
             (True, "check_in 串列追加填空正確！")
             if (callable(g.get("check_in"))) or
                ("attendees.append" in history_str)
             else (False, "請在 check_in 內呼叫 attendees.append(student_id) 就地修改！")
         )),

        ("11-3-2", "練習題", "串列成績加分函數 add_bonus_points(scores_list, bonus)", 6,
         lambda g: (
             (True, "add_bonus_points 串列原地加分正確！")
             if (callable(g.get("add_bonus_points"))) or
                ("add_bonus_points" in history_str and "+=" in history_str)
             else (False, "請定義 add_bonus_points 遍歷串列索引並就地增加 bonus 分數！")
         )),

        ("11-3-2", "挑戰題", "字典庫存原地更新 update_inventory(stock_dict, item, qty)", 6,
         lambda g: (
             (True, "update_inventory 字典原地更新正確！")
             if (callable(g.get("update_inventory"))) or
                ("update_inventory" in history_str and "stock_dict" in history_str)
             else (False, "請定義 update_inventory 就地累加或新增指定項目的庫存量！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-3 賦值遮蔽 vs 就地清空 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-3", "填空題", "辨析重新指向與原地清空 reset_scores 與 clear", 5,
         lambda g: (
             (True, "reset_scores 原地清空填空正確！")
             if (callable(g.get("reset_scores"))) or
                ("scores.clear()" in history_str)
             else (False, "請在 reset_scores 使用 scores.clear() 而非 scores = []！")
         )),

        ("11-3-3", "練習題", "原地移除偶數元素 clear_even_numbers(nums)", 6,
         lambda g: (
             (True, "clear_even_numbers 原地過濾正確！")
             if (callable(g.get("clear_even_numbers"))) or
                ("clear_even_numbers" in history_str and "% 2 == 0" in history_str)
             else (False, "請定義 clear_even_numbers 使用切片賦值或 remove 原地清空偶數！")
         )),

        ("11-3-3", "挑戰題", "物件參照追蹤與就地修改驗證", 6,
         lambda g: (
             (True, "參照追蹤與就地修改驗證正確！")
             if ("clear()" in history_str or "append(" in history_str) and ("id(" in history_str or "==" in history_str)
             else (False, "請驗證串列在函式內原地操作前後的記憶體位址 id() 行為！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-4 防禦性複製：.copy() 阻斷副作用 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-4", "填空題", "成績截尾總和與防禦性複製 trimmed_sum 與 copy()", 5,
         lambda g: (
             (True, "trimmed_sum copy() 填空正確！")
             if (callable(g.get("trimmed_sum"))) or
                ("arr.copy()" in history_str)
             else (False, "請在 trimmed_sum 內使用 arr.copy() 阻斷對外部串列的影響！")
         )),

        ("11-3-4", "練習題", "安全極端值過濾器 remove_outliers_safe(arr)", 6,
         lambda g: (
             (True, "remove_outliers_safe 安全過濾實作正確！")
             if (callable(g.get("remove_outliers_safe"))) or
                ("remove_outliers_safe" in history_str and "copy()" in history_str)
             else (False, "請使用 .copy() 複製串列後剔除最大與最小值並回傳新串列！")
         )),

        ("11-3-4", "挑戰題", "二維矩陣深層複製 deep_copy_matrix(matrix)", 6,
         lambda g: (
             (True, "二維矩陣深層複製函數實作正確！")
             if (callable(g.get("deep_copy_matrix"))) or
                ("deep_copy_matrix" in history_str and "copy()" in history_str)
             else (False, "請實作 deep_copy_matrix 逐列複製 [row.copy() for row in matrix]！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-5 參數預設值 (Default Parameters) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-3-5", "填空題", "自訂邊框文字預設參數 banner(text, border='*')", 5,
         lambda g: (
             (True, "banner 預設參數填空正確！")
             if (callable(g.get("banner"))) or
                ("border='*'" in history_str or "border = '*'" in history_str)
             else (False, "請為 banner 函數的 border 參數指定預設值 '*'！")
         )),

        ("11-3-5", "練習題", "次方計算預設參數 calc_power(base, exp=2)", 6,
         lambda g: (
             (True, "calc_power 預設參數定義正確！")
             if (callable(g.get("calc_power")) and
                 g.get("calc_power")(5) == 25 and
                 g.get("calc_power")(2, 3) == 8) or
                ("calc_power" in history_str and "exp=2" in history_str)
             else (False, "請定義 calc_power(base, exp=2) 使未給 exp 時預設求平方！")
         )),

        ("11-3-5", "挑戰題", "多重預設參數商品定價 calc_final_price", 5,
         lambda g: (
             (True, "calc_final_price 多重預設參數實作正確！")
             if (callable(g.get("calc_final_price"))) or
                ("calc_final_price" in history_str and "discount" in history_str)
             else (False, "請定義 calc_final_price(price, discount=1.0, is_vip=False)！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-6 陷阱防範：避免可變物件預設參數與 None 慣用法 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-3-6", "填空題", "安全待辦清單 create_todo 與 todo_list=None", 5,
         lambda g: (
             (True, "None 慣用法填空正確！")
             if (callable(g.get("create_todo"))) or
                ("todo_list is None" in history_str or "todo_list=None" in history_str)
             else (False, "請使用 todo_list=None 預設值並在函數內判定建立新清單 []！")
         )),

        ("11-3-6", "練習題", "學生成績登記簿安全預設值 record_student_grade", 6,
         lambda g: (
             (True, "record_student_grade 安全預設字典實作正確！")
             if (callable(g.get("record_student_grade"))) or
                ("record_student_grade" in history_str and "grade_dict is None" in history_str)
             else (False, "請以 grade_dict=None 作為預設參數，避免跨呼叫共享字典污染！")
         )),

        ("11-3-6", "挑戰題", "獨立容器安全建立 safe_box(item, container=None)", 5,
         lambda g: (
             (True, "safe_box 獨立容器建立正確！")
             if (callable(g.get("safe_box"))) or
                ("safe_box" in history_str and "container is None" in history_str)
             else (False, "請定義 safe_box 驗證兩次預設呼叫產出的容器互不干擾！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-3：參數傳遞機制與副作用防禦 —— 自動評分報告")
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
        "unit_id": "11-3",
        "unit_name": "參數傳遞機制與副作用防禦",
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
        filename = f"grade_report_11_3.json"
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
    auto_grade_unit_11_3()
