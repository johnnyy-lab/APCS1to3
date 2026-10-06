# ==============================================================================
# 🧪 《PythAPCS123》單元 6-3：條件迴圈 while 的運作機制與經典數值演算法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_3.py
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

def auto_grade_unit_6_3():
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
        # 6-3-1 什麼是 while 迴圈？「會重複執行的 if」心智模型 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-3-1", "填空題", "手機電池放電條件判斷 (while battery >= 12:)", 4,
         lambda g: (
             (True, "while 關鍵字與放電邊界條件填寫正確！")
             if ("whilebattery>=12:" in history_clean or "while battery >= 12" in history_str)
             else (False, "請在 6-3-1 填空題空格填入 while 關鍵字與判斷條件 battery >= 12！")
         )),

        ("6-3-1", "練習題", "魔王血量扣除與攻擊計數 (boss_hp > 0, attack_count)", 4,
         lambda g: (
             (True, "魔王扣血迴圈與總攻擊次數統計正確！")
             if (("boss_hp" in g or "boss_hp" in history_str) and
                 ("attack_count" in g or "attack_count" in history_str) and
                 ("-= 15" in history_str or "-=15" in history_clean))
             else (False, "請設定 boss_hp，在 while boss_hp > 0 中扣血並累加 attack_count！")
         )),

        ("6-3-1", "挑戰題", "存錢達標天數計算 (balance < target, days)", 5,
         lambda g: (
             (True, "儲蓄達標天數迴圈運算成功！")
             if (("target" in g or "target" in history_str) and
                 ("balance" in g or "balance" in history_str) and
                 ("days" in g or "days" in history_str) and
                 ("daily_save" in history_str or "+= 15" in history_str or "+=15" in history_clean))
             else (False, "請設定 target = 100, balance = 20, daily_save = 15，計算達標天數 days！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-2 while 迴圈三大黃金要件：初始值、條件檢查與步進更新 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-3-2", "填空題", "三大要件補齊 (num = 3, <= 15, += 3)", 4,
         lambda g: (
             (True, "初始值、條件式與步進更新三大黃金要件填寫精確！")
             if ("num<=15" in history_clean and ("+=3" in history_clean or "+= 3" in history_str))
             else (False, "請在 6-3-2 填空題填入初始值 3、條件 <= 15 與步進 += 3！")
         )),

        ("6-3-2", "練習題", "連續整數累加 (while cur <= n)", 4,
         lambda g: (
             (True, "while 累加 1 到 n 運算正確！")
             if (("cur" in g or "cur" in history_str) and
                 ("sum_val" in g or "sum_val" in history_str) and
                 ("cur <= n" in history_str or "cur<=n" in history_clean))
             else (False, "請使用 while cur <= n 累加 sum_val 並更新 cur += 1！")
         )),

        ("6-3-2", "挑戰題", "負步進推進點火模擬 (rocket_fuel > 20, burns)", 5,
         lambda g: (
             (True, "火箭推進點火次數與剩餘燃料計算成功！")
             if (("rocket_fuel" in g or "rocket_fuel" in history_str) and
                 ("burns" in g or "burns" in history_str) and
                 ("-= 15" in history_str or "-=15" in history_clean))
             else (False, "請設定 rocket_fuel = 100，每輪 -= 15 計算 burns 次數與剩餘燃料！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-3 for 與 while 迴圈的本質區別與選型判斷 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-3-3", "填空題", "for 改寫 while 等價結構 (x = 10, < 50, += 10)", 4,
         lambda g: (
             (True, "for 改寫 while 之起點、終止界限與步進填寫正確！")
             if ("x<50" in history_clean and ("+=10" in history_clean or "+= 10" in history_str))
             else (False, "請在 6-3-3 填空題填入起點 10、條件 < 50 與步進 += 10！")
         )),

        ("6-3-3", "練習題", "生活費開銷支撐天數計算 (max_days = 7)", 4,
         lambda g: (
             (True, "動態開銷消耗天數計算輸出正確！")
             if (("money" in g or "money" in history_str) and
                 ("day" in g or "day" in history_str) and
                 ("80" in history_str and "20" in history_str))
             else (False, "請使用 while 迴圈計算資金 1000 元最長可支撐的生活費天數！")
         )),

        ("6-3-3", "挑戰題", "累積首次突破上限門檻 (1+2+... 超過 500)", 5,
         lambda g: (
             (True, "連續累加首次超越 limit (500) 之整數與總和計算成功！")
             if (("limit" in g or "limit" in history_str) and
                 ("total" in g or "total" in history_str) and
                 ("last_num" in g or "last_num" in history_str) and
                 ("32" in history_str and "528" in history_str or (g.get("last_num") == 32 and g.get("total") == 528)))
             else (False, "請使用 while 迴圈計算連續正整數累加首次超越 500 的整數與總和！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-4 經典數值演算法（一）：整數數位剝皮術（Digit Peeling） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-3-4", "填空題", "數位剝皮兩把手術刀 (d = t % 10, t = t // 10)", 4,
         lambda g: (
             (True, "數位剝皮手術刀模除 10 與整除 10 填寫正確！")
             if ("%10" in history_clean and "//10" in history_clean)
             else (False, "請在 6-3-4 填空題填入模除 10 與整除 10！")
         )),

        ("6-3-4", "練習題", "特定數字 7 出現個數統計 (count_seven)", 4,
         lambda g: (
             (True, "數位剝皮統計數字 7 出現次數正確！")
             if (("count_seven" in g or "count_seven" in history_str) and
                 ("== 7" in history_str or "==7" in history_clean) and
                 ("// 10" in history_str or "//= 10" in history_str or "//=10" in history_clean))
             else (False, "請利用數位剝皮術檢查每位數，統計數字 7 出現的個數！")
         )),

        ("6-3-4", "挑戰題", "奇數位和與偶數位和之差 (abs(even_sum - odd_sum))", 5,
         lambda g: (
             (True, "奇偶數位分類求和與絕對差值運算成功！")
             if (("even_sum" in g or "even_sum" in history_str) and
                 ("odd_sum" in g or "odd_sum" in history_str) and
                 ("abs(" in history_clean))
             else (False, "請以數位剝皮分類累加偶數位和與奇數位和，並計算絕對差值！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-5 經典數值演算法（二）：數值反轉與回文數判定 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-3-5", "填空題", "純數值反轉構造與回文判定 (rev = rev * 10 + d)", 4,
         lambda g: (
             (True, "數值反轉乘 10 累加與回文原值比對填寫精確！")
             if ("rev*10+d" in history_clean or "rev * 10 + d" in history_str) and
                ("check_val //=" in history_str or "//= 10" in history_str or "//=10" in history_clean)
             else (False, "請在 6-3-5 填空題填入 10、//= 10 以及回文比對變數！")
         )),

        ("6-3-5", "練習題", "任意整數數值反轉與回文判定 (rev_val, is_pal)", 4,
         lambda g: (
             (True, "數值反轉與布林回文標記正確！")
             if (("rev_val" in g or "rev_val" in history_str) and
                 ("is_pal" in g or "is_pal" in history_str) and
                 ("* 10" in history_str or "*10" in history_clean))
             else (False, "請以 while 迴圈計算反轉數 rev_val 並判定 is_pal！")
         )),

        ("6-3-5", "挑戰題", "數論 196 演算法雛形 (start_n = 78 相加產出回文數)", 4,
         lambda g: (
             (True, "迭代反轉相加產生回文數 (4 輪得 4884) 成功！")
             if (("rounds" in g or "rounds" in history_str) and
                 ("curr" in g or "curr" in history_str) and
                 ("4884" in history_str or (g.get("rounds") == 4 and g.get("curr") == 4884)))
             else (False, "請以 while 迴圈實作 78 迭代反轉相加，直到產生回文數 4884！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-6 經典數值演算法（三）：進位制轉換與考拉茲猜想（Collatz Conjecture） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-3-6", "填空題", "二進位位元 1 計數 (num % 2, num // 2)", 4,
         lambda g: (
             (True, "二進位模除 2 與折半整除 2 填寫正確！")
             if ("% 2" in history_str or "%2" in history_clean) and
                ("// 2" in history_str or "//2" in history_clean)
             else (False, "請在 6-3-6 填空題填入模除 2 與整除 2！")
         )),

        ("6-3-6", "練習題", "考拉茲猜想最高峰值探測 (3n+1 與 n//2 擂台峰值)", 4,
         lambda g: (
             (True, "考拉茲 3n+1 演變軌跡最高峰值探測正確！")
             if (("max_val" in g or "max_val" in history_str) and
                 ("3 * n + 1" in history_str or "3*n+1" in history_clean) and
                 ("// 2" in history_str or "//= 2" in history_str or "//2" in history_clean))
             else (False, "請模擬考拉茲猜想軌跡，並找出過程中的最高峰值 max_val！")
         )),

        ("6-3-6", "挑戰題", "純數值十進位轉二進位構造 (25 轉 11001)", 4,
         lambda g: (
             (True, "權重倍增構造二進位整數 (11001) 成功！")
             if (g.get("binary_result") == 11001 or "11001" in history_str or
                 (("binary_result" in g or "binary_result" in history_str) and
                  ("factor" in history_str or "% 2" in history_str or "// 2" in history_str)))
             else (False, "請利用 factor *= 10 與 bit * factor 純數值構造二進位整數 11001！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-7 經典數值演算法（四）：輾轉相除法求最大公因數（Euclidean Algorithm） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-3-7", "填空題", "輾轉相除法與最小公倍數 (while y != 0, x % y, // gcd)", 4,
         lambda g: (
             (True, "輾轉相除不等於 0、模除更替與最小公倍數公式填寫正確！")
             if ("y!=0" in history_clean or "y != 0" in history_str) and
                ("%y" in history_clean or "% y" in history_str)
             else (False, "請在 6-3-7 填空題填入 0、x % y 以及除以 gcd_ans！")
         )),

        ("6-3-7", "練習題", "分數最簡約分 (GCD 與 simple_num / simple_den)", 4,
         lambda g: (
             (True, "最簡約分分子分母化簡輸出正確！")
             if (("simple_num" in g or "simple_num" in history_str) and
                 ("simple_den" in g or "simple_den" in history_str) and
                 ("%" in history_str and "//" in history_str))
             else (False, "請使用輾轉相除法求出 GCD 並求出最簡分子與最簡分母！")
         )),

        ("6-3-7", "挑戰題", "三數最大公因數求法 (72, 120, 168 共同 GCD = 24)", 4,
         lambda g: (
             (True, "兩段式輾轉相除求三數最大公因數 (24) 成功！")
             if (("three_gcd" in g or "three_gcd" in history_str) and
                 ("24" in history_str or g.get("three_gcd") == 24))
             else (False, "請利用兩次輾轉相除求出 72, 120, 168 的共同 GCD（結果為 24）！")
         )),

        # ----------------------------------------------------------------------
        # 6-3-8 無窮迴圈（Infinite Loop）陷阱與除錯心法 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-3-8", "填空題", "修正無窮迴圈扣除運算 (countdown -= 1)", 4,
         lambda g: (
             (True, "倒數步進更新運算子填寫正確：countdown -= 1！")
             if ("countdown-=1" in history_clean or "countdown -= 1" in history_str)
             else (False, "請在 6-3-8 填空題將加法修正為扣除運算子 -=！")
         )),

        ("6-3-8", "練習題", "安全閥門計數器 (steps >= 20, terminated_by_guard)", 4,
         lambda g: (
             (True, "防暴走安全步數閥門攔截機制正確！")
             if (("terminated_by_guard" in g or "terminated_by_guard" in history_str) and
                 ("steps" in g or "steps" in history_str) and
                 (">= 20" in history_str or ">=20" in history_clean))
             else (False, "請加上 steps 安全計數器，達到 20 步中斷並將 terminated_by_guard 設為 True！")
         )),

        ("6-3-8", "挑戰題", "業務條件與防暴走雙重條件審查", 4,
         lambda g: (
             (True, "業務邏輯與安全上限雙重條件審查成功！")
             if (("energy" in g or "energy" in history_str) and
                 ("loop_count" in g or "loop_count" in history_str) and
                 ("% 13" in history_str or "%13" in history_clean) and
                 ("< 100" in history_str or "<100" in history_clean))
             else (False, "請在 while 同時設置 energy % 13 != 0 與 loop_count < 100 雙重審查！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-3：條件迴圈 while 的運作機制與經典數值演算法 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 while 條件迴圈與四大經典數值演算法，數位剝皮與輾轉相除信手拈來！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，三大黃金要件掌握精準，進位轉換與考拉茲分析流暢！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調終止條件或步進更新！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "6-3",
        "unit_title": "條件迴圈 while 的運作機制與經典數值演算法",
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
        log_filename = "score_log_unit_6_3.json"
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
auto_grade_unit_6_3()
