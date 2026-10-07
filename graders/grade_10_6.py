# ==============================================================================
# 🧪 《PythAPCS123》單元 10-6：集合特性、建立與元素操作 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_6.py
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

def auto_grade_unit_10_6():
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
        # 10-6-1 集合概念：無序性與唯一性天然去重 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-6-1", "填空題", "大括號宣告集合 fruits_set = {'apple', 'banana', 'apple'}", 5,
         lambda g: (
             (True, "大括號集合宣告填空正確！")
             if ("fruits_set" in history_str and "banana" in history_str) or ("apple" in history_str and "{" in history_str)
             else (False, "請在 10-6-1 填空題宣告包含重複水果的集合！")
         )),

        ("10-6-1", "練習題", "單字相異字母統計器 unique_chars = set(word)", 6,
         lambda g: (
             (True, "相異字母集合統計正確！")
             if ("set(" in history_str or "{" in history_str) and ("unique_chars" in history_str or "word" in history_str)
             else (False, "請將單字中所有字母放入集合中並統計相異字母個數！")
         )),

        ("10-6-1", "挑戰題", "相異整數極值全距計算 max(raw_set) - min(raw_set)", 5,
         lambda g: (
             (True, "集合極值全距計算正確！")
             if ("max(" in history_str and "min(" in history_str) and ("raw_set" in history_str or "set" in history_str)
             else (False, "請計算集合中最大值與最小值的差距！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-2 集合建立語法與空集合陷阱 set() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-2", "填空題", "宣告真正的空集合 lucky_numbers = set()", 5,
         lambda g: (
             (True, "空集合 set() 填空正確！")
             if ("set()" in history_clean)
             else (False, "請在 10-6-2 填空題填入 set() 建立空集合！")
         )),

        ("10-6-2", "練習題", "動態收集非負整數集合 (.add())", 6,
         lambda g: (
             (True, "動態條件 .add() 收集正確！")
             if (".add(" in history_str and ">= 0" in history_str) or ("non_negative_set" in history_str)
             else (False, "請建立空集合並使用 .add() 收集非負整數！")
         )),

        ("10-6-2", "挑戰題", "連續字母遇到哨兵字元停機收集", 6,
         lambda g: (
             (True, "哨兵終止集合收集正確！")
             if (".add(" in history_str and "break" in history_str) or ("'X'" in history_str or '"X"' in history_str)
             else (False, "請走訪字母，遇到 'X' 立即中斷迴圈！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-3 可迭代物件快速去重 set(my_list) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-3", "填空題", "計算打卡名單不重複人數 len(set(checkin_logs))", 5,
         lambda g: (
             (True, "set() 快速去重人數統計填空正確！")
             if ("len(set(checkin_logs))" in history_clean or "set(checkin_logs)" in history_str)
             else (False, "請在 10-6-3 填空題填入 len(set(checkin_logs))！")
         )),

        ("10-6-3", "練習題", "相異整數計數與純度檢測 len(s) == len(lst)", 6,
         lambda g: (
             (True, "去重長度比對純度檢測正確！")
             if ("len(set(" in history_clean and "len(" in history_str) or ("==" in history_str and "set" in history_str)
             else (False, "請比較 len(set(lst)) 與 len(lst) 判斷是否完全無重複！")
         )),

        ("10-6-3", "挑戰題", "兩班選課名冊相加後快速求總科目數", 6,
         lambda g: (
             (True, "兩名冊串列合併去重正確！")
             if ("set(" in history_str and ("+" in history_str or "|" in history_str)) and ("list_a" in history_str)
             else (False, "請利用串列相加並轉為 set 求出兩班總科目數！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-4 元素動態增刪：.add(), .remove(), .discard() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-4", "填空題", "使用 discard 安全移除白名單 members.discard(target)", 5,
         lambda g: (
             (True, "discard() 安全移除填空正確！")
             if ("discard" in history_str)
             else (False, "請在 10-6-4 填空題填入 discard(target)！")
         )),

        ("10-6-4", "練習題", "動態聊天室在線名冊維護器 (IN 用 add, OUT 用 discard)", 6,
         lambda g: (
             (True, "聊天室人員進出維護正確！")
             if (".add(" in history_str and ".discard(" in history_str) or ("online_users" in history_str)
             else (False, "請依 IN/OUT 指令分別調用 add() 與 discard() 維護名冊！")
         )),

        ("10-6-4", "挑戰題", "黑名單批次安全過濾 (遍歷 blacklist 執行 discard)", 6,
         lambda g: (
             (True, "黑名單批次 discard 過濾正確！")
             if (".discard(" in history_str and "for" in history_str) and ("approved" in history_str)
             else (False, "請走訪 blacklist 帳號使用 .discard() 安全過濾！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-5 集合生成式（Set Comprehension） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-5", "填空題", "集合生成式篩選大於 50 分數 {s for s in scores if s > 50}", 5,
         lambda g: (
             (True, "集合生成式填空正確！")
             if ("> 50" in history_str or ">50" in history_clean) and ("{" in history_str and "}" in history_str)
             else (False, "請在 10-6-5 填空題填入 if s > 50 門檻！")
         )),

        ("10-6-5", "練習題", "相異字串首字母集合提取器 {w[0].upper() for w in words}", 6,
         lambda g: (
             (True, "單字大寫首字母集合生成式正確！")
             if ("w[0].upper()" in history_clean or ".upper()" in history_str) and ("for" in history_str and "{" in history_str)
             else (False, "請以一行集合生成式提取所有單字的大寫首字母！")
         )),

        ("10-6-5", "挑戰題", "英文句子中相異母音單行萃取 {c for c in quote if c in 'aeiou'}", 6,
         lambda g: (
             (True, "母音字元集合生成式正確！")
             if ("'aeiou'" in history_str or '"aeiou"' in history_str or "in vowel" in history_str) and ("{" in history_str)
             else (False, "請以單行集合生成式篩選出句子中的所有母音！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-6 集合元素限制：Hashable 限制 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-6-6", "填空題", "以元組 (r, c) 標記已拜訪座標 visited_coords.add((r, c))", 5,
         lambda g: (
             (True, "座標元組放入集合填空正確！")
             if (".add((" in history_clean or "visited_coords.add" in history_str)
             else (False, "請在 10-6-6 填空題將座標元組加到 visited_coords！")
         )),

        ("10-6-6", "練習題", "網格足跡重複踩踏偵測機 (pt in visited)", 6,
         lambda g: (
             (True, "網格重複足跡偵測正確！")
             if ("in visited" in history_str and ".add(" in history_str) or ("path_points" in history_str)
             else (False, "請使用集合紀錄走過的座標並回報重複踏足的點！")
         )),

        ("10-6-6", "挑戰題", "稀疏障礙物跨界安全過濾 (邊界範圍生成式)", 5,
         lambda g: (
             (True, "合法邊界障礙物過濾正確！")
             if ("0 <= r <" in history_str and "0 <= c <" in history_str) and ("{" in history_str)
             else (False, "請使用集合生成式過濾出所有位在合法邊界內的障礙物座標！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-6：集合特性、建立與元素操作 —— 自動評分報告")
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
        "unit_id": "10-6",
        "unit_name": "集合特性、建立與元素操作",
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
        filename = f"grade_report_10_6.json"
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
    auto_grade_unit_10_6()
