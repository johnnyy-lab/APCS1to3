# ==============================================================================
# 🧪 《PythAPCS123》單元 12-2：降序排序、字串字典序與數值轉型陷阱 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_2.py
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
    except Exception:
        return None, None

def get_submission_env():
    """取得 Colab / 本地端全域變數與執行歷史代碼"""
    try:
        import IPython
        ipython_inst = IPython.get_ipython()
        if ipython_inst is not None:
            user_ns = ipython_inst.user_ns
            history_cells = getattr(ipython_inst, 'user_ns', {}).get('_ih', [])
            return user_ns, history_cells
    except Exception:
        pass
    
    # 備用機制：若不在 IPython 環境，從呼叫棧主模組獲取
    try:
        import __main__
        return __main__.__dict__, []
    except Exception:
        return {}, []

def auto_grade_unit_12_2(student_name=""):
    """
    單元 12-2：降序排序、字串字典序與數值轉型陷阱 自動評分主程式
    滿分 100 分：
    - 填空題 6 題，每題 5 分，共 30 分
    - 練習題 6 題，每題 6 分，共 36 分
    - 挑戰題 6 題，共 34 分 (前 4 題各 6 分，後 2 題各 5 分)
    """
    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    # 1. 取得使用者身分
    declared_name = student_name.strip() if student_name else ""
    if not declared_name:
        for var_name in ["student_name", "my_name", "user_name", "author"]:
            val = env.get(var_name)
            if isinstance(val, str) and val.strip():
                declared_name = val.strip()
                break

    google_email, google_name = fetch_google_account_info()

    # 顯示姓名決策
    if declared_name and google_name:
        combined_display_name = f"{declared_name} ({google_name})"
    elif declared_name:
        combined_display_name = declared_name
    elif google_name:
        combined_display_name = google_name
    else:
        combined_display_name = "自主學習冒險者"

    final_email = google_email if google_email else "未綁定 Google 帳號"
    final_google_name = google_name if google_name else "無"

    # 2. 評分測試案例 (共 18 題，合計 100 分)
    total_score = 0
    max_score = 100
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    test_cases = [
        # ----------------------------------------------------------------------
        # 12-2-1 參數 reverse=True：從大到小反向降序排列 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-1", "填空題", "sorted(..., reverse=True) 降序排序與最高出價取值", 5,
         lambda g: (
             (True, "ranked_bids 降序排序正確，且最高出價取值無誤！")
             if (g.get("ranked_bids") == [950, 620, 480, 230, 150]) or
                ("sorted(bids,reverse=True)" in history_clean or "sorted(bids, reverse=True)" in history_str)
             else (False, "尚未找到符合預期的 ranked_bids，請在 sorted() 中指定 reverse=True 降序排列！")
         )),

        ("12-2-1", "練習題", "scores.sort(reverse=True) 原地降序與前三名得分總和", 6,
         lambda g: (
             (True, "練習題 12.2.1 scores 原地降序排序與前三名總和計算正確！")
             if (g.get("scores") == [35, 28, 24, 18, 12]) or
                ("scores.sort(reverse=True)" in history_str and ("87" in history_str or "scores[:3]" in history_str))
             else (False, "請使用 scores.sort(reverse=True) 進行原地由大到小排序，並計算前三名總和！")
         )),

        ("12-2-1", "挑戰題", "貪婪硬幣面額由大到小排序與前兩大金額合計", 6,
         lambda g: (
             (True, "挑戰題 12.2.1 硬幣面額降序排序與前二大面額合計正確！")
             if (g.get("sorted_coins") == [50, 20, 10, 5, 1] or g.get("first_two_sum") == 70) or
                ("reverse=True" in history_str and ("coins" in history_str or "70" in history_str))
             else (False, "請將硬幣面額 coins 由大到小排序，並取出前兩大面額合計（50 + 20 = 70）！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-2 數值排序 vs 字串字典序（Lexicographical Order） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-2", "填空題", "單字清單字典序排序 alpha_order 與首位語言", 5,
         lambda g: (
             (True, "alpha_order 字母字典序排序正確！首位語言為 'basic'！")
             if (g.get("alpha_order") == ['basic', 'c', 'java', 'pascal', 'python']) or
                ("sorted(languages)" in history_str and "alpha_order" in history_str)
             else (False, "請使用 alpha_order = sorted(languages) 依字母字典序排列程式語言名稱！")
         )),

        ("12-2-2", "練習題", "raw_words 字典序排序與末位單字首字元及長度", 6,
         lambda g: (
             (True, "練習題 12.2.2 單字字典序排序與末位單字特徵擷取正確！")
             if (g.get("res") == ['ant', 'bear', 'dog', 'monkey', 'zebra']) or
                ("sorted(raw_words)" in history_str and "zebra" in history_str)
             else (False, "請使用 sorted(raw_words) 進行字典序排序，並輸出最後一個單字的首字母與長度！")
         )),

        ("12-2-2", "挑戰題", "逐字元 ASCII 比對驗證器找出勝負索引", 6,
         lambda g: (
             (True, "挑戰題 12.2.2 逐字元比對驗證器實作正確！成功定位相異字元索引！")
             if ("wordA" in history_str and "wordB" in history_str and ("range(" in history_str or "!=" in history_str)) or
                (g.get("diff_found") is not None)
             else (False, "請撰寫迴圈逐字比對 wordA 與 wordB，找出首個相異字元之索引位置！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-3 考場世紀大陷阱：字串 '100' 小於 '2' 的成因與數值轉型 int 必要性 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-3", "填空題", "文字數字轉型 clean_numbers = [int(x) for x in ...] 防禦", 5,
         lambda g: (
             (False, "⚠️ 偵測到 clean_numbers 仍包含文字型態！踩到了文字數字字典序陷阱（'120' < '3'）！請使用 int(x) 進行轉型！")
             if (isinstance(g.get("clean_numbers"), list) and any(isinstance(x, str) for x in g.get("clean_numbers", [])))
             else (
                 (True, "clean_numbers 數值轉型防禦正確！數值由小到大排列無誤！")
                 if (g.get("clean_numbers") == [3, 9, 45, 88, 120]) or
                    ("int(x)" in history_str and "clean_numbers" in history_str)
                 else (False, "請使用列表生成式 [int(x) for x in raw_input_data] 將文字數字轉為整數後排序！")
             )
         )),

        ("12-2-3", "練習題", "token_list 字串轉型整數後進行由大到小降序排列", 6,
         lambda g: (
             (False, "⚠️ 偵測到排序結果仍為字串！請務必先透過 int() 轉為整數再排序！")
             if (isinstance(g.get("nums"), list) and any(isinstance(x, str) for x in g.get("nums", [])))
             else (
                 (True, "練習題 12.2.3 成功將字串數字轉為整數並完成降序排序！")
                 if (g.get("nums") == [100, 25, 12, 7, 3]) or
                    ("int(" in history_str and "reverse=True" in history_str and ("100" in history_str or "nums" in history_str))
                 else (False, "請將 token_list 內項目轉型為整數，並進行由大到小（reverse=True）降序排序！")
             )
         )),

        ("12-2-3", "挑戰題", "對比未轉型字串排序與整數排序之首位數值差距", 6,
         lambda g: (
             (True, "挑戰題 12.2.3 成功對比字串排序與數值排序之首位差距！")
             if ("wrong_sorted" in history_str and "right_sorted" in history_str) or
                ("105" in history_str and ("diff" in history_str or "100" in history_str or "abs(" in history_str))
             else (False, "請分別印出 records 未轉型排序與轉型整數排序結果，並計算第 0 個位置元素差距！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-4 大小寫混合字串排序規則：大寫字母永遠排在小寫前面 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-4", "填空題", "標準 ASCII 排序大寫字母優先 result = sorted(tags)", 5,
         lambda g: (
             (True, "result 標準 ASCII 排序正確！大寫字母開頭者成功排在最前方！")
             if (g.get("result") == ['AI', 'Data', 'algorithm', 'python']) or
                ("sorted(tags)" in history_str and "result" in history_str)
             else (False, "請使用 result = sorted(tags) 進行標準 ASCII 排序，並觀察排在第 0 位的單字！")
         )),

        ("12-2-4", "練習題", "code_names 排序並統計大寫開頭國家名稱個數", 6,
         lambda g: (
             (True, "練習題 12.2.4 國家名稱排序與大寫開頭個數統計正確！")
             if (g.get("upper_count") == 3 or g.get("sorted_names") == ['Canada', 'UK', 'USA', 'japan', 'taiwan']) or
                ("sorted(code_names)" in history_str and ("isupper()" in history_str or "<= 'Z'" in history_str))
             else (False, "請對 code_names 進行排序，並計算大寫字母開頭的國家名稱數量（'Canada', 'UK', 'USA' 共 3 個）！")
         )),

        ("12-2-4", "挑戰題", "帳號清單依大寫與小寫分層獨立排序後合併", 6,
         lambda g: (
             (True, "挑戰題 12.2.4 大小寫帳號分層排序並合併成功！")
             if (g.get("combined") == ['Alice', 'Charlie', 'bob', 'david', 'john']) or
                ("isupper()" in history_str and "islower()" in history_str and "sorted(" in history_str)
             else (False, "請分別挑出大寫與小寫開頭帳號並各自排序，最後合併為大寫在前、小寫在後的名冊！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-5 負號取反技巧：利用 -x 進行降序快速切換 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-2-5", "填空題", "定義 invert_sign(t) 回傳 -t 實現氣溫降序 hot_to_cold", 5,
         lambda g: (
             (True, "invert_sign 負號取反函數與 hot_to_cold 降序排列正確！")
             if (g.get("hot_to_cold") == [31.0, 29.8, 24.5, 22.0, 18.2]) or
                ("return -t" in history_str and "key=invert_sign" in history_str)
             else (False, "請定義 invert_sign(t) 回傳 -t，並傳入 key=invert_sign 將氣溫由高到低排序！")
         )),

        ("12-2-5", "練習題", "negative_key 高度降序排序與最高次高差距", 6,
         lambda g: (
             (True, "練習題 12.2.5 negative_key 高度降序排序與最高次高差距計算正確！")
             if (g.get("res") == [4200, 3500, 2100, 1200, 800]) or
                ("negative_key" in history_str and "altitudes" in history_str) or
                ("return -x" in history_str and "altitudes" in history_str)
             else (False, "請定義 negative_key(x) 回傳 -x，排序 altitudes 並計算最高與次高差距（700）！")
         )),

        ("12-2-5", "挑戰題", "利用負號取反函數排序利潤並找出最大虧損金額", 5,
         lambda g: (
             (True, "挑戰題 12.2.5 利潤降序排序與最大虧損金額確認正確！")
             if (g.get("desc_profits") == [4500, 2800, 1200, 0, -100, -300]) or
                ("return -x" in history_str and "profits" in history_str and "-300" in history_str)
             else (False, "請定義負號取反函數將 profits 降序排列，並印出虧損最多（數值最小者 -300）！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-6 字母大小寫不敏感排序初探：初探 key=str.lower (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-2-6", "填空題", "key=str.lower 不加括號實現姓名大小寫不敏感排序", 5,
         lambda g: (
             (False, "⚠️ 偵測到 key=str.lower() 帶有括號！傳入 key 的必須是函數名牌，請去掉小括號改寫為 key=str.lower！")
             if ("key=str.lower()" in history_clean or "key = str.lower()" in history_str)
             else (
                 (True, "sorted_names 成功使用 key=str.lower 實現大小寫不敏感排序！")
                 if (isinstance(g.get("sorted_names"), list) and [x.lower() for x in g.get("sorted_names", [])] == ['alice', 'alice', 'bob', 'charlie', 'dave']) or
                    ("key=str.lower" in history_clean)
                 else (False, "請使用 sorted(names, key=str.lower) 進行大小寫不敏感排序（請勿加括號）！")
             )
         )),

        ("12-2-6", "練習題", "城市名單大小寫不敏感升序排序與首個城市輸出", 6,
         lambda g: (
             (True, "練習題 12.2.6 城市名單大小寫不敏感排序正確！首個城市為 amsterdam！")
             if (g.get("res") == ['amsterdam', 'Berlin', 'London', 'paris', 'tokyo']) or
                ("cities" in history_str and "key=str.lower" in history_clean)
             else (False, "請使用 sorted(cities, key=str.lower) 對城市名單進行大小寫不敏感排序！")
         )),

        ("12-2-6", "挑戰題", "結合 key=str.lower 與 reverse=True 實現反向降序不分大小寫排序", 5,
         lambda g: (
             (True, "挑戰題 12.2.6 成功結合 key=str.lower 與 reverse=True 實現反向不分大小寫排序！")
             if (isinstance(g.get("desc_words"), list) and [w.lower() for w in g.get("desc_words", [])] == ['zebra', 'dog', 'cat', 'bear', 'ant']) or
                ("key=str.lower" in history_str and "reverse=True" in history_str and "vocabulary" in history_str)
             else (False, "請結合 key=str.lower 與 reverse=True 兩個參數，產出由 Z 到 A 的反向不分大小寫單字表！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 12-2：降序排序、字串字典序與數值轉型陷阱 —— 自動評分報告")
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
        level_comment = "🏆 完美滿分！你已經徹底識破字串字典序天坑與大小寫陷阱，具備極致敏銳的考場防禦力！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！逆序排列與數值轉型技巧掌握純熟，細心防禦即可在 APCS 考場百戰百勝！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本字典序與 reverse 概念已建立，請特別小心文字數字 '100' < '2' 的世紀地雷！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方各微階梯儲存格逐題點擊播放鍵執行代碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 3. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "12-2",
        "unit_name": "降序排序、字串字典序與數值轉型陷阱",
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
        filename = "grade_report_12_2.json"
        with open(filename, "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)
        print(f"💾 本地成績報告已儲存至: {filename}")
    except Exception as e:
        print(f"⚠️ 本地儲存失敗: {e}")

    # 4. 上傳雲端 Webhook
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
        except Exception:
            print("💡 （雲端記錄通道離線或連線逾時，本地成績記錄依然完全有效）")

if __name__ == "__main__":
    auto_grade_unit_12_2()
