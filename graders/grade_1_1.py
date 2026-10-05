# ==============================================================================
# 🧪 《PythAPCS123》單元 1-1：變數命名規則與記憶體參照 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_1.py
# 版權宣告：PythAPCS123 教材團隊版權所有
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

def auto_grade_unit_1_1():
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
        # 1-1-1 變數基本概念
        ("1-1-1", "填空題", "變數建立 score = 95", 5,
         lambda g: (True, "置物箱正確貼上名牌 score 並放入 95") if g.get("score") == 95
         else (False, "找不到變數 score 或數值不為 95，請確認已替換 ___ 並點擊播放鍵執行")),

        ("1-1-1", "練習題", "糖果箱 candy 變數與輸出", 8,
         lambda g: (True, f"成功建立 candy = {g.get('candy')}") if g.get("candy") in [5, 12]
         else ((False, "檢測到大寫 Candy，但題目要求全小寫 candy（Python 對大小寫很嚴格喔！）") if "Candy" in g
               else (False, "找不到變數 candy，請依照練習題說明建立並賦值 5 或 12"))),

        ("1-1-1", "挑戰題", "幸運數字 my_lucky_number", 4,
         lambda g: (True, f"幸運數字已設定為 {g.get('my_lucky_number')}") if isinstance(g.get("my_lucky_number"), (int, float))
         else (False, "找不到名為 my_lucky_number 的數值變數，請自己放進一顆幸運數字！")),

        # 1-1-2 記憶體參照與 NameError
        ("1-1-2", "填空題", "修復 NameError (hp = 100)", 5,
         lambda g: (True, "成功提前宣告變數，hp = 100") if g.get("hp") == 100
         else (False, "找不到變數 hp 或數值不為 100，請先建立 hp 再印出")),

        ("1-1-2", "練習題", "拼字修復 player_level", 8,
         lambda g: (True, f"拼字修正正確，player_level = {g.get('player_level')}") if g.get("player_level") in [1, 99]
         else ((False, "仍殘留拼錯的 player_leval，請在 1-1-2 練習題更正為 level！") if "player_leval" in g
               else (False, "找不到變數 player_level，請將其設為 1 或 99"))),

        ("1-1-2", "挑戰題", "雙變數宣告 (Alex 與 500 金幣)", 4,
         lambda g: (True, f"冒險者名牌就緒：{g.get('player_name')}（金幣：{g.get('player_gold')}）")
         if g.get("player_name") == "Alex" and g.get("player_gold") == 500
         else (False, "請確認 player_name 為 'Alex' 且 player_gold 為 500")),

        # 1-1-3 變數命名規則一：字母、數字與底線
        ("1-1-3", "填空題", "底線串接 monster_hp_2", 5,
         lambda g: (True, "合法使用底線連接：monster_hp_2 = 350") if g.get("monster_hp_2") == 350
         else (False, "找不到合法的 monster_hp_2 變數，請填入底線連接單字")),

        ("1-1-3", "練習題", "蛇形命名 user_gold_coin", 8,
         lambda g: (True, f"蛇形命名正確：user_gold_coin = {g.get('user_gold_coin')}") if g.get("user_gold_coin") in [300, 1500]
         else (False, "找不到 user_gold_coin 變數，請依練習題設為 300 或 1500")),

        ("1-1-3", "挑戰題", "字母+底線+數字自訂變數 (777)", 3,
         lambda g: (True, "成功找到符合規則且存放 777 之自訂變數！") if any(v == 777 and '_' in k for k, v in g.items() if not k.startswith('_'))
         else (False, "未檢測到數值為 777 且名稱包含底線的變數（如 item_bag_3 = 777）")),

        # 1-1-4 變數命名規則二：開頭不能是數字
        ("1-1-4", "填空題", "數字移至後方 prize_1", 5,
         lambda g: (True, "數字擺在後方正確：prize_1 = 8888") if g.get("prize_1") == 8888
         else (False, "找不到 prize_1 變數，請將 1 移至英文字母後面")),

        ("1-1-4", "練習題", "修改非法變數名 score1 與 score2", 8,
         lambda g: (True, f"分數變數命名合法：score1={g.get('score1')}, score2={g.get('score2')}")
         if (g.get("score1") in [85, 100] and g.get("score2") in [92, 60])
         else (False, "請將 1score 與 2score 修改為 score1 與 score2 並完成賦值")),

        ("1-1-4", "挑戰題", "三位選手名次 rank1, rank2, rank3", 4,
         lambda g: (True, f"三選手排名就緒：({g.get('rank1')}, {g.get('rank2')}, {g.get('rank3')})")
         if (g.get("rank1") == 100 and g.get("rank2") == 90 and g.get("rank3") == 80)
         else (False, "請宣告 rank1=100, rank2=90, rank3=80")),

        # 1-1-5 變數命名規則三：大小寫大不同
        ("1-1-5", "填空題", "平民 hero 與國王 HERO", 5,
         lambda g: (True, "大小寫置物箱識別正確：hero=50, HERO=999")
         if (g.get("hero") == 50 and g.get("HERO") == 999)
         else (False, "請確認 hero=50 與 HERO=999 皆已執行宣告")),

        ("1-1-5", "練習題", "大小寫蘋果 apple 與 Apple", 8,
         lambda g: (True, f"雙重大小寫蘋果正確：apple={g.get('apple')}, Apple={g.get('Apple')}")
         if (g.get("apple") in [3, 7] and g.get("Apple") in [10, 20])
         else (False, "請建立小寫 apple (3或7) 與大寫 Apple (10或20)")),

        ("1-1-5", "挑戰題", "三重大小寫 data, Data, DATA", 4,
         lambda g: (True, "三重大小寫箱子共存成功！(1, 2, 3)")
         if (g.get("data") == 1 and g.get("Data") == 2 and g.get("DATA") == 3)
         else (False, "請分別宣告 data=1, Data=2, DATA=3")),

        # 1-1-6 變數命名規則四：避開保留字
        ("1-1-6", "填空題", "避開保留字改為 pass_code", 5,
         lambda g: (True, "安全避開保留字：pass_code = 1234") if g.get("pass_code") == 1234
         else (False, "找不到變數 pass_code，請將 pass 後加上 _code")),

        ("1-1-6", "練習題", "保護內建 print 命名 print_pages", 8,
         lambda g: (True, f"安全變數 print_pages = {g.get('print_pages')}，未污染 print 嘴巴")
         if g.get("print_pages") in [20, 50]
         else (False, "請將變數命名為 print_pages 並設為 20 或 50")),

        ("1-1-6", "挑戰題", "安全統計變數（避開 sum/max 關鍵字）", 3,
         lambda g: (True, "成功避開關鍵字危險，建立合法的自訂統計變數！")
         if any(isinstance(v, (int, float)) and any(w in k.lower() for w in ['sum', 'max', 'total']) and k not in ['sum', 'max'] for k, v in g.items() if not k.startswith('_'))
         else (False, "請建立非 sum/max 之安全統計變數（如 total_sum, val_max）")),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-1：變數命名規則與記憶體參照 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 完全掌握記憶體與變數命名心法！"
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
        "unit": "1-1",
        "unit_title": "變數命名規則與記憶體參照",
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
        log_filename = f"score_log_unit_1_1.json"
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
auto_grade_unit_1_1()
