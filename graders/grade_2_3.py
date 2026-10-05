# ==============================================================================
# 🧪 《PythAPCS123》單元 2-3：整數除法商數（//）與取餘數（%） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_3.py
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

def auto_grade_unit_2_3():
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 2-3-1 整數除法雙斜線（//）——只留整數商數的無情去尾刀 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-1", "填空題", "蛋撻裝盒整數除法 (total_boxes = 6)", 6,
         lambda g: (
             (True, "整數除法成功：total_boxes = 38 // 6 = 6！")
             if (g.get("total_boxes") == 6 and type(g.get("total_boxes")) is int)
             else (False, "找不到變數 total_boxes 或數值不為 6，請在空格填入 // 並執行！")
         )),

        ("2-3-1", "練習題", "遊覽車所需車輛數計算 (students // bus_capacity)", 8,
         lambda g: (
             (True, f"遊覽車商數計算正確：{g.get('students')} // {g.get('bus_capacity')} = {g.get('students') // g.get('bus_capacity')}")
             if ("students" in g and "bus_capacity" in g and
                 type(g.get("students")) is int and type(g.get("bus_capacity")) is int and
                 (g.get("students") // g.get("bus_capacity") in [4, 5] or g.get("students") // g.get("bus_capacity") > 0))
             else (False, "找不到變數 students 或 bus_capacity，請依練習題說明使用 // 計算滿載車數！")
         )),

        ("2-3-1", "挑戰題", "雞蛋連續整除換算大箱 (total_eggs // 12 // 30)", 6,
         lambda g: (
             (True, "大箱數量計算完成（連續兩次 // 換算）！")
             if any(k in g and type(g.get(k)) is int and g.get(k) >= 0 for k in ["crates", "total_crates", "crate_count", "ans"]) or
                (g.get("total_eggs") and type(g.get("total_eggs")) is int and any(type(v) is int for v in g.values()))
             else (False, "請宣告 total_eggs 變數，並連續使用 // 12 與 // 30 計算能裝成的大箱數量！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-2 模除取餘數百分比（%）——撿回落單零頭的餘數探測器 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-2", "填空題", "獎勵貼紙模除取餘數 (remaining_stickers = 2)", 6,
         lambda g: (
             (True, "模除運算成功：remaining_stickers = 50 % 6 = 2！")
             if (g.get("remaining_stickers") == 2 and type(g.get("remaining_stickers")) is int)
             else (False, "找不到 remaining_stickers 或數值不為 2，請填入 % 並點擊播放鍵執行！")
         )),

        ("2-3-2", "練習題", "萬聖節糖果平分落單數量 (total_candies % students)", 8,
         lambda g: (
             (True, f"剩餘糖果計算正確：{g.get('total_candies')} % {g.get('students')} = {g.get('total_candies') % g.get('students')}")
             if ("total_candies" in g and "students" in g and
                 type(g.get("total_candies")) is int and type(g.get("students")) is int and
                 (g.get("total_candies") % g.get("students") in [3, 2] or g.get("total_candies") % g.get("students") >= 0))
             else (False, "找不到 total_candies 或 students，請依練習題計算 total_candies % students！")
         )),

        ("2-3-2", "挑戰題", "彈珠盒數與落單顆數雙重計算 (total_marbles)", 6,
         lambda g: (
             (True, "彈珠裝盒商數與落單餘數計算成功！")
             if any(k in g for k in ["boxes", "box_count"]) and any(k in g for k in ["remains", "remain_marbles", "leftover"]) or
                (g.get("total_marbles") and type(g.get("total_marbles")) is int)
             else (False, "請宣告 total_marbles，並分別計算 // 9（盒數）與 % 9（剩餘顆數）！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-3 奇偶數判定與分組循環——餘數的週期魔法 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-3", "填空題", "號碼牌小隊分配模除 (my_team = 2)", 6,
         lambda g: (
             (True, "小隊分組模除成功：my_team = 17 % 3 = 2！")
             if (g.get("my_team") == 2 and type(g.get("my_team")) is int)
             else (False, "找不到變數 my_team 或數值不為 2，請在空格填入 % 運算子！")
         )),

        ("2-3-3", "練習題", "遊戲公會職業分配 (ticket_num % 4)", 8,
         lambda g: (
             (True, f"職業分配計算正確：{g.get('ticket_num')} % 4 = {g.get('ticket_num') % 4}")
             if ("ticket_num" in g and type(g.get("ticket_num")) is int and
                 g.get("ticket_num") % 4 in [2, 1])
             else (False, "找不到變數 ticket_num，請計算 ticket_num % 4 分配職業公會編號！")
         )),

        ("2-3-3", "挑戰題", "每週值日生排別循環計算 ((week - 1) % 3)", 6,
         lambda g: (
             (True, "週次值日生分組週期計算成功！")
             if any(k in g and type(g.get(k)) is int and 0 <= g.get(k) <= 2 for k in ["duty_row", "row", "ans"]) or
                ("current_week" in g and type(g.get("current_week")) is int and (g.get("current_week") - 1) % 3 in [0, 1, 2])
             else (False, "請宣告 current_week 並利用 (current_week - 1) % 3 計算當週值日生排別！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-4 神奇位數拆解術——取出個位數（% 10）與右移剝皮（// 10） (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-4", "填空題", "兩位數拆解十位與個位 (tens = 7, units = 9)", 6,
         lambda g: (
             (True, "位數拆解成功：tens = 7, units = 9！")
             if (g.get("tens") == 7 and g.get("units") == 9 and
                 type(g.get("tens")) is int and type(g.get("units")) is int)
             else (False, "變數 tens 或 units 數值不正確，請在 tens 填入 // 在 units 填入 %！")
         )),

        ("2-3-4", "練習題", "兩位數各位數字相加總和 (num // 10 + num % 10)", 8,
         lambda g: (
             (True, f"位數總和計算正確：{g.get('num')} ➔ {g.get('num') // 10 + g.get('num') % 10}")
             if ("num" in g and type(g.get("num")) is int and
                 (g.get("num") // 10 + g.get("num") % 10 in [11, 13] or
                  any(g.get(k) in [11, 13] for k in ["total", "sum_digits", "ans"] if k in g)))
             else (False, "找不到變數 num，請拆解十位與個位並計算加總（如 47 ➔ 11，85 ➔ 13）！")
         )),

        ("2-3-4", "挑戰題", "三位數密碼鎖各位數字乘積 (secret = 642 ➔ 48)", 6,
         lambda g: (
             (True, "三位數位數乘積計算正確（6 * 4 * 2 = 48）！")
             if any(g.get(k) == 48 for k in ["password", "ans", "product", "secret_code"] if k in g) or
                (g.get("secret") == 642 and any(v == 48 for v in g.values()))
             else (False, "請設定 secret = 642 並利用 // 10 與 % 10 算出 6*4*2 = 48 解鎖密碼！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-5 時間與單位的複合進位換算——商與餘數的黃金雙重奏 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-5", "填空題", "公分換算公尺又公分 (meters = 2, remain_cm = 45)", 6,
         lambda g: (
             (True, "單位換算成功：meters = 2, remain_cm = 45！")
             if (g.get("meters") == 2 and g.get("remain_cm") == 45 and
                 type(g.get("meters")) is int and type(g.get("remain_cm")) is int)
             else (False, "meters 或 remain_cm 數值不符，請在 meters 填入 // 在 remain_cm 填入 %！")
         )),

        ("2-3-5", "練習題", "總秒數換算分鐘與剩餘秒數 (total_sec)", 8,
         lambda g: (
             (True, f"秒數換算正確：{g.get('total_sec')} 秒 ➔ {g.get('total_sec') // 60} 分 {g.get('total_sec') % 60} 秒")
             if ("total_sec" in g and type(g.get("total_sec")) is int and
                 ((g.get("total_sec") // 60 == 2 and g.get("total_sec") % 60 == 15) or
                  (g.get("total_sec") // 60 == 5 and g.get("total_sec") % 60 == 8) or
                  (g.get("total_sec") > 0)))
             else (False, "找不到變數 total_sec，請依練習題換算為分鐘（// 60）與秒數（% 60）！")
         )),

        ("2-3-5", "挑戰題", "深空飛行總小時換算天數與小時 (total_hours)", 6,
         lambda g: (
             (True, "飛行時間換算天數與剩餘小時成功（// 24 與 % 24）！")
             if any(k in g for k in ["days", "day_count"]) and any(k in g for k in ["hours", "remain_hours"]) or
                ("total_hours" in g and type(g.get("total_hours")) is int)
             else (False, "請宣告 total_hours，並利用 // 24 與 % 24 依序換算出完整天數與剩餘小時數！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-3：整數除法商數（//）與取餘數（%） —— 自動評分報告")
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

        print(f"{icon} [{uid} {qtype}] {name:<32} ➔ {status}")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通整除去尾與餘數探測之雙重奏！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，位數拆解與商餘掌控熟練！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌
    log_data = {
        "unit": "2-3",
        "unit_title": "整數除法商數（//）與取餘數（%）",
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
        log_filename = "score_log_unit_2_3.json"
        with open(log_filename, "w", encoding="utf-8") as lf:
            json.dump(log_data, lf, ensure_ascii=False, indent=2)
        print(f"💾 [本地存檔] 評分紀錄檔已生成：{log_filename}（可於左側檔案區下載備查）")
    except Exception as e:
        print(f"⚠️ 本地日誌寫入提示：{e}")

    # 2. 雲端 Webhook
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
auto_grade_unit_2_3()
