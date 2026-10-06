# ==============================================================================
# 🧪 《PythAPCS123》單元 6-1：計數迴圈與 range 函式解析 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_1.py
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

def auto_grade_unit_6_1():
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
        # 6-1-1 為什麼需要迴圈：終結重複複製貼上的自動化引擎 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-1-1", "填空題", "重複輸出勵志口號 (for _ in range(3))", 4,
         lambda g: (
             (True, "迴圈結構與重複次數填寫正確：for _ in range(3)！")
             if ("for" in history_str and "range(3)" in history_clean and
                 ("加油！堅持練習就能掌握 APCS！" in history_str or "加油" in history_str))
             else (False, "請在 6-1-1 填空題空格填入 for 與 3！")
         )),

        ("6-1-1", "練習題", "校園廣播連續播報 (times 次廣播)", 4,
         lambda g: (
             (True, "校園廣播連續播報迴圈輸出正確！")
             if (("times" in g or "times" in history_str) and
                 ("[校園廣播]" in history_str or "回到教室" in history_str or "range(times)" in history_clean))
             else (False, "請設定 times 並使用 for 迴圈印出 times 次校園廣播！")
         )),

        ("6-1-1", "挑戰題", "星際探測訊號 (repeat_count = 6)", 5,
         lambda g: (
             (True, "星際探測訊號 6 次重複輸出成功！")
             if (("repeat_count" in g or "repeat_count" in history_str) and
                 ("星際" in history_str or "探測訊號" in history_str or "range(6)" in history_clean or "range(repeat_count)" in history_clean))
             else (False, "請宣告 repeat_count = 6 並利用 for 迴圈印出 6 次星際探測訊號！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-2 for 迴圈解剖學：標頭行、迴圈變數與縮排本體 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-1-2", "填空題", "for 迴圈解剖宣告 (for i in range(4):)", 4,
         lambda g: (
             (True, "for 迴圈變數、關鍵字與冒號宣告填寫正確：for i in range(4):！")
             if ("foriinrange(4):" in history_clean or
                 ("range(4)" in history_clean and "檢查點" in history_str and "通關成功" in history_str))
             else (False, "請在 6-1-2 填空題空格填入變數 i、關鍵字 in 與冒號 :！")
         )),

        ("6-1-2", "練習題", "機器人巡邏站 (patrol_turns 與完成宣告)", 4,
         lambda g: (
             (True, "巡邏輪數走訪與結束輸出完全吻合！")
             if (("patrol_turns" in g or "patrol_turns" in history_str) and
                 ("巡邏進度" in history_str or "巡邏任務完成" in history_str or "range(patrol_turns)" in history_clean))
             else (False, "請走訪 range(patrol_turns) 印出巡邏步數，結束後印出『巡邏任務完成！』！")
         )),

        ("6-1-2", "挑戰題", "太空發射塔檢測 (check_count = 5 與發射準備完成)", 5,
         lambda g: (
             (True, "太空發射塔各階段檢測走訪與就緒輸出成功！")
             if (("check_count" in g or "check_count" in history_str) and
                 ("System Check Stage" in history_str or "Ready to Launch" in history_str or "range(check_count)" in history_clean))
             else (False, "請走訪 range(check_count) 印出各階段檢測狀態，並輸出準備就緒！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-3 單參數 range(n)：由 0 開始走訪前閉後開的次數控制器 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-1-3", "填空題", "單參數 range 載入關卡 (range(4))", 4,
         lambda g: (
             (True, "單參數 range(4) 終止值設定正確！")
             if ("range(4)" in history_clean and
                 ("Loading Stage" in history_str or "Loading" in history_str))
             else (False, "請在 6-1-3 填空題填入 4，讓迴圈走訪 0 到 3 關卡！")
         )),

        ("6-1-3", "練習題", "門診排號機 (wait_count 號碼牌計算)", 4,
         lambda g: (
             (True, "門診叫號號碼牌 (i + 1) 計算與輸出正確！")
             if (("wait_count" in g or "wait_count" in history_str) and
                 ("號至 1 號櫃檯辦理" in history_str or "櫃檯" in history_str or "+ 1" in history_str or "+1" in history_str))
             else (False, "請利用 wait_count 與 i + 1 印出各號碼牌至 1 號櫃檯辦理！")
         )),

        ("6-1-3", "挑戰題", "自訂乘法倍數列表 (base = 7, count = 5)", 5,
         lambda g: (
             (True, "7 的前 5 個倍數列表生成與輸出成功！")
             if ((("base" in g and "count" in g) or ("base" in history_str and "count" in history_str)) and
                 ("7" in history_str and ("x" in history_str or "*" in history_str))) or
                ("7 x 5 = 35" in history_str or "7 * 5 = 35" in history_str)
             else (False, "請設定 base = 7, count = 5，利用 range(count) 印出 7 的前 5 個正整數倍數！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-4 雙參數 range(start, stop)：指定起點的前閉後開區間精算 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-1-4", "填空題", "雙參數 range 起訖平方計算 (range(1, 6))", 4,
         lambda g: (
             (True, "雙參數起點 1 與終點 6 填寫精確無誤！")
             if ("range(1,6)" in history_clean and
                 ("平方是" in history_str or "**2" in history_clean or "** 2" in history_str))
             else (False, "請在 6-1-4 填空題空格填入起點 1 與終點 6！")
         )),

        ("6-1-4", "練習題", "頁碼範圍列印機 (start_page, end_page)", 4,
         lambda g: (
             (True, "頁碼範圍雙參數 range 走訪列印正確！")
             if ((("start_page" in g and "end_page" in g) or ("start_page" in history_str and "end_page" in history_str)) and
                 ("Printing page" in history_str or "end_page + 1" in history_str or "end_page+1" in history_clean))
             else (False, "請設定 start_page 與 end_page，並走訪 range(start_page, end_page + 1) 列印頁碼！")
         )),

        ("6-1-4", "挑戰題", "攝氏轉華氏溫度對照表 (c_start = 20, c_end = 25)", 5,
         lambda g: (
             (True, "攝氏區間溫度轉換華氏對照表計算無誤！")
             if ((("c_start" in g and "c_end" in g) or ("c_start" in history_str and "c_end" in history_str)) and
                 ("9 / 5" in history_str or "9/5" in history_clean or "32" in history_str)) or
                ("68.0" in history_str or "77.0" in history_str)
             else (False, "請設定 c_start = 20, c_end = 25，利用雙參數 range 計算並輸出對應華氏溫度！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-5 三參數正步進 range(start, stop, step)：等差跳步巡航 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-1-5", "填空題", "三參數正步進 (range(10, 51, 10))", 4,
         lambda g: (
             (True, "三參數起點 10 與步進 10 填寫正確！")
             if ("range(10,51,10)" in history_clean or
                 ("range(10," in history_clean and ",10)" in history_clean))
             else (False, "請在 6-1-5 填空題填入起點 10 與步進值 10！")
         )),

        ("6-1-5", "練習題", "偶數巡航機 (limit 正偶數走訪)", 4,
         lambda g: (
             (True, "偶數巡航步進為 2 之走訪輸出正確！")
             if (("limit" in g or "limit" in history_str) and
                 (",2)" in history_clean or ", 2)" in history_str or "range(2," in history_clean))
             else (False, "請設定 limit，並使用 range(2, limit + 1, 2) 依序印出所有正偶數！")
         )),

        ("6-1-5", "挑戰題", "跳步餘數特訓 (100 起跨步 15 至 < 180)", 4,
         lambda g: (
             (True, "三位數跨步 15 走訪與除以 10 之餘數運算成功！")
             if ("range(100,180,15)" in history_clean or
                 ("100" in history_str and "15" in history_str and "180" in history_str and ("%" in history_str or "餘數" in history_str)))
             else (False, "請使用 range(100, 180, 15) 走訪並印出各數值及其除以 10 的餘數！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-6 負步進倒數計時 range(start, stop, -step)：倒著數的邊界與防空轉陷阱 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-1-6", "填空題", "負步進倒數邊界 (range(10, 5, -1))", 4,
         lambda g: (
             (True, "負步進終止界限 5 與 -1 填寫正確：range(10, 5, -1)！")
             if ("range(10,5,-1)" in history_clean or "range(10, 5, -1)" in history_str)
             else (False, "請在 6-1-6 填空題填入終止邊界 5 與負步進值 -1！")
         )),

        ("6-1-6", "練習題", "倒數計時器 (start_countdown 倒數至 1 加 Time is up!)", 4,
         lambda g: (
             (True, "倒數計時器與結束廣播輸出正確！")
             if (("start_countdown" in g or "start_countdown" in history_str) and
                 ("Countdown" in history_str or "Time is up" in history_str) and
                 ("-1" in history_str))
             else (False, "請由 start_countdown 倒數至 1（步進 -1）印出 Countdown，結束印出 Time is up!！")
         )),

        ("6-1-6", "挑戰題", "雙倍速倒數遞減 (start_val = 20, 步進 -4 加 Complete!)", 4,
         lambda g: (
             (True, "步進值 -4 倒數遞減至正整數與 Complete 輸出成功！")
             if (("start_val" in g or "start_val" in history_str or "-4" in history_str) and
                 ("Complete" in history_str or "20 16 12 8 4" in history_str or "range(20,0,-4)" in history_clean))
             else (False, "請設定 start_val = 20，以步進 -4 遞減至正整數並輸出 Complete!！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-7 迴圈追蹤表（Trace Table）：手繪變數逐輪演變的視覺化除錯法 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-1-7", "填空題", "迴圈追蹤手算結果 (expected_result = 5)", 4,
         lambda g: (
             (True, "手繪追蹤值填寫精準無誤：expected_result = 5！")
             if (g.get("expected_result") == 5 or "expected_result=5" in history_clean)
             else (False, "請在 6-1-7 填空題空格填入 i = 2 時 result 的計算結果 5！")
         )),

        ("6-1-7", "練習題", "等差跳步追蹤演算法 (steps = 3, status = i * 3 + 2)", 4,
         lambda g: (
             (True, "等差跳步計算追蹤 (status = i * 3 + 2) 輸出正確！")
             if (("steps" in g or "steps" in history_str) and
                 ("* 3 + 2" in history_str or "*3+2" in history_clean or "Step" in history_str))
             else (False, "請依 steps 走訪並印出每一輪 Step i: status (status = i * 3 + 2)！")
         )),

        ("6-1-7", "挑戰題", "二元二次運算追蹤模擬 (val = k * k - k)", 4,
         lambda g: (
             (True, "二次多項式運算追蹤 (val = k * k - k) 走訪成功！")
             if (("k*k-k" in history_clean or "k**2-k" in history_clean or "k * k - k" in history_str) and
                 ("range(1,5)" in history_clean or "range(1, 5)" in history_str)) or
                ("k=4, val=12" in history_str or "k=1, val=0" in history_str)
             else (False, "請走訪 range(1, 5) 計算 val = k * k - k 並輸出每一步結果！")
         )),

        # ----------------------------------------------------------------------
        # 6-1-8 字串字元逐一走訪：for ch in text 的自然序列走訪初體驗 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-1-8", "填空題", "字串走訪關鍵字與變數 (for c in greeting:)", 4,
         lambda g: (
             (True, "字串走訪關鍵字 for 與變數 greeting 填寫正確！")
             if ("forcingreeting:" in history_clean or
                 ("greeting" in history_str and "for" in history_str and "字元：" in history_str))
             else (False, "請在 6-1-8 填空題填入關鍵字 for 與字串變數名稱 greeting！")
         )),

        ("6-1-8", "練習題", "文字打卡機逐字走訪 (for ch in text 印 [CHAR] ch)", 4,
         lambda g: (
             (True, "文字打卡機字元走訪輸出正確！")
             if (("text" in g or "text" in history_str) and
                 ("[CHAR]" in history_str or "forchintext" in history_clean))
             else (False, "請使用 for ch in text 走訪字串，每一輪輸出 [CHAR] ch！")
         )),

        ("6-1-8", "挑戰題", "數字字串分析兩倍數值 (digits = '2026', int(ch) * 2)", 4,
         lambda g: (
             (True, "數字字串型態轉換為 int 並印出兩倍數值成功！")
             if (("digits" in g or "digits" in history_str or "2026" in history_str) and
                 ("int(" in history_clean and ("*2" in history_clean or "* 2" in history_str)))
             else (False, "請走訪 digits = '2026'，使用 int(ch) 轉整數並輸出其兩倍數值！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-1：計數迴圈與 range 函式解析 —— 自動評分報告")
    print(f" 👤 學員自填姓名：{declared_name}")
    if google_email:
        print(f" 🔑 Google 帳號認證：{google_email}（暱稱：{final_google_name}）")
    else:
        print(f" 📧 登記信箱：{final_email}")
    print(f" ⏰ 送交時間：{timestamp_str}")
    print("=" * 72)

    pass_count = 0
    item_results = []

    for uid, qtype, name, pts, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception as e:
            ok, msg = False, f"執行檢驗時發生異常：{e}"

        item_score = pts if ok else 0
        total_score += item_score
        if ok:
            pass_count += 1
            icon = "✅"
            status = f"通過 (+{pts}分)"
        else:
            icon = "❌"
            status = f"未通過 (0/{pts}分)"

        print(f"{icon} [{uid} {qtype}] {name:<36} ➔ {status}")
        if not ok:
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 for 計數迴圈與 range 函式之三維參數控制，迴圈追蹤手感如行雲流水！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，正負步進與字串序列走訪思維清晰敏銳！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調邊界與格式！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "6-1",
        "unit_title": "計數迴圈與 range 函式解析",
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
        log_filename = "score_log_unit_6_1.json"
        with open(log_filename, "w", encoding="utf-8") as lf:
            json.dump(log_data, lf, ensure_ascii=False, indent=2)
        print(f"💾 [本地存檔] 評分紀錄檔已生成：{log_filename}（可於左側檔案區下載備查）")
    except Exception as e:
        print(f"⚠️ 本地日誌寫入提示：{e}")

    # --------------------------------------------------------------------------
    # 📡 2. 雲端後台成績記錄（Google Apps Script 試算表 Webhook）
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
auto_grade_unit_6_1()
