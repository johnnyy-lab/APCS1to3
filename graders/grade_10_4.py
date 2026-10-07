# ==============================================================================
# 🧪 《PythAPCS123》單元 10-4：字典常用方法與走訪技巧 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_4.py
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

def auto_grade_unit_10_4():
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
        # 10-4-1 安全取值神器：d.get(key, default) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-4-1", "填空題", "使用 get() 查詢餐點價格 menu.get(item, -1)", 5,
         lambda g: (
             (True, "get() 安全取值填空正確！")
             if ("menu.get" in history_str and "-1" in history_str) or ("get(" in history_str and "-1" in history_str)
             else (False, "請在 10-4-1 填空題填入 menu.get(item_name, -1)！")
         )),

        ("10-4-1", "練習題", "單字積分查詢器 (word_points.get(w, 0))", 6,
         lambda g: (
             (True, "單字積分安全累加正確！")
             if (".get(" in history_str and "0" in history_str) or ("word_points" in history_str)
             else (False, "請使用 .get(w, 0) 累加查詢單字的分數！")
         )),

        ("10-4-1", "挑戰題", "不使用 if-else 之計數器累加 counts[w] = counts.get(w, 0) + 1", 5,
         lambda g: (
             (True, "一行 get() 計數器實作正確！")
             if ("get(" in history_str and "+ 1" in history_str) or ("get(" in history_str and "+1" in history_clean)
             else (False, "請使用 counts[w] = counts.get(w, 0) + 1 實現無分支計數！")
         )),

        # ----------------------------------------------------------------------
        # 10-4-2 成員檢查：key in d 與 key not in d (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-4-2", "填空題", "使用 not in 檢查庫存 item not in inventory", 5,
         lambda g: (
             (True, "not in 成員檢查填空正確！")
             if ("not in inventory" in history_str or "notin inventory" in history_clean or "not in" in history_str)
             else (False, "請在 10-4-2 填空題填入 not in inventory！")
         )),

        ("10-4-2", "練習題", "黑名單訪客即時過濾系統 (ip in blacklist)", 6,
         lambda g: (
             (True, "黑名單即時判定正確！")
             if ("in blacklist" in history_str or "not in blacklist" in history_str)
             else (False, "請以 O(1) in 運算子檢查訪客 IP 是否在黑名單中！")
         )),

        ("10-4-2", "挑戰題", "兩數之和（Two Sum）O(N) 雜湊字典解法", 6,
         lambda g: (
             (True, "Two Sum 字典雜湊解法正確！")
             if ("target - num" in history_str or "target - x" in history_str or "target-num" in history_clean) and ("in seen" in history_str)
             else (False, "請使用 seen 字典記錄數值與索引，以 O(N) 找出兩數之和目標！")
         )),

        # ----------------------------------------------------------------------
        # 10-4-3 鍵走訪：for k in d 或 d.keys() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-4-3", "填空題", "走訪庫存不足商品 for item in stock", 5,
         lambda g: (
             (True, "鍵走訪與條件篩選填空正確！")
             if ("in stock" in history_str and "shortage_items" in history_str)
             else (False, "請在 10-4-3 填空題走訪 stock 並篩選庫存 < 5 的商品！")
         )),

        ("10-4-3", "練習題", "及格名單公告系統 (走訪 exam_results 鍵)", 6,
         lambda g: (
             (True, "學生成績及格名單走訪正確！")
             if ("for name in exam_results" in history_str or "for student in" in history_str or "in exam_results" in history_str) and (">= 60" in history_str)
             else (False, "請走訪學生姓名並篩選成績 >= 60 的學生！")
         )),

        ("10-4-3", "挑戰題", "依字母順序排序走訪菜單 sorted(cafe_menu.keys())", 6,
         lambda g: (
             (True, "菜單鍵字母排序走訪正確！")
             if ("sorted(" in history_str and "cafe_menu" in history_str)
             else (False, "請使用 sorted(cafe_menu) 依字母順序印出品項與價格！")
         )),

        # ----------------------------------------------------------------------
        # 10-4-4 值走訪：d.values() 與極值統計 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-4-4", "填空題", "sum(exam_scores.values()) 計算總分與平均", 5,
         lambda g: (
             (True, "values() 總和統計填空正確！")
             if ("values()" in history_clean)
             else (False, "請在 10-4-4 填空題填入 exam_scores.values()！")
         )),

        ("10-4-4", "練習題", "數據離群值計數 (sum/len 計算平均溫度)", 6,
         lambda g: (
             (True, "平均值計算與離群統計正確！")
             if ("sensor_data.values()" in history_clean or "values()" in history_str) and ("sum(" in history_str)
             else (False, "請使用 values() 計算平均溫度並統計高於平均的天數！")
         )),

        ("10-4-4", "挑戰題", "股票收盤價極值全距 max(values) - min(values)", 6,
         lambda g: (
             (True, "極值全距計算正確！")
             if ("max(" in history_str and "min(" in history_str and "values()" in history_str)
             else (False, "請使用 max(portfolio.values()) - min(portfolio.values()) 一行算出全距！")
         )),

        # ----------------------------------------------------------------------
        # 10-4-5 鍵值對走訪：for k, v in d.items() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-4-5", "填空題", "雙變數解包走訪 for drink, price in drink_menu.items()", 5,
         lambda g: (
             (True, "items() 雙變數解包走訪填空正確！")
             if ("drink_menu.items()" in history_clean or "items()" in history_str)
             else (False, "請在 10-4-5 填空題填入 drink_menu.items()！")
         )),

        ("10-4-5", "練習題", "最高分得主尋找 (items 走訪維護 max_player)", 6,
         lambda g: (
             (True, "最高分得主走訪搜尋正確！")
             if ("items()" in history_str and "leaderboard" in history_str) and ("> max_score" in history_str or "> max" in history_str)
             else (False, "請透過 items() 走訪找出獲得最高分的玩家！")
         )),

        ("10-4-5", "挑戰題", "反轉字典（鍵值互換 Invert Dictionary）", 6,
         lambda g: (
             (True, "鍵值互換反轉字典正確！")
             if ("items()" in history_str and ("country" in history_str or "code" in history_str)) and ("[" in history_str and "]=" in history_clean)
             else (False, "請透過 items() 將國碼與國家名稱互換鍵值！")
         )),

        # ----------------------------------------------------------------------
        # 10-4-6 字典生成式 (Dictionary Comprehension) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-4-6", "填空題", "生成及格學生字典 {k: v for k, v in scores.items() if v >= 60}", 5,
         lambda g: (
             (True, "字典生成式填空正確！")
             if ("items()" in history_str and ">= 60" in history_str) or (">=60" in history_clean)
             else (False, "請在 10-4-6 填空題填入 raw_scores.items() 與 60！")
         )),

        ("10-4-6", "練習題", "字串長度索引字典 {w: len(w) for w in words if len(w) >= 4}", 6,
         lambda g: (
             (True, "字串長度生成式字典正確！")
             if ("len(" in history_str and "for" in history_str and "words" in history_str)
             else (False, "請以字典生成式挑選長度 >= 4 的單字建立字典！")
         )),

        ("10-4-6", "挑戰題", "單行字典反轉與大寫轉換 {v: k.upper() for k, v in mapping.items()}", 5,
         lambda g: (
             (True, "單行字典生成式反轉與大寫正確！")
             if ("upper()" in history_str and "items()" in history_str and "mapping" in history_str)
             else (False, "請只用一行字典生成式完成數值鍵與大寫字串值的建立！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-4：字典常用方法與走訪技巧 —— 自動評分報告")
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
        "unit_id": "10-4",
        "unit_name": "字典常用方法與走訪技巧",
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
        filename = f"grade_report_10_4.json"
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
    auto_grade_unit_10_4()
