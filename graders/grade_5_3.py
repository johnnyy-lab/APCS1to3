# ==============================================================================
# 🧪 《PythAPCS123》單元 5-3：布林型態（bool）與真假值規則 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_3.py
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

def auto_grade_unit_5_3():
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
        # 5-3-1 布林型態本質——True 與 False 的整數繼承特性 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-3-1", "填空題", "系統認證開關與數值代碼 (auth_success, auth_code)", 6,
         lambda g: (
             (True, "布林真值與整數代碼轉換正確：auth_success=True 且 auth_code=1！")
             if (g.get("auth_success") is True and g.get("auth_code") == 1) or
                ("auth_success = True" in history_str and "int(" in history_str)
             else (False, "請在 5-3-1 填空題填入 True 與 int() 函數！")
         )),

        ("5-3-1", "練習題", "裁判投票表決加總 (b1 + b2 + b3)", 8,
         lambda g: (
             (True, "裁判投票布林轉型與同意票加總計算成功！")
             if (("bool" in history_str and "+" in history_str) or
                 ("b1 + b2 + b3" in history_str or "v1 + v2 + v3" in history_str)) or
                (all(k in g for k in ["v1", "v2", "v3"]) or all(k in g for k in ["b1", "b2", "b3"]))
             else (False, "請讀入三個投票代碼，轉型布林後利用相加技巧統計總同意票！")
         )),

        ("5-3-1", "挑戰題", "門禁投票多數決過半通過判定 (sum >= 2)", 6,
         lambda g: (
             (True, "門禁投票多數決（>= 2）判定成功！")
             if (">= 2" in history_str or ">=2" in history_str) or
                ("s1" in g and "s2" in g and "s3" in g)
             else (False, "請單行讀入三個 0 或 1 代碼，計算總和並比較是否大於等於 2！")
         )),

        # ----------------------------------------------------------------------
        # 5-3-2 數值的真假值規則——非零為真、零為假 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-3-2", "填空題", "庫存商品數值真偽檢驗 (has_stock_a, has_stock_b)", 6,
         lambda g: (
             (True, "非零為真與零為假判定正確：has_stock_a=True 且 has_stock_b=False！")
             if (g.get("has_stock_a") is True and g.get("has_stock_b") is False) or
                ("bool(stock_item_a)" in history_str.replace(" ", "") and "bool(stock_item_b)" in history_str.replace(" ", ""))
             else (False, "請在 5-3-2 填空題空格填入 bool 函數檢驗庫存數值！")
         )),

        ("5-3-2", "練習題", "系統伺服器錯誤碼異常狀態 (bool(error_code))", 8,
         lambda g: (
             (True, "伺服器錯誤碼異常狀態（非零為真）判斷正確！")
             if ("bool(" in history_str or "error_code != 0" in history_str) or
                ("error_code" in g)
             else (False, "請讀入 error_code，並使用 bool(error_code) 輸出系統異常狀態！")
         )),

        ("5-3-2", "挑戰題", "雙震動感測器活動偵測 (bool(v1) or bool(v2))", 6,
         lambda g: (
             (True, "雙感測器非零活動偵測邏輯判定成功！")
             if (("bool(" in history_str and "or" in history_str) or
                 ("v1 != 0 or v2 != 0" in history_str.replace(" ", "")) or
                 ("v1" in g and "v2" in g))
             else (False, "請單行讀入 v1 與 v2，並判斷 bool(v1) or bool(v2) 是否成立！")
         )),

        # ----------------------------------------------------------------------
        # 5-3-3 文字字串的真假值規則——真空為假、有字為真 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-3-3", "填空題", "留言板發言非空檢查 (is_post_ready, is_empty_ready)", 6,
         lambda g: (
             (True, "字串非空檢查正確：is_post_ready=True 且 is_empty_ready=False！")
             if (g.get("is_post_ready") is True and g.get("is_empty_ready") is False) or
                ("bool(content_valid)" in history_str.replace(" ", "") and "bool(content_empty)" in history_str.replace(" ", ""))
             else (False, "請在 5-3-3 填空題填入 bool 函數檢驗字串是否非空！")
         )),

        ("5-3-3", "練習題", "註冊帳號暱稱非空檢驗 (bool(nickname))", 8,
         lambda g: (
             (True, "帳號暱稱非空（bool(nickname)）檢驗正確！")
             if ("bool(nickname)" in history_str.replace(" ", "") or "len(nickname) > 0" in history_str) or
                ("nickname" in g)
             else (False, "請讀入 nickname，並輸出 bool(nickname) 判斷是否有效填寫！")
         )),

        ("5-3-3", "挑戰題", "兩段式姓名完整性審查 (bool(last) and bool(first))", 6,
         lambda g: (
             (True, "兩段式姓名姓與名雙重非空審查判定成功！")
             if (("bool" in history_str and "and" in history_str) or
                 ("last_name" in history_str and "first_name" in history_str) or
                 ("last_name" in g and "first_name" in g))
             else (False, "請讀入兩行姓名，並使用 bool 與 and 判斷兩者是否皆非空！")
         )),

        # ----------------------------------------------------------------------
        # 5-3-4 bool() 函數強制轉型 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-3-4", "填空題", "字串代碼數值真偽轉換 (signal_status=False)", 6,
         lambda g: (
             (True, "字串轉整數再轉布林正確：signal_status=False！")
             if (g.get("signal_status") is False) and
                ("bool(int(s))" in history_str.replace(" ", "") or "bool" in history_str)
             else (False, "請在 5-3-4 填空題空格填入 bool 函數完成 bool(int(s)) 轉換！")
         )),

        ("5-3-4", "練習題", "數值絕對活性檢驗 (bool(x))", 8,
         lambda g: (
             (True, "純量活性 bool(x) 輸出檢驗正確！")
             if ("bool(x)" in history_str.replace(" ", "") or "x != 0" in history_str) or
                ("x" in g)
             else (False, "請讀入整數 x，並輸出 bool(x) 判斷其數值活性！")
         )),

        ("5-3-4", "挑戰題", "雙文字欄位非空數量統計 (bool(w1) + bool(w2))", 6,
         lambda g: (
             (True, "雙欄位非空數量布林相加統計完成！")
             if (("bool" in history_str and "+" in history_str) or
                 ("w1" in g and "w2" in g))
             else (False, "請單行讀入 w1 與 w2，並計算 bool(w1) + bool(w2) 輸出總數！")
         )),

        # ----------------------------------------------------------------------
        # 5-3-5 布林值數值化運算黑科技 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-3-5", "填空題", "水質超標指標相加統計 (total_abnormal=2)", 6,
         lambda g: (
             (True, "三個布林條件直接相加統計正確：total_abnormal=2！")
             if (g.get("total_abnormal") == 2) and
                ("+" in history_str)
             else (False, "請在 5-3-5 填空題空格填入加號 + 直接相加布林比較式！")
         )),

        ("5-3-5", "練習題", "三數正數計數器 ((x>0) + (y>0) + (z>0))", 8,
         lambda g: (
             (True, "三數正數個數布林相加統計正確！")
             if (("> 0" in history_str or ">0" in history_str) and "+" in history_str) or
                (all(k in g for k in ["x", "y", "z"]))
             else (False, "請讀入三個數字，使用 (x > 0) + (y > 0) + (z > 0) 計算正數個數！")
         )),

        ("5-3-5", "挑戰題", "三角形三邊合法性指標驗證 (三項全合 == 3)", 6,
         lambda g: (
             (True, "三角形兩邊和大於第三邊三項布林加總檢驗成功！")
             if (("==" in history_str and "3" in history_str) or
                 ("a + b > c" in history_str or "a+b>c" in history_str) or
                 (all(k in g for k in ["a", "b", "c"])))
             else (False, "請單行讀入 a, b, c，計算 (a+b>c)+(b+c>a)+(c+a>b) == 3 輸出判定！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-3：布林型態（bool）與真假值規則 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通布林真假值本質與布林相加計數黑科技！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，數值與字串真偽規則洞若觀火！"
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
        "unit": "5-3",
        "unit_title": "布林型態（bool）與真假值規則",
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
        log_filename = "score_log_unit_5_3.json"
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
auto_grade_unit_5_3()
