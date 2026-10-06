# ==============================================================================
# 🧪 《PythAPCS123》單元 5-5：分支控制結構（if, if-else, if-elif-else） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_5.py
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

def auto_grade_unit_5_5():
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
        # 5-5-1 單向選擇 if 指令——冒號與縮排 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-5-1", "填空題", "體育破紀錄獎勵發放 (bonus_medal=1)", 6,
         lambda g: (
             (True, "單向 if 判斷與縮排正確：bonus_medal=1！")
             if (g.get("bonus_medal") == 1) and
                ("if" in history_str and ":" in history_str)
             else (False, "請在 5-5-1 填空題空格填入 if 與結尾冒號 :！")
         )),

        ("5-5-1", "練習題", "超速警示器分行輸出 (speed > 60: SPEEDING)", 8,
         lambda g: (
             (True, "車速讀入與超速 SPEEDING 單向 if 警示正確！")
             if (("SPEEDING" in history_str and "speed > 60" in history_str.replace(" ", "")) or
                 ("SPEEDING" in history_str and "if" in history_str)) or
                ("speed" in g and "SPEEDING" in history_str)
             else (False, "請讀入車速 speed，印出 speed，並在 speed > 60 時加印 SPEEDING！")
         )),

        ("5-5-1", "挑戰題", "帳戶提款餘額扣除 (withdraw <= balance)", 6,
         lambda g: (
             (True, "帳戶提款扣除單向 if 判斷成功！")
             if (("withdraw <= balance" in history_str.replace(" ", "") or "withdraw<=balance" in history_str.replace(" ", "")) and
                 ("balance - withdraw" in history_str.replace(" ", "") or "balance-=withdraw" in history_str.replace(" ", ""))) or
                ("withdraw" in g and "balance" in g)
             else (False, "請讀入 withdraw，若 withdraw <= balance 則扣款並輸出最終餘額！")
         )),

        # ----------------------------------------------------------------------
        # 5-5-2 雙向互斥選擇 if-else (共 20 分)
        # ----------------------------------------------------------------------
        ("5-5-2", "填空題", "奇數偶數判定印出器 (EVEN / ODD)", 6,
         lambda g: (
             (True, "奇偶數雙向 if-else 填寫正確！")
             if (("if" in history_str and "else:" in history_str.replace(" ", "")) and
                 ("EVEN" in history_str and "ODD" in history_str))
             else (False, "請在 5-5-2 填空題空格填入 if 與 else:！")
         )),

        ("5-5-2", "練習題", "門票年齡分流系統 (age < 12 ➔ 100, else ➔ 250)", 8,
         lambda g: (
             (True, "門票年齡分流 if-else 判定金額正確！")
             if (("100" in history_str and "250" in history_str and "if" in history_str and "else" in history_str) or
                 ("price" in g and ("100" in history_str or "250" in history_str)))
             else (False, "請讀入 age，使用 if-else 判定 age < 12 輸出 100，否則 250！")
         )),

        ("5-5-2", "挑戰題", "比賽勝負雙向判定 (Team A Wins / Team B Wins)", 6,
         lambda g: (
             (True, "比賽得分雙向勝負判定成功！")
             if (("Team A Wins" in history_str and "Team B Wins" in history_str) or
                 ("score_a > score_b" in history_str.replace(" ", "") and "Wins" in history_str)) or
                ("score_a" in g and "score_b" in g)
             else (False, "請讀入兩隊分數，並使用 if-else 輸出勝方隊伍！")
         )),

        # ----------------------------------------------------------------------
        # 5-5-3 多向互斥選擇 if-elif-else (共 20 分)
        # ----------------------------------------------------------------------
        ("5-5-3", "填空題", "水質酸鹼度三向分級 (water_type=NEUTRAL)", 6,
         lambda g: (
             (True, "水質酸鹼多向 elif-else 填寫正確：water_type=NEUTRAL！")
             if (g.get("water_type") == "NEUTRAL") and
                ("elif" in history_str and "else:" in history_str.replace(" ", ""))
             else (False, "請在 5-5-3 填空題填入 elif 與 else: 關鍵字！")
         )),

        ("5-5-3", "練習題", "遊戲戰力階級階梯判定 (LEGEND, MASTER, WARRIOR, NOVICE)", 8,
         lambda g: (
             (True, "四級戰力階級 if-elif-else 判定正確！")
             if (("LEGEND" in history_str and "MASTER" in history_str and "WARRIOR" in history_str and "NOVICE" in history_str) or
                 ("elif" in history_str and "combat" in history_str)) or
                ("combat" in g)
             else (False, "請讀入 combat，並依 1000/500/100 門檻以 if-elif-else 判定階級！")
         )),

        ("5-5-3", "挑戰題", "交通號誌燈號指引 (STOP, CAUTION, GO, INVALID)", 6,
         lambda g: (
             (True, "交通燈號四向判別輸出成功！")
             if (("STOP" in history_str and "CAUTION" in history_str and "GO" in history_str and "INVALID" in history_str) or
                 ("code" in history_str and "elif" in history_str)) or
                ("code" in g)
             else (False, "請讀入代碼 code，判定 R/Y/G 對應指引，其餘輸出 INVALID！")
         )),

        # ----------------------------------------------------------------------
        # 5-5-4 獨立多重 if vs 互斥 if-elif (共 20 分)
        # ----------------------------------------------------------------------
        ("5-5-4", "填空題", "停車費優惠方案互斥 (discount_fee=50)", 6,
         lambda g: (
             (True, "停車費互斥 elif 填寫正確：discount_fee=50！")
             if (g.get("discount_fee") == 50) and
                ("elif" in history_str)
             else (False, "請在 5-5-4 填空題空格填入 elif 確保方案互斥不重複判定！")
         )),

        ("5-5-4", "練習題", "體重 BMI 狀態階梯分級 (OBESE, OVERWEIGHT, NORMAL, UNDERWEIGHT)", 8,
         lambda g: (
             (True, "體重 BMI 四級互斥分級判定正確！")
             if (("OBESE" in history_str and "OVERWEIGHT" in history_str and "NORMAL" in history_str and "UNDERWEIGHT" in history_str) or
                 ("bmi" in history_str and "elif" in history_str)) or
                ("bmi" in g)
             else (False, "請讀入 bmi 浮點數，以 if-elif-else 階梯互斥分級印出狀態！")
         )),

        ("5-5-4", "挑戰題", "單字長度等級分類 (LONG, MEDIUM, SHORT)", 6,
         lambda g: (
             (True, "單字長度三級分類判定成功！")
             if (("LONG" in history_str and "MEDIUM" in history_str and "SHORT" in history_str) or
                 ("len(" in history_str and "elif" in history_str)) or
                ("word" in g)
             else (False, "請讀入 word，依 len(word) >= 10, >= 5 分類 LONG, MEDIUM, SHORT！")
         )),

        # ----------------------------------------------------------------------
        # 5-5-5 單行 if 簡寫語法 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-5-5", "填空題", "單行極大值更新 (max_score=88)", 6,
         lambda g: (
             (True, "單行 if 極大值更新正確：max_score=88！")
             if (g.get("max_score") == 88) and
                ("if" in history_str and "new_score" in history_str)
             else (False, "請在 5-5-5 填空題空格填入 if 與 new_score！")
         )),

        ("5-5-5", "練習題", "差值下限單行防禦 (diff < 0: diff = 0)", 8,
         lambda g: (
             (True, "差值下限防禦單行 if 判定正確！")
             if (("diff < 0" in history_str.replace(" ", "") or "diff<0" in history_str.replace(" ", "")) and
                 ("diff = 0" in history_str.replace(" ", "") or "diff=0" in history_str.replace(" ", ""))) or
                ("diff" in g)
             else (False, "請讀入 a 與 b，計算 diff = a - b，若 diff < 0 則更新 diff = 0！")
         )),

        ("5-5-5", "挑戰題", "最小值單行連續更新 (min_val 連續更新)", 6,
         lambda g: (
             (True, "三數最小值單行 if 連續更新成功！")
             if (("min_val" in history_str and "if" in history_str) or
                 ("min(" in history_str)) or
                (all(k in g for k in ["a", "b", "c"]))
             else (False, "請讀入 a, b, c，利用單行 if 逐步比較更新 min_val 並輸出！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-5：分支控制結構（if, if-else, if-elif-else） —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 if-elif-else 互斥分支與單行簡寫，決策架構無懈可擊！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，單向雙向與階梯多向分支判斷邏輯清晰！"
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
        "unit": "5-5",
        "unit_title": "分支控制結構（if, if-else, if-elif-else）",
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
        log_filename = "score_log_unit_5_5.json"
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
auto_grade_unit_5_5()
