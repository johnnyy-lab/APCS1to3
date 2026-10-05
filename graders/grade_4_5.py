# ==============================================================================
# 🧪 《PythAPCS123》單元 4-5：標準輸入 input() 基本讀取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_5.py
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

def auto_grade_unit_4_5():
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
        # 4-5-1 input() 的本質——電腦的靈敏耳朵與「輸入一律為字串」的鐵律 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-1", "填空題", "標準輸入 input() 讀入星座名稱 (constellation)", 6,
         lambda g: (
             (True, "字串輸入設定正確：成功使用 input() 讀取星座！")
             if (("constellation" in g or "constellation = input()" in history_str.replace(" ", "")) and
                 ("觀測日誌" in history_str or "constellation" in history_str))
             else (False, "請在 4-5-1 填空題填入 input() 讀入星座並印出！")
         )),

        ("4-5-1", "練習題", "圖書館智慧借書通知 (book_title)", 8,
         lambda g: (
             (True, f"借閱書籍讀入成功：book_title='{g.get('book_title')}'！")
             if (("book_title" in g) and
                 ("借閱手續完成" in history_str))
             else (False, "請使用 book_title = input() 讀取書名，並印出借閱成功通知！")
         )),

        ("4-5-1", "挑戰題", "傳奇公會勇者報到系統 (title)", 6,
         lambda g: (
             (True, "勇者稱號讀入與公會公告排版成功！")
             if (("title" in g or "title = input()" in history_str.replace(" ", "")) and
                 ("歡迎傳奇勇者" in history_str or "*" in history_str))
             else (False, "請宣告 title = input() 讀入稱號，並印出星號裝飾線與公會公告！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-2 字串轉整數 int(input())——破解 \"10\" + \"20\" = \"1020\" 陷阱 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-2", "填空題", "神聖仙丹整數轉型 int(input()) (heal_hp)", 6,
         lambda g: (
             (True, "整數轉型填寫正確：heal_hp = int(input())！")
             if (("int(input())" in history_str.replace(" ", "") or "heal_hp" in g) and
                 ("神聖仙丹" in history_str or g.get("initial_hp") == 150))
             else (False, "請在 4-5-2 填空題空格填入 int 與 input 讀入整數！")
         )),

        ("4-5-2", "練習題", "正方形農場圍籬與面積計算器 (side)", 8,
         lambda g: (
             (True, f"正方形農場計算正確：邊長={g.get('side')}！")
             if (("side" in g and isinstance(g.get("side"), int)) and
                 ("正方形農場邊長" in history_str or "圍籬總長度" in history_str))
             else (False, "請使用 side = int(input()) 讀取邊長，並輸出圍籬長度與土地面積！")
         )),

        ("4-5-2", "挑戰題", "智慧零錢硬幣兌換機 (total_money, coin_50)", 6,
         lambda g: (
             (True, "零錢硬幣兌換邏輯計算正確！")
             if (("total_money" in g or "total_money = int(input())" in history_str.replace(" ", "")) and
                 ("// 50" in history_str or "//50" in history_str or "50元" in history_str))
             else (False, "請宣告 total_money = int(input())，並計算各面額硬幣數量印出報告！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-3 小數輸入 float(input())——精準量測身高體重與實數幾何計算 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-3", "填空題", "身高浮點數 float(input()) 與 BMI 計算 (height_m)", 6,
         lambda g: (
             (True, "小數輸入設定正確：height_m = float(input())！")
             if (("float(input())" in history_str.replace(" ", "") or "height_m" in g) and
                 ("BMI" in history_str or g.get("weight_kg") == 55.0))
             else (False, "請在 4-5-3 填空題空格填入 float 與 input 讀入身高！")
         )),

        ("4-5-3", "練習題", "攝氏轉華氏溫標轉換 (c, f)", 8,
         lambda g: (
             (True, f"溫標換算完成：攝氏={g.get('c')}°C！")
             if (("c" in g and (isinstance(g.get("c"), float) or isinstance(g.get("c"), int))) and
                 ("9 / 5" in history_str or "9/5" in history_str or "1.8" in history_str or "°F" in history_str))
             else (False, "請使用 c = float(input()) 讀取溫度，並計算華氏溫度 f 印出！")
         )),

        ("4-5-3", "挑戰題", "精品百貨 VIP 折扣收銀計算 (discount_rate)", 6,
         lambda g: (
             (True, "VIP 折扣金額計算與排版完成！")
             if (("discount_rate" in g or "discount_rate = float(input())" in history_str.replace(" ", "") or "discount_rate" in history_str) and
                 ("VIP" in history_str or "現省" in history_str or "original_price" in g or "discount_rate" in g))
             else (False, "請使用 discount_rate = float(input()) 讀取折扣，並輸出漂亮帳單！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-4 循序多次調用 input() 讀入多行單一資料 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-4", "填空題", "超商商品三行讀取與總額計算 (item_name, price, count)", 6,
         lambda g: (
             (True, "三行資料循序讀取設定正確！")
             if (("item_name" in g or "price" in g or "count" in g) or
                 ("item_name" in history_str and "input" in history_str))
             else (False, "請在 4-5-4 填空題依序使用 input() 與 int(input()) 讀取三行！")
         )),

        ("4-5-4", "練習題", "雙數四則運算分析儀 (num1, num2)", 8,
         lambda g: (
             (True, f"雙數分析儀運算完成：num1={g.get('num1')}, num2={g.get('num2')}！")
             if (("num1" in g and "num2" in g) and
                 ("兩數為：" in history_str or "商：" in history_str))
             else (False, "請連續兩行讀入 num1 與 num2 整數，並印出和、差、積、商、餘數！")
         )),

        ("4-5-4", "挑戰題", "競賽選手總分加權計算模組 (theory_score, practical_score)", 6,
         lambda g: (
             (True, "選手四行成績與加權總分計算成功！")
             if (("theory_score" in g or "practical_score" in g or "candidate_name" in g) and
                 ("加權" in history_str or "總成績" in history_str))
             else (False, "請連續四行讀取選手資料，並計算筆試與實作加權總分！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-5 競技程式 APCS / OJ 生死線——嚴禁提示文字的「純淨讀入」 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-5", "填空題", "APCS 純淨讀入求較大者 (max(num1, num2))", 6,
         lambda g: (
             (True, "APCS 純淨讀入格式正確：input() 無多餘字串！")
             if (("int(input())" in history_str.replace(" ", "") or "num1" in g) and
                 ("max(num1" in history_str.replace(" ", "") or "max" in history_str))
             else (False, "請在 4-5-5 填空題使用純淨 int(input()) 讀入兩數並輸出較大者！")
         )),

        ("4-5-5", "練習題", "APCS 規格模擬題：兩數之差的絕對值 (abs(x - y))", 8,
         lambda g: (
             (True, f"絕對值純淨計算完成：x={g.get('x')}, y={g.get('y')}！")
             if (("x" in g and "y" in g) and
                 ("abs(x - y)" in history_str.replace(" ", "") or "abs(x-y)" in history_str.replace(" ", "") or "abs" in history_str))
             else (False, "請純淨讀入 x, y 並輸出 abs(x - y)，不印出任何多餘文字！")
         )),

        ("4-5-5", "挑戰題", "APCS 規格模擬題：三數極端全距純淨輸出 (max - min)", 6,
         lambda g: (
             (True, "三數全距純淨輸出成功！")
             if (("max(" in history_str and "min(" in history_str) or
                 ("a" in g and "b" in g and "c" in g and ("max" in history_str or "-" in history_str)))
             else (False, "請連續三行純淨讀入 a, b, c，並直接輸出 max(a, b, c) - min(a, b, c)！")
         )),
    ]

    # 執行所有測資評分
    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 4-5 學習成效自動評分診斷報告")
    print(f"👤 受評學員：{combined_display_name}")
    print(f"📧 驗證信箱：{final_email}")
    print(f"🕒 評分時間：{timestamp_str}")
    print("=" * 72)

    pass_count = 0
    item_results = []

    for sub_unit, q_type, q_title, score, validator in test_cases:
        try:
            passed, feedback = validator(env)
        except Exception as e:
            passed, feedback = False, f"評分邏輯檢查異常：{e}"

        earned = score if passed else 0
        total_score += earned
        if passed:
            pass_count += 1
            status_icon = "✅ 通過"
        else:
            status_icon = "❌ 未過"

        item_results.append({
            "sub_unit": sub_unit,
            "type": q_type,
            "title": q_title,
            "max_score": score,
            "earned_score": earned,
            "status": "PASS" if passed else "FAIL",
            "feedback": feedback
        })

        print(f"[{status_icon}] ({earned:2d}/{score:2d}分) 【{sub_unit} {q_type}】{q_title}")
        print(f"       👉 評語：{feedback}")

    print("-" * 72)
    # 計算榮譽稱號
    if total_score == 100:
        badge = "🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美掌握 input() 標準輸入與 APCS 純淨讀入規範！"
    elif total_score >= 80:
        badge = "🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！"
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
        "unit": "4-5",
        "unit_title": "標準輸入 input() 基本讀取",
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
        log_filename = "score_log_unit_4_5.json"
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
auto_grade_unit_4_5()
