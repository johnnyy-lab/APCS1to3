# ==============================================================================
# 🧪 《PythAPCS123》單元 12-3：自訂排序鍵值基礎：key 參數與具名函數（Named Functions） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_3.py
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

def auto_grade_unit_12_3(student_name=""):
    """
    單元 12-3：自訂排序鍵值基礎：key 參數與具名函數（Named Functions） 自動評分主程式
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
        # 12-3-1 什麼是 key= 參數？投射轉換比喻 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-1", "填空題", "定義 word_len 回傳長度並以 key=word_len 排序口號", 5,
         lambda g: (
             (True, "sorted_slogans 依長度排序正確！特徵投射模型理解深刻！")
             if (g.get("sorted_slogans") == ['Hi', 'Go!', 'Never give up', 'Keep learning python']) or
                ("key=word_len" in history_clean and "return len(s)" in history_str)
             else (False, "尚未找到符合預期的 sorted_slogans，請定義 word_len 回傳 len(s) 並傳入 key=word_len！")
         )),

        ("12-3-1", "練習題", "定義 text_length 依長度升序排列 phrases 並標註最長字串", 6,
         lambda g: (
             (True, "練習題 12.3.1 phrases 依長度排序正確！最長字串標註無誤！")
             if (g.get("res") == ['pie', 'fig', 'apple', 'banana', 'watermelon']) or
                ("text_length" in history_str and "phrases" in history_str and "watermelon" in history_str)
             else (False, "請定義 text_length(text) 回傳 len(text)，將 phrases 由短到長排序並輸出最長字串！")
         )),

        ("12-3-1", "挑戰題", "結合 key 函數與 reverse=True 依文章標題長度降序排列", 6,
         lambda g: (
             (True, "挑戰題 12.3.1 文章標題依長度降序排列正確！")
             if (isinstance(g.get("long_to_short"), list) and g.get("long_to_short") and g.get("long_to_short")[0] == "AI Revolution in Modern World") or
                ("titles" in history_str and "reverse=True" in history_str and ("len" in history_str or "get_len" in history_str))
             else (False, "請定義長度特徵函數並搭配 reverse=True，將文章標題 titles 依長度由長到短排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-2 內建函數作為鍵值：key=abs 與 key=len (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-2", "填空題", "內建 key=abs 絕對值排序與 key=len 標籤降序排序", 5,
         lambda g: (
             (False, "⚠️ 偵測到 key=abs() 或 key=len() 帶有括號！內建函數作為鍵值只傳名牌，千萬不要加小括號呼叫！")
             if ("key=abs()" in history_clean or "key=len()" in history_clean)
             else (
                 (True, "sorted_deviations (key=abs) 與 sorted_tags (key=len) 填空皆完全正確！")
                 if (g.get("sorted_deviations") == [-1, 3, -4, 12, 18, -25] and g.get("sorted_tags") == ['programming', 'algorithm', 'python', 'ai', 'it']) or
                    ("key=abs" in history_clean and "key=len" in history_clean)
                 else (False, "請分別填入 key=abs 進行離原點距離排序，與 key=len, reverse=True 進行標籤降序排序！")
             )
         )),

        ("12-3-2", "練習題", "errors.sort(key=abs) 原地依絕對值排序誤差數值", 6,
         lambda g: (
             (True, "練習題 12.3.2 errors.sort(key=abs) 原地絕對值排序正確！")
             if (g.get("errors") == [-0.1, 0.2, 0.5, -0.8, 1.2, -1.5]) or
                ("errors.sort(key=abs)" in history_clean or "errors.sort(key = abs)" in history_str)
             else (False, "請使用 errors.sort(key=abs) 對電壓誤差數值進行原地絕對值排序，並輸出最小與最大誤差！")
         )),

        ("12-3-2", "挑戰題", "使用 key=len 找出最短與最長候選密碼並計算字數差", 6,
         lambda g: (
             (True, "挑戰題 12.3.2 成功使用 key=len 定位極值密碼並計算字元差距！")
             if ("passwords" in history_str and "key=len" in history_clean and ("max_pw" in history_str or "29" in history_str or "sorted_pw" in history_str)) or
                (g.get("min_pw") == "a" and g.get("max_pw") == "super_secret_master_key_2026")
             else (False, "請使用 sorted(passwords, key=len) 找出長度最短與最長的密碼，並計算字數差距！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-3 自訂具名函數作為鍵值：def get_feature(x) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-3", "填空題", "count_vowels 回傳母音總次數並依母音數量排序單字", 5,
         lambda g: (
             (True, "count_vowels 函數與 vowel_order 母音數量排序完全正確！")
             if (g.get("vowel_order") == ['sky', 'python', 'tea', 'queue', 'beautiful']) or
                ("count_vowels" in history_str and "key=count_vowels" in history_clean)
             else (False, "請在 count_vowels 函數中 return cnt，並傳入 key=count_vowels 排序單字！")
         )),

        ("12-3-3", "練習題", "定義 distance_from_50 排序離 50 距離並找出最接近數值", 6,
         lambda g: (
             (True, "練習題 12.3.3 distance_from_50 距離排序與最接近數值輸出正確！")
             if (g.get("res") == [48, 53, 42, 65, 20, 80]) or
                ("distance_from_50" in history_str and "raw_vals" in history_str and "48" in history_str)
             else (False, "請定義 distance_from_50(x) 回傳 abs(x - 50)，將 raw_vals 排序並輸出最接近 50 的數值！")
         )),

        ("12-3-3", "挑戰題", "定義 calc_digit_sum 依數字各位數之和升序排序", 6,
         lambda g: (
             (True, "挑戰題 12.3.3 calc_digit_sum 各位數和計算與升序排序正確！")
             if (g.get("sorted_by_digit_sum") == [11, 123, 204, 45, 90]) or
                ("calc_digit_sum" in history_str and "numbers" in history_str and "sorted(" in history_str)
             else (False, "請定義 calc_digit_sum(num) 計算各位數和，將 numbers 依數位和由小到大排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-4 元組第二欄位排序：def get_second(item): return item[1] (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-4", "填空題", "定義 get_y 回傳 pt[1] 依 Y 軸座標升序排序 points", 5,
         lambda g: (
             (True, "sorted_by_y 依 Y 軸高度排序正確！第二欄位索引 item[1] 運用精準！")
             if (g.get("sorted_by_y") == [(3, 1), (2, 4), (10, 5), (8, 9)]) or
                ("pt[1]" in history_clean and "key=get_y" in history_clean)
             else (False, "請在 get_y(pt) 中回傳 pt[1]，並傳入 key=get_y 依 Y 軸排序點座標！")
         )),

        ("12-3-4", "練習題", "定義 get_seniority 依年資降序排序 records 並輸出最資深代號", 6,
         lambda g: (
             (True, "練習題 12.3.4 get_seniority 員工年資降序排序與資深代號輸出正確！")
             if (g.get("sorted_emp") == [('E02', 12), ('E03', 7), ('E01', 3), ('E04', 1)]) or
                ("get_seniority" in history_str and "records" in history_str and "E02" in history_str)
             else (False, "請定義 get_seniority(rec) 回傳 rec[1]，將 records 依年資由高到低降序排序！")
         )),

        ("12-3-4", "挑戰題", "定義 get_total_value 計算水果庫存總價值並降序排序", 6,
         lambda g: (
             (True, "挑戰題 12.3.4 水果庫存總資產計算與降序排序正確！")
             if (isinstance(g.get("sorted_inv"), list) and g.get("sorted_inv") and g.get("sorted_inv")[0][0] in ["香蕉", "櫻桃"]) or
                ("get_total_value" in history_str and "inventory" in history_str and ("price * qty" in history_str or "item[1] * item[2]" in history_clean))
             else (False, "請定義 get_total_value(item) 回傳單價乘數量，將 inventory 依總價值由大到小排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-5 字典走訪排序：以 sorted(d.items(), key=...) 依 Value 排序 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-3-5", "填空題", "定義 get_price 提取 item_pair[1] 將 cart.items() 依價格排序", 5,
         lambda g: (
             (True, "sorted_items 成功將購物車品項依價格由便宜到貴排序！")
             if (g.get("sorted_items") == [('Eraser', 20), ('Pen', 45), ('Book', 350), ('Headphones', 1200)]) or
                ("cart.items()" in history_clean and "key=get_price" in history_clean)
             else (False, "請在 get_price 中回傳 item_pair[1]，並使用 sorted(cart.items(), key=get_price)！")
         )),

        ("12-3-5", "練習題", "定義 get_frequency 依詞頻降序排序 freq.items() 並印出最高頻單字", 6,
         lambda g: (
             (True, "練習題 12.3.5 詞頻字典降序排行與最高頻單字輸出正確！")
             if (g.get("res") == [('the', 42), ('is', 30), ('python', 15), ('code', 8)]) or
                ("get_frequency" in history_str and "freq.items()" in history_clean and "the" in history_str)
             else (False, "請定義 get_frequency(pair) 回傳 pair[1]，將 freq.items() 依出現次數降序排列！")
         )),

        ("12-3-5", "挑戰題", "線上商店 VIP 顧客前兩大消費金額合計與營業額佔比分析", 5,
         lambda g: (
             (True, "挑戰題 12.3.5 VIP 顧客消費排序與營業額佔比計算正確！")
             if ("customers.items()" in history_clean and ("sorted_customers" in history_str or "top2_sum" in history_str or "ratio" in history_str)) or
                (g.get("top2_sum") == 13800)
             else (False, "請將 customers.items() 依消費金額由高到低排序，並計算前兩大 VIP 消費總和之全體佔比！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-6 排序除錯心法：如何單獨測試 key 函數確認特徵值抽取無誤 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-3-6", "填空題", "修復 safe_second_char 長度不足 2 防禦並安全排序", 5,
         lambda g: (
             (True, "safe_second_char 防禦修復正確！邊界極端測資單獨檢驗與排序成功！")
             if (g.get("safe_sorted") == ['a', '', 'banana', 'cat', 'dog'] or (isinstance(g.get("safe_sorted"), list) and len(g.get("safe_sorted")) == 5)) or
                ("len(s) < 2" in history_str and "key=safe_second_char" in history_clean)
             else (False, "當長度不足 2 時請 return \"\" 空字串，並傳入 key=safe_second_char 進行安全排序！")
         )),

        ("12-3-6", "練習題", "定義 get_month 提取月份整數、單獨印出驗證並排序 dates", 6,
         lambda g: (
             (True, "練習題 12.3.6 get_month 月份提取、單獨除錯驗證與 dates 排序正確！")
             if (g.get("res") == ['2026-01-30', '2026-03-21', '2026-08-14', '2026-11-05']) or
                ("get_month" in history_str and "dates" in history_str and "2026-09-15" in history_str)
             else (False, "請定義 get_month(date_str) 提取月份整數，先單獨測試 '2026-09-15' 再排序 dates！")
         )),

        ("12-3-6", "挑戰題", "time_to_seconds 時間轉秒數、單獨測試驗證並評選賽車冠軍", 5,
         lambda g: (
             (True, "挑戰題 12.3.6 賽車時間轉秒數、單獨樣本驗證與冠軍定位正確！")
             if (isinstance(g.get("ranked_racers"), list) and g.get("ranked_racers") and g.get("ranked_racers")[0][0] == "Mario") or
                ("time_to_seconds" in history_str and "racer_data" in history_str and "125" in history_str)
             else (False, "請定義 time_to_seconds 轉換總秒數，單獨驗證 ('Luigi', '2:05') 為 125 秒後排序找出冠軍！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 12-3：自訂排序鍵值基礎：key 參數與具名函數（Named Functions） —— 自動評分報告")
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
        level_comment = "🏆 完美滿分！你已經徹底精通自訂鍵值與特徵抽取技術，具備駕馭複雜多維資料排序的強悍實力！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！具名函數特徵投射與字典走訪排序掌握極佳，單獨除錯意識非常出色！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本 key 參數概念已建立，請留意元組索引對齊與 key 函數傳名牌不加括號的鐵律！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方各微階梯儲存格逐題點擊播放鍵執行代碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 3. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "12-3",
        "unit_name": "自訂排序鍵值基礎：key 參數與具名函數（Named Functions）",
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
        filename = "grade_report_12_3.json"
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
    auto_grade_unit_12_3()
