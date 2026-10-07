# ==============================================================================
# 🧪 《PythAPCS123》單元 9-3：二維陣列初始化與參照共用致命陷阱 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_3.py
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

def auto_grade_unit_9_3():
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
        # 9-3-1 淺拷貝參照共用致命陷阱 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-3-1", "填空題", "觀察 trap_grid 參照連動現象", 5,
         lambda g: (
             (True, "trap_grid 參照共用現象填空正確！")
             if ("trap_grid" in history_str and "[0]" in history_str) or ("trap_grid" in g)
             else (False, "請在 9-3-1 填空題執行並觀察 trap_grid 的參照連動！")
         )),

        ("9-3-1", "練習題", "刻意使用乘號建立 2x3 trap_matrix 並修改驗證", 6,
         lambda g: (
             (True, "trap_matrix 乘法陷阱驗證正確！")
             if ("trap_matrix" in history_str and "* 2" in history_str) or ("trap_matrix" in g)
             else (False, "請故意使用 [[0]*3]*2 建立 trap_matrix 並修改第 0 列元素觀察連動！")
         )),

        ("9-3-1", "挑戰題", "預測 trap[3][0] 數值", 5,
         lambda g: (
             (True, "trap 連動預測正確！")
             if ("15" in history_str or "trap[3][0]" in history_clean)
             else (False, "請預測執行 trap[0][0] += 5 後 trap[3][0] 的數值（為 15）！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-2 正確初始化黃金法則 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-2", "填空題", "列表生成式建立全 0 陣列 [[0]*C for _ in range(R)]", 5,
         lambda g: (
             (True, "二維全 0 陣列正確生成式填空正確！")
             if ("[[0]*Cfor_inrange(R)]" in history_clean or "[[0] * C for _ in range(R)]" in history_str)
             else (False, "請在 9-3-2 填空題填入 [[0] * C for _ in range(R)]！")
         )),

        ("9-3-2", "練習題", "正確建立 3x3 全 0 陣列並將 (1, 1) 改為 999", 6,
         lambda g: (
             (True, "獨立網格建立與單點修改驗證正確！")
             if ("999" in history_str and "for _ in range(R)" in history_str) or
                ("grid[1][1] = 999" in history_str or "grid[1][1]=999" in history_clean)
             else (False, "請使用生成式建立 3x3 全 0 網格，將 (1, 1) 改為 999，並確認其他列未被影響！")
         )),

        ("9-3-2", "挑戰題", "動態讀入 R, C 建立全 0 陣列並解包輸出", 6,
         lambda g: (
             (True, "動態建立全 0 陣列與解包輸出正確！")
             if ("print(*row)" in history_str and "for _ in range(R)" in history_str)
             else (False, "請動態讀入 R, C，使用列表生成式建立全 0 矩陣並逐列解包輸出！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-3 記憶體指標探測：id() 與 is (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-3", "填空題", "使用 id() 比對第 0 列與第 1 列記憶體", 5,
         lambda g: (
             (True, "id() 比對填空正確！")
             if ("id(my_grid[0])" in history_clean and "id(my_grid[1])" in history_clean)
             else (False, "請在 9-3-3 填空題填入 id(my_grid[0]) 與 id(my_grid[1])！")
         )),

        ("9-3-3", "練習題", "使用 is 運算子判斷 row 0 is row 1", 6,
         lambda g: (
             (True, "is 運算子判斷邏輯正確！")
             if (" is " in history_str and "test_grid[0]" in history_str) or ("False" in history_str)
             else (False, "請使用 is 運算子比對第 0 列與第 1 列是否為同一個物件！")
         )),

        ("9-3-3", "挑戰題", "迴圈巡檢所有相鄰列獨立性", 6,
         lambda g: (
             (True, "相鄰列 id 比對巡檢正確！")
             if ("is not" in history_str or "is" in history_str or "!=" in history_str) and "range" in history_str
             else (False, "請用迴圈巡檢相鄰各列是否全為獨立記憶體位址！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-4 布林標記地圖與符號地圖 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-4", "填空題", "初始化 visited 布林陣列全為 False", 5,
         lambda g: (
             (True, "visited 布林陣列初始化填空正確！")
             if ("[[False]*Cfor_inrange(R)]" in history_clean or "[[False] * C for _ in range(R)]" in history_str)
             else (False, "請在 9-3-4 填空題填入 [[False] * C for _ in range(R)]！")
         )),

        ("9-3-4", "練習題", "3x3 字元陣列 '.'，對角線改為 'O'", 6,
         lambda g: (
             (True, "符號地圖初始化與對角線修改正確！")
             if ("'O'" in history_str or '"O"' in history_str) and ("grid[0][0]" in history_clean or "i == j" in history_str or "range(3)" in history_str)
             else (False, "請初始化 3x3 '.' 網格，並將對角線三格原地修改為 'O'！")
         )),

        ("9-3-4", "挑戰題", "4x5 布林陣列最外圍一圈設為 True", 6,
         lambda g: (
             (True, "外圍邊界布林標記設定正確！")
             if ("True" in history_str and "False" in history_str) and ("visited" in history_str or "range" in history_str)
             else (False, "請將 4x5 布林陣列外圍邊界一圈設為 True，內部維持 False！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-5 動態規律填值 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-5", "填空題", "棋盤交錯網格公式 (r + c) % 2", 5,
         lambda g: (
             (True, "棋盤奇偶交錯公式填空正確！")
             if ("(r+c)%2" in history_clean or "(r + c) % 2" in history_str)
             else (False, "請在 9-3-5 填空題填入 (r + c) % 2！")
         )),

        ("9-3-5", "練習題", "2x3 規律填值 r * C + c + 1", 6,
         lambda g: (
             (True, "連續編號矩陣規律填值正確！")
             if ("r * C + c + 1" in history_str or "r*C+c+1" in history_clean or "r * 3 + c + 1" in history_str)
             else (False, "請建立 2x3 網格，每格填入 r * C + c + 1 並解包印出！")
         )),

        ("9-3-5", "挑戰題", "NxN 座標和矩陣 r + c", 6,
         lambda g: (
             (True, "NxN 座標和矩陣建立正確！")
             if ("r + c" in history_str or "r+c" in history_clean) and "print(*row)" in history_str
             else (False, "請建立 N x N 矩陣，每格值為 r + c 並解包印出！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-6 二維獨立深拷貝：[row[:] for row in grid] (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-3-6", "填空題", "切片深拷貝 [row[:] for row in base_grid]", 5,
         lambda g: (
             (True, "切片深拷貝語法填空正確！")
             if ("[row[:] for row in base_grid]" in history_str or "[row[:]forrowinbase_grid]" in history_clean or
                 "row[:]" in history_clean)
             else (False, "請在 9-3-6 填空題填入 [row[:] for row in base_grid]！")
         )),

        ("9-3-6", "練習題", "複製 src 至 dst 並修改驗證獨立性", 6,
         lambda g: (
             (True, "深拷貝獨立副本與修改驗證正確！")
             if ("dst = [row[:] for row in src]" in history_str or "[row[:] for row in src]" in history_str or
                 "dst[0][0]" in history_clean)
             else (False, "請深拷貝 dst = [row[:] for row in src]，修改 dst[0][0] 並確認 src 不受影響！")
         )),

        ("9-3-6", "挑戰題", "深拷貝迷宮並替換 'S' 與 'E' 為 '*'", 5,
         lambda g: (
             (True, "迷宮深拷貝與字元替換正確！")
             if ("maze_copy" in history_str and "*" in history_str and ("S" in history_str or "E" in history_str))
             else (False, "請深拷貝迷宮為 maze_copy，並將 'S' 與 'E' 替換為 '*'！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-3：二維陣列初始化與參照共用致命陷阱 —— 自動評分報告")
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
        "unit_id": "9-3",
        "unit_name": "二維陣列初始化與參照共用致命陷阱",
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
        filename = f"grade_report_9_3.json"
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
    auto_grade_unit_9_3()
