# ==============================================================================
# 🧪 《PythAPCS123》單元 6-5：雙重與多重巢狀迴圈（時鐘模型與維度展開） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_5.py
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

def auto_grade_unit_6_5():
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

    # 取得 IPython 執行歷史（若在 Colab 環境）
    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 6-5-1 雙重迴圈心智模型：時鐘的分針與時針 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-1", "填空題", "雙重集訓週數與天數走訪 (for week, for day)", 4,
         lambda g: (
             (True, "雙重迴圈外層週數與內層天數填寫正確！")
             if (g.get("total_training_days") == 6 or
                 ("forweekinrange" in history_clean and "fordayinrange" in history_clean))
             else (False, "請在 6-5-1 填空題填入外層 for week 與內層 for day 迴圈！")
         )),

        ("6-5-1", "練習題", "巡邏大樓房間二維走訪 (F{floor}-R{room})", 4,
         lambda g: (
             (True, "大樓樓層與房間雙層巡查累加輸出正確！")
             if (("inspected_count" in g or "inspected_count" in history_str) and
                 ("F{floor}-R{room}" in history_str or "floor" in history_str and "room" in history_str))
             else (False, "請走訪 total_floors 與 rooms_per_floor，累加 inspected_count！")
         )),

        ("6-5-1", "挑戰題", "投籃訓練條件得分結算 (total_shots = 15, score = 16)", 5,
         lambda g: (
             (True, "雙重迴圈模擬投籃條件判定與得分累加成功！")
             if (("total_shots" in g or "total_shots" in history_str) and
                 ("score" in g or "score" in history_str) and
                 ("(set_idx + shot_idx) % 2 == 0" in history_str or "16" in history_str or g.get("score") == 16))
             else (False, "請模擬 3 組各 5 球投籃，偶數得分累加，驗證 score = 16！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-2 變數命名鐵律與常見命名天坑（遮蔽同名 Bug） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-2", "填空題", "內層變數獨立命名避免衝突 (for j in range(1, 4))", 4,
         lambda g: (
             (True, "內層計數器獨立命名 j 填寫正確，9 組配對無誤！")
             if (g.get("pair_count") == 9 or "forjinrange" in history_clean or "({i}, {j})" in history_str)
             else (False, "請在 6-5-2 填空題將內層變數更正為 j！")
         )),

        ("6-5-2", "練習題", "二維座標乘積合格篩選 (qualified_cells)", 4,
         lambda g: (
             (True, "二維網格座標乘積門檻篩選統計正確！")
             if (("qualified_cells" in g or "qualified_cells" in history_str) and
                 ("product >= threshold" in history_str or "qualified_cells +=" in history_str))
             else (False, "請走訪 r 與 c，統計 product >= threshold 的合格格子數！")
         )),

        ("6-5-2", "挑戰題", "西洋棋盤黑白染色統計 (white_count = 10, black_count = 10)", 5,
         lambda g: (
             (True, "棋盤黑白染色雙重走訪與總格數驗證成功！")
             if (("white_count" in g or "white_count" in history_str) and
                 ("black_count" in g or "black_count" in history_str) and
                 ("(r + c) % 2 == 0" in history_str or "(r+c)%2==0" in history_clean))
             else (False, "請以 (r + c) % 2 == 0 分類統計 4x5 棋盤之白格與黑格！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-3 end 參數與 print() 換行節奏控制（矩陣視覺化排版） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-3", "填空題", "矩陣水平輸出與列尾換行 (end=' ', print())", 4,
         lambda g: (
             (True, "矩陣 end=' ' 水平排版與列尾換行填寫正確！")
             if ('end=" "' in history_str or "end=' '" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-3 填空題填入 end=' ' 以及列尾換行 print()！")
         )),

        ("6-5-3", "練習題", "乘積矩陣排版與總和累加 (sum_val = 18)", 4,
         lambda g: (
             (True, "乘積矩陣排版與數值總和累加輸出正確！")
             if (("sum_val" in g or "sum_val" in history_str) and
                 ("18" in history_str or g.get("sum_val") == 18))
             else (False, "請排版 r * c 矩陣並累加數值總和至 sum_val！")
         )),

        ("6-5-3", "挑戰題", "斑馬線條紋矩陣排版 (hash_count = 12)", 5,
         lambda g: (
             (True, "奇偶欄位交錯斑馬線條紋矩陣輸出成功！")
             if (g.get("hash_count") == 12 or
                 (("hash_count" in g or "hash_count" in history_str) and
                  ("12" in history_str or ("#" in history_str and "-" in history_str))))
             else (False, "請依欄位奇偶排版 # 與 -，統計 4x5 矩陣中井字號為 12！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-4 九九乘法表排版藝術與對齊格式化 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-4", "填空題", "乘法表內層邊界與列尾換行 (range(1, 6), print())", 4,
         lambda g: (
             (True, "九九乘法表內層 range(1, 6) 與換行填寫精確！")
             if ("range(1,6)" in history_clean or "range(1, 6)" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-4 填空題填入內層 1 到 6 與換行指令 print()！")
         )),

        ("6-5-4", "練習題", "取餘數矩陣排版與整除次數 (zero_count = 5)", 4,
         lambda g: (
             (True, "模運算矩陣排版與整除個數 (zero_count = 5) 正確！")
             if (g.get("zero_count") == 5 or
                 (("zero_count" in g or "zero_count" in history_str) and
                  ("5" in history_str or "a % b" in history_str or "a%b" in history_clean)))
             else (False, "請排版 a % b 矩陣並統計餘數為 0 的整除次數！")
         )),

        ("6-5-4", "挑戰題", "加法方陣與主對角線和 (total = 80, diag_sum = 20)", 5,
         lambda g: (
             (True, "方陣全元素總和 (80) 與主對角線和 (20) 計算成功！")
             if ((g.get("total_matrix_sum") == 80 and g.get("diag_sum") == 20) or
                 (("total_matrix_sum" in g or "total_matrix_sum" in history_str) and
                  ("diag_sum" in g or "diag_sum" in history_str) and
                  ("80" in history_str or "20" in history_str or "i == j" in history_str)))
             else (False, "請計算 4x4 加法方陣全元素總和與 i == j 對角線和！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-5 內層邊界依賴外層變數（三角形與階梯模型） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-5", "填空題", "同數階梯內層上限與換行 (range(1, row + 1), print())", 4,
         lambda g: (
             (True, "同數階梯內層依賴 row 與換行填寫正確！")
             if ("row+1" in history_clean or "row + 1" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-5 填空題填入 row + 1 與換行 print()！")
         )),

        ("6-5-5", "練習題", "階梯數列總和計算 (grand_total = 10)", 4,
         lambda g: (
             (True, "階梯數列雙重走訪累加總和 (10) 輸出正確！")
             if (("grand_total" in g or "grand_total" in history_str) and
                 ("10" in history_str or g.get("grand_total") == 10))
             else (False, "請使用階梯雙重迴圈累加出現的所有數字至 grand_total！")
         )),

        ("6-5-5", "挑戰題", "倒階梯遞減走訪與奇數統計 (odd_count = 9)", 4,
         lambda g: (
             (True, "倒階梯遞減圖形排版與奇數次數統計 (9) 成功！")
             if (("odd_count" in g or "odd_count" in history_str) and
                 ("9" in history_str or g.get("odd_count") == 9))
             else (False, "請排版倒階梯圖形並統計奇數出現總次數 (9 次)！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-6 雙重迴圈的雙變數枚舉（窮舉法初步） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-6", "填空題", "和為 10 且 a < b 防重複枚舉 (range(a + 1, 10))", 4,
         lambda g: (
             (True, "防止重複枚舉之 b 起點 a + 1 填寫正確！")
             if ("a+1" in history_clean or "a + 1" in history_str)
             else (False, "請在 6-5-6 填空題填入內層起點 a + 1！")
         )),

        ("6-5-6", "練習題", "雞兔同籠雙變數窮舉 (chickens = 23, rabbits = 12)", 4,
         lambda g: (
             (True, "雞兔同籠窮舉命中解 (23 雞 12 兔) 正確！")
             if (("chickens" in g or "chickens" in history_str) and
                 ("rabbits" in g or "rabbits" in history_str) and
                 ("23" in history_str and "12" in history_str))
             else (False, "請以雙重迴圈窮舉雞兔數量，求出 23 雞與 12 兔！")
         )),

        ("6-5-6", "挑戰題", "邊長 20 內畢氏三元組枚舉 (pythagorean_count = 6)", 4,
         lambda g: (
             (True, "畢氏三元整數組枚舉統計 (6 組) 成功！")
             if (("pythagorean_count" in g or "pythagorean_count" in history_str) and
                 ("6" in history_str or g.get("pythagorean_count") == 6))
             else (False, "請枚舉 a < b <= 20 找出滿足 a^2 + b^2 = c^2 的 6 組畢氏三元組！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-7 雙重迴圈的中斷控制：旗標變數連鎖跳出 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-7", "填空題", "雙重中斷旗標連鎖跳出 (found = True; break; if found: break)", 4,
         lambda g: (
             (True, "布林旗標更新與外層連鎖 break 填寫精確！")
             if (("found=True" in history_clean or "found = True" in history_str) and
                 ("iffound:break" in history_clean.replace("\n", "") or "if found" in history_str))
             else (False, "請在 6-5-7 填空題填入 found = True、break 以及外層 if found: break！")
         )),

        ("6-5-7", "練習題", "二維搜尋目標和與步數統計 (found 連鎖跳出)", 4,
         lambda g: (
             (True, "二維搜尋目標和連鎖中斷與步數統計正確！")
             if (("steps" in g or "steps" in history_str) and
                 ("found" in g or "found" in history_str) and
                 ("break" in history_str))
             else (False, "請搜尋 a + b == target_sum，記錄 steps 並以旗標連鎖 break！")
         )),

        ("6-5-7", "挑戰題", "半質數拆解密碼鎖 (77 = 7 * 11 旗標連鎖中斷)", 4,
         lambda g: (
             (True, "半質數分解 (77 = 7 * 11) 雙重迴圈旗標鎖定成功！")
             if (("ans_p" in g or "ans_p" in history_str) and
                 ("ans_q" in g or "ans_q" in history_str) and
                 ("7" in history_str and "11" in history_str))
             else (False, "請以雙重迴圈枚舉 p * q == 77，找到 7 與 11 並連鎖 break！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-8 三重與多重巢狀迴圈：空間維度展開與效能警示 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-8", "填空題", "三重座標盒子枚舉次數 (total_runs = 24)", 4,
         lambda g: (
             (True, "三重迴圈層次與執行次數 (24 次) 填寫正確！")
             if (g.get("total_runs") == 24 or "range(1, 4)" in history_str or "range(1, 5)" in history_str)
             else (False, "請在 6-5-8 填空題填入中層 1 到 4 與內層 1 到 5 範圍！")
         )),

        ("6-5-8", "練習題", "三角形三邊長整數解枚舉 (valid_triangles)", 4,
         lambda g: (
             (True, "周長 P 之三角形不等式三重枚舉輸出正確！")
             if (("valid_triangles" in g or "valid_triangles" in history_str) and
                 ("a + b > c" in history_str or "a+b>c" in history_clean))
             else (False, "請三重枚舉 a, b, c，統計滿足 a + b + c == P 且 a + b > c 的個數！")
         )),

        ("6-5-8", "挑戰題", "湊 25 元零錢硬幣枚舉 (coin_ways = 12)", 4,
         lambda g: (
             (True, "硬幣面額湊錢方案枚舉 (12 種) 成功！")
             if (("coin_ways" in g or "coin_ways" in history_str) and
                 ("12" in history_str or g.get("coin_ways") == 12))
             else (False, "請枚舉 10元、5元、1元湊出 25 元，方案數為 12 種！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-5：雙重與多重巢狀迴圈 —— 自動評分報告")
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

        print(f"{icon} [{uid} {qtype}] {name:<36} ➔ {status}")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通雙重與多重巢狀迴圈之時鐘模型，二維矩陣排版與旗標連鎖跳出登峰造極！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，變數命名嚴謹，階梯依賴與雙變數窮舉架構清晰！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調排版換行或連鎖旗標！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄（在 Colab 環境中產生評分紀錄檔）
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "6-5",
        "unit_title": "雙重與多重巢狀迴圈（時鐘模型與維度展開）",
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
        log_filename = "score_log_unit_6_5.json"
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
auto_grade_unit_6_5()
