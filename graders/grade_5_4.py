# ==============================================================================
# 🧪 《PythAPCS123》單元 5-4：笛摩根定律的邏輯改寫 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_4.py
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

def auto_grade_unit_5_4():
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
        # 5-4-1 口語否定與數理邏輯陷阱——「非（A 且 B）」 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-4-1", "填空題", "雙重違規防呆檢查 (can_race=True)", 6,
         lambda g: (
             (True, "雙重違規防呆填寫正確：can_race=True！")
             if (g.get("can_race") is True) and
                ("not" in history_str and "and" in history_str)
             else (False, "請在 5-4-1 填空題空格填入 not 與 and 運算子！")
         )),

        ("5-4-1", "練習題", "機械雙重超標警示器 (not (temp >= 100 and press >= 50))", 8,
         lambda g: (
             (True, "機械雙重超標否定防呆邏輯判定正確！")
             if (("not" in history_str and "100" in history_str and "50" in history_str and "and" in history_str) or
                 ("temp < 100 or press < 50" in history_str.replace(" ", ""))) or
                ("temp" in g and "press" in g)
             else (False, "請讀入 temp 與 press，並判定 not (temp >= 100 and press >= 50)！")
         )),

        ("5-4-1", "挑戰題", "雙重未滿額門檻防護 (not (score < 3 and amount < 500))", 6,
         lambda g: (
             (True, "雙重未滿額門檻否定邏輯判定成功！")
             if (("not" in history_str and "3" in history_str and "500" in history_str and "and" in history_str) or
                 ("score >= 3 or amount >= 500" in history_str.replace(" ", ""))) or
                ("score" in g and "amount" in g)
             else (False, "請單行讀入 score 與 amount，並判斷 not (score < 3 and amount < 500)！")
         )),

        # ----------------------------------------------------------------------
        # 5-4-2 笛摩根第一定律——not (A and B) 等價於 (not A) or (not B) (共 20 分)
        # ----------------------------------------------------------------------
        ("5-4-2", "填空題", "笛摩根第一定律代數改寫 (right_side=True)", 6,
         lambda g: (
             (True, "笛摩根第一定律填寫正確：(not has_key) or (not has_password)=True！")
             if (g.get("right_side") is True) and
                ("not" in history_str and "or" in history_str)
             else (False, "請在 5-4-2 填空題填入 not、or、not 完成等價改寫！")
         )),

        ("5-4-2", "練習題", "笛摩根第一定律雙式驗證 (左式 not (A and B) 與 右式 (not A) or (not B))", 8,
         lambda g: (
             (True, "笛摩根第一定律雙式計算輸出正確！")
             if (("and" in history_str and "or" in history_str and "not" in history_str) or
                 ("a >= 0" in history_str or "b >= 0" in history_str)) or
                ("a" in g and "b" in g)
             else (False, "請讀入 a 與 b，分別輸出左式 not (A and B) 與右式 (not A) or (not B)！")
         )),

        ("5-4-2", "挑戰題", "笛摩根定律化簡實戰 (x % 2 != 0 or x % 3 != 0)", 6,
         lambda g: (
             (True, "笛摩根第一定律倍數檢定化簡成功！")
             if (("!=" in history_str and "or" in history_str and "2" in history_str and "3" in history_str) or
                 ("not" in history_str and "==" in history_str and "and" in history_str)) or
                ("x" in g)
             else (False, "請讀入整數 x，並使用 (x % 2 != 0 or x % 3 != 0) 輸出判斷結果！")
         )),

        # ----------------------------------------------------------------------
        # 5-4-3 笛摩根第二定律——not (A or B) 等價於 (not A) and (not B) (共 20 分)
        # ----------------------------------------------------------------------
        ("5-4-3", "填空題", "笛摩根第二定律代數改寫 (right_side=True)", 6,
         lambda g: (
             (True, "笛摩根第二定律填寫正確：(not is_rainy) and (not is_snowy)=True！")
             if (g.get("right_side") is True) and
                ("not" in history_str and "and" in history_str)
             else (False, "請在 5-4-3 填空題填入 not、and、not 完成等價改寫！")
         )),

        ("5-4-3", "練習題", "笛摩根第二定律雙式比對 (左式 not (A or B) 與 右式 (not A) and (not B))", 8,
         lambda g: (
             (True, "笛摩根第二定律雙式比對輸出正確！")
             if (("or" in history_str and "and" in history_str and "not" in history_str) or
                 ("x == 0" in history_str or "y == 0" in history_str)) or
                ("x" in g and "y" in g)
             else (False, "請讀入 x 與 y，分別輸出左式 not (A or B) 與右式 (not A) and (not B)！")
         )),

        ("5-4-3", "挑戰題", "排除兩端極值區間檢驗 (val <= 100 and val >= 0)", 6,
         lambda g: (
             (True, "排除兩端極值區間化簡檢驗成功！")
             if (("100" in history_str and "0" in history_str and "and" in history_str) or
                 ("val <= 100" in history_str or "val >= 0" in history_str or "0 <= val <= 100" in history_str.replace(" ", ""))) or
                ("val" in g)
             else (False, "請讀入 val，並使用 (val <= 100 and val >= 0) 輸出判定結果！")
         )),

        # ----------------------------------------------------------------------
        # 5-4-4 比較運算子的對偶反轉——徹底消除比較式外層的 not (共 20 分)
        # ----------------------------------------------------------------------
        ("5-4-4", "填空題", "消除 not 的正向及格改寫 (passing_positive=True)", 6,
         lambda g: (
             (True, "對偶反轉消去 not 正確：score >= 60 為 True！")
             if (g.get("passing_positive") is True) and
                (">=" in history_str)
             else (False, "請在 5-4-4 填空題空格填入 >= 運算子完成及格判定！")
         )),

        ("5-4-4", "練習題", "未成年門檻對偶反轉 (age < 18)", 8,
         lambda g: (
             (True, "未成年門檻對偶反轉 (age < 18) 判斷正確！")
             if ("< 18" in history_str or "<18" in history_str.replace(" ", "")) or
                ("age" in g and "<" in history_str)
             else (False, "請讀入 age，並使用 (age < 18) 輸出未成年布林結果！")
         )),

        ("5-4-4", "挑戰題", "雙運算子對偶反轉消去 not (x == y)", 6,
         lambda g: (
             (True, "雙運算子對偶反轉 (x == y) 判定成功！")
             if ("==" in history_str) or
                ("x" in g and "y" in g)
             else (False, "請單行讀入 x 與 y，並使用 (x == y) 輸出判定結果！")
         )),

        # ----------------------------------------------------------------------
        # 5-4-5 複合條件化簡實戰 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-4-5", "填空題", "開區間外部化簡以 or 串接 (simplified_expr=True)", 6,
         lambda g: (
             (True, "開區間外部化簡正確：(x <= 10) or (x >= 50) 為 True！")
             if (g.get("simplified_expr") is True) and
                ("<=" in history_str and ">=" in history_str and "or" in history_str)
             else (False, "請在 5-4-5 填空題空格依序填入 <=、or、>= 完成化簡！")
         )),

        ("5-4-5", "練習題", "體溫異常警示化簡判別 (temp < 36.0 or temp > 37.4)", 8,
         lambda g: (
             (True, "體溫異常警示化簡表示式判斷正確！")
             if (("36.0" in history_str or "36" in history_str) and
                 ("37.4" in history_str) and
                 "or" in history_str) or
                ("temp" in g and "or" in history_str)
             else (False, "請讀入 temp，並使用 (temp < 36.0 or temp > 37.4) 判斷異常！")
         )),

        ("5-4-5", "挑戰題", "笛卡兒平面非第四象限判定 (x <= 0 or y >= 0)", 6,
         lambda g: (
             (True, "非第四象限內部化簡判定成功！")
             if (("<=" in history_str and ">=" in history_str and "or" in history_str) or
                 ("not" in history_str and "> 0" in history_str and "< 0" in history_str)) or
                ("x" in g and "y" in g)
             else (False, "請單行讀入 x 與 y，並使用 (x <= 0 or y >= 0) 輸出判斷結果！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-4：笛摩根定律的邏輯改寫 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通笛摩根定律與邏輯等價化簡，思維通透神乎其技！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，笛摩根第一與第二定律掌握熟練！"
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
        "unit": "5-4",
        "unit_title": "笛摩根定律的邏輯改寫",
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
        log_filename = "score_log_unit_5_4.json"
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
auto_grade_unit_5_4()
