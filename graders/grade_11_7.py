# ==============================================================================
# 🧪 《PythAPCS123》單元 11-7：樹狀分支遞迴與數論演算法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_7.py
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

def auto_grade_unit_11_7(student_name=""):
    """
    單元 11-7：樹狀分支遞迴與數論演算法 自動評分主程式
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
        # 11-7-1 雙分支遞迴：一分二的展開樹 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-1", "填空題", "二元樹葉節點計數 count_leaves(depth)", 5,
         lambda g: (
             (True, "count_leaves 雙分支填空正確！")
             if (callable(g.get("count_leaves")) and g.get("count_leaves")(3) == 8) or
                ("2 * count_leaves" in history_str or "count_leaves(depth - 1) + count_leaves" in history_str)
             else (False, "請完成 count_leaves：depth == 0 回傳 1，否則分支呼叫兩側子樹！")
         )),

        ("11-7-1", "練習題", "雙分支印出符號樹 branch_shapes(n)", 6,
         lambda g: (
             (True, "branch_shapes 符號樹實作正確！")
             if (callable(g.get("branch_shapes"))) or
                ("branch_shapes" in history_str)
             else (False, "請定義 branch_shapes 展開雙分支結構並印出分支型態！")
         )),

        ("11-7-1", "挑戰題", "雙分支金幣累加樹 tree_coins(level)", 6,
         lambda g: (
             (True, "tree_coins 金幣累加樹正確！")
             if (callable(g.get("tree_coins")) and g.get("tree_coins")(3) == 7) or
                ("tree_coins" in history_str and "2 *" in history_str)
             else (False, "請實作 tree_coins：level == 1 回傳 1，其餘回傳 1 + 2 * tree_coins(level - 1)！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-2 經典費氏數列與爬樓梯 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-2", "填空題", "經典費氏數列 get_fib(n) 雙遞迴呼叫", 5,
         lambda g: (
             (True, "get_fib 費氏數列填空正確！")
             if (callable(g.get("get_fib")) and g.get("get_fib")(6) == 8) or
                (g.get("ans") == 8) or
                ("get_fib(n - 1) + get_fib(n - 2)" in history_str)
             else (False, "請在 get_fib 填入 get_fib(n - 1) + get_fib(n - 2)！")
         )),

        ("11-7-2", "練習題", "三分支變形數列 trib(n)", 6,
         lambda g: (
             (True, "trib 三分支變形數列實作正確！")
             if (callable(g.get("trib")) and g.get("trib")(4) == 7) or
                ("trib" in history_str and "trib(n - 1) + trib(n - 2) + trib(n - 3)" in history_str)
             else (False, "請定義 trib 遞迴加總前三項 trib(n-1) + trib(n-2) + trib(n-3)！")
         )),

        ("11-7-2", "挑戰題", "爬樓梯問題遞迴解 count_stair_ways(n)", 6,
         lambda g: (
             (True, "count_stair_ways 爬樓梯遞迴正確！")
             if (callable(g.get("count_stair_ways")) and g.get("count_stair_ways")(4) == 5) or
                ("count_stair_ways" in history_str)
             else (False, "請定義 count_stair_ways：n == 1 回傳 1，n == 2 回傳 2，其餘兩項相加！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-3 重疊子問題與記憶化查表 Memoization (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-3", "填空題", "記憶化查表消除重複計算 memo_fib(n, memo)", 5,
         lambda g: (
             (True, "memo_fib 記憶化填空正確！")
             if (callable(g.get("memo_fib"))) or
                ("if n in memo:" in history_str or "memo[n] = " in history_str)
             else (False, "請在 memo_fib 檢查若 n in memo 則直接回傳，否則算完存入 memo！")
         )),

        ("11-7-3", "練習題", "統計特定數值被重複計算次數 count_target_calls", 6,
         lambda g: (
             (True, "count_target_calls 重複呼叫統計正確！")
             if (callable(g.get("count_target_calls"))) or
                ("count_target_calls" in history_str and "target" in history_str)
             else (False, "請定義 count_target_calls 統計指定值在遞迴樹中出現的次數！")
         )),

        ("11-7-3", "挑戰題", "極限對抗：樸素費氏 vs 記憶化查表效能評比", 6,
         lambda g: (
             (True, "記憶化極限對抗實驗完成！")
             if ("memo" in history_str and "fib" in history_str) or
                ("time" in history_str or "call_count" in history_str)
             else (False, "請比較 slow_fib 與 memo_fib 計算大數時的呼叫次數與速度差異！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-4 歐幾里得輾轉相除法 GCD (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-4", "填空題", "輾轉相除法求最大公因數 fast_gcd(a, b)", 5,
         lambda g: (
             (True, "fast_gcd 輾轉相除填空正確！")
             if (callable(g.get("fast_gcd")) and g.get("fast_gcd")(48, 18) == 6) or
                ("fast_gcd(b, a % b)" in history_str)
             else (False, "請在 fast_gcd 填入 fast_gcd(b, a % b) 遞迴求公因數！")
         )),

        ("11-7-4", "練習題", "分數約分化簡器 simplify_fraction(num, den)", 6,
         lambda g: (
             (True, "simplify_fraction 分數約分實作正確！")
             if (callable(g.get("simplify_fraction")) and g.get("simplify_fraction")(12, 18) == (2, 3)) or
                ("simplify_fraction" in history_str and "// g" in history_str)
             else (False, "請使用 gcd 求出最大公因數 g 並回傳 (num // g, den // g)！")
         )),

        ("11-7-4", "挑戰題", "三個整數的最大公因數 gcd_three(a, b, c)", 6,
         lambda g: (
             (True, "gcd_three 三數最大公因數正確！")
             if (callable(g.get("gcd_three")) and g.get("gcd_three")(24, 36, 60) == 12) or
                ("gcd_three" in history_str and "fast_gcd" in history_str)
             else (False, "請運用結合律實作 gcd_three(a, b, c) = gcd(gcd(a, b), c)！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-5 快速冪運算遞迴版 (Fast Power) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-7-5", "填空題", "遞迴快速冪折半平方 rec_pow(base, exp)", 5,
         lambda g: (
             (True, "rec_pow 快速冪填空正確！")
             if (callable(g.get("rec_pow")) and g.get("rec_pow")(2, 10) == 1024) or
                ("rec_pow(base, exp // 2)" in history_str and "half * half" in history_str)
             else (False, "請在 rec_pow 計算 half = rec_pow(base, exp // 2) 並依奇偶平方！")
         )),

        ("11-7-5", "練習題", "取模快速冪運算 modular_pow(base, exp, mod)", 6,
         lambda g: (
             (True, "modular_pow 取模快速冪正確！")
             if (callable(g.get("modular_pow")) and g.get("modular_pow")(2, 10, 1000) == 24) or
                ("modular_pow" in history_str and "% mod" in history_str)
             else (False, "請定義 modular_pow 在每次乘法後皆 % mod，防止大數溢位！")
         )),

        ("11-7-5", "挑戰題", "快速冪與樸素累乘運算次數與耗時對比", 5,
         lambda g: (
             (True, "快速冪對比實驗挑戰成功！")
             if ("rec_pow" in history_str or "power" in history_str) and ("//" in history_str or "time" in history_str)
             else (False, "請對比 2^100 在迴圈 100 次乘法 vs 快速冪 7 次乘法之巨大落差！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-6 遞迴與迴圈選型思維 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-7-6", "填空題", "平方和選型對比 square_sum_loop 與 square_sum_rec", 5,
         lambda g: (
             (True, "平方和雙模式選型填空正確！")
             if (callable(g.get("square_sum_loop")) and callable(g.get("square_sum_rec"))) or
                ("square_sum_loop" in history_str and "square_sum_rec" in history_str)
             else (False, "請分別完成迴圈版與遞迴版平方和函數實作！")
         )),

        ("11-7-6", "練習題", "二分折半步數計算器 count_steps_loop 與 count_steps_rec", 6,
         lambda g: (
             (True, "折半查詢步數計算實作正確！")
             if (callable(g.get("count_steps_loop")) or callable(g.get("count_steps_rec"))) or
                ("count_steps" in history_str and "// 2" in history_str)
             else (False, "請實作折半次數計算器，計算長度 N 降至 1 的次數！")
         )),

        ("11-7-6", "挑戰題", "演算法選型診斷器 algorithm_advisor", 5,
         lambda g: (
             (True, "algorithm_advisor 選型診斷器正確！")
             if (callable(g.get("algorithm_advisor"))) or
                ("algorithm_advisor" in history_str and "RECURSION" in history_str or "LOOP" in history_str)
             else (False, "請定義 algorithm_advisor 依問題類型與資料規模給出適當演算法建議！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-7：樹狀分支遞迴與數論演算法 —— 自動評分報告")
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
        "unit_id": "11-7",
        "unit_name": "樹狀分支遞迴與數論演算法",
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
        filename = f"grade_report_11_7.json"
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
    auto_grade_unit_11_7()
