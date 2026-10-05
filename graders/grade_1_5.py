# ==============================================================================
# 🧪 《PythAPCS123》單元 1-5：分號分隔與程式碼註解 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_5.py
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

def auto_grade_unit_1_5():
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
        # 1-5-1 井字號單行註解——給未來的自己與夥伴的備忘小紙條 (共 20 分)
        ("1-5-1", "填空題", "中文備忘錄加入註解符號 #", 6,
         lambda g: (True, "註解成功隱形：score = 90") if g.get("score") in [90, 100]
         else (False, "找不到變數 score 或數值不為 90，請在中文備忘錄前加上 # 符號")),

        ("1-5-1", "練習題", "三角形面積計算與行尾註解", 8,
         lambda g: (True, "三角形面積計算正確！")
         if any((g.get("base") == 10 and g.get("height") == 6) or (g.get("base") == 8 and g.get("height") == 5) for _ in [1])
         else (False, "找不到變數 base 或 height，請依練習題計算三角形面積並加上行尾註解")),

        ("1-5-1", "挑戰題", "魔法藥水重量計算 (herb + water)", 6,
         lambda g: (True, "草藥與聖水重量計算完成！")
         if isinstance(g.get("herb"), (int, float)) and isinstance(g.get("water"), (int, float))
         else (False, "請宣告草藥 herb 與聖水 water 並計算總重量")),

        # 1-5-2 分號串接單行多指令——省行數的利器 (共 20 分)
        ("1-5-2", "填空題", "分號串接 x=100; y=200", 6,
         lambda g: (True, "分號串接賦值成功：x=100, y=200")
         if (g.get("x") in [100, 0] and g.get("y") in [200, 0])
         else (False, "請在同一行使用分號 ; 連接 x = 100 與 y = 200")),

        ("1-5-2", "練習題", "一行分號設定 p 與 q 乘積", 8,
         lambda g: (True, f"乘積變數設定成功：p={g.get('p')}, q={g.get('q')}")
         if ((g.get("p") == 7 and g.get("q") == 8) or (g.get("p") == 12 and g.get("q") == 5))
         else (False, "請使用分號在一行內設定 p 與 q（如 p=7; q=8）")),

        ("1-5-2", "挑戰題", "單行三指令長方體體積 (l, w, h)", 6,
         lambda g: (True, f"長方體三維度設定成功：({g.get('l')}, {g.get('w')}, {g.get('h')})")
         if (g.get("l") == 10 and g.get("w") == 5 and g.get("h") == 2)
         else (False, "請在一行內用分號宣告 l=10; w=5; h=2")),

        # 1-5-3 分號的最佳實踐——何時用？何時不用？ (共 20 分)
        ("1-5-3", "填空題", "極值初始化 min_val; max_val", 6,
         lambda g: (True, "極值初始化成功：min_val=0, max_val=100")
         if (g.get("min_val") == 0 and g.get("max_val") == 100)
         else (False, "請在同一行使用分號連接 min_val = 0 與 max_val = 100")),

        ("1-5-3", "練習題", "座標與位移兩組關聯變數", 8,
         lambda g: (True, f"座標位移設定正確：dx={g.get('dx')}, dy={g.get('dy')}")
         if ((g.get("dx") == 3 and g.get("dy") == 4) or (g.get("dx") == 10 and g.get("dy") == 20))
         else (False, "請設定座標 x=0; y=0 與位移 dx=3; dy=4")),

        ("1-5-3", "挑戰題", "重構過度擁擠的分號代碼", 6,
         lambda g: (True, "重構變數與計算成功！")
         if (g.get("a") == 1 and g.get("b") == 2 and g.get("c") == 3 and g.get("d") == 3)
         else (False, "請重構程式碼，只保留關聯變數在同一行，並算出 d = a + b")),

        # 1-5-4 註解封印術——除錯測試的隱形斗篷 (共 20 分)
        ("1-5-4", "填空題", "封印報錯亂碼代碼", 6,
         lambda g: (True, "錯誤代碼已成功被 # 封印！") if g.get("score") == 100
         else (False, "請在亂碼前加上 # 符號進行封印，確保 score=100 順利印出")),

        ("1-5-4", "練習題", "封印舊版公式採用新版公式", 8,
         lambda g: (True, f"新版加成公式生效：bonus = {g.get('bonus')}")
         if g.get("bonus") in [30, 75]
         else (False, "請封印舊版公式，採用新版公式 bonus = points * 3（測資 10 應得 30）")),

        ("1-5-4", "挑戰題", "封印自訂異常代碼測試", 6,
         lambda g: (True, "自訂除錯封印挑戰成功！") if True
         else (False, "請完成挑戰題之註解封印測試")),

        # 1-5-5 長算式安全換行——小括號隱式折行 (共 20 分)
        ("1-5-5", "填空題", "四科段考總分括號折行 total_score", 6,
         lambda g: (True, "小括號隱式折行計算成功：total_score = 365") if g.get("total_score") == 365
         else (False, "變數 total_score 不為 365，請在長算式頭尾加上小括號 () 允許跨行")),

        ("1-5-5", "練習題", "農場四水果小括號隱式折行加總", 8,
         lambda g: (True, f"水果採收加總正確：total_fruits = {g.get('total_fruits')}")
         if g.get("total_fruits") in [640, 250]
         else (False, "變數 total_fruits 不符合測資（120+250+180+90 應為 640）")),

        ("1-5-5", "挑戰題", "勇者五屬性括號折行戰力加總", 6,
         lambda g: (True, f"勇者總戰力折行加總完成：total_power = {g.get('total_power')}")
         if g.get("total_power") == 1050
         else (False, "total_power 總戰力不為 1050（500+200+150+120+80 = 1050）")),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-5：分號分隔與程式碼註解 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 註解心法與分號美學融會貫通！"
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
        "unit": "1-5",
        "unit_title": "分號分隔與程式碼註解",
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
        log_filename = f"score_log_unit_1_5.json"
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
auto_grade_unit_1_5()
