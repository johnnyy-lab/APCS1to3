# ==============================================================================
# 🧪 《PythAPCS123》單元 1-4：複合賦值運算子 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_4.py
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

def auto_grade_unit_1_4():
    env = globals()
    total_score = 0
    max_score = 100

    declared_name = str(env.get("student_name", "")).strip()
    if not declared_name or declared_name == "自學冒險者":
        declared_name = "自學冒險者（未填姓名）"

    google_email, google_name = fetch_google_account_info()

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
        # 1-4-1 最常見的累加捷徑：+= (共 20 分)
        ("1-4-1", "填空題", "撲滿零用錢累加 coin_box += 20", 6,
         lambda g: (True, "累加運算正確：coin_box = 100") if g.get("coin_box") == 100
         else (False, "找不到 coin_box 或數值不為 100，請填入 += 20")),

        ("1-4-1", "練習題", "經驗值兩次連續累加 exp", 8,
         lambda g: (True, f"經驗值連續累加正確：exp = {g.get('exp')}") if g.get("exp") in [75, 125]
         else (False, "變數 exp 數值不正確（初始 0 依序 +30, +45 應為 75）")),

        ("1-4-1", "挑戰題", "全日跑步里程累加 total_distance", 6,
         lambda g: (True, f"總公里數累加完成：total_distance = {g.get('total_distance')}")
         if g.get("total_distance") in [10, 10.0]
         else (False, "total_distance 總距離不為 10（3 + 5 + 2 = 10）")),

        # 1-4-2 扣血與折扣捷徑：-= (共 20 分)
        ("1-4-2", "填空題", "毒沼澤扣血 hp -= 15 + 25", 6,
         lambda g: (True, "複合傷害扣血正確：hp = 60") if g.get("hp") == 60
         else (False, "找不到 hp 或數值不為 60，請使用 -= 扣除 15 + 25")),

        ("1-4-2", "練習題", "錢包早餐飲料支出 balance", 8,
         lambda g: (True, f"餘額計算正確：balance = {g.get('balance')}") if g.get("balance") in [400, 350]
         else (False, "變數 balance 不為 400（500 - (65 + 35) = 400）")),

        ("1-4-2", "挑戰題", "水庫兩天用水扣除 water", 6,
         lambda g: (True, f"水庫剩餘水量正確：water = {g.get('water')}") if g.get("water") == 650
         else (False, "water 剩餘水量不為 650（1000 - 120 - (150 + 80) = 650）")),

        # 1-4-3 翻倍與縮小捷徑：*= 與 /= (共 20 分)
        ("1-4-3", "填空題", "狂暴藥水倍數升級 attack *= 3", 6,
         lambda g: (True, "攻擊力翻倍正確：attack = 75") if g.get("attack") == 75
         else (False, "找不到 attack 或數值不為 75，請使用 *= 3")),

        ("1-4-3", "練習題", "細菌連續兩次分裂翻倍 bacteria", 8,
         lambda g: (True, f"細菌分裂翻倍正確：bacteria = {g.get('bacteria')}") if g.get("bacteria") in [40, 80]
         else (False, "bacteria 數值不符合測資（初始 10 經兩次 *= 2 應為 40）")),

        ("1-4-3", "挑戰題", "複合乘法賦值 val *= (2 + 3 * 2)", 6,
         lambda g: (True, f"右側先算再乘賦值成功：val = {g.get('val')}") if g.get("val") == 40
         else (False, "變數 val 數值不為 40（5 * (2 + 6) = 40）")),

        # 1-4-4 整數除法與求餘數捷徑：//= 與 %= (共 20 分)
        ("1-4-4", "填空題", "蘋果裝袋求餘數 apples %= 6", 6,
         lambda g: (True, "求餘數賦值正確：apples = 2") if g.get("apples") == 2
         else (False, "找不到 apples 或數值不為 2，請填入 %= 6")),

        ("1-4-4", "練習題", "三位數剪除個位十位 code //= 10", 8,
         lambda g: (True, f"兩次整數除法取得百位數正確：code = {g.get('code')}") if g.get("code") in [7, 5, 9]
         else (False, "code 數值不正確（測資 789 經兩次 //= 10 應為 7）")),

        ("1-4-4", "挑戰題", "時間換算小時與分鐘 minutes, remain", 6,
         lambda g: (True, f"時間換算成功：{g.get('minutes')} 小時 {g.get('remain')} 分鐘")
         if (g.get("minutes") == 2 and g.get("remain") == 5)
         else (False, "請設定 minutes //= 60 (得2) 與 remain %= 60 (得5)")),

        # 1-4-5 次方捷徑：**= 與右側整體先算優先權 (共 20 分)
        ("1-4-5", "填空題", "立方運算 base **= 3", 6,
         lambda g: (True, "次方賦值正確：base = 64") if g.get("base") == 64
         else (False, "找不到 base 或數值不為 64，請使用 **= 3")),

        ("1-4-5", "練習題", "正方形面積計算 side **= 2", 8,
         lambda g: (True, f"正方形面積計算正確：side = {g.get('side')}") if g.get("side") in [25, 49, 100]
         else (False, "變數 side 數值不符合測資（初始 5 經 side **= 2 應為 25）")),

        ("1-4-5", "挑戰題", "右側整體先算次方運算 n **= 2 + 1", 6,
         lambda g: (True, f"魔王級次方運算成功：n = {g.get('n')}") if g.get("n") == 27
         else (False, "變數 n 不為 27（3 ** (2 + 1) = 3 ** 3 = 27）")),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-4：複合賦值運算子 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 複合賦值運算子掌控得出神入化！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，僅少數細節需微調！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌記錄
    log_data = {
        "unit": "1-4",
        "unit_title": "複合賦值運算子",
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
        log_filename = f"score_log_unit_1_4.json"
        with open(log_filename, "w", encoding="utf-8") as lf:
            json.dump(log_data, lf, ensure_ascii=False, indent=2)
        print(f"💾 [本地存檔] 評分紀錄檔已生成：{log_filename}（可於左側檔案區下載備查）")
    except Exception as e:
        print(f"⚠️ 本地日誌寫入提示：{e}")

    # 2. 雲端後台成績記錄
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
auto_grade_unit_1_4()
