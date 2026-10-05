# ==============================================================================
# 🧪 《PythAPCS123》單元 3-4：絕對值計算（abs） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_3_4.py
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

def auto_grade_unit_3_4():
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
        # 3-4-1 認識 abs() 絕對值函數——數線上的無向距離守護者 (共 25 分)
        # ----------------------------------------------------------------------
        ("3-4-1", "填空題", "abs 取得非負偏差幅度 (positive_magnitude = 24)", 7,
         lambda g: (
             (True, "絕對值計算成功：abs(-24) = 24！")
             if (g.get("positive_magnitude") == 24)
             else (False, "找不到 positive_magnitude 或數值不為 24，請在空格填入 abs 並執行！")
         )),

        ("3-4-1", "練習題", "整數絕對值計算並印出 (check_val)", 10,
         lambda g: (
             (True, f"絕對值運算正確！(check_val={g.get('check_val')})")
             if ("check_val" in g and
                 isinstance(g.get("check_val"), (int, float)) and
                 (abs(g.get("check_val")) in [128, 75] or
                  any(v in [128, 75] for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到 check_val，請宣告整數並使用 abs() 計算其絕對值！")
         )),

        ("3-4-1", "挑戰題", "測量長度誤差絕對值 (error_val ≈ 2.6)", 8,
         lambda g: (
             (True, "測量誤差計算正確：abs(97.4 - 100.0) = 2.6！")
             if any(isinstance(v, (int, float)) and abs(v - 2.6) < 1e-4 for v in g.values()) or
                (all(k in g for k in ["standard_len", "measured_len"]) and
                 any(isinstance(v, (int, float)) and abs(v - abs(g['measured_len'] - g['standard_len'])) < 1e-4 for v in g.values()))
             else (False, "請宣告 standard_len=100.0, measured_len=97.4，以 abs() 計算誤差絕對值 2.6 並印出！")
         )),

        # ----------------------------------------------------------------------
        # 3-4-2 兩數無向差值計算——一行求得差距，取代正負號手動調整 (共 25 分)
        # ----------------------------------------------------------------------
        ("3-4-2", "填空題", "數線上兩點幾何距離 (distance = 45)", 7,
         lambda g: (
             (True, "數線距離計算成功：abs(28 - 73) = 45！")
             if (g.get("distance") == 45)
             else (False, "找不到 distance 或數值不為 45，請在空格填入 abs 與 pos2！")
         )),

        ("3-4-2", "練習題", "兩整數數線幾何距離 (p1, p2)", 10,
         lambda g: (
             (True, "兩點幾何距離計算正確！")
             if ("p1" in g and "p2" in g and
                 isinstance(g.get("p1"), (int, float)) and
                 isinstance(g.get("p2"), (int, float)) and
                 (any(v in [45, 60] for v in g.values() if isinstance(v, (int, float))) or
                  any(v == abs(g['p1'] - g['p2']) for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到 p1 或 p2，請計算 abs(p1 - p2) 並印出！")
         )),

        ("3-4-2", "挑戰題", "水庫蓄水量絕對偏離值 (deviation = 15)", 8,
         lambda g: (
             (True, "蓄水偏離值計算成功：abs(85 - 100) = 15 萬噸！")
             if any(isinstance(v, (int, float)) and v == 15 for k, v in g.items() if "dev" in k or "ans" in k or "diff" in k) or
                (all(k in g for k in ["current_water", "baseline_water"]) and
                 any(isinstance(v, (int, float)) and v == abs(g['current_water'] - g['baseline_water']) for v in g.values()))
             else (False, "請以 abs(current_water - baseline_water) 計算蓄水偏離值 15 並印出！")
         )),

        # ----------------------------------------------------------------------
        # 3-4-3 曼哈頓距離（兩點網格距離）計算——abs(x1 - x2) + abs(y1 - y2) (共 25 分)
        # ----------------------------------------------------------------------
        ("3-4-3", "填空題", "外送曼哈頓距離計算 (delivery_dist = 12)", 7,
         lambda g: (
             (True, "曼哈頓距離計算成功：|3-9| + |8-2| = 12！")
             if (g.get("delivery_dist") == 12)
             else (False, "找不到 delivery_dist 或數值不為 12，請在兩處空格填入 abs！")
         )),

        ("3-4-3", "練習題", "兩座標點曼哈頓網格距離 (x1, y1, x2, y2)", 10,
         lambda g: (
             (True, "座標點曼哈頓距離計算正確！")
             if (all(k in g for k in ["x1", "y1", "x2", "y2"]) and
                 isinstance(g.get("x1"), (int, float)) and
                 isinstance(g.get("y1"), (int, float)) and
                 isinstance(g.get("x2"), (int, float)) and
                 isinstance(g.get("y2"), (int, float)) and
                 (any(v in [7, 10] for v in g.values() if isinstance(v, (int, float))) or
                  any(v == abs(g['x1'] - g['x2']) + abs(g['y1'] - g['y2']) for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到坐標點 (x1, y1), (x2, y2)，請使用 abs(x1 - x2) + abs(y1 - y2) 計算並印出！")
         )),

        ("3-4-3", "挑戰題", "餐廳送餐機器人出發基地到顧客桌號步數 (8)", 8,
         lambda g: (
             (True, "送餐機器人導航步數計算成功：|2-8| + |3-1| = 8 步！")
             if any(isinstance(v, (int, float)) and v == 8 for k, v in g.items() if "dist" in k or "step" in k or "ans" in k or "walk" in k) or
                any(isinstance(v, (int, float)) and v == 8 for v in g.values())
             else (False, "請以 abs(2 - 8) + abs(3 - 1) 計算機器人從基地 (2, 3) 到顧客 (8, 1) 的曼哈頓步數 8！")
         )),

        # ----------------------------------------------------------------------
        # 3-4-4 兩組總和差距計算實務——abs(odd_sum - even_sum) 的純數學化身 (共 25 分)
        # ----------------------------------------------------------------------
        ("3-4-4", "填空題", "兩組總和差距絕對值 (diff_val = 16)", 7,
         lambda g: (
             (True, "總和差距計算成功：abs(34 - 18) = 16！")
             if (g.get("diff_val") == 16)
             else (False, "找不到 diff_val 或數值不為 16，請在空格填入 abs！")
         )),

        ("3-4-4", "練習題", "兩群組數值總和差距 (group_a, group_b)", 10,
         lambda g: (
             (True, "群組總和差距計算正確！")
             if ("group_a" in g and "group_b" in g and
                 isinstance(g.get("group_a"), (int, float)) and
                 isinstance(g.get("group_b"), (int, float)) and
                 (any(v in [7, 12] for v in g.values() if isinstance(v, (int, float))) or
                  any(v == abs(g['group_a'] - g['group_b']) for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到 group_a 或 group_b，請以 abs(group_a - group_b) 計算差距並印出！")
         )),

        ("3-4-4", "挑戰題", "比賽紅藍隊勝負分差 (7)", 8,
         lambda g: (
             (True, "比賽分差計算成功：abs(82 - 89) = 7 分！")
             if any(isinstance(v, (int, float)) and v == 7 for k, v in g.items() if "diff" in k or "ans" in k or "score" in k or "pts" in k) or
                any(isinstance(v, str) and "7" in v for v in g.values()) or
                (all(k in g for k in ["red_pts", "blue_pts"]) and
                 any(isinstance(v, (int, float)) and v == abs(g['red_pts'] - g['blue_pts']) for v in g.values()))
             else (False, "請宣告 red_pts=82, blue_pts=89，以 abs() 算出兩隊分差 7 分並印出！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 3-4：絕對值計算（abs） —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 abs() 數線距離與曼哈頓網格距離，純數學一行解題神乎其技！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，絕對值距離與無向差距觀念清晰！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "3-4",
        "unit_title": "絕對值計算（abs）",
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
        log_filename = "score_log_unit_3_4.json"
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
auto_grade_unit_3_4()
