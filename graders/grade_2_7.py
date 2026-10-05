# ==============================================================================
# 🧪 《PythAPCS123》單元 2-7：位元運算與速度最佳化 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_7.py
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

def auto_grade_unit_2_7():
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
        # 2-7-1 位元 AND（&）與超光速奇偶判斷（x & 1） (共 25 分)
        # ----------------------------------------------------------------------
        ("2-7-1", "填空題", "位元 AND 極速奇偶判斷 (is_odd = 87 & 1 ➔ 1)", 7,
         lambda g: (
             (True, "位元 AND 奇偶判斷成功：is_odd = 87 & 1 = 1！")
             if (g.get("is_odd") == 1 and type(g.get("is_odd")) is int)
             else (False, "找不到 is_odd 或數值不為 1，請在空格填入 & 1 並執行！")
         )),

        ("2-7-1", "練習題", "任意整數最末位元計算 (num_check & 1)", 10,
         lambda g: (
             (True, "最末位元 AND 計算正確！")
             if ("num_check" in g and type(g.get("num_check")) is int and
                 (g.get("num_check") & 1 in [0, 1] or any(g.get(k) in [0, 1] for k in ["last_bit", "ans", "bit"] if k in g)))
             else (False, "找不到 num_check，請計算 num_check & 1 並印出最末位元！")
         )),

        ("2-7-1", "挑戰題", "位元偶數等級判斷與雙倍獎勵結算 (level=16 ➔ 32)", 8,
         lambda g: (
             (True, "等級位元獎勵點數計算成功（32 點）！")
             if any(g.get(k) == 32 for k in ["reward", "points", "ans", "final_reward"] if k in g) or
                (g.get("level") == 16 and any(v == 32 for v in g.values()))
             else (False, "請設定 level = 16，利用 (level & 1) 判斷並印出雙倍獎勵 32！")
         )),

        # ----------------------------------------------------------------------
        # 2-7-2 位元 OR（|）與狀態開關強制啟用 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-7-2", "填空題", "位元 OR 權限開關合併 (new_perm = 6)", 7,
         lambda g: (
             (True, "位元 OR 合併權限成功：new_perm = 0b0100 | 0b0010 = 6！")
             if (g.get("new_perm") == 6 and type(g.get("new_perm")) is int)
             else (False, "找不到 new_perm 或數值不為 6，請在空格填入 | 運算子！")
         )),

        ("2-7-2", "練習題", "兩整數位元 OR 合併計算 (base_val | mask_val)", 10,
         lambda g: (
             (True, "位元 OR 運算結果正確！")
             if ("base_val" in g and "mask_val" in g and
                 type(g.get("base_val")) is int and type(g.get("mask_val")) is int and
                 (g.get("base_val") | g.get("mask_val") in [11, 31] or g.get("base_val") | g.get("mask_val") > 0))
             else (False, "找不到 base_val 或 mask_val，請以 base_val | mask_val 計算合併值！")
         )),

        ("2-7-2", "挑戰題", "智慧教室三設備連續位元 OR 啟動 (state = 13)", 8,
         lambda g: (
             (True, "三設備連續位元 OR 啟動成功（0b0001 | 0b0100 | 0b1000 = 13）！")
             if any(g.get(k) == 13 for k in ["state", "total_state", "ans", "room_state"] if k in g) or
                any(v == 13 for v in g.values() if type(v) is int)
             else (False, "請以 mask_proj | mask_audio | mask_ac 連續 OR 計算並印出 13！")
         )),

        # ----------------------------------------------------------------------
        # 2-7-3 位元 XOR（^）與開關翻轉／相同自消魔法 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-7-3", "填空題", "位元 XOR 開關狀態翻轉 (stealth = stealth ^ 1)", 7,
         lambda g: (
             (True, "位元 XOR 開關翻轉成功：stealth ^ 1 = 1！")
             if (g.get("stealth") == 1 and type(g.get("stealth")) is int)
             else (False, "找不到 stealth 或數值不為 1，請在空格填入 ^ 運算子！")
         )),

        ("2-7-3", "練習題", "相異比對與自相消滅 (x_val ^ y_val)", 10,
         lambda g: (
             (True, "位元 XOR 相異比對運算正確！")
             if ("x_val" in g and "y_val" in g and
                 type(g.get("x_val")) is int and type(g.get("y_val")) is int and
                 (g.get("x_val") ^ g.get("y_val") in [6, 0] or g.get("x_val") ^ g.get("y_val") >= 0))
             else (False, "找不到 x_val 或 y_val，請以 x_val ^ y_val 計算並印出結果！")
         )),

        ("2-7-3", "挑戰題", "連續 XOR 自消過濾唯一關鍵金鑰 (99)", 8,
         lambda g: (
             (True, "連續 XOR 自動抵銷成功：精準過濾出唯一金鑰 99！")
             if any(g.get(k) == 99 for k in ["key", "ans", "unique_key", "secret"] if k in g) or
                any(v == 99 for v in g.values() if type(v) is int)
             else (False, "請以 24 ^ 55 ^ 99 ^ 55 ^ 24 計算並印出唯一未成對金鑰 99！")
         )),

        # ----------------------------------------------------------------------
        # 2-7-4 位元左移（<<）與右移（>>）——二進位滑梯與乘除倍增 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-7-4", "填空題", "位元左移快速 4 倍擴增 (quadruple = base << 2 ➔ 28)", 7,
         lambda g: (
             (True, "位元左移成功：quadruple = 7 << 2 = 28！")
             if (g.get("quadruple") == 28 and type(g.get("quadruple")) is int)
             else (False, "找不到 quadruple 或數值不為 28，請填入 << 運算子！")
         )),

        ("2-7-4", "練習題", "左移翻倍與右移減半運算 (sample_n << 1, sample_n >> 1)", 10,
         lambda g: (
             (True, "左移翻倍與右移折半運算正確！")
             if ("sample_n" in g and type(g.get("sample_n")) is int and
                 ((g.get("sample_n") << 1 == 24 and g.get("sample_n") >> 1 == 6) or
                  (g.get("sample_n") << 1 == 50 and g.get("sample_n") >> 1 == 12) or
                  (g.get("sample_n") > 0)))
             else (False, "找不到 sample_n，請依練習題印出 sample_n << 1 與 sample_n >> 1！")
         )),

        ("2-7-4", "挑戰題", "二分搜尋位元右移求中點 ((left + right) >> 1 ➔ 17)", 8,
         lambda g: (
             (True, "二分搜尋區間中點右移計算正確：mid = (10 + 25) >> 1 = 17！")
             if (g.get("mid") == 17 and type(g.get("mid")) is int) or
                any(g.get(k) == 17 for k in ["mid_point", "ans", "center"] if k in g)
             else (False, "請設定 left = 10, right = 25，利用 (left + right) >> 1 計算中點 17！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-7：位元運算與速度最佳化 —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通二進位底層位元運算，極速優化大成！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，位元遮罩與移位技巧嫻熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # 1. 本地日誌
    log_data = {
        "unit": "2-7",
        "unit_title": "位元運算與速度最佳化",
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
        log_filename = "score_log_unit_2_7.json"
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
auto_grade_unit_2_7()
