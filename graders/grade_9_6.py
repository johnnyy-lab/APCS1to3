# ==============================================================================
# 🧪 《PythAPCS123》單元 9-6：矩陣幾何操作與逆推還原（APCS b266 專題） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_6.py
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

def auto_grade_unit_9_6():
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
        # 9-6-1 矩陣水平翻轉 (Horizontal Flip) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-6-1", "填空題", "水平翻轉切片 row[::-1]", 5,
         lambda g: (
             (True, "水平翻轉 row[::-1] 填空正確！")
             if ("row[::-1]" in history_clean)
             else (False, "請在 9-6-1 填空題填入 row[::-1]！")
         )),

        ("9-6-1", "練習題", "讀入網格並輸出水平翻轉後成果", 6,
         lambda g: (
             (True, "水平翻轉與解包輸出正確！")
             if ("[row[::-1] for row in grid]" in history_str or "row[::-1]" in history_clean) and "print" in history_str
             else (False, "請將讀入的網格水平翻轉並印出！")
         )),

        ("9-6-1", "挑戰題", "兩次水平翻轉等同還原驗證", 5,
         lambda g: (
             (True, "兩次翻轉還原驗證正確！")
             if ("== grid" in history_str or "==" in history_str) and "row[::-1]" in history_clean
             else (False, "請驗證兩次水平翻轉後是否與原始網格完全相同！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-2 矩陣垂直翻轉 (Vertical Flip) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-2", "填空題", "垂直翻轉切片 matrix[::-1]", 5,
         lambda g: (
             (True, "垂直翻轉 matrix[::-1] 填空正確！")
             if ("matrix[::-1]" in history_clean or "board[::-1]" in history_clean)
             else (False, "請在 9-6-2 填空題填入 matrix[::-1]！")
         )),

        ("9-6-2", "練習題", "垂直翻轉矩陣並解包輸出", 6,
         lambda g: (
             (True, "垂直翻轉操作與輸出正確！")
             if ("::-1" in history_str and "print" in history_str)
             else (False, "請使用 grid[::-1] 進行垂直翻轉並解包印出每一列！")
         )),

        ("9-6-2", "挑戰題", "垂直翻轉後再水平翻轉 (旋轉 180 度)", 6,
         lambda g: (
             (True, "水平垂直雙重翻轉正確！")
             if ("::-1" in history_str and "row[::-1]" in history_clean)
             else (False, "請依序執行垂直翻轉與水平翻轉！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-3 矩陣轉置操作 (Transpose) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-3", "填空題", "二維轉置列表生成式 origin[r][c]", 5,
         lambda g: (
             (True, "轉置生成式填空正確！")
             if ("origin[r][c]" in history_clean or "matrix[r][c]" in history_clean) and ("for r in range(R)" in history_str)
             else (False, "請在 9-6-3 填空題填入 origin[r][c] 完成轉置！")
         )),

        ("9-6-3", "練習題", "非方陣轉置與尺寸互換 (R, C 變為 C, R)", 6,
         lambda g: (
             (True, "非方陣轉置與尺寸轉換正確！")
             if ("for c in range(C)" in history_str and "for r in range(R)" in history_str) or "zip(*grid)" in history_str
             else (False, "請將 R x C 矩陣轉置為 C x R 矩陣並輸出！")
         )),

        ("9-6-3", "挑戰題", "連續兩次轉置恢復原貌", 6,
         lambda g: (
             (True, "二次轉置恢復驗證正確！")
             if ("transpose" in history_str or "T" in history_str or "==" in history_str)
             else (False, "請驗證轉置兩次後矩陣恢復原始樣貌！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-4 矩陣旋轉 90 度 (Rotate 90) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-4", "填空題", "順時針 90 度旋轉 (轉置後每列水平翻轉)", 5,
         lambda g: (
             (True, "順時針 90 度旋轉填空正確！")
             if ("row[::-1]" in history_clean or "matrix[R - 1 - r][c]" in history_clean)
             else (False, "請在 9-6-4 填空題完成順時針 90 度旋轉！")
         )),

        ("9-6-4", "練習題", "實作逆時針 90 度旋轉", 6,
         lambda g: (
             (True, "逆時針 90 度旋轉實作正確！")
             if ("rotate" in history_str or "90" in history_str) and ("::-1" in history_str)
             else (False, "請實作逆時針旋轉 90 度（水平翻轉後轉置）！")
         )),

        ("9-6-4", "挑戰題", "連轉四次 360 度恢復初始", 6,
         lambda g: (
             (True, "360 度四次旋轉循環驗證正確！")
             if ("range(4)" in history_str or "4" in history_str) and "==" in history_str
             else (False, "請連續旋轉 4 次驗證是否完全回到原陣列！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-5 連續操作與變數尺寸動態追蹤 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-6-5", "填空題", "動態追蹤列數 curr_R = len(mat)", 5,
         lambda g: (
             (True, "動態尺寸追蹤填空正確！")
             if ("len(mat)" in history_clean or "len(grid)" in history_clean)
             else (False, "請在 9-6-5 填空題填入 len(mat)！")
         )),

        ("9-6-5", "練習題", "執行操作序列 [0, 1] 並印出最終網格", 6,
         lambda g: (
             (True, "操作指令分流執行正確！")
             if ("cmd == 0" in history_str or "cmd == 1" in history_str or "op == 0" in history_str or "op == 1" in history_str)
             else (False, "請依操作序列依序執行翻轉與旋轉！")
         )),

        ("9-6-5", "挑戰題", "動態追蹤多步操作之網格行列尺寸變化", 6,
         lambda g: (
             (True, "動態維度追蹤正確！")
             if ("len(" in history_str and "print" in history_str)
             else (False, "請在每次操作後即時更新並輸出網格的新維度 R 與 C！")
         )),

        # ----------------------------------------------------------------------
        # 9-6-6 APCS b266 矩陣轉換：逆操作還原心法 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-6-6", "填空題", "逆操作順序 ops[::-1]", 5,
         lambda g: (
             (True, "逆操作反轉 ops[::-1] 填空正確！")
             if ("ops[::-1]" in history_clean or "reversed(ops)" in history_str)
             else (False, "請在 9-6-6 填空題填入 ops[::-1] 將操作序列倒轉！")
         )),

        ("9-6-6", "練習題", "APCS b266 單組測資逆推還原原型", 6,
         lambda g: (
             (True, "APCS b266 逆推還原正確！")
             if ("ops[::-1]" in history_clean or "reversed(" in history_str) and ("print(*row)" in history_str)
             else (False, "請依照 APCS b266 規格逆序執行操作還原原始矩陣！")
         )),

        ("9-6-6", "挑戰題", "APCS b266 多組測資 while True 逆推終極通關", 5,
         lambda g: (
             (True, "APCS b266 完整多測資框架正確！")
             if ("while True:" in history_str or "try:" in history_str or "EOFError" in history_str)
             else (False, "請以 while True 搭配 try-except 完成 APCS b266 多測資逆推！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 9-6：矩陣幾何操作與逆推還原（APCS b266 專題） —— 自動評分報告")
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
        "unit_id": "9-6",
        "unit_name": "矩陣幾何操作與逆推還原（APCS b266 專題）",
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
        filename = f"grade_report_9_6.json"
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
    auto_grade_unit_9_6()
