# ==============================================================================
# 🧪 《PythAPCS123》單元 4-7：多行固定筆數讀取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_7.py
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

def auto_grade_unit_4_7():
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
        # 4-7-1 連續三行純整數讀入模式 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-1", "填空題", "紙箱長寬高三行讀入與表面積計算 (width, surface_area)", 6,
         lambda g: (
             (True, "紙箱三行尺寸讀取與容積表面積計算正確！")
             if (("length" in g or "width" in g or "height" in g) and
                 ("volume" in history_str or "surface_area" in history_str or "紙箱容積" in history_str))
             else (False, "請在 4-7-1 填空題空格填入 int(input()) 讀取寬度並補齊表面積算式！")
         )),

        ("4-7-1", "練習題", "射箭選拔賽三輪得分與穩定度指標 (score1, score2, score3)", 8,
         lambda g: (
             (True, "射箭三輪得分讀入與最高分、穩定度計算成功！")
             if (("score1" in g and "score2" in g and "score3" in g) and
                 ("max(" in history_str or "stability" in history_str))
             else (False, "請連續三行讀入 score1, score2, score3，並計算總分、最高分與穩定度！")
         )),

        ("4-7-1", "挑戰題", "健走四天步數與極端差距統計 (day1, day2, day3, day4)", 6,
         lambda g: (
             (True, "連續四天步數讀取與極端差距計算完成！")
             if (("day1" in g or "day2" in g or "day3" in g or "day4" in g) or
                 ("day1" in history_str and "int(input())" in history_str))
             else (False, "請連續四行讀取四天步數，並計算總步數與極端差距！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-2 混合型態（文字、整數、小數）的多行讀入 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-2", "填空題", "定存帳戶文字、整數與年利率多型態讀取 (acc_name, annual_rate)", 6,
         lambda g: (
             (True, "混合型態讀取填寫正確：成功計算年利息與本利和！")
             if (("acc_name" in g or "annual_rate" in g or "interest" in g) and
                 ("total_balance" in history_str or "持有人" in history_str))
             else (False, "請在 4-7-2 填空題分別使用 input() 與 float(input()) 完成讀取！")
         )),

        ("4-7-2", "練習題", "百米短跑姓名、距離與秒數平均秒速 (runner_name, speed_mps)", 8,
         lambda g: (
             (True, "短跑選手三行資料讀入與平均秒速計算完成！")
             if (("runner_name" in g and "distance_m" in g and "time_sec" in g) or
                 ("runner_name" in g and "speed_mps" in g) or
                 ("runner_name" in history_str and "float(input())" in history_str))
             else (False, "請連續三行讀取姓名、距離、秒數，並計算平均秒速！")
         )),

        ("4-7-2", "挑戰題", "咖啡館外帶點餐品名、杯數與折扣結帳 (drink_name, final_pay)", 6,
         lambda g: (
             (True, "咖啡外帶結帳單品名、原價與實付金額計算完成！")
             if (("drink_name" in g or "cups" in g or "discount" in g) or
                 ("drink_name" in history_str and "float(input())" in history_str))
             else (False, "請依序讀入品名、杯數與折扣數，並輸出原價與實付金額！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-3 單一整數與單行多整數的混合輸入 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-3", "填空題", "滿額購物金與商品單價混合行讀取 (coupon, item1, item2)", 6,
         lambda g: (
             (True, "單值行與同行多值混合讀取設定正確！")
             if (("coupon" in g or "item1" in g) and
                 ("subtotal" in history_str or "total_pay" in history_str or "商品原總價" in history_str))
             else (False, "請在 4-7-3 填空題第一行讀入 coupon，第二行使用 map 讀入兩商品單價！")
         )),

        ("4-7-3", "練習題", "及格基準分與兩科成績差值計算 (passing_score, s1, s2)", 8,
         lambda g: (
             (True, "及格基準分與兩科成績讀入與差值計算完成！")
             if (("passing_score" in g and "s1" in g and "s2" in g) or
                 ("passing_score" in g and "diff" in g) or
                 ("passing_score" in history_str and "map(int" in history_str.replace(" ", "")))
             else (False, "請第一行讀取 passing_score，第二行讀取 s1, s2，並印出總分、平均與差值！")
         )),

        ("4-7-3", "挑戰題", "遊樂園基礎門票與同行雙人代幣花費 (ticket_price, tokens_a, tokens_b)", 6,
         lambda g: (
             (True, "遊樂園雙人總花費與差額計算完成！")
             if (("ticket_price" in g or "tokens_a" in g or "tokens_b" in g) or
                 ("ticket_price" in history_str and "map(int" in history_str.replace(" ", "")))
             else (False, "請第一行讀取門票單價，第二行讀取兩位遊客代幣數，並輸出花費與差額！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-4 連續兩行座標讀入與幾何距離計算 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-4", "填空題", "對角兩點外接矩形尺寸與周長面積 (width, height, area)", 6,
         lambda g: (
             (True, "兩行座標讀取與外接矩形幾何數值計算正確！")
             if (("x1" in g or "x2" in g or "width" in g) and
                 ("perimeter" in history_str or "area" in history_str or "矩形寬與高" in history_str))
             else (False, "請在 4-7-4 填空題空格補齊第 2 行座標讀取與 height、area 計算式！")
         )),

        ("4-7-4", "練習題", "無人機兩行座標曼哈頓與歐式距離 (manhattan_dist, euclidean_dist)", 8,
         lambda g: (
             (True, "無人機兩點座標讀入與曼哈頓、歐式距離計算成功！")
             if (("ax" in g and "bx" in g) or
                 ("manhattan_dist" in g or "euclidean_dist" in g) or
                 ("**0.5" in history_str or "** 0.5" in history_str))
             else (False, "請讀入兩行座標，並分別輸出曼哈頓距離與直線距離！")
         )),

        ("4-7-4", "挑戰題", "兩頂點最小外接正方形邊長與面積 (side_len, square_area)", 6,
         lambda g: (
             (True, "兩頂點最小外接正方形邊長與面積計算完成！")
             if (("p1x" in g or "p2x" in g or "side_len" in g) or
                 ("side_len" in history_str and "max(" in history_str))
             else (False, "請讀入兩頂點座標，取 dx 與 dy 較大者為正方形邊長並輸出邊長與面積！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-5 APCS 競技程式多行固定筆數讀取實戰 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-5", "填空題", "紅藍兩隊趣味競賽兩行得分純淨讀取 (r1, b1, r2, b2)", 6,
         lambda g: (
             (True, "兩行趣味競賽得分純淨讀取與總分差計算正確！")
             if (("r1" in g or "total_r" in g or "diff" in g) and
                 ("total_b" in history_str or "紅隊總分" in history_str))
             else (False, "請在 4-7-5 填空題依序使用 map 讀入兩行競賽得分並計算總分差！")
         )),

        ("4-7-5", "練習題", "APCS 模擬實作：冒險者戰鬥結算 (remaining_hp, remaining_mp)", 8,
         lambda g: (
             (True, "戰鬥結算兩行數值純淨讀入與血魔結算輸出成功！")
             if (("hp" in g and "damage" in g) or
                 ("remaining_hp" in g and "remaining_mp" in g) or
                 ("remaining_hp" in history_str and "remaining_mp" in history_str))
             else (False, "請純淨讀入初始血魔與傷害消耗，並分兩行輸出剩餘血量與魔力！")
         )),

        ("4-7-5", "挑戰題", "APCS 模擬實作：文具批發採購三行結算 (revenue)", 6,
         lambda g: (
             (True, "文具採購三行資料純淨讀入與總營業額計算完成！")
             if (("unit_price" in g or "q_a" in g or "revenue" in g) or
                 ("revenue" in history_str or "unit_price" in history_str))
             else (False, "請嚴格依格式讀入三行批發資料，並輸出實付金額與總營業額！")
         )),
    ]

    # 執行所有測資評分
    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 4-7 學習成效自動評分診斷報告")
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
        badge = "🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完全制霸多行固定筆數讀取，第四章輸入輸出全章通關！"
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
        "unit": "4-7",
        "unit_title": "多行固定筆數讀取",
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
        log_filename = "score_log_unit_4_7.json"
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
auto_grade_unit_4_7()
