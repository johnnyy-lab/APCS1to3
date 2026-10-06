# ==============================================================================
# 🧪 《PythAPCS123》單元 5-2：邏輯運算子（and, or, not） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_2.py
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

def auto_grade_unit_5_2():
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 5-2-1 邏輯交集運算子：and（且） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-2-1", "填空題", "實驗室安全門禁雙重檢驗 (is_safe_to_enter)", 6,
         lambda g: (
             (True, "雙重安全門禁檢驗正確：is_safe_to_enter=True！")
             if (g.get("is_safe_to_enter") is True) and
                (("temperature < 37.5" in history_str or "37.5" in history_str) and
                 ("badge_level >= 2" in history_str or "badge_level>=2" in history_str or "and" in history_str))
             else (False, "請在 5-2-1 填空題空格依序填入 < 37.5、and 與 >= 2 完成雙重檢驗！")
         )),

        ("5-2-1", "練習題", "遊戲角色等級與能量雙重覺醒 (level, mana)", 8,
         lambda g: (
             (True, "角色雙重覺醒條件（level >= 50 and mana >= 200）檢驗正確！")
             if (("level >= 50" in history_str.replace(" ", "") or "level>=50" in history_str.replace(" ", "")) and
                 ("mana >= 200" in history_str.replace(" ", "") or "mana>=200" in history_str.replace(" ", "")) and
                 "and" in history_str) or
                ("level" in g and "mana" in g and "and" in history_str)
             else (False, "請讀入 level 與 mana，並使用 and 判斷 level >= 50 and mana >= 200！")
         )),

        ("5-2-1", "挑戰題", "二維平面第一象限內部點檢驗 (x > 0 and y > 0)", 6,
         lambda g: (
             (True, "第一象限內部點交集邏輯判定成功！")
             if (("x > 0" in history_str or "x>0" in history_str) and
                 ("y > 0" in history_str or "y>0" in history_str) and
                 "and" in history_str) or
                ("x" in g and "y" in g and "and" in history_str)
             else (False, "請單行讀入 x 與 y，並使用 and 判斷 x > 0 and y > 0 是否成立！")
         )),

        # ----------------------------------------------------------------------
        # 5-2-2 邏輯聯集運算子：or（或） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-2-2", "填空題", "氣象防颱警戒通報標準 (is_alert_triggered)", 6,
         lambda g: (
             (True, "防颱警戒指標判定正確：is_alert_triggered=True！")
             if (g.get("is_alert_triggered") is True) and
                (("wind_scale >= 10" in history_str or "10" in history_str) and
                 ("rainfall >= 350" in history_str or "350" in history_str) and
                 "or" in history_str)
             else (False, "請在 5-2-2 填空題填入 >= 10、or 與 >= 350 完成警戒發布檢驗！")
         )),

        ("5-2-2", "練習題", "棋盤出界警報檢測 (col < 0 or col >= 8)", 8,
         lambda g: (
             (True, "棋盤邊界出界（col < 0 or col >= 8）聯集判斷正確！")
             if (("col < 0" in history_str or "col<0" in history_str) and
                 ("col >= 8" in history_str or "col>=8" in history_str) and
                 "or" in history_str) or
                ("col" in g and "or" in history_str)
             else (False, "請讀入 col，並使用 or 運算子判斷 col < 0 or col >= 8 是否出界！")
         )),

        ("5-2-2", "挑戰題", "幸運摸彩中獎資格判定 (number == 77 or number % 11 == 0)", 6,
         lambda g: (
             (True, "發票特別號與對子號摸彩中獎邏輯判定成功！")
             if (("77" in history_str and "11" in history_str and "or" in history_str) or
                 ("number" in g and "or" in history_str))
             else (False, "請讀入 number，並使用 or 判斷 number == 77 or number % 11 == 0！")
         )),

        # ----------------------------------------------------------------------
        # 5-2-3 邏輯否定運算子：not（非） (共 20 分)
        # ----------------------------------------------------------------------
        ("5-2-3", "填空題", "防盜電子鎖警報開關 (should_alarm)", 6,
         lambda g: (
             (True, "邏輯反相否定填寫正確：should_alarm=True！")
             if (g.get("should_alarm") is True) and
                ("not" in history_str)
             else (False, "請在 5-2-3 填空題空格填入 not 運算子反轉授權狀態！")
         )),

        ("5-2-3", "練習題", "排除星期天維修日預約檢驗 (not (day == 7))", 8,
         lambda g: (
             (True, "排除維修日開放預約邏輯判斷正確！")
             if (("not" in history_str and "7" in history_str) or "day != 7" in history_str) or
                ("day" in g and ("not" in history_str or "!=" in history_str))
             else (False, "請讀入 day，並使用 not (day == 7) 或 day != 7 判斷是否開放預約！")
         )),

        ("5-2-3", "挑戰題", "分母非零防呆檢驗 (not (denominator == 0))", 6,
         lambda g: (
             (True, "分母非零安全防呆判定成功！")
             if (("not" in history_str and "0" in history_str and "==" in history_str) or
                 "denominator != 0" in history_str) or
                ("denominator" in g)
             else (False, "請讀入 denominator，並使用 not (denominator == 0) 判斷分母非零！")
         )),

        # ----------------------------------------------------------------------
        # 5-2-4 複合邏輯與優先級鐵律：not > and > or (共 20 分)
        # ----------------------------------------------------------------------
        ("5-2-4", "填空題", "電商 VIP 免運資格判定 (is_free_shipping)", 6,
         lambda g: (
             (True, "複合條件免運資格判定正確：is_free_shipping=True！")
             if (g.get("is_free_shipping") is True) and
                ("and" in history_str and "or" in history_str)
             else (False, "請在 5-2-4 填空題填入 and 與 or 完成複合免運資格判定！")
         )),

        ("5-2-4", "練習題", "兼職錄取資格複合檢驗 (age, has_coding, has_recommendation)", 8,
         lambda g: (
             (True, "兼職實習生複合資格檢驗邏輯正確！")
             if (("and" in history_str and "or" in history_str and ("18" in history_str or "age" in history_str)) or
                 (all(k in g for k in ["age", "has_coding", "has_recommendation"]) or "age" in g))
             else (False, "請依題意組合 (age >= 18 and has_coding == 1) or has_recommendation == 1 判斷！")
         )),

        ("5-2-4", "挑戰題", "閏年判斷純邏輯一行式 (year % 4 == 0 and year % 100 != 0 or year % 400 == 0)", 6,
         lambda g: (
             (True, "西元閏年經典複合邏輯判定成功！")
             if (("4" in history_str and "100" in history_str and "400" in history_str and "and" in history_str and "or" in history_str) or
                 ("year" in g and "and" in history_str and "or" in history_str))
             else (False, "請讀入 year，並使用 (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) 判斷！")
         )),

        # ----------------------------------------------------------------------
        # 5-2-5 邏輯代數實戰：互斥或 XOR (共 20 分)
        # ----------------------------------------------------------------------
        ("5-2-5", "填空題", "雙感應器 XOR 互斥檢驗 (is_xor_active)", 6,
         lambda g: (
             (True, "經典手刻 XOR 邏輯填寫正確：is_xor_active=True！")
             if (g.get("is_xor_active") is True) and
                ("not" in history_str and "or" in history_str)
             else (False, "請依序填入 not、or 與 not 完成經典 XOR 互斥或公式！")
         )),

        ("5-2-5", "練習題", "數值奇偶互斥判定 (恰好一奇一偶)", 8,
         lambda g: (
             (True, "兩數恰好一奇一偶 XOR 互斥檢驗正確！")
             if (("is_a_odd" in history_str or "a % 2" in history_str or "a%2" in history_str) and
                 ("or" in history_str or "!=" in history_str or "^" in history_str)) or
                ("a" in g and "b" in g and ("or" in history_str or "!=" in history_str or "^" in history_str))
             else (False, "請讀入 a 與 b，並使用 XOR 邏輯判斷兩數是否恰好一奇一偶！")
         )),

        ("5-2-5", "挑戰題", "APCS c461 前哨戰——XOR 單元驗證", 6,
         lambda g: (
             (True, "布林轉型與 XOR 互斥或單元驗證成功！")
             if (("bool" in history_str or "in1" in history_str or "b1" in history_str) and
                 ("or" in history_str or "!=" in history_str or "^" in history_str)) or
                ("in1" in g and "in2" in g)
             else (False, "請單行讀入 in1 與 in2，轉型布林後以 XOR 邏輯輸出判斷結果！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-2：邏輯運算子（and, or, not） —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 and/or/not 複合邏輯與 XOR 互斥或，思維嚴密滴水不漏！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，交集聯集否定與運算優先級掌握純熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "5-2",
        "unit_title": "邏輯運算子（and, or, not）",
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
        log_filename = "score_log_unit_5_2.json"
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
auto_grade_unit_5_2()
