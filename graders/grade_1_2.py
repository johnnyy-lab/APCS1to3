# ==============================================================================
# 🧪 《PythAPCS123》單元 1-2：等號賦值與運算順序 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_2.py
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
        # 非 Colab 環境、無網路或學生略過授權
        return None, None

def auto_grade_unit_1_2():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生在表單自行輸入之姓名（中文全名或學號）
    declared_name = str(env.get("student_name", "")).strip()
    if not declared_name or declared_name == "自學冒險者":
        declared_name = "自學冒險者（未填姓名）"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info()

    # 3. 整合身分識別欄位
    if google_email:
        final_email = google_email
        final_google_name = google_name if google_name else "Google無暱稱"
        combined_display_name = f"{declared_name} (Google暱稱: {final_google_name})"
    else:
        # 若未授權 Google，回退讀取表單自填 email 或預設值
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未授權 Google / 匿名"
        final_google_name = "未綁定 Google"
        combined_display_name = declared_name

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # 1-2-1 等號不是等於！認識單向賦值輸送帶（Assignment） (共 19 分)
        ("1-2-1", "填空題", "賦值運算子 energy = 250", 6,
         lambda g: (True, "輸送帶順利運作：energy = 250") if g.get("energy") == 250
         else (False, "找不到變數 energy 或數值不為 250，請確認填入等號 = 並點擊播放鍵執行")),

        ("1-2-1", "練習題", "書本價格 book_price 變數", 8,
         lambda g: (True, f"成功建立 book_price = {g.get('book_price')}") if g.get("book_price") in [320, 580]
         else ((False, "檢測到大寫 Book_price 或 BookPrice，題目要求全小寫蛇形命名 book_price 喔！")
               if any(k.lower() == "book_price" for k in g)
               else (False, "找不到變數 book_price，請依照練習題說明宣告並設定價格為 320 或 580"))),

        ("1-2-1", "挑戰題", "身高變數 my_height 賦值", 5,
         lambda g: (True, f"身高置物箱已放入數值：{g.get('my_height')}") if isinstance(g.get("my_height"), (int, float)) and g.get("my_height") > 0
         else (False, "找不到名為 my_height 的正數數值變數，請建立 my_height 記錄身高數值！")),

        # 1-2-2 賦值的黃金順序——「先算右邊，再存左邊」 (共 19 分)
        ("1-2-2", "填空題", "先乘除後加減 total_cost = 65", 6,
         lambda g: (True, "右側先算 3*20+5 完成：total_cost = 65") if g.get("total_cost") == 65
         else (False, "找不到 total_cost 或數值不為 65，請將底線替換為單價 20 並執行")),

        ("1-2-2", "練習題", "長寬高複合運算式 ans", 8,
         lambda g: (True, f"右側複合算式運算正確：ans = {g.get('ans')}") if g.get("ans") in [26, 32]
         else (False, "找不到變數 ans 或數值不符合測資（預期長*寬 + 高*2 算出 26 或 32）")),

        ("1-2-2", "挑戰題", "冒險者金幣計算 final_gold", 5,
         lambda g: (True, f"總金幣數計算正確：final_gold = {g.get('final_gold')}") if g.get("final_gold") == 145
         else (False, "找不到變數 final_gold 或數值不為 145（3*50 + 15 - 20 = 145）")),

        # 1-2-3 等號左側的嚴格鐵律——左邊只能是「單一變數箱子」！ (共 19 分)
        ("1-2-3", "填空題", "移項修正變數 a = 35 - 10", 6,
         lambda g: (True, "成功將變數 a 置於等號左側：a = 25") if g.get("a") == 25
         else (False, "找不到變數 a 或數值不為 25，請將 ___ 填入變數 a 並執行")),

        ("1-2-3", "練習題", "常數在左錯誤修正 speed 變數", 8,
         lambda g: (True, f"左側單一變數修正正確：speed = {g.get('speed')}") if g.get("speed") in [60, 120]
         else (False, "找不到變數 speed，請將 60 = speed 修正為 speed = 60（或 120）")),

        ("1-2-3", "挑戰題", "移項解方程式變數 x = 100 // 2", 5,
         lambda g: (True, f"方程式移項求解成功：x = {g.get('x')}") if g.get("x") in [50, 50.0]
         else (False, "找不到變數 x 或數值不為 50，請以 x 為左側變數計算 100 // 2 或 100 / 2")),

        # 1-2-4 舊的不去新的不來——變數賦值的覆蓋（Overwrite）特性 (共 20 分)
        ("1-2-4", "填空題", "等級覆蓋更新 level = 50", 6,
         lambda g: (True, "舊等級 1 已成功被新等級 50 覆蓋：level = 50") if g.get("level") == 50
         else (False, "變數 level 數值未更新為 50，請將 ___ 填入 level 覆蓋舊值")),

        ("1-2-4", "練習題", "氣溫覆蓋更新 temperature", 8,
         lambda g: (True, f"氣溫成功覆蓋為中午最新數值：temperature = {g.get('temperature')}") if g.get("temperature") in [26, 19]
         else (False, "找不到變數 temperature 或數值非最新中午氣溫（測資 1 為 26，測資 2 為 19）")),

        ("1-2-4", "挑戰題", "三次覆蓋生命值 hp 最終值 90", 6,
         lambda g: (True, f"生命值三次覆蓋後最終值正確：hp = {g.get('hp')}") if g.get("hp") == 90
         else (False, "變數 hp 最終值不為 90（經過 100 ➔ 70 ➔ 90 兩次覆蓋）")),

        # 1-2-5 自己算自己——右側引用舊值自我更新（`x = x + 1` 的魔法） (共 23 分)
        ("1-2-5", "填空題", "存錢筒自我累加 pig_bank = pig_bank + 50", 7,
         lambda g: (True, "右側引用舊值存入成功：pig_bank = 150") if g.get("pig_bank") == 150
         else (False, "找不到 pig_bank 或數值不為 150，請在 ___ 填入舊變數名稱 pig_bank")),

        ("1-2-5", "練習題", "計數器兩次自我累加 counter", 9,
         lambda g: (True, f"計數器自我累加兩次正確：counter = {g.get('counter')}") if g.get("counter") in [2, 10]
         else (False, "變數 counter 數值不符合測資（初始 0 ➔ 2，或初始 8 ➔ 10）")),

        ("1-2-5", "挑戰題", "史萊姆兩次自我減法扣血 slime_hp", 7,
         lambda g: (True, f"史萊姆扣血運算完全正確：slime_hp = {g.get('slime_hp')}") if g.get("slime_hp") == 75
         else (False, "slime_hp 剩餘生命值不為 75（200 - 40 - 85 = 75）")),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-2：等號賦值與運算順序 —— 自動評分報告")
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

        print(f"{icon} [{uid} {qtype}] {name:<26} ➔ {status}")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通等號賦值與運算順序之奧義！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，僅少數細節需微調！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "1-2",
        "unit_title": "等號賦值與運算順序",
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
        log_filename = f"score_log_unit_1_2.json"
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
auto_grade_unit_1_2()
