# ==============================================================================
# 🧪 《PythAPCS123》單元 12-1：就地排序（sort）與新物件排序（sorted） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_1.py
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

def auto_grade_unit_12_1(student_name=""):
    """
    單元 12-1：就地排序（sort）與新物件排序（sorted） 自動評分主程式
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
        # 12-1-1 排序核心概念：升序預設行為 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-1", "填空題", "sorted() 升序排序與最高身高索引用法", 5,
         lambda g: (
             (True, "sorted_heights 升序排序正確，且最高身高取值無誤！")
             if (g.get("sorted_heights") == [158, 165, 169, 172, 175, 180]) or
                ("sorted(heights)" in history_str and "sorted_heights" in history_str)
             else (False, "尚未找到符合預期的 sorted_heights，請使用 sorted(heights) 並確認已點擊儲存格播放鍵執行！")
         )),

        ("12-1-1", "練習題", "整數數列升序排序與全距計算", 6,
         lambda g: (
             (True, "練習題 12.1.1 raw_data 升序排序與全距計算正確！")
             if (g.get("res") == [12, 34, 45, 67, 89]) or
                ("sorted(raw_data)" in history_str and ("- res[0]" in history_str or "77" in history_str or "res[-1]" in history_str))
             else (False, "請將 raw_data 進行 sorted() 升序排序，並計算最大值與最小值之全距（最大值 - 最小值）！")
         )),

        ("12-1-1", "挑戰題", "浮點數跑步成績排序與前三名切片選取", 6,
         lambda g: (
             (True, "挑戰題 12.1.1 浮點數跑步成績排序與前三名切片成功！")
             if (isinstance(g.get("ordered_times"), list) and len(g.get("ordered_times")) >= 5 and g.get("ordered_times") == sorted(g.get("ordered_times"))) or
                ("sorted(" in history_str and "[:3]" in history_str and ("times" in history_str or "ordered" in history_str))
             else (False, "請宣告至少 5 筆浮點數之跑步秒數串列，使用 sorted() 升序排序後以 [:3] 取出前三名！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-2 原地修改方法 list.sort() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-2", "填空題", "避免 a = a.sort() 陷阱，單獨一行呼叫 cards.sort()", 5,
         lambda g: (
             (False, "⚠️ 偵測到 cards 變數值為 None！這是經典的 cards = cards.sort() 陷阱！.sort() 是原地修改且回傳 None，請單獨一行呼叫 cards.sort()！")
             if g.get("cards") is None
             else (
                 (True, "cards.sort() 單獨一行原地排序正確，成功避開 None 陷阱！")
                 if (g.get("cards") == [1, 2, 4, 7, 9]) or ("cards.sort()" in history_str and "cards = cards.sort()" not in history_clean)
                 else (False, "請使用 cards.sort() 原地排序撲克牌串列，切勿覆蓋原變數！")
             )
         )),

        ("12-1-2", "練習題", "data.sort() 原地修改負數與正數串列", 6,
         lambda g: (
             (False, "⚠️ 偵測到 data 變數值為 None！請勿對 .sort() 進行賦值（避免 data = data.sort()）！")
             if g.get("data") is None
             else (
                 (True, "練習題 12.1.2 data.sort() 原地排序與首元素取值正確！")
                 if (g.get("data") == [-9, -3, 0, 15, 42]) or ("data.sort()" in history_str and "data = data.sort()" not in history_clean)
                 else (False, "請使用 data.sort() 對 data 進行原地升序排序，並印出排序後內容與第一個元素！")
             )
         )),

        ("12-1-2", "挑戰題", "捕捉 .sort() 回傳值為 None 之防呆警告機制", 6,
         lambda g: (
             (True, "挑戰題 12.1.2 成功驗證 .sort() 回傳值為 None 並發出警示！")
             if ("test_list.sort()" in history_str and ("is None" in history_str or "== None" in history_str)) or
                (g.get("ret") is None and "test_list" in g)
             else (False, "請執行 test_list.sort() 並檢查其回傳值是否為 None，若為 None 則印出警告訊息！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-3 內建函數 sorted(iterable) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-3", "填空題", "sorted() 生成獨立新串列且原串列完好無損", 5,
         lambda g: (
             (True, "leaderboard 成功由 sorted(log_order) 生成，且原 log_order 完整保留！")
             if (g.get("leaderboard") == [60, 72, 88, 91, 95] and g.get("log_order") == [88, 95, 72, 60, 91]) or
                ("sorted(log_order)" in history_str and "leaderboard" in history_str)
             else (False, "請使用 leaderboard = sorted(log_order) 產出新排序串列，同時維持 log_order 原樣！")
         )),

        ("12-1-3", "練習題", "raw_temps 溫度計紀錄雙軌保留與排序", 6,
         lambda g: (
             (True, "練習題 12.1.3 成功產生 sorted_temps 排序串列並保留原始 raw_temps！")
             if (g.get("sorted_temps") == [19.8, 23.0, 25.4, 28.5, 31.2] and g.get("raw_temps") == [28.5, 23.0, 31.2, 19.8, 25.4]) or
                ("sorted(raw_temps)" in history_str and "sorted_temps" in history_str)
             else (False, "請使用 sorted_temps = sorted(raw_temps) 進行排序，並確認 raw_temps 未受竄改！")
         )),

        ("12-1-3", "挑戰題", "結合 sorted() 極值與原串列 arr.index() 原始索引定位", 6,
         lambda g: (
             (True, "挑戰題 12.1.3 成功結合 sorted() 與 arr.index() 找出極值原始索引！")
             if ("arr.index" in history_str and "sorted(" in history_str) or
                (isinstance(g.get("arr"), list) and "min_val" in g and "max_val" in g)
             else (False, "請宣告包含至少 5 個整數的 arr，以 sorted() 找出最大與最小值後，透過 arr.index() 找出其原始索引！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-4 記憶體耗損與使用時機對照 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-4", "填空題", "依場景精準選用 nums1.sort() 與 sorted(nums2)", 5,
         lambda g: (
             (True, "nums1 原地排序與 sorted_nums2 新串列生成填空皆完全正確！")
             if (g.get("nums1") == [1, 3, 7, 9] and g.get("sorted_nums2") == [2, 4, 6, 8] and g.get("nums2") == [8, 4, 6, 2]) or
                ("nums1.sort()" in history_str and "sorted(nums2)" in history_str)
             else (False, "場景 1 請使用 nums1.sort() 原地修改；場景 2 請使用 sorted_nums2 = sorted(nums2)！")
         )),

        ("12-1-4", "練習題", "遊戲戰力排行榜 leaderboard 雙軌維護", 6,
         lambda g: (
             (True, "練習題 12.1.4 成功以 sorted(power_list) 建立排行榜並印出首位與戰力天花板！")
             if (g.get("leaderboard") == [1500, 1800, 2400, 2900, 3200] and g.get("power_list") == [2400, 1500, 3200, 1800, 2900]) or
                ("sorted(power_list)" in history_str and "leaderboard" in history_str)
             else (False, "請使用 leaderboard = sorted(power_list) 產生排行榜，並輸出原始第一位與最高戰力者！")
         )),

        ("12-1-4", "挑戰題", "使用 id() 探測驗證原地修改 O(1) 與副本生成 O(N) 記憶體差異", 6,
         lambda g: (
             (True, "挑戰題 12.1.4 成功以 id() 探測驗證原地排序前後 id 相同與 sorted 副本 id 不同！")
             if ("id(items)" in history_str and "items.sort()" in history_str and "sorted(" in history_str) or
                (g.get("id_before") is not None and g.get("id_before") == g.get("id_after"))
             else (False, "請使用 id() 記錄 items 於 items.sort() 前後的記憶體位址，並對比 sorted(items2) 的新位址！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-5 非串列容器的排序 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-1-5", "填空題", "字母易位字（Anagram）檢驗神器 is_anagram", 5,
         lambda g: (
             (True, "is_anagram 字母易位字檢驗填空正確！sorted(word1) == sorted(word2)！")
             if (g.get("is_anagram") is True) or
                ("sorted(word1)" in history_str and "sorted(word2)" in history_str and "is_anagram" in history_str)
             else (False, "請使用 is_anagram = sorted(word1) == sorted(word2) 進行易位字驗證！")
         )),

        ("12-1-5", "練習題", "結合 set() 去重與 sorted() 升序輸出 unique_sorted", 6,
         lambda g: (
             (True, "練習題 12.1.5 集合去重與 sorted() 升序排序整合正確！")
             if (g.get("unique_sorted") == [1, 2, 3, 7, 9]) or
                ("sorted(set(raw_list))" in history_str or "unique_sorted" in history_str)
             else (False, "請使用 unique_sorted = sorted(set(raw_list)) 將 raw_list 先去重後再排序！")
         )),

        ("12-1-5", "挑戰題", "密碼字元 ASCII 排序後首字元數字檢驗", 5,
         lambda g: (
             (True, "挑戰題 12.1.5 密碼排序後首字元數字範圍檢驗正確！")
             if ("sorted(password)" in history_str or "sorted_chars" in history_str) and
                (("<= sorted_chars[0] <=" in history_str) or ("isdigit()" in history_str) or ("0" in history_str and "9" in history_str))
             else (False, "請宣告密碼字串 password，以 sorted() 排序後檢查首字元是否介於 '0' 至 '9' 之間！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-6 穩定排序（Stable Sort）特性 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-1-6", "填空題", "穩定排序概念檢驗，相等鍵值保留相對順序", 5,
         lambda g: (
             (True, "sorted_data 穩定排序填空正確！相同鍵值項目順序完全保持原樣！")
             if (g.get("sorted_data") == [('B', 5), ('D', 5), ('A', 10), ('C', 10)]) or
                ("sorted(data, key=get_value)" in history_str or "sorted(data,key=get_value)" in history_clean)
             else (False, "請使用 sorted_data = sorted(data, key=get_value) 驗證穩定排序特性！")
         )),

        ("12-1-6", "練習題", "選手同分成績穩定排序保留登記順序", 6,
         lambda g: (
             (True, "練習題 12.1.6 選手成績穩定排序正確！同分者登記先後完全維持！")
             if (g.get("res") == [(80, 'T2'), (80, 'T4'), (100, 'T1'), (100, 'T3')]) or
                ("sorted(athletes" in history_str and ("take_score" in history_str or "lambda" in history_str))
             else (False, "請以分數為鍵值對 athletes 進行 sorted 排序，確認同分選手保持原始相對順序！")
         )),

        ("12-1-6", "挑戰題", "商品類別穩定排序示範", 5,
         lambda g: (
             (True, "挑戰題 12.1.6 商品類別穩定排序示範正確！")
             if ("sorted(" in history_str and "category" in history_str) or
                (isinstance(g.get("sorted_products"), list) and len(g.get("sorted_products")) >= 4)
             else (False, "請建立商品清單並依「商品類別」進行穩定排序，展示同類別商品先後順序不變！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 12-1：就地排序（sort）與新物件排序（sorted） —— 自動評分報告")
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
        level_comment = "🏆 完美滿分！你已經徹底攻克就地排序與新物件排序的核心記憶體機制，具備 APCS 演算法高手的穩健實力！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！對於 sort() 與 sorted() 的使用時機與底層差異掌握非常扎實，稍微細心檢查即可登峰造極！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本排序概念已建立，請特別注意原地修改回傳 None 的考場經典地雷！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方各個微階梯儲存格逐題點擊播放鍵執行代碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 3. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "12-1",
        "unit_name": "就地排序（sort）與新物件排序（sorted）",
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
        filename = "grade_report_12_1.json"
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
    auto_grade_unit_12_1()
