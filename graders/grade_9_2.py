# ==============================================================================
# 🧪 《PythAPCS123》單元 9-2：二維陣列動態輸入讀取與解包輸出 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_2.py
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

def auto_grade_unit_9_2():
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
        # 9-2-1 多行數值輸入流程 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-2-1", "填空題", "動態讀入列數 R 並迴圈 append", 5,
         lambda g: (
             (True, "動態讀入列數 R 與逐列追加正確！")
             if ("int(input())" in history_clean and "grid.append" in history_clean) or
                ("grid" in g and isinstance(g.get("grid"), list))
             else (False, "請在 9-2-1 填空題填入 int(input()) 與 grid.append！")
         )),

        ("9-2-1", "練習題", "迴圈搭配 .append() 讀入 R 列網格", 6,
         lambda g: (
             (True, "迴圈逐列讀取網格完全正確！")
             if ("for _ in range(R)" in history_str or "for i in range(R)" in history_str) and "append" in history_str
             else (False, "請使用 for 迴圈搭配 .append() 讀入 R 列整數串列！")
         )),

        ("9-2-1", "挑戰題", "統計網格全部大於 0 的正整數個數", 5,
         lambda g: (
             (True, "網格正整數走訪過濾與計數正確！")
             if ("> 0" in history_str or ">0" in history_clean) and ("count" in history_str or "+= 1" in history_str or "+=1" in history_clean)
             else (False, "請在讀入網格後統計所有大於 0 的正整數個數並輸出！")
         )),

        # ----------------------------------------------------------------------
        # 9-2-2 逐列拼裝網格與列統計 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-2-2", "填空題", "列表生成式拆詞轉整數 [int(x) for x in input().split()]", 5,
         lambda g: (
             (True, "同行拆詞轉整數生成式填空正確！")
             if ("int(x) for x in input().split()" in history_clean or "int(x)forxininput().split()" in history_clean)
             else (False, "請在 9-2-2 填空題填入 [int(x) for x in input().split()]！")
         )),

        ("9-2-2", "練習題", "讀入 R 列整數網格並印出每一列的總和", 6,
         lambda g: (
             (True, "讀入網格並逐列印出 sum(row) 正確！")
             if ("sum(row)" in history_clean or "sum(r)" in history_clean) or
                ("列總和" in history_str or "sum(" in history_str)
             else (False, "請逐列讀入網格並使用 sum(row) 印出每一橫列的加總！")
         )),

        ("9-2-2", "挑戰題", "讀入網格並累加全部元素總和", 6,
         lambda g: (
             (True, "全網格元素總和累加正確！")
             if ("total_sum" in history_str or "total" in history_str or "sum(sum" in history_clean)
             else (False, "請計算整張網格中所有數字的累加總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-2-3 一行巢狀列表生成式讀取 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-2-3", "填空題", "巢狀列表生成式一行讀取矩陣", 5,
         lambda g: (
             (True, "巢狀列表生成式讀取正確！")
             if ("[[int(x)forxininput().split()]for_inrange(R)]" in history_clean or
                 "[[int(x) for x in input().split()] for _ in range(R)]" in history_str)
             else (False, "請在 9-2-3 填空題填入完整的雙層列表生成式！")
         )),

        ("9-2-3", "練習題", "以巢狀生成式讀入網格並印出長度 R, C", 6,
         lambda g: (
             (True, "巢狀生成式讀入與長度確認正確！")
             if ("for _ in range(R)" in history_str and "len(grid)" in history_str) or
                ("len(grid[0])" in history_str)
             else (False, "請使用一行巢狀生成式讀入 R 列資料，並印出 R 與 C！")
         )),

        ("9-2-3", "挑戰題", "巢狀生成式讀入並計算全圖最大值", 6,
         lambda g: (
             (True, "全圖最大值搜尋正確！")
             if ("max(" in history_str and ("max_val" in history_str or "max(row)" in history_clean))
             else (False, "請讀入網格後找出全圖最大值並輸出！")
         )),

        # ----------------------------------------------------------------------
        # 9-2-4 二維解包輸出：print(*row) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-2-4", "填空題", "解包輸出語法 print(*row)", 5,
         lambda g: (
             (True, "print(*row) 解包語法填空正確！")
             if ("print(*row)" in history_str or "print(*row)" in history_clean)
             else (False, "請在 9-2-4 填空題填入 print(*row)！")
         )),

        ("9-2-4", "練習題", "解包輸出網格以逗號隔開 (sep=', ')", 6,
         lambda g: (
             (True, "自訂分隔符解包輸出正確！")
             if ("sep=', '" in history_str or 'sep=", "' in history_str or "sep=','" in history_clean) and "print(*" in history_str
             else (False, "請使用 print(*row, sep=', ') 印出每一列！")
         )),

        ("9-2-4", "挑戰題", "逆序解包輸出 (grid[::-1])", 6,
         lambda g: (
             (True, "逆序走訪與解包輸出正確！")
             if ("::-1" in history_str and "print(*" in history_str) or "reversed(grid)" in history_str
             else (False, "請由下往上逆序印出每一列，並以 print(*row) 解包！")
         )),

        # ----------------------------------------------------------------------
        # 9-2-5 工整格式化排版輸出 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-2-5", "填空題", "f-string 固定寬度格式化 :3d", 5,
         lambda g: (
             (True, "f-string 寬度排版格式填空正確！")
             if (":3d" in history_str or ":4d" in history_str or ":5d" in history_str)
             else (False, "請在 9-2-5 填空題填入 :3d 格式化設定！")
         )),

        ("9-2-5", "練習題", "雙重迴圈與 f'{val:5d}' 工整印出", 6,
         lambda g: (
             (True, "雙重迴圈搭配 :5d 工整排版正確！")
             if (":5d" in history_str and "end=" in history_str) or ("2   10  800" in history_str)
             else (False, "請使用雙重迴圈搭配 f'{val:5d}' 與 end='' 排版輸出！")
         )),

        ("9-2-5", "挑戰題", "3x3 乘法表排版輸出", 6,
         lambda g: (
             (True, "3x3 乘法表排版印出正確！")
             if ("* " in history_str and (":3d" in history_str or ":2d" in history_str)) or
                ("1  2  3" in history_str or "1   2   3" in history_str)
             else (False, "請撰寫雙重迴圈印出 3x3 乘法表並以固定寬度排版！")
         )),

        # ----------------------------------------------------------------------
        # 9-2-6 字元網格字串輸入 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-2-6", "填空題", "字元地圖 list() 拆解為字元串列", 5,
         lambda g: (
             (True, "list(line.strip()) 拆解填空正確！")
             if ("list(" in history_str and "strip()" in history_str) or "list(input().strip())" in history_clean
             else (False, "請在 9-2-6 填空題填入 list() 函式將字串轉為字元串列！")
         )),

        ("9-2-6", "練習題", "讀入迷宮並修改 (1, 1) 為 'X'", 6,
         lambda g: (
             (True, "字元網格讀入與單格修改正確！")
             if ("grid[1][1] = 'X'" in history_str or 'grid[1][1] = "X"' in history_str or
                 "grid[1][1]='X'" in history_clean or 'grid[1][1]="X"' in history_clean)
             else (False, "請讀入 3x3 迷宮並將 (1, 1) 修改為 'X'！")
         )),

        ("9-2-6", "挑戰題", "統計字元地圖中 '*' 星號總數", 5,
         lambda g: (
             (True, "字元地圖星號統計正確！")
             if ("'*'" in history_str or '"*"' in history_str) and ("count" in history_str or "+= 1" in history_str or "+=1" in history_clean)
             else (False, "請統計字元網格中 '*' 的出現總次數！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-2：二維陣列動態輸入讀取與解包輸出 —— 自動評分報告")
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
        "unit_id": "9-2",
        "unit_name": "二維陣列動態輸入讀取與解包輸出",
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
        filename = f"grade_report_9_2.json"
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
    auto_grade_unit_9_2()
