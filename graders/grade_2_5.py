# ==============================================================================
# 🧪 《PythAPCS123》單元 2-5：浮點數除法（/）與精度限制 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_5.py
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

def auto_grade_unit_2_5():
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
        # 2-5-1 單斜線除法（/）——必定產生浮點數的魔法轉身 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-5-1", "填空題", "單斜線除法精確平均單價 (avg_price = 35.0)", 7,
         lambda g: (
             (True, "單斜線除法成功：avg_price = 140 / 4 = 35.0（<class 'float'>）！")
             if (g.get("avg_price") == 35.0 and type(g.get("avg_price")) is float)
             else (
                 (False, "注意：請使用單斜線除法 / 產生浮點數 35.0，勿使用 // 整除喔！")
                 if (g.get("avg_price") == 35 and type(g.get("avg_price")) is int)
                 else (False, "找不到變數 avg_price 或數值不為 35.0，請填入 / 並執行！")
             )
         )),

        ("2-5-1", "練習題", "汽車平均時速浮點除法 (distance / hours)", 10,
         lambda g: (
             (True, f"平均時速計算正確：{g.get('distance')} / {g.get('hours')} = {g.get('distance') / g.get('hours')}")
             if ("distance" in g and "hours" in g and
                 (g.get("distance") / g.get("hours") in [75.0, 22.5] or
                  any(g.get(k) == g.get('distance') / g.get('hours') for k in ["speed", "avg_speed", "ans"] if k in g)))
             else (False, "找不到 distance 或 hours，請使用單斜線除法計算平均時速並印出！")
         )),

        ("2-5-1", "挑戰題", "三科成績加總平均浮點除法 ((c+e+m) / 3)", 8,
         lambda g: (
             (True, "三科平均成績計算完成（精確浮點數輸出）！")
             if any(abs(g.get(k) - (85 + 92 + 88) / 3) < 1e-6 for k in ["avg", "average", "ans", "mean_score"] if k in g) or
                (g.get("chinese") == 85 and g.get("english") == 92 and g.get("math") == 88 and
                 any(isinstance(v, float) and abs(v - 88.33333333333333) < 1e-4 for v in g.values()))
             else (False, "請宣告三科成績，並用 (chinese + english + math) / 3 計算精確平均值！")
         )),

        # ----------------------------------------------------------------------
        # 2-5-2 電腦底層的二進位秘密——0.1 + 0.2 != 0.3 的精度誤差真相 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-5-2", "填空題", "浮點數精度微偏差觀察 (sum_ab = 0.1 + 0.7)", 7,
         lambda g: (
             (True, "成功重現二進位浮點數微小偏差：sum_ab ≈ 0.7999999999999999！")
             if ("sum_ab" in g and type(g.get("sum_ab")) is float and abs(g.get("sum_ab") - 0.8) < 1e-9)
             else (False, "找不到 sum_ab 或數值不正確，請在空格填入 + 運算子完成相加！")
         )),

        ("2-5-2", "練習題", "小數兩次累加精度觀察 (start_val + step_val*2)", 10,
         lambda g: (
             (True, "小數累加運算正確！")
             if ("start_val" in g and "step_val" in g and
                 type(g.get("start_val")) in [int, float] and type(g.get("step_val")) in [int, float] and
                 (abs(g.get("start_val") + g.get("step_val") * 2 - 0.4) < 1e-9 or
                  abs(g.get("start_val") + g.get("step_val") * 2 - 0.5) < 1e-9 or
                  any(isinstance(g.get(k), float) for k in ["res", "ans", "total"] if k in g)))
             else (False, "找不到 start_val 或 step_val，請進行兩次連續累加並印出！")
         )),

        ("2-5-2", "挑戰題", "0.3 - 0.2 浮點數精度真相探究 (val)", 8,
         lambda g: (
             (True, "0.3 - 0.2 精度現象觀察完成！")
             if ("val" in g and type(g.get("val")) is float and abs(g.get("val") - 0.1) < 1e-9) or
                any(isinstance(v, float) and abs(v - 0.1) < 1e-9 for v in g.values())
             else (False, "請宣告 val = 0.3 - 0.2，並分兩行印出真實數值與 val == 0.1 比對結果！")
         )),

        # ----------------------------------------------------------------------
        # 2-5-3 APCS 浮點數相等的安全比對法——容許誤差（Epsilon）與 abs() (共 25 分)
        # ----------------------------------------------------------------------
        ("2-5-3", "填空題", "abs 容許誤差安全比對 (safe_check = True)", 7,
         lambda g: (
             (True, "安全比對成功：safe_check = abs(x - y) < 1e-9 判定為 True！")
             if (g.get("safe_check") is True)
             else (False, "safe_check 必須為 True，請填入 abs 與 < 符號完成安全比對！")
         )),

        ("2-5-3", "練習題", "兩浮點數容差安全比對 (abs(num_a - num_b) < 1e-6)", 10,
         lambda g: (
             (True, "浮點數容差安全檢查正確！")
             if ("num_a" in g and "num_b" in g and
                 type(g.get("num_a")) in [int, float] and type(g.get("num_b")) in [int, float] and
                 any(type(g.get(k)) is bool for k in ["is_equal", "check", "ans", "same"] if k in g) or
                 any(type(v) is bool for v in g.values()))
             else (False, "找不到 num_a 或 num_b，請利用 abs(num_a - num_b) < 1e-6 進行安全比對！")
         )),

        ("2-5-3", "挑戰題", "直角三角形斜邊計算安全容差比對", 8,
         lambda g: (
             (True, "斜邊容差安全比對成功（判定為 True）！")
             if (g.get("calc_c") is not None and abs(g.get("calc_c") - 0.5) < 1e-6) or
                any(v is True for k, v in g.items() if "check" in k or "safe" in k or "ans" in k or "is_" in k)
             else (False, "請計算 calc_c = (a**2 + b**2)**0.5，並以 abs(calc_c - target_c) < 1e-9 比對！")
         )),

        # ----------------------------------------------------------------------
        # 2-5-4 浮點數輸出修剪術——round() 四捨五入 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-5-4", "填空題", "round 四捨五入指定小數位數", 7,
         lambda g: (
             (True, "四捨五入指定成功：round(125.6789, 2) = 125.68！")
             if any(abs(v - 125.68) < 1e-6 for v in g.values() if isinstance(v, (int, float))) or
                g.get("raw_usd") == 125.6789
             else (False, "請在 round 第二個空格填入保留位數 2 並執行！")
         )),

        ("2-5-4", "練習題", "除法後 round 四捨五入取兩位小數 (num_x / num_y)", 10,
         lambda g: (
             (True, "除法後四捨五入計算正確！")
             if ("num_x" in g and "num_y" in g and
                 (round(g.get("num_x") / g.get("num_y"), 2) in [3.33, 3.5] or
                  any(round(g.get("num_x") / g.get("num_y"), 2) == round(v, 2) for v in g.values() if isinstance(v, float))))
             else (False, "找不到 num_x 或 num_y，請計算 num_x / num_y 並使用 round(..., 2) 四捨五入！")
         )),

        ("2-5-4", "挑戰題", "旅遊換匯計算機 (round(ntd / rate, 2) ➔ 1569.86)", 8,
         lambda g: (
             (True, "旅遊換匯美金四捨五入計算正確（1569.86 美元）！")
             if any(abs(v - 1569.86) < 1e-2 for v in g.values() if isinstance(v, (int, float))) or
                (g.get("ntd_amount") == 50000 and any(abs(v - 1569.86) < 1e-2 for v in g.values() if isinstance(v, float)))
             else (False, "請以 round(ntd_amount / exchange_rate, 2) 計算 50000 台幣換算美金（1569.86）！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-5：浮點數除法（/）與精度限制 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通浮點數除法本質與容許誤差比對奧義！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，浮點精度與 round 技巧純熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌
    log_data = {
        "unit": "2-5",
        "unit_title": "浮點數除法（/）與精度限制",
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
        log_filename = "score_log_unit_2_5.json"
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
auto_grade_unit_2_5()
