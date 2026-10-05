# ==============================================================================
# 🧪 《PythAPCS123》單元 1-3：多變數同時賦值與變數交換（Swap） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_3.py
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

def auto_grade_unit_1_3():
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
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未授權 Google / 匿名"
        final_google_name = "未綁定 Google"
        combined_display_name = declared_name

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # 1-3-1 多變數同時賦值——雙手齊發的打包與解包 (共 19 分)
        ("1-3-1", "填空題", "雙變數同時賦值 x, y = 10, 20", 6,
         lambda g: (True, "雙變數同時賦值成功：x=10, y=20") if g.get("x") in [10, 20] and g.get("y") in [20, 30]
         else (False, "找不到變數 x, y 或數值不正確，請在 1-3-1 填空題設定 x, y = 10, 20")),

        ("1-3-1", "練習題", "一行宣告寬高 width, height", 8,
         lambda g: (True, f"寬高設定正確：width={g.get('width')}, height={g.get('height')}")
         if (g.get("width") in [40, 15] and g.get("height") in [30, 25])
         else (False, "找不到變數 width 或 height，請依練習題說明使用一行多重賦值設定數值")),

        ("1-3-1", "挑戰題", "RGB三原色同時賦值 (red, green, blue)", 5,
         lambda g: (True, f"RGB色彩代碼設定成功：({g.get('red')}, {g.get('green')}, {g.get('blue')})")
         if (g.get("red") == 255 and g.get("green") == 128 and g.get("blue") == 0)
         else (False, "請在一行中同時設定 red, green, blue 為 255, 128, 0")),

        # 1-3-2 等號兩側天平必須對稱——個數不符的 ValueError 警報 (共 19 分)
        ("1-3-2", "填空題", "天平平衡補齊三數 p, q, r", 6,
         lambda g: (True, "三變數對稱賦值完成：p=100, q=200, r=300")
         if (g.get("p") == 100 and g.get("q") == 200 and g.get("r") == 300)
         else (False, "變數 p, q, r 未正確設定為 100, 200, 300，請補齊右側數值")),

        ("1-3-2", "練習題", "修復 ValueError (x1, x2, x3)", 8,
         lambda g: (True, f"三變數對稱修復正確：({g.get('x1')}, {g.get('x2')}, {g.get('x3')})")
         if (g.get("x1") in [5, 1] and g.get("x2") in [10, 2] and g.get("x3") in [15, 3])
         else (False, "請修正 x1, x2, x3 的賦值，確認等號兩側均為 3 個元素")),

        ("1-3-2", "挑戰題", "四季代號一行四變數 (a, b, c, d)", 5,
         lambda g: (True, f"四變數對稱宣告成功：a={g.get('a')}, b={g.get('b')}, c={g.get('c')}, d={g.get('d')}")
         if (g.get("a") in [1, 4] and g.get("b") in [2, 1] and g.get("c") in [3, 2] and g.get("d") in [4, 3])
         else (False, "請在一行中宣告 a, b, c, d 分別對應 1, 2, 3, 4")),

        # 1-3-3 傳統變數交換的慘痛悲劇——為什麼需要第三個空杯子 temp？ (共 19 分)
        ("1-3-3", "填空題", "第三空杯備份交換 m 與 n", 6,
         lambda g: (True, "傳統暫存變數交換正確：m=99, n=88, temp=88")
         if (g.get("m") == 99 and g.get("n") == 88 and g.get("temp") == 88)
         else (False, "請在 ___ 填入 n，完成 m=n 與 n=temp 的三步驟交換")),

        ("1-3-3", "練習題", "卡牌交換 card1 與 card2 (透過 t)", 8,
         lambda g: (True, f"卡牌交換完成：card1={g.get('card1')}, card2={g.get('card2')}")
         if ((g.get("card1") == 2 and g.get("card2") == 7) or (g.get("card1") == 4 and g.get("card2") == 9))
         else (False, "卡牌數值未成功對調，請透過暫存變數 t 將 card1 與 card2 數值互換")),

        ("1-3-3", "挑戰題", "金銀蘋果守衛交換 guard_temp", 5,
         lambda g: (True, f"金銀蘋果對調成功：gold={g.get('gold_apple')}, silver={g.get('silver_apple')}")
         if (g.get("gold_apple") == 2 and g.get("silver_apple") == 1 and g.get("guard_temp") == 1)
         else (False, "請宣告 guard_temp 備份，將 gold_apple (1->2) 與 silver_apple (2->1) 成功交換")),

        # 1-3-4 Python 專屬的瞬間乾坤大挪移——`a, b = b, a` 變數交換 (共 20 分)
        ("1-3-4", "填空題", "乾坤大挪移 u, v = v, u", 6,
         lambda g: (True, "單行交換成功：u=555, v=111")
         if (g.get("u") == 555 and g.get("v") == 111)
         else (False, "請填入 u, v = v, u 實現一行變數乾坤大挪移")),

        ("1-3-4", "練習題", "左右數值對調 left, right", 8,
         lambda g: (True, f"左右交換正確：left={g.get('left')}, right={g.get('right')}")
         if ((g.get("left") == 200 and g.get("right") == 100) or (g.get("left") == 50 and g.get("right") == 10))
         else (False, "請使用 left, right = right, left 將左右變數數值對調")),

        ("1-3-4", "挑戰題", "大小號碼牌對調 small, big", 6,
         lambda g: (True, f"大小牌對調成功：small={g.get('small')}, big={g.get('big')}")
         if (g.get("small") == 10 and g.get("big") == 50)
         else (False, "請使用一行交換語法，讓原本 50 與 10 的 small 與 big 數值對調")),

        # 1-3-5 三人傳球大輪替——多變數循環交換（Cyclic Swap） (共 23 分)
        ("1-3-5", "填空題", "三變數循環輪替 x, y, z = y, z, x", 7,
         lambda g: (True, "三變數輪替完成：x=20, y=30, z=10")
         if (g.get("x") == 20 and g.get("y") == 30 and g.get("z") == 10)
         else (False, "請填入 x, y, z = y, z, x 完成循環輪替")),

        ("1-3-5", "練習題", "隊員分數循環傳球 p1, p2, p3", 9,
         lambda g: (True, f"隊員分數輪替正確：({g.get('p1')}, {g.get('p2')}, {g.get('p3')})")
         if ((g.get("p1") == 200 and g.get("p2") == 300 and g.get("p3") == 100) or
             (g.get("p1") == 60 and g.get("p2") == 70 and g.get("p3") == 50))
         else (False, "請透過一行語法將 p1, p2, p3 循環輪替（p1拿p2, p2拿p3, p3拿p1）")),

        ("1-3-5", "挑戰題", "四變數逆向大輪替 a, b, c, d", 7,
         lambda g: (True, f"四變數逆向輪替成功：({g.get('a')}, {g.get('b')}, {g.get('c')}, {g.get('d')})")
         if (g.get("a") == 4 and g.get("b") == 1 and g.get("c") == 2 and g.get("d") == 3)
         else (False, "請以 a, b, c, d = d, a, b, c 完成逆向輪替（a=4, b=1, c=2, d=3）")),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-3：多變數同時賦值與變數交換 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 變數交換與多重賦值神乎其技！"
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
        "unit": "1-3",
        "unit_title": "多變數同時賦值與變數交換",
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
        log_filename = f"score_log_unit_1_3.json"
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
auto_grade_unit_1_3()
