# ==============================================================================
# 🧪 《PythAPCS123》單元 7-4：字串索引、長度與走訪 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_4.py
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

def auto_grade_unit_7_4():
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
        # 7-4-1 字串長度函數 len() 與邊界守護 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-4-1", "填空題", "字串長度函數 len() 安全長度檢驗 (result)", 6,
         lambda g: (
             (True, "len(password) >= 8 長度判斷完全正確！")
             if g.get("result") == "Password is strong" or
                ("len(password)" in history_clean and ">= 8" in history_str)
             else (False, "請在 7-4-1 填空題空格填入函數名稱 len！")
         )),

        ("7-4-1", "練習題", "帳號格式長度檢核器 (VALID / TOO SHORT / TOO LONG)", 9,
         lambda g: (
             (True, "帳號長度三區間檢驗邏輯正確！")
             if ("len(" in history_str and "VALID" in history_str and
                 ("TOO SHORT" in history_str or "TOO LONG" in history_str))
             else (False, "請讀入 username，使用 len() 判斷長度並輸出 VALID、TOO SHORT 或 TOO LONG！")
         )),

        ("7-4-1", "挑戰題", "雙單字長度擂台賽 (比較 w1 與 w2 長度)", 5,
         lambda g: (
             (True, "雙單字長度比較與差值輸出正確！")
             if ("len(" in history_str and "longer by" in history_str and "chars" in history_str) or
                ("Both words have" in history_str)
             else (False, "請比較 w1 與 w2 之 len()，印出長度領先者與字元差數！")
         )),

        # ----------------------------------------------------------------------
        # 7-4-2 正向索引（0 到 len-1）與字元提取 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-4-2", "填空題", "首字 dna[0] 與末字正向索引提取 (first, last)", 6,
         lambda g: (
             (True, "正向索引 0 與末位字元取出成功！")
             if (g.get("first") == 'C' and g.get("last") == 'G') or
                ("dna[0]" in history_clean and ("dna[5]" in history_clean or "dna[len(dna)-1]" in history_clean))
             else (False, "請在 7-4-2 填空題填入索引 0 與末位索引！")
         )),

        ("7-4-2", "練習題", "頭尾字元對照器 (MATCH: c vs DIFFERENT: p vs n)", 9,
         lambda g: (
             (True, "頭尾字元正向索引取出與比對正確！")
             if (("s[0]" in history_clean or "s[len(s)-1]" in history_clean) and
                 ("MATCH" in history_str or "DIFFERENT" in history_str)) or
                ("MATCH: l" in history_str or "DIFFERENT: p vs n" in history_str)
             else (False, "請取出第一個字元與最後一個字元，比對相同輸出 MATCH，不同輸出 DIFFERENT！")
         )),

        ("7-4-2", "挑戰題", "奇數長度字串正中央字元抽取 (Center: d)", 5,
         lambda g: (
             (True, "整數除法 // 2 中心索引計算與字元提取正確！")
             if ("// 2" in history_str or "//2" in history_clean) and
                ("Center:" in history_str or "s[" in history_str)
             else (False, "請以 len(s) // 2 計算中間索引，並印出 Center: [中央字元]！")
         )),

        # ----------------------------------------------------------------------
        # 7-4-3 負向索引（-1 到 -len）倒數鎖定 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-4-3", "填空題", "負向倒數末位索引 cheer[-1] (msg)", 6,
         lambda g: (
             (True, "負向索引 -1 鎖定末尾字元成功！")
             if g.get("msg") == "Ends with exclamation mark" or
                ("cheer[-1]" in history_clean)
             else (False, "請在 7-4-3 填空題中括號內填入負向索引 -1！")
         )),

        ("7-4-3", "練習題", "語氣標點辨識器 (負向索引 sentence[-1])", 9,
         lambda g: (
             (True, "句末標點符號 [-1] 辨識分支完整！")
             if ("[-1]" in history_str and
                 ("QUESTION" in history_str or "EXCLAMATION" in history_str or "STATEMENT" in history_str))
             else (False, "請使用負向索引 sentence[-1] 判定結尾標點並輸出對應語氣！")
         )),

        ("7-4-3", "挑戰題", "倒數前二後二組合代碼 (Code: AP26)", 5,
         lambda g: (
             (True, "前二 (0, 1) 與後二 (-2, -1) 組合代碼印出正確！")
             if (("[-2]" in history_str and "[-1]" in history_str) or ("[0]" in history_str and "[1]" in history_str)) and
                ("Code:" in history_str or "AP26" in history_str)
             else (False, "請取出 s[0], s[1], s[-2], s[-1] 拼成 4 碼代碼並印出！")
         )),

        # ----------------------------------------------------------------------
        # 7-4-4 字串不可變性（Immutable）與拼接重建 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-4-4", "填空題", "新字串拼接重建 (new_word = 'P' + word[1] + ...)", 6,
         lambda g: (
             (True, "利用索引提取與加法拼接成功重構單字 Pain！")
             if g.get("new_word") == "Pain" or
                ('word[1]' in history_clean and 'word[2]' in history_clean and 'word[3]' in history_clean)
             else (False, "請在 7-4-4 填空題空格分別填入 1, 2, 3 完成 Pain 拼接！")
         )),

        ("7-4-4", "練習題", "首尾字元替換魔術 (s[2] + s[1] + s[0])", 9,
         lambda g: (
             (True, "3 字母單字首尾字元交換拼接輸出正確！")
             if (("s[2]" in history_str or "s[-1]" in history_str) and "s[1]" in history_str and "s[0]" in history_str) or
                ("god" in history_str or "pot" in history_str or "tac" in history_str)
             else (False, "請讀入 3 字母單字，交換首尾字元位置後印出！")
         )),

        ("7-4-4", "挑戰題", "字母去頭去尾安全殼 (迴圈走訪 1 到 len-2)", 5,
         lambda g: (
             (True, "去頭去尾迴圈走訪與核心文字組裝正確！")
             if ("range(1" in history_clean or "range( 1" in history_str) and
                ("Core:" in history_str or "+=" in history_str)
             else (False, "請以迴圈走訪 1 到 len(s)-2，組裝中間字串並印出 Core: [核心]！")
         )),

        # ----------------------------------------------------------------------
        # 7-4-5 字串走訪雙模式：直接字元 vs 索引位置 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-4-5", "填空題", "直接字元走訪計數 (for ch in banana)", 6,
         lambda g: (
             (True, "直接字元走訪 for ch in banana 語法完全正確！")
             if g.get("count_a") == 3 or
                ("for ch in banana:" in history_str or "forchbanana" in history_clean)
             else (False, "請在 7-4-5 填空題空格填入 in！")
         )),

        ("7-4-5", "練習題", "奇數位數字加總器 (索引走訪 i=1, 3, 5...)", 9,
         lambda g: (
             (True, "奇數索引走訪與數字轉型累加正確！")
             if ("range(1" in history_clean and ", 2)" in history_str) or
                ("% 2 != 0" in history_str or "% 2 == 1" in history_str or "%2!=0" in history_clean) and
                ("int(" in history_str and "+=" in history_str)
             else (False, "請走訪所有奇數索引位置，將字元轉為整數累加求和並輸出！")
         )),

        ("7-4-5", "挑戰題", "相鄰重複字元探測器 (s[i] == s[i+1])", 5,
         lambda g: (
             (True, "相鄰字元比對 s[i] == s[i+1] 與狀態判定正確！")
             if ("s[i] == s[i+1]" in history_clean or "s[i]==s[i+1]" in history_clean) and
                ("FOUND DOUBLE" in history_str or "ALL UNIQUE CONSECUTIVE" in history_str)
             else (False, "請走訪比較相鄰字元 s[i] == s[i+1]，輸出判定結果！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-4 學習成效自動評分檢驗報告")
    print(f"👤 學員姓名：{combined_display_name}")
    print(f"⏰ 檢驗時間：{timestamp_str}")
    print("=" * 72)

    for uid, qtype, name, pts, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception as e:
            ok, msg = False, f"評分邏輯執行異常：{e}"

        if ok:
            item_score = pts
            total_score += pts
            pass_count += 1
            print(f"✅ [{uid}] {qtype} - {name} ({pts}/{pts} 分)")
        else:
            item_score = 0
            print(f"❌ [{uid}] {qtype} - {name} (0/{pts} 分)")
            print(f"   💡 提示：{msg}")

        item_results.append({
            "uid": uid,
            "type": qtype,
            "name": name,
            "passed": ok,
            "score": item_score,
            "max_score": pts,
            "message": msg
        })

    print("-" * 72)
    if total_score >= 95:
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通字串正負雙向索引、不可變性重建與兩種走訪模式，字串探勘神射手！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，索引邊界守護與字元走訪思維清晰！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調索引與走訪步進！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-4",
        "unit_title": "字串索引、長度與走訪",
        "student_name": combined_display_name,
        "declared_name": declared_name,
        "google_name": final_google_name,
        "student_email": final_email,
        "google_email": google_email if google_email else final_email,
        "timestamp": timestamp_str,
        "total_score": total_score,
        "max_score": max_score,
        "pass_count": pass_count,
        "total_count": len(test_cases),
        "badge": badge,
        "details": item_results
    }

    try:
        log_filename = "score_log_unit_7_4.json"
        with open(log_filename, "w", encoding="utf-8") as lf:
            json.dump(log_data, lf, ensure_ascii=False, indent=2)
        print(f"💾 [本地存檔] 評分紀錄檔已生成：{log_filename}（可於左側檔案區下載備查）")
    except Exception as e:
        print(f"⚠️ 本地日誌寫入提示：{e}")

    # --------------------------------------------------------------------------
    # 📡 2. 雲端後台成績記錄
    # --------------------------------------------------------------------------
    if LOG_WEBHOOK_URL:
        try:
            req_data = json.dumps(log_data).encode('utf-8')
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=req_data,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                print("📡 [雲端回報] 成績已成功上傳並登錄至授課試算表！")
        except Exception as e:
            print(f"📡 [雲端回報] 雲端登錄通訊提示（不影響本地測驗）：{e}")

    if total_score < 100:
        print("\n💡 小技巧：若有題目顯示 ❌ 未通過，請回到上方對應題目的儲存格修改程式碼，")
        print("   並務必重新點擊該題的『▶ 播放鍵』執行，再回來執行此評分儲存格就可以刷新成績與紀錄囉！")
        print("=" * 72)

# 執行評分
auto_grade_unit_7_4()
