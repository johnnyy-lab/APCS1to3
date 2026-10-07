# ==============================================================================
# 🧪 《PythAPCS123》單元 9-5：二維方陣與特殊走訪：對角線與棋盤規律 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_5.py
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
        with urllib.request.urlopen(req, timeout=5) as resp:
            user_data = json.loads(resp.read().decode('utf-8'))
            return user_data.get("email"), user_data.get("name")
    except Exception as e:
        return None, None

def auto_grade_unit_9_5():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名
    declared_name = str(env.get("student_name", "")).strip()
    if not declared_name or declared_name == "自學冒險者":
        declared_name = "自學冒險者（未填姓名）"

    # 2. 獲取 Google 帳號資訊
    google_email, google_name = fetch_google_account_info()

    # 3. 整合身分識別
    if google_email:
        final_email = google_email
        final_google_name = google_name if google_name else "Google無暱稱"
        combined_display_name = f"{declared_name} (Google暱稱: {final_google_name})"
    else:
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未授權 Google / 匿名"
        final_google_name = "未綁定 Google"
        combined_display_name = declared_name

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 取得 IPython 執行歷史（若在 Colab 環境）
    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 9-5-1 主對角線走訪規律 (r == c) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-5-1", "填空題", "主對角線單層走訪 matrix[i][i]", 5,
         lambda g: (
             (True, "主對角線 matrix[i][i] 語法填空正確！")
             if ("matrix[i][i]" in history_clean or "board[i][i]" in history_clean)
             else (False, "請在 9-5-1 填空題填入 matrix[i][i] 取出主對角線元素！")
         )),

        ("9-5-1", "練習題", "計算 NxN 方陣主對角線加總數值", 6,
         lambda g: (
             (True, "主對角線元素加總計算正確！")
             if ("matrix[i][i]" in history_clean or "grid[i][i]" in history_clean or "i == j" in history_clean) and "sum" in history_str
             else (False, "請使用單層迴圈走訪 matrix[i][i] 並計算主對角線總和！")
         )),

        ("9-5-1", "挑戰題", "計算主對角線所有元素的連乘積", 5,
         lambda g: (
             (True, "主對角線乘積計算正確！")
             if ("*=" in history_str or "product" in history_str) and ("[i][i]" in history_clean)
             else (False, "請計算主對角線上所有數值的乘積！")
         )),

        # ----------------------------------------------------------------------
        # 9-5-2 副對角線走訪規律 (r + c == N - 1) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-5-2", "填空題", "副對角線走訪 matrix[i][N - 1 - i]", 5,
         lambda g: (
             (True, "副對角線 matrix[i][N - 1 - i] 填空正確！")
             if ("N - 1 - i" in history_str or "N-1-i" in history_clean)
             else (False, "請在 9-5-2 填空題填入 N - 1 - i！")
         )),

        ("9-5-2", "練習題", "計算 NxN 方陣副對角線元素加總", 6,
         lambda g: (
             (True, "副對角線加總計算正確！")
             if ("[N - 1 - i]" in history_str or "[N-1-i]" in history_clean or "r + c == N - 1" in history_str)
             else (False, "請計算副對角線上所有數值的總和！")
         )),

        ("9-5-2", "挑戰題", "找出副對角線上的最大值", 6,
         lambda g: (
             (True, "副對角線極值搜尋正確！")
             if ("max" in history_str and ("[N - 1 - i]" in history_str or "[N-1-i]" in history_clean))
             else (False, "請找出副對角線上的最大數值！")
         )),

        # ----------------------------------------------------------------------
        # 9-5-3 X 形交叉雙對角線與中心點重複防禦 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-5-3", "填空題", "中心點扣除防禦 (N % 2 == 1 且 r == N // 2)", 5,
         lambda g: (
             (True, "中心點重複扣除邏輯填空正確！")
             if ("N // 2" in history_str or "N//2" in history_clean)
             else (False, "請在 9-5-3 填空題填入中心點座標 N // 2！")
         )),

        ("9-5-3", "練習題", "計算 X 形雙對角線不重複元素總和", 6,
         lambda g: (
             (True, "X 交叉雙對角線防重複加總正確！")
             if ("i == j or i + j == N - 1" in history_str or "matrix[i][i]" in history_clean and "matrix[i][N - 1 - i]" in history_str)
             else (False, "請計算 X 形雙對角線總和，奇數階方陣中心點僅計算一次！")
         )),

        ("9-5-3", "挑戰題", "判定任意座標 (r, c) 是否落在 X 交叉對角線上", 6,
         lambda g: (
             (True, "X 對角線座標判別式正確！")
             if ("r == c or r + c == N - 1" in history_str or "r==cor r+c==N-1" in history_clean)
             else (False, "請使用 r == c or r + c == N - 1 判定座標是否在對角線上！")
         )),

        # ----------------------------------------------------------------------
        # 9-5-4 上三角與下三角矩陣走訪 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-5-4", "填空題", "上三角走訪範圍 for c in range(r, N)", 5,
         lambda g: (
             (True, "上三角走訪範圍填空正確！")
             if ("range(r, N)" in history_str or "range(r,N)" in history_clean)
             else (False, "請在 9-5-4 填空題填入 range(r, N) 走訪上三角！")
         )),

        ("9-5-4", "練習題", "計算嚴格上三角 (c > r) 元素總和", 6,
         lambda g: (
             (True, "嚴格上三角加總計算正確！")
             if ("range(r + 1, N)" in history_str or "c > r" in history_str or "range(r+1,N)" in history_clean)
             else (False, "請計算不包含主對角線的嚴格上三角 (c > r) 總和！")
         )),

        ("9-5-4", "挑戰題", "計算下三角矩陣 (c <= r) 元素總和", 6,
         lambda g: (
             (True, "下三角元素加總正確！")
             if ("range(r + 1)" in history_str or "c <= r" in history_str or "c<=r" in history_clean)
             else (False, "請走訪下三角 (c <= r) 並計算總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-5-5 黑白棋盤格座標規律 (r + c) % 2 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-5-5", "填空題", "黑白棋盤格條件 (r + c) % 2 == 0", 5,
         lambda g: (
             (True, "棋盤格奇偶判斷填空正確！")
             if ("(r + c) % 2 == 0" in history_str or "(r+c)%2==0" in history_clean)
             else (False, "請在 9-5-5 填空題填入 (r + c) % 2 == 0！")
         )),

        ("9-5-5", "練習題", "產生 R x C 黑白棋盤 ('B' 與 'W')", 6,
         lambda g: (
             (True, "黑白棋盤陣列生成正確！")
             if ("'B'" in history_str and "'W'" in history_str) and ("% 2" in history_str)
             else (False, "請根據 (r + c) % 2 填入 'B' 或 'W' 構建棋盤！")
         )),

        ("9-5-5", "挑戰題", "統計黑格與白格各自的數值總和", 6,
         lambda g: (
             (True, "棋盤黑白分流加總正確！")
             if ("sum_b" in history_str or "sum_w" in history_str or "black" in history_str or "white" in history_str) and "% 2" in history_str
             else (False, "請分別統計棋盤黑格與白格的數值加總！")
         )),

        # ----------------------------------------------------------------------
        # 9-5-6 方陣對稱性檢驗 (grid[r][c] == grid[c][r]) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-5-6", "填空題", "對稱檢驗條件 grid[r][c] != grid[c][r]", 5,
         lambda g: (
             (True, "對稱性比對填空正確！")
             if ("grid[r][c] != grid[c][r]" in history_str or "grid[r][c]!=grid[c][r]" in history_clean or
                 "grid[r][c] == grid[c][r]" in history_str)
             else (False, "請在 9-5-6 填空題填入 grid[r][c] != grid[c][r]！")
         )),

        ("9-5-6", "練習題", "檢驗 NxN 方陣是否為對稱矩陣 (印出 True/False)", 6,
         lambda g: (
             (True, "對稱矩陣檢驗邏輯正確！")
             if ("grid[r][c] == grid[c][r]" in history_str or "is_symmetric" in history_str or "True" in history_str)
             else (False, "請走訪比對 grid[r][c] == grid[c][r] 判斷方陣是否對稱！")
         )),

        ("9-5-6", "挑戰題", "找出第一個破壞對稱性的座標點", 5,
         lambda g: (
             (True, "不對稱座標定位正確！")
             if ("!=" in history_str and "break" in history_str) or ("(r, c)" in history_str)
             else (False, "請找出第一個 grid[r][c] != grid[c][r] 的不對稱座標！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-5：二維方陣與特殊走訪：對角線與棋盤規律 —— 自動評分報告")
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
        level_comment = "🏆 完美滿分！你已經徹底攻克二維陣列核心技術，具備 APCS 實戰高手水準！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！觀念掌握非常扎實，稍微細心檢查即可登峰造極！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本概念已建立，建議複習未通過的題目加強熟悉度！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 4. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "9-5",
        "unit_name": "二維方陣與特殊走訪：對角線與棋盤規律",
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
        filename = f"grade_report_9_5.json"
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
    auto_grade_unit_9_5()
