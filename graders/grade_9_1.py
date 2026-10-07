# ==============================================================================
# 🧪 《PythAPCS123》單元 9-1：二維陣列概念與座標元素存取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_1.py
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

def auto_grade_unit_9_1():
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
        # 9-1-1 二維陣列物理模型與座位宣告 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-1-1", "填空題", "宣告 3x2 座位表 seating", 5,
         lambda g: (
             (True, "seating 3x2 陣列宣告正確！")
             if ("seating" in g and isinstance(g.get("seating"), list) and len(g.get("seating")) == 3 and
                 len(g.get("seating")[0]) == 2 and "小明" in str(g.get("seating"))) or
                ("seating" in history_str and "小明" in history_str and "小強" in history_str)
             else (False, "請在 9-1-1 填空題完成 seating 3x2 座位表宣告！")
         )),

        ("9-1-1", "練習題", "手動宣告 2x3 整數陣列 grid 並印出兩列", 6,
         lambda g: (
             (True, "grid 2x3 整數陣列建立與兩列輸出正確！")
             if ("grid" in g and isinstance(g.get("grid"), list) and len(g.get("grid")) == 2 and
                 g.get("grid")[0] == [1, 2, 3] and g.get("grid")[1] == [4, 5, 6]) or
                ("[1, 2, 3]" in history_str and "[4, 5, 6]" in history_str) or
                ("grid[0]" in history_clean and "grid[1]" in history_clean)
             else (False, "請建立 2x3 整數陣列 grid = [[1, 2, 3], [4, 5, 6]] 並分別印出第 0 與 1 列！")
         )),

        ("9-1-1", "挑戰題", "2x4 巴士座位分佈 bus_seats", 5,
         lambda g: (
             (True, "2x4 巴士座位陣列宣告與印出正確！")
             if ("bus_seats" in g and isinstance(g.get("bus_seats"), list) and len(g.get("bus_seats")) == 2 and len(g.get("bus_seats")[0]) == 4) or
                ("bus_seats" in history_str and ("Empty" in history_str or "empty" in history_str or "print" in history_str))
             else (False, "請宣告 2x4 的字串陣列 bus_seats 並依序印出兩排座位！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-2 網格尺寸掌握：R 與 C (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-2", "填空題", "長度函式計算 R, C 與 total_cells", 5,
         lambda g: (
             (True, "尺寸測量與總格子數計算正確！")
             if (g.get("R") == 3 and g.get("C") == 4 and g.get("total_cells") == 12) or
                ("len(map_data)" in history_clean and "len(map_data[0])" in history_clean)
             else (False, "請在 9-1-2 填空題填入 len(map_data) 與 len(map_data[0])！")
         )),

        ("9-1-2", "練習題", "計算矩陣維度 R, C 與格式化輸出", 6,
         lambda g: (
             (True, "矩陣維度 R, C 計算與格式化字串輸出正確！")
             if ("維度:" in history_str or ("R = len(matrix)" in history_str and "C = len(matrix[0])" in history_str)) or
                ("3列2行" in history_str or "6" in history_str)
             else (False, "請計算 matrix 的 R 與 C，並輸出『維度: R列C行, 總數: 總數值』！")
         )),

        ("9-1-2", "挑戰題", "棋盤方陣判定 (R == C)", 6,
         lambda g: (
             (True, "方陣網格判定邏輯正確！")
             if ("方陣網格: True" in history_str or "R == C" in history_clean or "R==C" in history_clean)
             else (False, "請測量 8x8 棋盤尺寸，判斷 R == C 並輸出『方陣網格: True』！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-3 整列提取 vs 單格存取 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-3", "填空題", "整列提取 row_1 與單格 student", 5,
         lambda g: (
             (True, "整列 row_1 與單格 student 存取正確！")
             if (g.get("row_1") == ["David", "Eva", "Frank"] and g.get("student") == "Frank") or
                ("classroom[1]" in history_clean and "classroom[1][2]" in history_clean)
             else (False, "請在 9-1-3 填空題填入 classroom[1] 與 classroom[1][2]！")
         )),

        ("9-1-3", "練習題", "成績矩陣第 0 列總和與單格提取", 6,
         lambda g: (
             (True, "第 0 列總和與 grades[2][1] 取值正確！")
             if ("sum(grades[0])" in history_clean or "60" in history_str) and
                ("grades[2][1]" in history_clean or "80" in history_str)
             else (False, "請計算 sum(grades[0]) 並取出 grades[2][1] 印出！")
         )),

        ("9-1-3", "挑戰題", "水果清單第 1 列長度與成員檢查", 6,
         lambda g: (
             (True, "第 1 列長度統計與 in 關鍵字檢查正確！")
             if ("芭樂" in history_str and ("in items[1]" in history_clean or "len(items[1])" in history_clean or "True" in history_str))
             else (False, "請印出 items[1] 的長度，並檢查 '芭樂' 是否在 items[1] 中！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-4 座標定位存取：grid[r][c] (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-4", "填空題", "井字棋盤四個角落 corners", 5,
         lambda g: (
             (True, "井字棋盤四角座標取值正確！")
             if (g.get("corners") == ["X", "O", "O", "X"]) or
                ("board[0][0]" in history_clean and "board[0][2]" in history_clean and
                 "board[2][0]" in history_clean and "board[2][2]" in history_clean)
             else (False, "請在 9-1-4 填空題填入四個角落座標 (0,0), (0,2), (2,0), (2,2)！")
         )),

        ("9-1-4", "練習題", "數值矩陣四角加總 corner_sum", 6,
         lambda g: (
             (True, "四角落元素加總計算正確！")
             if (g.get("corner_sum") == 20 or "四角總和: 20" in history_str or
                 ("data[0][0]" in history_clean and "data[2][2]" in history_clean))
             else (False, "請計算 data 四個角落元素的總和（預期為 20）！")
         )),

        ("9-1-4", "挑戰題", "十字中心五格數值總和", 6,
         lambda g: (
             (True, "十字中心與上下左右五格加總正確！")
             if ("(1, 1)" in history_str or "matrix[1][1]" in history_clean or
                 ("matrix[0][1]" in history_clean and "matrix[2][1]" in history_clean))
             else (False, "請加總中心點 (1,1) 與上下左右四格的數值！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-5 網格元素原地修改：grid[r][c] = val (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-5", "填空題", "庫存網格修改 inventory[0][1] = 50", 5,
         lambda g: (
             (True, "庫存單格原地修改正確！")
             if (g.get("inventory") and g.get("inventory")[0][1] == 50) or
                ("inventory[0][1]=50" in history_clean or "inventory[0][1] = 50" in history_str)
             else (False, "請在 9-1-5 填空題完成 inventory[0][1] = 50！")
         )),

        ("9-1-5", "練習題", "3x3 全 0 矩陣三點原地修改 (0,0), (1,1), (2,2)", 6,
         lambda g: (
             (True, "三處座標原地賦值正確！")
             if (g.get("grid") and g.get("grid")[0][0] == 1 and g.get("grid")[1][1] == 5 and g.get("grid")[2][2] == 9) or
                ("grid[0][0]=1" in history_clean and "grid[1][1]=5" in history_clean and "grid[2][2]=9" in history_clean) or
                ("[1, 0, 0]" in history_str and "[0, 5, 0]" in history_str and "[0, 0, 9]" in history_str)
             else (False, "請將 grid 的 (0,0) 改為 1、(1,1) 改為 5、(2,2) 改為 9！")
         )),

        ("9-1-5", "挑戰題", "打地鼠地圖三處冒頭原地替換為 'M'", 6,
         lambda g: (
             (True, "打地鼠地圖三處座標原地修改為 'M' 正確！")
             if ("grid[0][3] = 'M'" in history_str or 'grid[0][3] = "M"' in history_str or
                 'grid[1][1] = "M"' in history_str or "M" in history_str)
             else (False, "請將 (0,3), (1,1), (2,0) 原地修改為 'M' 並印出地圖！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-6 負向索引定位與維度混淆防禦 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-1-6", "填空題", "負向索引存取 last_item 與 second_last_first", 5,
         lambda g: (
             (True, "負向索引定位取值正確！")
             if (g.get("last_item") == 20 and g.get("second_last_first") == 11) or
                ("data[-1][-1]" in history_clean and "data[-2][0]" in history_clean)
             else (False, "請在 9-1-6 填空題填入 data[-1][-1] 與 data[-2][0]！")
         )),

        ("9-1-6", "練習題", "末列首項與末項相加總和", 6,
         lambda g: (
             (True, "末列負向索引兩數相加計算正確！")
             if ("arr[-1][0]" in history_clean and "arr[-1][-1]" in history_clean) or
                ("40" in history_str or "總和: 40" in history_str)
             else (False, "請讀取 arr[-1][0] 與 arr[-1][-1] 並印出兩數總和！")
         )),

        ("9-1-6", "挑戰題", "負向索引元素對調交換 (values[-1][-1] 與 values[-2][-2])", 5,
         lambda g: (
             (True, "負向索引元素對調賦值正確！")
             if ("values[-1][-1]" in history_clean and "values[-2][-2]" in history_clean and "=" in history_str)
             else (False, "請使用負向索引將倒數第一列末項與倒數第二列倒數第二項對調！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-1：二維陣列概念與座標元素存取 —— 自動評分報告")
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
        "unit_id": "9-1",
        "unit_name": "二維陣列概念與座標元素存取",
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
        filename = f"grade_report_9_1.json"
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
    auto_grade_unit_9_1()
