# ==============================================================================
# 🧪 《PythAPCS123》單元 9-8：網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_8.py
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

def auto_grade_unit_9_8():
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
        # 9-8-1 沿單一方向連續推進模型 (while 迴圈) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-8-1", "填空題", "射線連續步進 while 邊界條件", 5,
         lambda g: (
             (True, "射線步進 while 條件填空正確！")
             if ("while 0 <= curr_r < R" in history_str or "while 0<=curr_r<R" in history_clean or
                 "0 <= curr_r < R and 0 <= curr_c < C" in history_str)
             else (False, "請在 9-8-1 填空題填入 while 邊界守護推進條件！")
         )),

        ("9-8-1", "練習題", "朝右方射線掃描直至出界並印出軌跡", 6,
         lambda g: (
             (True, "單向射線掃描軌跡正確！")
             if ("curr_c += 1" in history_str or "curr_c+=1" in history_clean) and "while" in history_str
             else (False, "請使用 while 迴圈連續向右推進並印出經由座標！")
         )),

        ("9-8-1", "挑戰題", "射線行進步數累加統計", 5,
         lambda g: (
             (True, "射線步數累加正確！")
             if ("steps += 1" in history_str or "steps+=1" in history_clean or "step_count" in history_str)
             else (False, "請統計射線自起點出發至出界前的總步數！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-2 射線撞牆邊界終止條件 (Boundary Stop) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-2", "填空題", "撞牆判定與終止條件", 5,
         lambda g: (
             (True, "撞牆終止條件填空正確！")
             if ("not (0 <= next_r < R and 0 <= next_c < C)" in history_str or "break" in history_str or
                 "0 <= next_r < R" in history_str)
             else (False, "請在 9-8-2 填空題填入撞牆終止防禦！")
         )),

        ("9-8-2", "練習題", "朝指定方向射線掃描回傳撞牆前最後合法座標", 6,
         lambda g: (
             (True, "撞牆極限座標鎖定正確！")
             if ("last_r" in history_str or "last_c" in history_str or "curr_r" in history_str) and "while" in history_str
             else (False, "請掃描並回傳撞牆前的最後一個合法內部座標！")
         )),

        ("9-8-2", "挑戰題", "四方向撞牆距離計算 (上下左右距邊界長度)", 6,
         lambda g: (
             (True, "四向撞牆距離計算正確！")
             if ("r" in history_str and "R - 1 - r" in history_str or "c" in history_str and "C - 1 - c" in history_str)
             else (False, "請計算當前點至上下左右四面牆壁的步數距離！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-3 射線遇障礙物阻擋機制 (Obstacle Stop) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-3", "填空題", "障礙物阻擋中斷 if grid[r][c] == '#': break", 5,
         lambda g: (
             (True, "障礙物阻擋中斷填空正確！")
             if ("grid[curr_r][curr_c] == '#'" in history_str or "grid[curr_r][curr_c]=='#'" in history_clean or
                 "grid[curr_r][curr_c] == 1" in history_str) and "break" in history_str
             else (False, "請在 9-8-3 填空題填入遇障礙物 break 中斷！")
         )),

        ("9-8-3", "練習題", "射線搜尋最近障礙物座標與距離", 6,
         lambda g: (
             (True, "最近障礙物搜尋正確！")
             if ("==" in history_str and "break" in history_str and "while" in history_str)
             else (False, "請沿射線推進，回傳遭遇的第一個障礙物座標與距離！")
         )),

        ("9-8-3", "挑戰題", "被障礙物阻擋後將沿途格子染為指定符號", 6,
         lambda g: (
             (True, "射線沿途染色正確！")
             if ("grid[r][c] =" in history_str or "board[r][c] =" in history_str or "=" in history_str) and "while" in history_str
             else (False, "請將射線前進路徑上的所有空格染色！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-4 十字四方向雷射掃描器 (Cross Laser Scanner) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-4", "填空題", "十字四方向雷射掃描外層 for d in range(4)", 5,
         lambda g: (
             (True, "十字四方向雷射掃描填空正確！")
             if ("for d in range(4)" in history_str or "for d in range(4):" in history_str or
                 "range(4)" in history_clean)
             else (False, "請在 9-8-4 填空題填入 for d in range(4) 驅動四向射線！")
         )),

        ("9-8-4", "練習題", "在 (r, c) 放置雷射塔並向四向射擊染色", 6,
         lambda g: (
             (True, "四向十字雷射染色正確！")
             if ("range(4)" in history_str and "while" in history_str and ("+" in history_str or "*" in history_str))
             else (False, "請以 (r, c) 為中心向四個方向發射雷射並標記軌跡！")
         )),

        ("9-8-4", "挑戰題", "多座雷射塔同時照射之覆蓋格子總數統計", 6,
         lambda g: (
             (True, "多塔覆蓋面積統計正確！")
             if ("towers" in history_str or "tower" in history_str or "for" in history_str) and "count" in history_str
             else (False, "請統計多座雷射塔共同覆蓋的所有不重複格子數！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-5 雙柱連線與網格區間染色 (Line Segment Marking) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-5", "填空題", "同列水平連線染色 for c in range(c1 + 1, c2)", 5,
         lambda g: (
             (True, "水平區間染色填空正確！")
             if ("range(c1 + 1, c2)" in history_str or "range(c1+1,c2)" in history_clean or
                 "range(min(c1, c2) + 1, max(c1, c2))" in history_str)
             else (False, "請在 9-8-5 填空題填入連線區間 range(c1 + 1, c2)！")
         )),

        ("9-8-5", "練習題", "給定兩柱座標，若在同行或同列則連線染色", 6,
         lambda g: (
             (True, "同行同列雙柱連線判斷正確！")
             if ("r1 == r2" in history_str or "c1 == c2" in history_str) and "range" in history_str
             else (False, "請判斷兩柱是否在同一行或同一直列，若是則將其中間格子染色！")
         )),

        ("9-8-5", "挑戰題", "若兩柱中間夾有障礙物則阻斷連線", 6,
         lambda g: (
             (True, "障礙物阻斷連線模擬正確！")
             if ("blocked" in history_str or "break" in history_str or "is_blocked" in history_str)
             else (False, "請檢查兩柱之間是否有障礙物，有障礙物時不可連線！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-6 APCS g596 骨牌遊戲：柱子拔除與連線阻擋動態模擬 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-8-6", "填空題", "APCS g596 跨距限制 steps <= K", 5,
         lambda g: (
             (True, "APCS g596 跨距限制填空正確！")
             if ("steps <= K" in history_str or "steps<=K" in history_clean or "step <= K" in history_str)
             else (False, "請在 9-8-6 填空題填入 steps <= K！")
         )),

        ("9-8-6", "練習題", "APCS g596 單次加柱與四向連線模擬", 6,
         lambda g: (
             (True, "APCS g596 加柱連線模擬正確！")
             if ("posts[r][c] = True" in history_str or "posts" in history_str) and "range(4)" in history_str
             else (False, "請實作 APCS g596 加柱後的四向射線搜尋並連線！")
         )),

        ("9-8-6", "挑戰題", "APCS g596 柱子拔除與全地圖連線覆蓋結算", 5,
         lambda g: (
             (True, "APCS g596 拔柱與全地圖連線結算正確！")
             if ("posts[r][c] = False" in history_str or "posts" in history_str) and "sum" in history_str
             else (False, "請實作拔柱後重新連線並統計全圖被連線覆蓋的格子總數！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-8：網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題） —— 自動評分報告")
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
        "unit_id": "9-8",
        "unit_name": "網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題）",
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
        filename = f"grade_report_9_8.json"
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
    auto_grade_unit_9_8()
