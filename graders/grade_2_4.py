# ==============================================================================
# 🧪 《PythAPCS123》單元 2-4：次方運算與開根號求解 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_4.py
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

def auto_grade_unit_2_4():
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
        # 2-4-1 次方運算雙星號（**）與脫字符號（^）的巨大陷阱 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-4-1", "填空題", "正方形草皮平方運算 (area = 49)", 7,
         lambda g: (
             (True, "雙星號次方運算成功：area = 7 ** 2 = 49！")
             if (g.get("area") == 49 and type(g.get("area")) is int)
             else (
                 (False, "注意：在 Python 中次方為雙星號 **，不可使用脫字符號 ^ 喔！")
                 if (g.get("area") == (7 ^ 2))
                 else (False, "找不到變數 area 或數值不為 49，請在空格填入 ** 並執行！")
             )
         )),

        ("2-4-1", "練習題", "底數與指數次方計算 (base ** exp)", 10,
         lambda g: (
             (True, f"次方計算正確：{g.get('base')} ** {g.get('exp')} = {g.get('base') ** g.get('exp')}")
             if ("base" in g and "exp" in g and
                 type(g.get("base")) is int and type(g.get("exp")) is int and
                 (g.get("base") ** g.get("exp") in [81, 125] or g.get("base") ** g.get("exp") > 0))
             else (False, "找不到變數 base 或 exp，請依練習題說明使用 ** 計算次方並印出！")
         )),

        ("2-4-1", "挑戰題", "益生菌週期暴增次方運算 (initial * 3**cycles)", 8,
         lambda g: (
             (True, "益生菌繁殖暴增計算完成！")
             if any(k in g and type(g.get(k)) is int and g.get(k) >= 5 for k in ["total_bacteria", "bacteria", "ans", "final_count"]) or
                ("cycles" in g and type(g.get("cycles")) is int and any(type(v) is int and v >= 15 for v in g.values()))
             else (False, "請宣告 cycles 變數並利用 initial_count * (3 ** cycles) 計算益生菌總數！")
         )),

        # ----------------------------------------------------------------------
        # 2-4-2 次方的超高優先級與負數括號陷阱 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-4-2", "填空題", "負數底數小括號保護 (ans_positive = 9)", 7,
         lambda g: (
             (True, "負數小括號保護成功：ans_positive = (-3) ** 2 = 9！")
             if (g.get("ans_positive") == 9 and type(g.get("ans_positive")) is int)
             else (
                 (False, "未加小括號會被算成 -(3**2) = -9！請在 -3 前後補上小括號 (-3) 喔！")
                 if (g.get("ans_positive") == -9)
                 else (False, "找不到 ans_positive 或數值不為 9，請填入括號 ( 與 ) 並執行！")
             )
         )),

        ("2-4-2", "練習題", "負底數偶數次方計算 (neg_base, even_exp)", 10,
         lambda g: (
             (True, f"負數次方正確：({g.get('neg_base')}) ** {g.get('even_exp')} = {g.get('neg_base') ** g.get('even_exp')}")
             if ("neg_base" in g and "even_exp" in g and
                 type(g.get("neg_base")) is int and type(g.get("even_exp")) is int and
                 g.get("neg_base") < 0 and g.get("even_exp") % 2 == 0 and
                 (g.get("neg_base") ** g.get("even_exp") in [16, 625] or g.get("neg_base") ** g.get("even_exp") > 0))
             else (False, "找不到 neg_base（負數）或 even_exp（偶數），請以小括號計算次方並印出！")
         )),

        ("2-4-2", "挑戰題", "二次多項式數值計算 (y = a*x**2 + b*x + c ➔ 25)", 8,
         lambda g: (
             (True, "二次多項式計算成功：當 x = -2 時 y = 25！")
             if (g.get("y") == 25 and type(g.get("y")) is int) or
                any(g.get(k) == 25 for k in ["poly_val", "ans", "res"] if k in g)
             else (False, "請設定 a=3, b=-4, c=5, x=-2，計算 a*(x**2) + b*x + c 的值（預期 y = 25）！")
         )),

        # ----------------------------------------------------------------------
        # 2-4-3 用 a ** 0.5 進行開根號計算與浮點型態轉變 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-4-3", "填空題", "0.5 次方開根號求斜邊 (hypotenuse = 5.0)", 7,
         lambda g: (
             (True, "開根號成功：hypotenuse = 25 ** 0.5 = 5.0（<class 'float'>）！")
             if (g.get("hypotenuse") == 5.0 and type(g.get("hypotenuse")) is float)
             else (False, "找不到 hypotenuse 或數值不為 5.0，請在空格填入 0.5 並點擊播放鍵執行！")
         )),

        ("2-4-3", "練習題", "正方形面積開根號求邊長 (area_val ** 0.5)", 10,
         lambda g: (
             (True, f"開根號求邊長正確：{g.get('area_val')} ** 0.5 = {g.get('area_val') ** 0.5}")
             if ("area_val" in g and
                 type(g.get("area_val")) in [int, float] and
                 (abs(g.get("area_val") ** 0.5 - 8.0) < 1e-9 or abs(g.get("area_val") ** 0.5 - 12.0) < 1e-9 or
                  any(abs(g.get(k) - (g.get('area_val') ** 0.5)) < 1e-9 for k in ["side", "length", "ans"] if k in g)))
             else (False, "找不到變數 area_val，請宣告面積並使用 ** 0.5 計算邊長！")
         )),

        ("2-4-3", "挑戰題", "畢氏定理斜邊長度計算 ((6**2 + 8**2)**0.5 ➔ 10.0)", 8,
         lambda g: (
             (True, "畢氏定理計算正確：斜邊 c = 10.0！")
             if any(abs(g.get(k) - 10.0) < 1e-9 for k in ["c", "hypotenuse", "ans"] if k in g) or
                (g.get("a") == 6 and g.get("b") == 8 and any(abs(v - 10.0) < 1e-9 for v in g.values() if isinstance(v, (int, float))))
             else (False, "請宣告兩股 a = 6, b = 8，並用 (a**2 + b**2)**0.5 計算斜邊 c = 10.0！")
         )),

        # ----------------------------------------------------------------------
        # 2-4-4 APCS 實戰質數判定加速——開根號取整 int(n ** 0.5) 技巧 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-4-4", "填空題", "開根號取整質數檢查上限 (check_limit = 8)", 7,
         lambda g: (
             (True, "開根號取整成功：check_limit = int(80 ** 0.5) = 8！")
             if (g.get("check_limit") == 8 and type(g.get("check_limit")) is int)
             else (False, "找不到 check_limit 或數值不為 8，請填入 int 與 ** 0.5 並執行！")
         )),

        ("2-4-4", "練習題", "任意正整數開根號取整 (int(target_n ** 0.5))", 10,
         lambda g: (
             (True, f"開根號取整正確：int({g.get('target_n')} ** 0.5) = {int(g.get('target_n') ** 0.5)}")
             if ("target_n" in g and type(g.get("target_n")) is int and
                 (int(g.get("target_n") ** 0.5) in [7, 14] or
                  any(g.get(k) == int(g.get("target_n") ** 0.5) for k in ["res", "ans", "limit", "root"] if k in g)))
             else (False, "找不到變數 target_n，請依練習題使用 int(target_n ** 0.5) 取整數並印出！")
         )),

        ("2-4-4", "挑戰題", "整數平方根檢測器 (r 與 r**2 精準還原)", 8,
         lambda g: (
             (True, "整數平方根檢測器運作正確！")
             if any(k in g for k in ["r", "root"]) and any(k in g for k in ["sq", "r_squared", "restore"]) or
                ("test_val" in g and type(g.get("test_val")) is int)
             else (False, "請宣告 test_val，並分別計算整數平方根 r 與還原平方值 r ** 2！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-4：次方運算與開根號求解 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通次方高特權與開根號取整核心實戰！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，次方與根號運算熟練！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌
    log_data = {
        "unit": "2-4",
        "unit_title": "次方運算與開根號求解",
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
        log_filename = "score_log_unit_2_4.json"
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
auto_grade_unit_2_4()
