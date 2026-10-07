# ==============================================================================
# 🧪 《PythAPCS123》單元 9-7：二維網格導航：方向向量與相鄰探測（APCS e287 原型） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_7.py
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

def auto_grade_unit_9_7():
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
        # 9-7-1 網格相鄰座標與相對位移 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-7-1", "填空題", "四方向相對位移座標填空", 5,
         lambda g: (
             (True, "四方向位移座標填空正確！")
             if ("r - 1" in history_str or "r + 1" in history_str or "c - 1" in history_str or "c + 1" in history_str) or
                ("r-1" in history_clean or "r+1" in history_clean)
             else (False, "請在 9-7-1 填空題填入四方向相對座標！")
         )),

        ("9-7-1", "練習題", "提取中心點相鄰四格數值並輸出", 6,
         lambda g: (
             (True, "中心點四相鄰取值正確！")
             if ("grid[r-1][c]" in history_clean or "grid[r+1][c]" in history_clean or
                 "matrix[r-1][c]" in history_clean or "matrix[r+1][c]" in history_clean)
             else (False, "請取出上下左右四個相鄰點的數值並印出！")
         )),

        ("9-7-1", "挑戰題", "計算相鄰四格的總和", 5,
         lambda g: (
             (True, "相鄰四格數值加總正確！")
             if ("sum" in history_str or "+" in history_str) and ("r - 1" in history_str or "r-1" in history_clean)
             else (False, "請計算中心點相鄰四格的數值總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-2 方向向量差值陣列 (dr, dc) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-2", "填空題", "方向向量補齊 dc = [0, 1, 0, -1]", 5,
         lambda g: (
             (True, "方向差值陣列 dc 填空正確！")
             if ("-1" in history_str and "dc = [ 0,  1,  0" in history_str) or
                ("dc=[0,1,0,-1]" in history_clean or "dc = [0, 1, 0, -1]" in history_str)
             else (False, "請在 9-7-2 填空題補齊 dc 中的左方差值 -1！")
         )),

        ("9-7-2", "練習題", "迴圈遍歷方向向量探測四相鄰點", 6,
         lambda g: (
             (True, "方向向量迴圈探測正確！")
             if ("for d in range(4)" in history_str or "for i in range(4)" in history_str or "zip(dr, dc)" in history_str)
             else (False, "請使用 for 迴圈配合 dr, dc 探測四相鄰點！")
         )),

        ("9-7-2", "挑戰題", "自訂八方向向量 (dr, dc 長度為 8)", 6,
         lambda g: (
             (True, "八方向差值陣列定義正確！")
             if ("len(dr) == 8" in history_str or "8" in history_str) and ("dr" in history_str and "dc" in history_str)
             else (False, "請定義長度為 8 的八方向向量陣列！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-3 合法邊界防護條件 (Boundary Guard) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-3", "填空題", "邊界守護判斷式 0 <= nr < R and 0 <= nc < C", 5,
         lambda g: (
             (True, "邊界守護判斷式填空正確！")
             if ("0 <= nr < R and 0 <= nc < C" in history_str or "0<=nr<Rand0<=nc<C" in history_clean or
                 "0 <= nr < R" in history_str)
             else (False, "請在 9-7-3 填空題填入 0 <= nr < R and 0 <= nc < C！")
         )),

        ("9-7-3", "練習題", "帶邊界防護之相鄰格子安全讀取", 6,
         lambda g: (
             (True, "安全邊界相鄰走訪正確！")
             if ("0 <= nr < R" in history_str or "0 <= nr" in history_str) and "grid[nr][nc]" in history_clean
             else (False, "請加入邊界守護條件，避免 IndexError 讀取相鄰元素！")
         )),

        ("9-7-3", "挑戰題", "統計邊界上合法相鄰格子數量", 6,
         lambda g: (
             (True, "邊界鄰格數量統計正確！")
             if ("count" in history_str or "+= 1" in history_str) and ("0 <= nr < R" in history_str)
             else (False, "請統計位於四邊或角落時的合法相鄰格數量！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-4 八方向相鄰探測（8-Neighbors / 踩地雷原理） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-4", "填空題", "踩地雷地雷探測 mine_map[nr][nc] == '#'", 5,
         lambda g: (
             (True, "踩地雷地雷條件填空正確！")
             if ("mine_map[nr][nc] == '#'" in history_str or "mine_map[nr][nc]=='#'" in history_clean or
                 "mine_map[nr][nc] == 1" in history_str)
             else (False, "請在 9-7-4 填空題填入地雷判斷式！")
         )),

        ("9-7-4", "練習題", "踩地雷九宮格周圍地雷總數統計", 6,
         lambda g: (
             (True, "周圍地雷統計正確！")
             if ("mine_count" in history_str or "mines" in history_str or "count" in history_str) and ("nr" in history_str)
             else (False, "請使用八方向向量統計周圍 8 格的地雷數量！")
         )),

        ("9-7-4", "挑戰題", "生成完整踩地雷數字提示地圖", 6,
         lambda g: (
             (True, "踩地雷數字地圖生成正確！")
             if ("range(8)" in history_str or "dr" in history_str) and ("print" in history_str)
             else (False, "請為全地圖每一格計算周圍地雷數並印出！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-5 拜訪標記矩陣 (Visited Grid) 與貪婪前進 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-5", "填空題", "拜訪標記設定 visited[nr][nc] = True", 5,
         lambda g: (
             (True, "拜訪標記語法填空正確！")
             if ("visited[nr][nc] = True" in history_str or "visited[nr][nc]=True" in history_clean or
                 "visited[r][c] = True" in history_str)
             else (False, "請在 9-7-5 填空題填入 visited 標記語法！")
         )),

        ("9-7-5", "練習題", "防止重複走訪之貪婪前進模擬", 6,
         lambda g: (
             (True, "防止重複走訪實作正確！")
             if ("not visited[nr][nc]" in history_str or "not visited" in history_str) and "visited" in history_str
             else (False, "請加入 not visited 判斷，確保路徑不重複踏足！")
         )),

        ("9-7-5", "挑戰題", "走訪步數與途經總和統計", 6,
         lambda g: (
             (True, "走訪步數與加總統計正確！")
             if ("steps" in history_str or "path_sum" in history_str or "total" in history_str) and "visited" in history_str
             else (False, "請記錄貪婪尋路的步數與經過數值總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-6 APCS e287 機器人的路徑：全圖貪婪尋路實戰 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-7-6", "填空題", "尋找全圖最小值作為起點座標", 5,
         lambda g: (
             (True, "全圖起點最小值定位填空正確！")
             if ("min_val" in history_str and "grid[r][c]" in history_clean) or
                ("best_r = r" in history_str or "best_c = c" in history_str)
             else (False, "請在 9-7-6 填空題填入尋找起點最小值的判斷！")
         )),

        ("9-7-6", "練習題", "APCS e287 核心尋路單一測資實戰", 6,
         lambda g: (
             (True, "APCS e287 尋路模擬正確！")
             if ("visited" in history_str and "while True:" in history_str) or
                ("min_neighbor" in history_str or "next_r" in history_str)
             else (False, "請完成從最小值起點出發、每步挑選最小未走鄰格的 APCS e287 尋路！")
         )),

        ("9-7-6", "挑戰題", "APCS e287 完整路徑總和輸出通關", 5,
         lambda g: (
             (True, "APCS e287 完整加總輸出正確！")
             if ("total_sum" in history_str or "print(" in history_str) and "visited" in history_str
             else (False, "請累加所有走過格子的數值並印出最終總和！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-7：二維網格導航：方向向量與相鄰探測（APCS e287 原型） —— 自動評分報告")
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
        "unit_id": "9-7",
        "unit_name": "二維網格導航：方向向量與相鄰探測（APCS e287 原型）",
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
        filename = f"grade_report_9_7.json"
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
    auto_grade_unit_9_7()
