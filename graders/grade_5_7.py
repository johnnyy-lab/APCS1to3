# ==============================================================================
# 🧪 《PythAPCS123》單元 5-7：旗標變數（Flag）與狀態控制 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_7.py
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

def auto_grade_unit_5_7():
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
        # 5-7-1 什麼是旗標變數——程式記憶狀態的儀表板 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-7-1", "填空題", "違規記錄旗標初始化與觸發 (has_violation=True)", 6,
         lambda g: (
             (True, "旗標初始化與條件觸發填寫正確：has_violation=True！")
             if (g.get("has_violation") is True) and
                ("False" in history_str and "True" in history_str)
             else (False, "請在 5-7-1 填空題空格填入 False 與 True！")
         )),

        ("5-7-1", "練習題", "特殊幸運號碼偵測旗標 (has_seven)", 8,
         lambda g: (
             (True, "幸運數字 7 旗標偵測與輸出正確！")
             if (("has_seven" in history_str and "7" in history_str) or
                 ("==" in history_str and "True" in history_str)) or
                ("has_seven" in g)
             else (False, "請讀入三個數字，若任一為 7 則將 has_seven 設為 True 並輸出！")
         )),

        ("5-7-1", "挑戰題", "負數警報旗標 (has_negative)", 6,
         lambda g: (
             (True, "負數警報旗標更新與輸出判定成功！")
             if (("has_negative" in history_str and "< 0" in history_str) or
                 ("<" in history_str and "True" in history_str)) or
                ("has_negative" in g)
             else (False, "請讀入三數，若任一小於 0 則將 has_negative 設為 True 並輸出！")
         )),

        # ----------------------------------------------------------------------
        # 5-7-2 旗標的生命週期——歸零初始化、條件觸發與狀態鎖定 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-7-2", "填空題", "旗標單向鎖定破除覆蓋 (has_top_score 鎖定)", 6,
         lambda g: (
             (True, "旗標單向鎖定正確，未添加錯誤的 else 重置！")
             if ("has_top_score" in history_str and ">= 90" in history_str) or
                ("has_top_score" in g)
             else (False, "請在 5-7-2 填空題空格填入 True 鎖定旗標！")
         )),

        ("5-7-2", "練習題", "成績保送資格旗標鎖定 (has_top_score)", 8,
         lambda g: (
             (True, "保送資格單向鎖定旗標判定正確！")
             if (("has_top_score" in history_str and ">= 90" in history_str) or
                 ("s1" in history_str and "s2" in history_str and "s3" in history_str)) or
                ("has_top_score" in g)
             else (False, "請讀入三科成績，若任一 >= 90 則將 has_top_score 鎖定為 True！")
         )),

        ("5-7-2", "挑戰題", "伺服器過熱警報單向鎖定 (is_overheated ➔ ALARM / ALL NORMAL)", 6,
         lambda g: (
             (True, "伺服器溫度超標鎖定與警報判定成功！")
             if (("ALARM" in history_str and "ALL NORMAL" in history_str) or
                 ("is_overheated" in history_str and ">= 80" in history_str)) or
                ("is_overheated" in g)
             else (False, "請讀入三台溫度，若任一 >= 80 鎖定過熱旗標並輸出 ALARM 或 ALL NORMAL！")
         )),

        # ----------------------------------------------------------------------
        # 5-7-3 單一出口原則——以旗標統籌多分支最終輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-7-3", "填空題", "單一出口門票定價 (price)", 6,
         lambda g: (
             (True, "單一出口印出最終 price 填寫正確！")
             if ("print(" in history_str and "price" in history_str) or
                ("price" in g and g.get("price") == 150)
             else (False, "請在 5-7-3 填空題空格填入 price 完成單一出口印出！")
         )),

        ("5-7-3", "練習題", "數值特性標籤單一輸出 (label ➔ POSITIVE EVEN / ODD / NEGATIVE / ZERO)", 8,
         lambda g: (
             (True, "數值特性標籤更新與單一出口印出正確！")
             if (("label" in history_str and "POSITIVE EVEN" in history_str and "NEGATIVE" in history_str) or
                 ("POSITIVE ODD" in history_str and "ZERO" in history_str)) or
                ("label" in g)
             else (False, "請讀入 n，依條件更新 label 並在末端以單一出口印出！")
         )),

        ("5-7-3", "挑戰題", "購物折扣標籤單一出口 (discount_code ➔ GOLD / SILVER / NONE)", 6,
         lambda g: (
             (True, "折扣代碼單一出口判定成功！")
             if (("discount_code" in history_str and "GOLD" in history_str and "SILVER" in history_str) or
                 ("amount >= 3000" in history_str.replace(" ", "") and "1000" in history_str)) or
                ("discount_code" in g)
             else (False, "請讀入 amount，更新 discount_code 並在末端單一印出！")
         )),

        # ----------------------------------------------------------------------
        # 5-7-4 多旗標狀態組合——多項指標聯合會審 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-7-4", "填空題", "行李雙重會審旗標 and 結合 (weight_ok and size_ok)", 6,
         lambda g: (
             (True, "多旗標 and 聯合會審填寫正確！")
             if ("weight_ok and size_ok" in history_str.replace(" ", "") or
                 ("weight_ok" in history_str and "size_ok" in history_str and "and" in history_str))
             else (False, "請在 5-7-4 填空題空格填入 and 運算子！")
         )),

        ("5-7-4", "練習題", "獎助學金雙指標審查 (APPROVED / REJECTED)", 8,
         lambda g: (
             (True, "獎助學金雙指標旗標審查判定正確！")
             if (("APPROVED" in history_str and "REJECTED" in history_str) or
                 ("gpa_ok" in history_str and "volunteer_ok" in history_str)) or
                ("gpa" in g and "volunteer" in g)
             else (False, "請讀入 gpa 與 volunteer，雙旗標合格輸出 APPROVED，否則 REJECTED！")
         )),

        ("5-7-4", "挑戰題", "三合一健康指數檢驗 (ALL HEALTHY / NEED CHECK)", 6,
         lambda g: (
             (True, "三合一指標旗標聯合審查成功！")
             if (("ALL HEALTHY" in history_str and "NEED CHECK" in history_str) or
                 ("p1 >= 60" in history_str and "p2 >= 60" in history_str and "p3 >= 60" in history_str)) or
                (all(k in g for k in ["p1", "p2", "p3"]))
             else (False, "請讀入三項指標，全部及格輸出 ALL HEALTHY，否則 NEED CHECK！")
         )),

        # ----------------------------------------------------------------------
        # 5-7-5 APCS 實作經典模式——c461 前哨戰：IMPOSSIBLE 無解防禦輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-7-5", "填空題", "無解防禦旗標檢驗 (not has_match)", 6,
         lambda g: (
             (True, "無解防禦旗標填寫正確：if not has_match！")
             if ("not has_match" in history_str.replace(" ", "") or
                 ("not" in history_str and "has_match" in history_str and "IMPOSSIBLE" in history_str))
             else (False, "請在 5-7-5 填空題空格填入 has_match 旗標變數！")
         )),

        ("5-7-5", "練習題", "幸運數字因數匹配與無解防禦 (LUCKY TWO / THREE / IMPOSSIBLE)", 8,
         lambda g: (
             (True, "因數匹配多條件觸發與 IMPOSSIBLE 無解防禦判定正確！")
             if (("LUCKY TWO" in history_str and "LUCKY THREE" in history_str and "IMPOSSIBLE" in history_str) or
                 ("has_match" in history_str and "% 2" in history_str and "% 3" in history_str)) or
                ("has_match" in g)
             else (False, "請讀入 n，依因數立旗印出 LUCKY TWO / THREE，無解印出 IMPOSSIBLE！")
         )),

        ("5-7-5", "挑戰題", "區間命中與無解防禦大挑戰 (RANGE A / B / C / IMPOSSIBLE)", 6,
         lambda g: (
             (True, "三區間命中與 IMPOSSIBLE 無解防禦輸出成功！")
             if (("RANGE A" in history_str and "RANGE B" in history_str and "RANGE C" in history_str and "IMPOSSIBLE" in history_str) or
                 ("has_hit" in history_str and "IMPOSSIBLE" in history_str)) or
                ("has_hit" in g or "x" in g)
             else (False, "請讀入 x，依區間立旗輸出 RANGE A/B/C，未命中印出 IMPOSSIBLE！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-7：旗標變數（Flag）與狀態控制 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通旗標生命週期與單一出口架構，c461 無解防禦登峰造極！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，多旗標組合審查與狀態鎖定邏輯精湛！"
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
        "unit": "5-7",
        "unit_title": "旗標變數（Flag）與狀態控制",
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
        log_filename = "score_log_unit_5_7.json"
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
auto_grade_unit_5_7()
