# ==============================================================================
# 🧪 《PythAPCS123》單元 2-2：整數基本算術運算與優先級 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_2.py
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

def auto_grade_unit_2_2():
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
        # 2-2-1 整數加法與減法（+、-）——數值增減與負數運算 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-1", "填空題", "零用錢增減計算 (final_wallet = 275)", 6,
         lambda g: (
             (True, "加減運算成功：final_wallet = 275！")
             if (g.get("final_wallet") == 275 and type(g.get("final_wallet")) is int)
             else (False, "找不到變數 final_wallet 或數值不為 275，請確認 wallet - lunch + reward 並執行！")
         )),

        ("2-2-1", "練習題", "前後氣溫溫差變化量 (temp_yesterday, temp_today)", 8,
         lambda g: (
             (True, f"溫差變化計算正確：昨天 {g.get('temp_yesterday')} 度，今天 {g.get('temp_today')} 度（變化量 {g.get('temp_today') - g.get('temp_yesterday')}）")
             if ("temp_yesterday" in g and "temp_today" in g and
                 type(g.get("temp_yesterday")) is int and type(g.get("temp_today")) is int and
                 (g.get("temp_today") - g.get("temp_yesterday") in [8, -8] or
                  any(g.get(k) in [8, -8] for k in ["diff", "change", "ans", "temp_diff"] if k in g)))
             else (False, "找不到 temp_yesterday 或 temp_today，請依練習題宣告氣溫變數並印出差值！")
         )),

        ("2-2-1", "挑戰題", "勇者地底迷宮生命值結算 (hp > 0)", 6,
         lambda g: (
             (True, f"勇者生命值計算完成：{next(g.get(k) for k in ['hp', 'base_hp', 'final_hp'] if k in g and type(g.get(k)) is int and g.get(k) > 0)}")
             if any(k in g and type(g.get(k)) is int and g.get(k) > 0 for k in ["hp", "final_hp"]) or
                (g.get("base_hp") == 80 and any(type(v) is int and v > 0 for k, v in g.items() if "hp" in k.lower()))
             else (False, "請宣告勇者生命值變數（如 base_hp = 80），並計算經增減扣血後的最終血量！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-2 整數乘法（*）與代數陷阱——星號連乘與嚴禁省略乘號 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-2", "填空題", "操場長寬相乘面積計算 (area = 96)", 6,
         lambda g: (
             (True, "乘法運算成功：area = length * width = 96！")
             if (g.get("area") == 96 and type(g.get("area")) is int)
             else (False, "找不到變數 area 或數值不為 96，請在空格填入乘號 * 並點擊播放鍵執行！")
         )),

        ("2-2-2", "練習題", "營養午餐便當總額 (unit_price, quantity)", 8,
         lambda g: (
             (True, f"便當總額計算正確：{g.get('unit_price')} * {g.get('quantity')} = {g.get('unit_price') * g.get('quantity')}")
             if ("unit_price" in g and "quantity" in g and
                 type(g.get("unit_price")) is int and type(g.get("quantity")) is int and
                 (g.get("unit_price") * g.get("quantity") in [340, 1800] or g.get("unit_price") * g.get("quantity") > 0))
             else (False, "找不到變數 unit_price 或 quantity，請依練習題說明計算單價乘以數量！")
         )),

        ("2-2-2", "挑戰題", "開學特賣文具結帳總金額計算", 6,
         lambda g: (
             (True, "文具結帳金額計算成功（包含鉛筆、筆記本、橡皮擦總額）！")
             if any(k in g and type(g.get(k)) is int and g.get(k) > 0 for k in ["total", "total_price", "cost", "ans_stationery", "total_cost"]) or
                (any("pencil" in k for k in g) and any(type(v) is int and v > 0 for k, v in g.items() if "total" in k or "cost" in k))
             else (False, "請宣告文具數量並使用乘法與加法計算出結帳總金額（存入如 total 變數）！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-3 運算子優先級鐵則——先乘後加減與由左至右結合性 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-3", "填空題", "打工日薪先乘後加 (total_salary = 1100)", 6,
         lambda g: (
             (True, "日薪計算正確：total_salary = 200 + 180 * 5 = 1100！")
             if (g.get("total_salary") == 1100 and type(g.get("total_salary")) is int)
             else (False, "找不到 total_salary 或數值不為 1100，請填入乘號 * 並執行！")
         )),

        ("2-2-3", "練習題", "計程車跳表總車資 (base_fare, rate_per_km, extra_km)", 8,
         lambda g: (
             (True, f"車資先乘後加正確：基本費 {g.get('base_fare')} + 單價 {g.get('rate_per_km')} * 里程 {g.get('extra_km')}")
             if ("base_fare" in g and "rate_per_km" in g and "extra_km" in g and
                 type(g.get("base_fare")) is int and type(g.get("rate_per_km")) is int and type(g.get("extra_km")) is int and
                 g.get("base_fare") + g.get("rate_per_km") * g.get("extra_km") in [205, 400])
             else (False, "找不到 base_fare, rate_per_km, extra_km，請依練習題說明計算總車資！")
         )),

        ("2-2-3", "挑戰題", "野餐採購先乘後加減折價券 (應付 700)", 6,
         lambda g: (
             (True, "野餐採購總額計算正確（150 + 8*45 + 8*30 - 50 = 700）！")
             if any(g.get(k) == 700 for k in ["total", "ans", "pay", "final_pay", "total_cost"] if k in g) or
                any(type(v) is int and v == 700 for v in g.values())
             else (False, "請依挑戰題情境計算野餐應付總額（150 + 8*45 + 8*30 - 50 = 700）！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-4 運算順序的王牌指揮官——小括號 (...) 搶先執行權 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-4", "填空題", "禮物與包裝分攤小括號 (each_pay = 200)", 6,
         lambda g: (
             (True, "小括號搶先加總成功：each_pay = (500 + 100) // 3 = 200！")
             if (g.get("each_pay") == 200 and type(g.get("each_pay")) is int)
             else (False, "找不到 each_pay 或數值不為 200，請在 gift + wrap 外圍加上小括號 () 並執行！")
         )),

        ("2-2-4", "練習題", "梯形上底加下底乘高 (top, bottom, height)", 8,
         lambda g: (
             (True, f"梯形公式小括號運算正確：({g.get('top')} + {g.get('bottom')}) * {g.get('height')} = {(g.get('top') + g.get('bottom')) * g.get('height')}")
             if ("top" in g and "bottom" in g and "height" in g and
                 type(g.get("top")) is int and type(g.get("bottom")) is int and type(g.get("height")) is int and
                 (g.get("top") + g.get("bottom")) * g.get("height") in [50, 200])
             else (False, "找不到 top, bottom, height，請使用小括號 (top + bottom) * height 計算並印出！")
         )),

        ("2-2-4", "挑戰題", "好友同行特惠小括號結算 ((main + drink) * 4 = 900)", 6,
         lambda g: (
             (True, "好友同行金額計算成功：(180 + 45) * 4 = 900！")
             if any(g.get(k) == 900 for k in ["total", "ans", "table_total", "total_price"] if k in g) or
                (g.get("main_meal") == 180 and g.get("drink") == 45 and any(v == 900 for v in g.values()))
             else (False, "請使用一組小括號 (main_meal + drink) * count 計算總金額（預期 900 元）！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-5 多重巢狀小括號與括號大忌——由內而外層層拆解 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-5", "填空題", "禁絕中括號改用合法小括號 (math_formula = 150)", 6,
         lambda g: (
             (True, "合法小括號運算成功：math_formula = 5 * ((10 - 2) * 3 + 6) = 150！")
             if (g.get("math_formula") == 150 and type(g.get("math_formula")) is int)
             else (False, "找不到 math_formula 或數值不為 150，請在外層填入合法小括號 () 並執行！")
         )),

        ("2-2-5", "練習題", "五變數雙層巢狀小括號 ((a+b)*c - d)*e", 8,
         lambda g: (
             (True, f"雙層巢狀小括號運算正確：((a+b)*c - d)*e = {((g.get('a')+g.get('b'))*g.get('c') - g.get('d'))*g.get('e')}")
             if ("a" in g and "b" in g and "c" in g and "d" in g and "e" in g and
                 type(g.get("a")) is int and type(g.get("b")) is int and type(g.get("c")) is int and
                 type(g.get("d")) is int and type(g.get("e")) is int and
                 ((g.get('a')+g.get('b'))*g.get('c') - g.get('d'))*g.get('e') in [36, 50])
             else (False, "找不到變數 a, b, c, d, e，請依練習題宣告並計算 ((a+b)*c - d)*e！")
         )),

        ("2-2-5", "挑戰題", "戰略遊戲傷害結算雙重小括號一行整合", 6,
         lambda g: (
             (True, "戰略遊戲最終傷害計算成功（雙層小括號整合運算）！")
             if any(k in g and type(g.get(k)) in [int, float] and g.get(k) > 0 for k in ["final_damage", "damage", "ans", "total_damage"]) or
                (any(k in g for k in ["attack", "weapon", "critical_rate"]) and any(type(v) in [int, float] and v > 0 for k, v in g.items() if "damage" in k.lower()))
             else (False, "請宣告 5 個戰鬥變數，並以包含雙重小括號的一行算式計算最終傷害！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-2：整數基本算術運算與優先級 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通四則運算優先級與小括號統御力！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，算術與優先級觀念扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌
    log_data = {
        "unit": "2-2",
        "unit_title": "整數基本算術運算與優先級",
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
        log_filename = "score_log_unit_2_2.json"
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
auto_grade_unit_2_2()
