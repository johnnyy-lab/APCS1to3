# ==============================================================================
# 🧪 《PythAPCS123》單元 6-2：迴圈累加器、計數器與極值維護 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_2.py
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

def auto_grade_unit_6_2():
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
        # 6-2-1 累加器（Accumulator）模式：存錢筒模型與初始值歸零 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-2-1", "填空題", "累加器歸零與複合賦值運算 (sum_val = 0, sum_val += i)", 4,
         lambda g: (
             (True, "累加器歸零初始化與複合加法運算子填寫正確！")
             if (g.get("sum_val") == 55 or "sum_val=0" in history_clean and "+=" in history_str)
             else (False, "請在 6-2-1 填空題空格填入初始值 0 與複合運算子 +=！")
         )),

        ("6-2-1", "練習題", "連續整數求和器 (1 加到 limit_n)", 4,
         lambda g: (
             (True, "連續整數求和累加器輸出正確！")
             if (("limit_n" in g or "limit_n" in history_str) and
                 ("Total sum from 1 to" in history_str or "+= i" in history_str or "+=i" in history_clean))
             else (False, "請設定 limit_n，利用 for 迴圈計算 1 到 limit_n 的總和！")
         )),

        ("6-2-1", "挑戰題", "前 5 個正整數平方和 (1^2 + ... + 5^2 = 55)", 5,
         lambda g: (
             (True, "前 5 個整數平方和累加計算成功 (55)！")
             if ("** 2" in history_str or "**2" in history_clean or "* i" in history_str) and
                ("55" in history_str or g.get("total_square") == 55 or "平方和" in history_str)
             else (False, "請利用迴圈與累加器模式計算 1 到 5 的平方和（結果為 55）！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-2 計數器（Counter）模式：打勾記次機與條件觸發 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-2-2", "填空題", "偶數計數器初始化與記次 (even_count += 1)", 4,
         lambda g: (
             (True, "計數器歸零與條件觸發記次 (+ 1) 正確！")
             if (g.get("even_count") == 6 or "even_count=0" in history_clean and ("+= 1" in history_str or "+=1" in history_clean))
             else (False, "請在 6-2-2 填空題填入初始值 0 與記次運算！")
         )),

        ("6-2-2", "練習題", "因數計數器 (Number of factors of target)", 4,
         lambda g: (
             (True, "因數個數計數器輸出正確！")
             if (("target" in g or "target" in history_str) and
                 ("Number of factors of" in history_str or "% i == 0" in history_str or "%i==0" in history_clean))
             else (False, "請設定 target，走訪檢查 target % i == 0 並統計因數個數！")
         )),

        ("6-2-2", "挑戰題", "字母出現頻率統計 (ABRACADABRA 中 A 出現 5 次)", 5,
         lambda g: (
             (True, "字串中字母 'A' 出現次數統計精準無誤！")
             if (("ABRACADABRA" in history_str or "text" in g) and
                 ("== 'A'" in history_str or '== "A"' in history_str) and
                 ("5" in history_str or g.get("count_a") == 5 or g.get("count") == 5))
             else (False, "請走訪 text = 'ABRACADABRA'，統計 'A' 出現的次數！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-3 累乘器（Multiplicative Accumulator）與階乘 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-2-3", "填空題", "累乘器初始值與複合乘法 (product = 1, product *= k)", 4,
         lambda g: (
             (True, "累乘器乘法單位元素 1 與 *= 填寫正確！")
             if (g.get("product") == 24 or "product=1" in history_clean and "*=" in history_str)
             else (False, "請在 6-2-3 填空題填入乘法初始值 1 與運算子 *=！")
         )),

        ("6-2-3", "練習題", "階乘計算機 (num_n! = product)", 4,
         lambda g: (
             (True, "階乘累乘計算與格式化輸出正確！")
             if (("num_n" in g or "num_n" in history_str) and
                 ("!" in history_str and ("*=" in history_str or "*= i" in history_str)))
             else (False, "請設定 num_n，利用累乘器計算階乘並依格式輸出！")
         )),

        ("6-2-3", "挑戰題", "2 的次方倍增累乘 (2^8 = 256)", 5,
         lambda g: (
             (True, "累乘器模擬 2 的次方運算成功 (256)！")
             if ("*= 2" in history_str or "*=2" in history_clean or "* 2" in history_str) and
                ("256" in history_str or g.get("power_val") == 256)
             else (False, "請以累乘器模式（勿用 **）執行 8 次乘以 2，算出 256！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-4 條件篩選加總：過濾閥門（Filter & Accumulate） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-2-4", "填空題", "倍數聯集篩選加總 (or 運算子與 += x)", 4,
         lambda g: (
             (True, "邏輯 or 條件聯集與符合項目累加填寫正確！")
             if (g.get("sum_multiples") == 98 or ("or" in history_str and "+= x" in history_str))
             else (False, "請在 6-2-4 填空題空格填入 or 與 +=！")
         )),

        ("6-2-4", "練習題", "非 3 之倍數條件加總 (Sum of numbers not divisible by 3)", 4,
         lambda g: (
             (True, "排除 3 的倍數之條件加總正確！")
             if (("limit_num" in g or "limit_num" in history_str) and
                 ("% 3 != 0" in history_str or "%3!=0" in history_clean) and
                 ("Sum of numbers not divisible by 3" in history_str or "+=" in history_str))
             else (False, "請設定 limit_num，僅累加不能被 3 整除的數字！")
         )),

        ("6-2-4", "挑戰題", "絕對差距條件加總 (abs(num - center) > 5)", 5,
         lambda g: (
             (True, "中心點絕對差距篩選累加成功！")
             if (("center" in g or "center" in history_str) and
                 ("abs(" in history_clean and "> 5" in history_str or ">5" in history_clean))
             else (False, "請計算 abs(num - center) > 5 並累加至 total_far！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-5 複合縮減指標：平均值（Average）與除零安全防護 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-2-5", "填空題", "平均值雙指標維護與防除零 (item_count += 1, > 0, /)", 4,
         lambda g: (
             (True, "雙指標維護、除零防護與平均值計算填寫精確！")
             if ("item_count += 1" in history_str or "+=1" in history_clean) and
                ("> 0" in history_str or ">0" in history_clean) and
                ("/" in history_str)
             else (False, "請在 6-2-5 填空題填入計數遞增 1、防除零 > 以及除法 /！")
         )),

        ("6-2-5", "練習題", "倍數平均值計算器 (Count 與 Average)", 4,
         lambda g: (
             (True, "5 的倍數統計與平均值計算輸出正確！")
             if (("limit_val" in g or "limit_val" in history_str) and
                 ("Average" in history_str or "No multiples found" in history_str))
             else (False, "請設定 limit_val，統計 5 的倍數之總和、個數與平均值！")
         )),

        ("6-2-5", "挑戰題", "奇數平均值與保留兩位小數格式化", 4,
         lambda g: (
             (True, "奇數平均值計算與小數點後兩位格式化成功！")
             if (("N" in g or "N" in history_str) and
                 ("% 2 != 0" in history_str or "% 2 == 1" in history_str or "%2!=0" in history_clean) and
                 (".2f" in history_str or "round(" in history_str))
             else (False, "請計算 1 到 N 奇數平均值，並以保留兩位小數格式印出！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-6 擂台盟主法：極值維護（Max / Min Tracking） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-2-6", "填空題", "最大值初始安全值與盟主退位更新 (float('-inf'), max_val = current)", 4,
         lambda g: (
             (True, "負無窮大安全初值與盟主挑戰更新填寫正確！")
             if ("float('-inf')" in history_str or 'float("-inf")' in history_str or "-inf" in history_clean) and
                ("max_val = current" in history_str or "max_val=current" in history_clean)
             else (False, "請在 6-2-6 填空題填入 float('-inf') 與 max_val = current！")
         )),

        ("6-2-6", "練習題", "函數極值探測器 (Max value of y is: max_y)", 4,
         lambda g: (
             (True, "二次函數 y = x * (10 - x) 擂台極值探測成功！")
             if (("n" in g or "n" in history_str) and
                 ("10 - x" in history_str or "10-x" in history_clean) and
                 ("Max value of y is" in history_str or "max_y" in history_str))
             else (False, "請走訪 x 計算 y = x * (10 - x)，以盟主法探測最大值！")
         )),

        ("6-2-6", "挑戰題", "餘數極值雙向探測 (max_r 與 min_r)", 4,
         lambda g: (
             (True, "最大餘數與最小餘數雙向盟主維護成功！")
             if (("base" in g or "base" in history_str) and
                 ("% base" in history_str or "%base" in history_clean) and
                 ("Max Remainder" in history_str or ("max_r" in history_str and "min_r" in history_str)))
             else (False, "請走訪 k 計算 r = (k * 17) % base，同時維護 max_r 與 min_r！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-7 APCS 實戰典範：連續 N 筆測資流式讀取與即時縮減 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-2-7", "填空題", "APCS 純淨讀入次數控制與數值轉換 (range(count), int(input()))", 4,
         lambda g: (
             (True, "APCS 純淨讀入迴圈次數與整數型態轉換填寫正確！")
             if ("range(count)" in history_clean and ("int(input())" in history_clean or "int" in history_str))
             else (False, "請在 6-2-7 填空題填入 range(count) 與 int(input())！")
         )),

        ("6-2-7", "練習題", "及格人數動態統計 (pass_count 統計 >= 60)", 4,
         lambda g: (
             (True, "流式讀取及格人數統計結構正確！")
             if (("pass_count" in history_str or "pass_count" in g) and
                 (">= 60" in history_str or ">=60" in history_clean) and
                 ("input()" in history_clean))
             else (False, "請讀入 n 與每筆成績，統計 >= 60 的及格人數！")
         )),

        ("6-2-7", "挑戰題", "動態最高分流式探測 (以擂台盟主法讀入 N 筆找最大值)", 4,
         lambda g: (
             (True, "N 筆流式輸入動態盟主最大值探測架構正確！")
             if ("input()" in history_clean and
                 ("max_val" in history_str or "max_score" in history_str or ">" in history_str))
             else (False, "請第一行讀入 N，接下來 N 行邊讀邊更新最大值並輸出！")
         )),

        # ----------------------------------------------------------------------
        # 6-2-8 綜合實戰：同步維護多重縮減指標與全距運算 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-2-8", "填空題", "雙向極值與全距計算 (x < min_v, max_v - min_v)", 4,
         lambda g: (
             (True, "最小值維護條件與全距減法公式填寫精準！")
             if ("< min_v" in history_str or "<min_v" in history_clean) and
                ("- min_v" in history_str or "-min_v" in history_clean)
             else (False, "請在 6-2-8 填空題填入 < 以及全距減號 -！")
         )),

        ("6-2-8", "練習題", "數列全距與極值報表 (Max, Min, Range)", 4,
         lambda g: (
             (True, "極值與全距流式統計報表輸出正確！")
             if (("Range" in history_str or "max_val - min_val" in history_str or "max_val-min_val" in history_clean) and
                 ("Max:" in history_str or "Min:" in history_str))
             else (False, "請讀入 n 筆資料，輸出最大值、最小值與全距 (Range)！")
         )),

        ("6-2-8", "挑戰題", "評審去極值有效總分 (total - max_val - min_val)", 4,
         lambda g: (
             (True, "去頭去尾去極值裁判評分總和運算成功！")
             if (("- max_val - min_val" in history_str or "-max_val-min_val" in history_clean or
                  ("total" in history_str and "max_val" in history_str and "min_val" in history_str)))
             else (False, "請同時維護 total, max_val, min_val，並輸出去除極值後的有效總分！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-2：迴圈累加器、計數器與極值維護 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通資料縮減（Data Reduction）核心心法，擂台盟主與極值維護臻於化境！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，累加、計數、累乘與流式讀取架構清晰嚴謹！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調初始值或條件式！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "6-2",
        "unit_title": "迴圈累加器、計數器與極值維護",
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
        log_filename = "score_log_unit_6_2.json"
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
auto_grade_unit_6_2()
