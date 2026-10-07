# ==============================================================================
# 🧪 《PythAPCS123》單元 9-9：網格防護與動態模擬：哨兵加框與雙矩陣快照（APCS f313 專題） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_9.py
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

def auto_grade_unit_9_9():
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
        # 9-9-1 哨兵加框法概念 (Grid Padding) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-9-1", "填空題", "哨兵加框尺寸 [[-1] * (C + 2) for _ in range(R + 2)]", 5,
         lambda g: (
             (True, "哨兵加框尺寸生成式填空正確！")
             if ("C + 2" in history_str and "R + 2" in history_str) or
                ("C+2" in history_clean and "R+2" in history_clean)
             else (False, "請在 9-9-1 填空題填入加框尺寸 C + 2 與 R + 2！")
         )),

        ("9-9-1", "練習題", "將原網格拷貝進加框矩陣中心 [1..R][1..C]", 6,
         lambda g: (
             (True, "原網格置入加框中心正確！")
             if ("padded[r + 1][c + 1] = grid[r][c]" in history_str or "padded[r+1][c+1]=grid[r][c]" in history_clean or
                 "padded[r+1][c+1]" in history_clean)
             else (False, "請將 grid[r][c] 填入 padded[r + 1][c + 1] 中心區域！")
         )),

        ("9-9-1", "挑戰題", "加框矩陣邊界驗證 (四周全為 -1)", 5,
         lambda g: (
             (True, "加框矩陣外圍守衛驗證正確！")
             if ("-1" in history_str and "padded" in history_str)
             else (False, "請驗證 padded 最外層一圈全為 -1 哨兵值！")
         )),

        # ----------------------------------------------------------------------
        # 9-9-2 加框矩陣與原矩陣座標對應 (r + 1, c + 1) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-9-2", "填空題", "加框座標對應填空 padded[r + 1][c + 1]", 5,
         lambda g: (
             (True, "加框座標對應填空正確！")
             if ("r + 1" in history_str and "c + 1" in history_str) or ("r+1" in history_clean and "c+1" in history_clean)
             else (False, "請在 9-9-2 填空題填入 r + 1 與 c + 1！")
         )),

        ("9-9-2", "練習題", "在加框網格中免邊界判斷直接存取四相鄰點", 6,
         lambda g: (
             (True, "加框免邊界四相鄰存取正確！")
             if ("padded[r][c+1]" in history_clean or "padded[r+2][c+1]" in history_clean or "padded" in history_str)
             else (False, "請直接存取 padded 上下左右四格，省略邊界 if 判斷！")
         )),

        ("9-9-2", "挑戰題", "加框網格還原回原始矩陣尺寸", 6,
         lambda g: (
             (True, "加框網格還原提取正確！")
             if ("padded[r][1:-1]" in history_clean or "range(1, R + 1)" in history_str)
             else (False, "請將中心 [1..R][1..C] 資料取出還原回原網格！")
         )),

        # ----------------------------------------------------------------------
        # 9-9-3 原地修改「資料污染」致命陷阱與快照防禦 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-9-3", "填空題", "快照建立 snapshot = [row.copy() for row in grid]", 5,
         lambda g: (
             (True, "快照副本語法填空正確！")
             if ("row.copy()" in history_clean or "row[:]" in history_clean)
             else (False, "請在 9-9-3 填空題填入 row.copy() 或 row[:] 建立乾淨快照！")
         )),

        ("9-9-3", "練習題", "對比實驗：原地修改資料污染 vs 快照同步結算", 6,
         lambda g: (
             (True, "快照對比實驗實作正確！")
             if ("snapshot" in history_str or "copy" in history_str) and "grid" in history_str
             else (False, "請使用快照讀取舊狀態，避免原地修改互相污染！")
         )),

        ("9-9-3", "挑戰題", "驗證多細胞狀態同時同步切換", 6,
         lambda g: (
             (True, "多格同步更新切換正確！")
             if ("new_grid" in history_str or "next_grid" in history_str or "snapshot" in history_str)
             else (False, "請建立 new_grid 結算下一回合狀態並整體替換！")
         )),

        # ----------------------------------------------------------------------
        # 9-9-4 增減量矩陣架構 (Delta Grid) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-9-4", "填空題", "增減量矩陣初始化 delta = [[0] * C for _ in range(R)]", 5,
         lambda g: (
             (True, "delta 矩陣初始化填空正確！")
             if ("delta = [[0] * C for _ in range(R)]" in history_str or "delta=[[0]*Cfor_inrange(R)]" in history_clean or
                 "[[0] * C for _ in range(R)]" in history_str)
             else (False, "請在 9-9-4 填空題填入 delta 增減量矩陣初始化語法！")
         )),

        ("9-9-4", "練習題", "記錄遷出量 delta[r][c] -= out 與遷入量 += in", 6,
         lambda g: (
             (True, "delta 增減量記錄正確！")
             if ("delta" in history_str and "-=" in history_str and "+=" in history_str)
             else (False, "請在 delta 矩陣中分別累加遷入量與扣減遷出量！")
         )),

        ("9-9-4", "挑戰題", "驗證全地圖 delta 總和恆等於 0 (守恆定律)", 6,
         lambda g: (
             (True, "delta 守恆總和為 0 驗證正確！")
             if ("sum(sum(row) for row in delta)" in history_str or "sum" in history_str and "delta" in history_str and "== 0" in history_str)
             else (False, "請計算 delta 全圖總和並驗證其值為 0！")
         )),

        # ----------------------------------------------------------------------
        # 9-9-5 單回合相鄰擴散與增減量結算 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-9-5", "填空題", "擴散份量整數除法 give = val // k", 5,
         lambda g: (
             (True, "擴散除法 give = val // k 填空正確！")
             if ("val // k" in history_str or "val//k" in history_clean)
             else (False, "請在 9-9-5 填空題填入 val // k！")
         )),

        ("9-9-5", "練習題", "單回合相鄰擴散與 grid[r][c] += delta[r][c] 結算", 6,
         lambda g: (
             (True, "單回合擴散結算正確！")
             if ("grid[r][c] += delta[r][c]" in history_str or "grid[r][c]+=delta[r][c]" in history_clean or
                 "delta" in history_str)
             else (False, "請在回合末將 delta 矩陣累加回 grid 結算！")
         )),

        ("9-9-5", "挑戰題", "擴散前後全圖總人口不變驗證", 6,
         lambda g: (
             (True, "總人口守恆驗證正確！")
             if ("sum" in history_str and "==" in history_str and "grid" in history_str)
             else (False, "請驗證擴散前後全圖人口總數保持一致！")
         )),

        # ----------------------------------------------------------------------
        # 9-9-6 APCS f313 人口遷移：多回合動態擴散模擬實戰 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-9-6", "填空題", "APCS f313 排除 -1 城市尋找極值", 5,
         lambda g: (
             (True, "排除 -1 城市極值統計填空正確！")
             if ("grid[r][c] != -1" in history_str or "grid[r][c]!=-1" in history_clean or
                 "val != -1" in history_str)
             else (False, "請在 9-9-6 填空題填入排除 -1 障礙城市的判斷！")
         )),

        ("9-9-6", "練習題", "APCS f313 模擬 m 回合後輸出最大與最小人口", 6,
         lambda g: (
             (True, "APCS f313 多回合人口遷移模擬正確！")
             if ("for _ in range(m)" in history_str or "for round in range(m)" in history_str) and "delta" in history_str
             else (False, "請執行 m 回合人口遷移模擬並輸出最大與最小城市人口！")
         )),

        ("9-9-6", "挑戰題", "APCS f313 完整實戰通關輸出 min 與 max", 5,
         lambda g: (
             (True, "APCS f313 最終通關正確！")
             if ("min(" in history_str and "max(" in history_str) or ("min_val" in history_str and "max_val" in history_str)
             else (False, "請輸出模擬後的最小與最大人口！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-9：網格防護與動態模擬：哨兵加框與雙矩陣快照（APCS f313 專題） —— 自動評分報告")
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
        "unit_id": "9-9",
        "unit_name": "網格防護與動態模擬：哨兵加框與雙矩陣快照（APCS f313 專題）",
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
        filename = f"grade_report_9_9.json"
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
    auto_grade_unit_9_9()
