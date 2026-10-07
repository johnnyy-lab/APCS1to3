# ==============================================================================
# 🧪 《PythAPCS123》單元 7-6：常用字串方法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_6.py
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

def auto_grade_unit_7_6():
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
        # 7-6-1 子字串存在判定：in 與 not in (共 20 分)
        # ----------------------------------------------------------------------
        ("7-6-1", "填空題", "成員運算子 in 子字串偵測 (verdict)", 6,
         lambda g: (
             (True, "成員運算子 in 偵測敏感詞成功！")
             if g.get("verdict") == "SPAM DETECTED" or
                ('"spam"incomment' in history_clean or "'spam'incomment" in history_clean)
             else (False, "請在 7-6-1 填空題空格填入成員運算子 in！")
         )),

        ("7-6-1", "練習題", "字母母音身分檢查器 (in 'aeiouAEIOU')", 9,
         lambda g: (
             (True, "母音字元 in 集合比對與判定分支正確！")
             if ("in" in history_str and ("aeiou" in history_str or "AEIOU" in history_str) and
                 ("VOWEL" in history_str or "CONSONANT" in history_str)) or
                ("VOWEL" in history_str and "CONSONANT" in history_str)
             else (False, "請讀入字元 ch，使用 in 檢查是否屬於母音，輸出 VOWEL 或 CONSONANT！")
         )),

        ("7-6-1", "挑戰題", "安全密碼多重元素檢驗 (數字與特殊符號)", 5,
         lambda g: (
             (True, "數字與特殊符號雙重包含檢驗正確！")
             if ("STRONG PASSWORD" in history_str or "WEAK PASSWORD" in history_str) and
                ("in" in history_str)
             else (False, "請檢驗密碼是否同時包含數字與特殊符號 (!@#$%) 並輸出評估結果！")
         )),

        # ----------------------------------------------------------------------
        # 7-6-2 子字串出現次數統計：.count() (共 20 分)
        # ----------------------------------------------------------------------
        ("7-6-2", "填空題", ".count() 方法次數統計 (s_count)", 6,
         lambda g: (
             (True, "使用 river.count('s') 成功統計出 4 次！")
             if g.get("s_count") == 4 or
                ("river.count(" in history_clean)
             else (False, "請在 7-6-2 填空題空格填入方法名稱 count！")
         )),

        ("7-6-2", "練習題", "括號平衡簡易檢查器 (.count('(') vs .count(')'))", 9,
         lambda g: (
             (True, "左右括號 count 次數統計與平衡判定正確！")
             if (".count(" in history_str and
                 ("BALANCED:" in history_str or "UNBALANCED:" in history_str)) or
                ("BALANCED: 2" in history_str or "UNBALANCED: 3 vs 1" in history_str)
             else (False, "請使用 .count() 統計左括號與右括號數量，輸出平衡報告！")
         )),

        ("7-6-2", "挑戰題", "多子字串佔比分析器 (X 與 O 出現勝負判定)", 5,
         lambda g: (
             (True, "X 與 O 出現頻率統計與勝負比對完整！")
             if (".count(" in history_str and
                 ("WINS" in history_str or "TIE" in history_str)) or
                ("X WINS" in history_str or "O WINS" in history_str)
             else (False, "請使用 .count() 統計 X 與 O 數量，比較印出勝負結果！")
         )),

        # ----------------------------------------------------------------------
        # 7-6-3 字串分割成串列：.split() (共 20 分)
        # ----------------------------------------------------------------------
        ("7-6-3", "填空題", ".split() 空白分割與詞數走訪 (word_count)", 6,
         lambda g: (
             (True, "使用 motto.split() 完成單字切分與詞數統計！")
             if g.get("word_count") == 4 or
                ("motto.split()" in history_clean)
             else (False, "請在 7-6-3 填空題空格填入方法名稱 split！")
         )),

        ("7-6-3", "練習題", "句子最長單字搜尋器 (split() 搭配長度比對)", 9,
         lambda g: (
             (True, "split() 單字拆分與最長單字搜尋輸出正確！")
             if (".split(" in history_str and "len(" in history_str and
                 ("Longest:" in history_str and "Length:" in history_str)) or
                ("Longest: quick" in history_str or "Longest: Practice" in history_str)
             else (False, "請使用 .split() 切分單字，找出最長單字與長度並輸出！")
         )),

        ("7-6-3", "挑戰題", "逐詞反轉印出 (split() 各單字 [::-1])", 5,
         lambda g: (
             (True, "句子 split 拆分與單字各自 [::-1] 反轉輸出正確！")
             if (".split(" in history_str and "[::-1]" in history_str) or
                ("I evol nohtyp" in history_str)
             else (False, "請使用 .split() 切出單字，將各單字各自反轉後以空格分隔輸出！")
         )),

        # ----------------------------------------------------------------------
        # 7-6-4 搜尋子字串索引位置：.find() (共 20 分)
        # ----------------------------------------------------------------------
        ("7-6-4", "填空題", ".find(':') 冒號定位與數值切片 (score_str)", 6,
         lambda g: (
             (True, "使用 .find(':') 定位成功分離數值字串 98！")
             if g.get("score_str") == "98" or
                ('data_record.find(":")' in history_clean or "data_record.find(':')" in history_clean)
             else (False, "請在 7-6-4 填空題空格填入方法名稱 find！")
         )),

        ("7-6-4", "練習題", "關鍵字雷達定位回報器 (.find(keyword))", 9,
         lambda g: (
             (True, "關鍵字 .find() 索引定位與 NOT FOUND 分支正確！")
             if (".find(" in history_str and
                 ("FOUND AT INDEX" in history_str or "NOT FOUND" in history_str)) or
                ("FOUND AT INDEX 11" in history_str or "NOT FOUND" in history_str)
             else (False, "請使用 .find() 尋找關鍵字位置，印出 FOUND AT INDEX 或 NOT FOUND！")
         )),

        ("7-6-4", "挑戰題", "標籤文字解碼器 (find('[') 與 find(']'))", 5,
         lambda g: (
             (True, "左右方括號定位與標籤文字切片提取正確！")
             if (".find(" in history_str and ("[" in history_str and "]" in history_str) and
                 ("Tag:" in history_str or "INVALID TAG" in history_str)) or
                ("Tag: ADMIN" in history_str)
             else (False, "請以 .find() 尋找 '[' 與 ']'，截取中間標籤文字輸出 Tag: [內容]！")
         )),

        # ----------------------------------------------------------------------
        # 7-6-5 大小寫轉換：.lower() 與 .upper() (共 20 分)
        # ----------------------------------------------------------------------
        ("7-6-5", "填空題", ".lower() 標準化大小寫比對 (action)", 6,
         lambda g: (
             (True, "使用 command.lower() 達成不分大小寫比對！")
             if g.get("action") == "CONFIRMED" or
                ("command.lower()" in history_clean)
             else (False, "請在 7-6-5 填空題空格填入方法名稱 lower！")
         )),

        ("7-6-5", "練習題", "不分大小寫單字搜尋器 (lower() 與 in 比對)", 9,
         lambda g: (
             (True, "全句與關鍵字轉小寫比對 (MATCH FOUND / NO MATCH) 正確！")
             if (".lower()" in history_str and "in" in history_str and
                 ("MATCH FOUND" in history_str or "NO MATCH" in history_str)) or
                ("MATCH FOUND" in history_str or "NO MATCH" in history_str)
             else (False, "請以 .lower() 將兩者皆轉小寫後比對，輸出 MATCH FOUND 或 NO MATCH！")
         )),

        ("7-6-5", "挑戰題", "終極進階迴文檢測器 (lower + 去除空格 + [::-1])", 5,
         lambda g: (
             (True, "去空格、轉小寫與 [::-1] 終極迴文檢測設計完整！")
             if (".lower()" in history_str and "[::-1]" in history_str and
                 ("PALINDROME:" in history_str or "NOT PALINDROME" in history_str)) or
                ("PALINDROME: racecar" in history_str)
             else (False, "請將句子轉小寫並去除空格後，判定是否為迴文並依格式輸出！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-6 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 in 探測、.count() 統計、.split() 分割、.find() 定位與大小寫標準化，字串百寶箱統帥！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，核心字串方法靈活調用！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調方法參數與大小寫邏輯！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-6",
        "unit_title": "常用字串方法",
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
        log_filename = "score_log_unit_7_6.json"
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
auto_grade_unit_7_6()
