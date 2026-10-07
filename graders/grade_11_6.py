# ==============================================================================
# 🧪 《PythAPCS123》單元 11-6：線性遞迴：呼叫堆疊展開與終止條件 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_6.py
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

def auto_grade_unit_11_6(student_name=""):
    """
    單元 11-6：線性遞迴：呼叫堆疊展開與終止條件 自動評分主程式
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
        # 11-6-1 遞迴第一步：認識函數呼叫自己 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-1", "填空題", "遞迴倒數記數 rec_count 與終止條件 if n == 0", 5,
         lambda g: (
             (True, "rec_count 遞迴倒數填空正確！")
             if (callable(g.get("rec_count"))) or
                ("def rec_count" in history_str and "rec_count(n - 1)" in history_str)
             else (False, "請定義 rec_count 並在 n == 0 時終止，其餘呼叫 rec_count(n - 1)！")
         )),

        ("11-6-1", "練習題", "發射倒數線性遞迴 countdown_launch(n)", 6,
         lambda g: (
             (True, "countdown_launch 線性遞迴實作正確！")
             if (callable(g.get("countdown_launch"))) or
                ("countdown_launch" in history_str and "發射" in history_str)
             else (False, "請定義 countdown_launch 遞迴倒數至 1 並在終止時輸出發射！")
         )),

        ("11-6-1", "挑戰題", "遞迴連續區間印出 rec_print_range(start, end)", 6,
         lambda g: (
             (True, "rec_print_range 區間遞迴實作正確！")
             if (callable(g.get("rec_print_range"))) or
                ("rec_print_range" in history_str)
             else (False, "請定義 rec_print_range 從 start 印至 end 遞迴推進！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-2 呼叫堆疊 (Call Stack) 模型：前序與後序 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-2", "填空題", "對稱鏡像遞迴 mirror_box 與堆疊推入彈出", 5,
         lambda g: (
             (True, "mirror_box 鏡像堆疊填空正確！")
             if (callable(g.get("mirror_box"))) or
                ("mirror_box" in history_str and "進盒" in history_str or "出盒" in history_str)
             else (False, "請在遞迴呼叫前後分別印出標記，觀察堆疊先進後出對稱性！")
         )),

        ("11-6-2", "練習題", "視覺化堆疊層級 trace visualize_stack(n)", 6,
         lambda g: (
             (True, "visualize_stack 堆疊追蹤實作正確！")
             if (callable(g.get("visualize_stack"))) or
                ("visualize_stack" in history_str and "Push" in history_str or "Pop" in history_str)
             else (False, "請定義 visualize_stack 顯示堆疊深度的進入與返回時序！")
         )),

        ("11-6-2", "挑戰題", "遞迴巢狀方框符號包裹 nested_boxes(size)", 6,
         lambda g: (
             (True, "nested_boxes 巢狀符號包裹正確！")
             if (callable(g.get("nested_boxes"))) or
                ("nested_boxes" in history_str and "[" in history_str)
             else (False, "請定義 nested_boxes 遞迴產出巢狀對稱括號或符號！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-3 終止條件 (Base Case)：煞車皮機制 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-3", "填空題", "連續折半次數計算 count_halves 與煞車條件", 5,
         lambda g: (
             (True, "count_halves 煞車條件填空正確！")
             if (callable(g.get("count_halves")) and g.get("count_halves")(16) == 4) or
                ("count_halves" in history_str and "// 2" in history_str)
             else (False, "請定義 count_halves 在 n <= 1 時回傳 0，否則 1 + count_halves(n // 2)！")
         )),

        ("11-6-3", "練習題", "安全階梯減法遞迴 subtract_step(n, step)", 6,
         lambda g: (
             (True, "subtract_step 減法遞迴正確！")
             if (callable(g.get("subtract_step"))) or
                ("subtract_step" in history_str and "step" in history_str)
             else (False, "請定義 subtract_step 每次扣除 step 直到 <= 0 停止！")
         )),

        ("11-6-3", "挑戰題", "純手工遞迴求餘數 rec_mod(a, b)", 6,
         lambda g: (
             (True, "rec_mod 遞迴取餘數實作正確！")
             if (callable(g.get("rec_mod")) and g.get("rec_mod")(17, 5) == 2) or
                ("rec_mod" in history_str and "a < b" in history_str)
             else (False, "請實作 rec_mod：若 a < b 則回傳 a，否則回傳 rec_mod(a - b, b)！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-4 線性遞迴累計：次方與數列 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-4", "填空題", "遞迴計算 2 的次方 power_of_two(n)", 5,
         lambda g: (
             (True, "power_of_two 填空正確！")
             if (callable(g.get("power_of_two")) and g.get("power_of_two")(5) == 32) or
                (g.get("ans") == 32) or
                ("power_of_two(n - 1)" in history_str and "2 *" in history_str)
             else (False, "請實作 power_of_two：n == 0 回傳 1，其餘回傳 2 * power_of_two(n - 1)！")
         )),

        ("11-6-4", "練習題", "遞迴計算連續奇數和 sum_odd(n)", 6,
         lambda g: (
             (True, "sum_odd 奇數累加遞迴正確！")
             if (callable(g.get("sum_odd")) and g.get("sum_odd")(4) == 16) or
                ("sum_odd" in history_str and "2 * n - 1" in history_str)
             else (False, "請定義 sum_odd 遞迴計算前 n 個奇數總和 (1 + 3 + ... + 2n-1)！")
         )),

        ("11-6-4", "挑戰題", "遞迴等比數列總和 geometric_series(a, r, n)", 6,
         lambda g: (
             (True, "geometric_series 等比數列遞迴正確！")
             if (callable(g.get("geometric_series"))) or
                ("geometric_series" in history_str)
             else (False, "請實作 geometric_series(a, r, n) 遞迴計算首項 a 公比 r 前 n 項和！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-5 串列與字串的線性遞迴：切片縮小 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-6-5", "填空題", "遞迴串列加總 rec_sum_list(arr) 與 arr[1:]", 5,
         lambda g: (
             (True, "rec_sum_list 串列遞迴加總填空正確！")
             if (callable(g.get("rec_sum_list")) and g.get("rec_sum_list")([1, 2, 3, 4, 5]) == 15) or
                ("rec_sum_list(arr[1:])" in history_str or "arr[0] +" in history_str)
             else (False, "請在 rec_sum_list 使用 arr[0] + rec_sum_list(arr[1:]) 推進！")
         )),

        ("11-6-5", "練習題", "字元間插入連字號 insert_hyphens(s)", 6,
         lambda g: (
             (True, "insert_hyphens 字串遞迴處理正確！")
             if (callable(g.get("insert_hyphens")) and g.get("insert_hyphens")("APCS") == "A-P-C-S") or
                ("insert_hyphens" in history_str and "'-'" in history_str)
             else (False, "請定義 insert_hyphens 遞迴在每對相鄰字元間插入 '-'！")
         )),

        ("11-6-5", "挑戰題", "遞迴母音字元清洗 remove_vowels(s)", 5,
         lambda g: (
             (True, "remove_vowels 遞迴母音清洗正確！")
             if (callable(g.get("remove_vowels")) and g.get("remove_vowels")("apple") == "ppl") or
                ("remove_vowels" in history_str and "aeiou" in history_str)
             else (False, "請實作 remove_vowels 遞迴去除字串中所有的英文母音字母！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-6 遞迴深度限制與防爆防禦 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-6-6", "填空題", "安全深度下潛 safe_dive 與深度上限檢查", 5,
         lambda g: (
             (True, "safe_dive 深度限制填空正確！")
             if (callable(g.get("safe_dive"))) or
                ("depth >= max_safe_depth" in history_str or "safe_dive" in history_str)
             else (False, "請在 safe_dive 內於達到上限時提早煞車，杜絕無限遞迴！")
         )),

        ("11-6-6", "練習題", "遞迴累加安全防禦器 safe_rec_sum(n, limit=500)", 6,
         lambda g: (
             (True, "safe_rec_sum 安全防禦器實作正確！")
             if (callable(g.get("safe_rec_sum")) and g.get("safe_rec_sum")(1000) == -1) or
                ("safe_rec_sum" in history_str and "limit" in history_str)
             else (False, "請定義 safe_rec_sum：當 n > limit 時提早攔截回傳 -1！")
         )),

        ("11-6-6", "挑戰題", "遞迴與迴圈空間效能實測對比 loop_sum 與 rec_sum", 5,
         lambda g: (
             (True, "遞迴迴圈對比實驗完成！")
             if ("loop_sum" in history_str and "rec_sum" in history_str) or
                ("RecursionError" in history_str or "sys.getrecursionlimit" in history_str)
             else (False, "請分別實作 loop_sum 與 rec_sum 並比較極限深度下的表現！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-6：線性遞迴：呼叫堆疊展開與終止條件 —— 自動評分報告")
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
        "unit_id": "11-6",
        "unit_name": "線性遞迴：呼叫堆疊展開與終止條件",
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
        filename = f"grade_report_11_6.json"
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
    auto_grade_unit_11_6()
