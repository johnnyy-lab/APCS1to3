# ==============================================================================
# 🧪 《PythAPCS123》單元 9-4：二維網格雙重走訪與行列統計 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_4.py
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

def auto_grade_unit_9_4():
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
        # 9-4-1 雙重迴圈時鐘模型與座標對生成 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-4-1", "填空題", "雙重迴圈走訪 range(R) 與 range(C)", 5,
         lambda g: (
             (True, "雙重迴圈走訪範圍填空正確！")
             if ("for r in range(R)" in history_str and "for c in range(C)" in history_str) or
                ("forrinrange(R)" in history_clean and "forcinrange(C)" in history_clean)
             else (False, "請在 9-4-1 填空題填入 range(R) 與 range(C)！")
         )),

        ("9-4-1", "練習題", "雙重迴圈逐一走訪並印出座標與值 (r, c): val", 6,
         lambda g: (
             (True, "雙重迴圈走訪印出元素正確！")
             if ("matrix[r][c]" in history_clean or "grid[r][c]" in history_clean) and "print" in history_str
             else (False, "請使用雙重迴圈走訪 matrix 並印出每個元素的座標與數值！")
         )),

        ("9-4-1", "挑戰題", "雙重迴圈印出『只有第 1 列 (r == 1)』的所有字元", 5,
         lambda g: (
             (True, "條件走訪過濾列索引正確！")
             if ("r == 1" in history_clean or "r==1" in history_clean) and "print" in history_str
             else (False, "請使用雙重迴圈搭配 if r == 1 印出第 1 列的所有字元！")
         )),

        # ----------------------------------------------------------------------
        # 9-4-2 橫列直接走訪與 sum(row) 極速列統計 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-4-2", "填空題", "直接走訪每一列並使用 sum(row)", 5,
         lambda g: (
             (True, "直接走訪與 sum(row) 填空正確！")
             if ("for row in sales" in history_str and "sum(row)" in history_clean) or
                ("sum(row)" in history_clean and "in sales" in history_str)
             else (False, "請在 9-4-2 填空題填入 for row in sales 與 sum(row)！")
         )),

        ("9-4-2", "練習題", "走訪每一列印出總和與平均值 (sum/len)", 6,
         lambda g: (
             (True, "列總和與列平均計算輸出正確！")
             if ("sum(row)" in history_clean and ("len(row)" in history_clean or "/ 3" in history_str or "/3" in history_clean))
             else (False, "請直接走訪每一列並印出 sum(row) 與 sum(row)/len(row) 平均值！")
         )),

        ("9-4-2", "挑戰題", "找出哪一橫列的總和最大 (max_row_sum)", 6,
         lambda g: (
             (True, "最大列總和搜尋正確！")
             if ("max_row_sum" in history_str or "max_sum" in history_str or "max(" in history_str) and "sum(" in history_str
             else (False, "請走訪各列並找出最大列總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-4-3 橫列索引走訪與帶編號統計 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-4-3", "填空題", "索引走訪 for r in range(R) 與 matrix[r]", 5,
         lambda g: (
             (True, "帶編號走訪語法填空正確！")
             if ("range(R)" in history_clean and "matrix[r]" in history_clean) or
                ("sum(matrix[r])" in history_clean)
             else (False, "請在 9-4-3 填空題填入 range(R) 與 sum(matrix[r])！")
         )),

        ("9-4-3", "練習題", "走訪 table，列總和大於等於 100 則印出達標訊息", 6,
         lambda g: (
             (True, "列總和條件篩選與通報正確！")
             if (">= 100" in history_str or ">=100" in history_clean) and ("sum(" in history_str and "達標" in history_str)
             else (False, "請走訪各列，若總和 >= 100 則印出『列 r 達標: 總和值』！")
         )),

        ("9-4-3", "挑戰題", "偶數列索引 (r % 2 == 0) 加總", 6,
         lambda g: (
             (True, "偶數列過濾加總正確！")
             if ("r % 2 == 0" in history_clean or "r%2==0" in history_clean) and "sum(" in history_str
             else (False, "請走訪網格並加總偶數列（r 為 0, 2）的元素總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-4-4 直行（直欄）維度翻轉縱向走訪 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-4-4", "填空題", "縱向走訪累加 matrix[r][c]", 5,
         lambda g: (
             (True, "縱向直行走訪語法填空正確！")
             if ("range(C)" in history_clean and "matrix[r][c]" in history_clean) or
                ("for c in range(C)" in history_str and "matrix[r][c]" in history_str)
             else (False, "請在 9-4-4 填空題填入 range(C) 與 matrix[r][c]！")
         )),

        ("9-4-4", "練習題", "計算出第 0 直行與第 1 直行的加總數值", 6,
         lambda g: (
             (True, "直行加總計算正確！")
             if ("col_sum" in history_str or "col0" in history_str or "grid[r][0]" in history_clean or "grid[r][1]" in history_clean)
             else (False, "請縱向走訪計算第 0 直行與第 1 直行的加總數值！")
         )),

        ("9-4-4", "挑戰題", "縱向走訪找出哪一直行的最大值最高", 6,
         lambda g: (
             (True, "直行最大值統計正確！")
             if ("max" in history_str and "range(C)" in history_str)
             else (False, "請縱向走訪計算各直行最大值，找出最高峰直行！")
         )),

        # ----------------------------------------------------------------------
        # 9-4-5 全網格全域極值搜尋與座標定位 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-4-5", "填空題", "搜尋最小值與座標定位 (min_val, min_r, min_c)", 5,
         lambda g: (
             (True, "全域最小值與座標搜尋填空正確！")
             if ("min_val" in history_str and "depth[r][c]" in history_clean) or
                ("min_r = r" in history_str or "min_c = c" in history_str)
             else (False, "請在 9-4-5 填空題填入比對條件與座標更新！")
         )),

        ("9-4-5", "練習題", "搜尋整張網格的『最大值』與座標", 6,
         lambda g: (
             (True, "全網格最大值與座標鎖定正確！")
             if ("max_val" in history_str or "max_r" in history_str or "max_c" in history_str) and "grid[r][c]" in history_clean
             else (False, "請走訪全網格搜尋最大值並印出其數值與座標！")
         )),

        ("9-4-5", "挑戰題", "搜尋最高峰數值並統計全圖出現次數", 6,
         lambda g: (
             (True, "最高峰搜尋與出現頻率統計正確！")
             if ("max" in history_str and ("count" in history_str or "+= 1" in history_str or "+=1" in history_clean))
             else (False, "請找出全網格最高峰數值，並統計它共出現幾次！")
         )),

        # ----------------------------------------------------------------------
        # 9-4-6 網格條件計數與布林過濾 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-4-6", "填空題", "統計不及格科目人次 (score < 60)", 5,
         lambda g: (
             (True, "不及格條件篩選填空正確！")
             if ("< 60" in history_str or "<60" in history_clean) and ("fail_count += 1" in history_str or "fail_count+=1" in history_clean)
             else (False, "請在 9-4-6 填空題填入 score < 60 與計數累加！")
         )),

        ("9-4-6", "練習題", "統計網格中所有偶數 (val % 2 == 0) 總個數", 6,
         lambda g: (
             (True, "網格偶數計數正確！")
             if ("% 2 == 0" in history_clean or "%2==0" in history_clean) and ("count" in history_str or "+= 1" in history_str)
             else (False, "請統計網格中所有偶數個數並印出！")
         )),

        ("9-4-6", "挑戰題", "統計大於全圖平均值的元素個數", 5,
         lambda g: (
             (True, "大於平均值之元素個數統計正確！")
             if ("avg" in history_str or "average" in history_str or "total" in history_str) and (">" in history_str and "count" in history_str)
             else (False, "請先算全圖平均，再統計大於平均值的格子數量！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-4：二維網格雙重走訪與行列統計 —— 自動評分報告")
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
        "unit_id": "9-4",
        "unit_name": "二維網格雙重走訪與行列統計",
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
        filename = f"grade_report_9_4.json"
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
    auto_grade_unit_9_4()
