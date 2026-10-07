# ==============================================================================
# 🧪 《PythAPCS123》單元 8-5：串列走訪模式與成員存在性 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_5.py
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

def auto_grade_unit_8_5():
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
        # 8-5-1 直接元素走訪：for item in my_list: (共 20 分)
        # ----------------------------------------------------------------------
        ("8-5-1", "填空題", "直接元素走訪統計及格人數 (for num in numbers)", 6,
         lambda g: (
             (True, "直接元素走訪 for num in numbers 正確！")
             if ("for num in numbers:" in history_str or "fornuminnumbers:" in history_clean) and
                ("pass_count += 1" in history_str or "pass_count+=1" in history_clean)
             else (False, "請在 8-5-1 填空題填入 in 與累加數值 1！")
         )),

        ("8-5-1", "練習題", "問候語依序走訪輸出 (Hello, <名字>!)", 9,
         lambda g: (
             (True, "姓名串列走訪與問候語格式印出正確！")
             if ("Hello," in history_str and "for" in history_str and "names" in history_str) or
                ("Hello, Alice!" in history_str and "Hello, Bob!" in history_str)
             else (False, "請走訪 names 串列，為每個人印出 Hello, <名字>!！")
         )),

        ("8-5-1", "挑戰題", "一週步數資料走訪統計達標天數 (>= 10000 步)", 5,
         lambda g: (
             (True, "步數串列走訪與 >= 10000 條件達標天數統計正確！")
             if (">= 10000" in history_str or ">=10000" in history_clean) and "for" in history_str
             else (False, "請走訪 daily_steps 串列，統計 >= 10000 步的達標天數並印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-5-2 索引走訪與元素更新：for i in range(len(my_list)): (共 20 分)
        # ----------------------------------------------------------------------
        ("8-5-2", "填空題", "索引走訪負數轉正數 (range(len(nums)) 與 -nums[i])", 6,
         lambda g: (
             (True, "range(len(nums)) 索引走訪與就地更新正確！")
             if ("range(len(nums))" in history_clean and ("-nums[i]" in history_clean))
             else (False, "請在 8-5-2 填空題空格填入 len 與索引 i！")
         )),

        ("8-5-2", "練習題", "整數串列平方就地更新 (values[i] = values[i] ** 2)", 9,
         lambda g: (
             (True, "平方就地替換與完整串列輸出正確！")
             if ("range(len(values))" in history_clean and ("** 2" in history_str or "**2" in history_clean)) or
                ("[1, 4, 9, 16, 25]" in history_str or "[100, 9, 0]" in history_str)
             else (False, "請使用 range(len(values)) 將每個數就地替換為平方並印出！")
         )),

        ("8-5-2", "挑戰題", "週年慶折扣活動 (滿千九折 price * 9 // 10 就地更新)", 5,
         lambda g: (
             (True, "滿千折扣判斷與索引就地更新正確！")
             if (">= 1000" in history_str or ">=1000" in history_clean) and
                ("* 9 // 10" in history_str or "*9//10" in history_clean)
             else (False, "請使用索引走訪法，將 >= 1000 的價格替換為 9 折並輸出！")
         )),

        # ----------------------------------------------------------------------
        # 8-5-3 雙軌資訊走訪：同時掌握索引與數值 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-5-3", "填空題", "偶數索引位置與數值雙重判定 (% 2 == 0)", 6,
         lambda g: (
             (True, "偶數判定與雙軌位置顯示完全正確！")
             if ("% 2 == 0" in history_str or "%2==0" in history_clean) and
                ("{i}" in history_str or "{data[i]}" in history_str or "索引位置" in history_str)
             else (False, "請在 8-5-3 填空題空格填入 0 與索引變數 i！")
         )),

        ("8-5-3", "練習題", "一週氣溫天數格式輸出 (第 i+1 天氣溫為 Y 度)", 9,
         lambda g: (
             (True, "天數 (i+1) 與氣溫 temps[i] 雙軌格式印出正確！")
             if ("第" in history_str and "天氣溫為" in history_str and "度" in history_str and
                 ("i + 1" in history_str or "i+1" in history_clean or "range(" in history_str)) or
                ("第 1 天氣溫為 26 度" in history_str)
             else (False, "請使用迴圈走訪依序印出「第 X 天氣溫為 Y 度」（天數由 1 起算）！")
         )),

        ("8-5-3", "挑戰題", "超重貨物箱號與超重公斤數查詢 (箱號 i+1, weight-50)", 5,
         lambda g: (
             (True, "超重貨物判定與箱號 (i+1) 輸出正確！")
             if ("> 50" in history_str or ">50" in history_clean) and
                ("- 50" in history_str or "-50" in history_clean or "i + 1" in history_str or "i+1" in history_clean)
             else (False, "請走訪找出 > 50 的箱號（索引+1）與超重數（weight-50）並印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-5-4 成員查詢與存在性判斷：in 與 not in (共 20 分)
        # ----------------------------------------------------------------------
        ("8-5-4", "填空題", "成員運算子 in 黑名單判定", 6,
         lambda g: (
             (True, "使用 in 運算子進行黑名單檔案查詢正確！")
             if ("filename in blacklist" in history_str or "filename in blacklist" in history_clean or
                 "if filename in blacklist:" in history_str)
             else (False, "請在 8-5-4 填空題填入成員運算子 in！")
         )),

        ("8-5-4", "練習題", "帳號註冊重複查詢 (if new_user in registered_users)", 9,
         lambda g: (
             (True, "帳號重複存在性查詢分支輸出正確！")
             if ("in registered_users" in history_str and ("帳號已被使用" in history_str or "帳號可用" in history_str)) or
                ("帳號已被使用" in history_str and "帳號可用" in history_str)
             else (False, "請判斷 new_user 是否在 registered_users 中，輸出已被使用或可用！")
         )),

        ("8-5-4", "挑戰題", "購物車防重複加入商品 (in 檢查與 append)", 5,
         lambda g: (
             (True, "購物車防重複檢驗與 append 加入邏輯正確！")
             if ("in cart" in history_str and (".append(" in history_str or "重複" in history_str))
             else (False, "請檢查商品是否已在購物車中，若在提示重複，不在則 append 加入！")
         )),

        # ----------------------------------------------------------------------
        # 8-5-5 定位元素索引：index() 方法與安全查詢模式 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-5-5", "填空題", "安全查詢樣式 in 檢查搭配 index() (target in queue)", 6,
         lambda g: (
             (True, "先 in 把關後呼叫 .index() 安全查詢成功！")
             if ("target in queue" in history_str or "targetinqueue" in history_clean) and
                ("queue.index(target)" in history_clean)
             else (False, "請在 8-5-5 填空題空格填入 in 與方法名稱 index！")
         )),

        ("8-5-5", "練習題", "安全查詢樣板 (目標位於索引 X / 查無此數值)", 9,
         lambda g: (
             (True, "安全定位索引與查無數值分支輸出正確！")
             if (".index(" in history_str and ("目標位於索引" in history_str or "查無此數值" in history_str)) or
                ("目標位於索引 2" in history_str or "查無此數值" in history_str)
             else (False, "請以安全查詢樣板查詢 target 索引，輸出目標位置或查無此數值！")
         )),

        ("8-5-5", "挑戰題", "賽跑名次查詢 (美美 名次為 index + 1)", 5,
         lambda g: (
             (True, "選手名次安全定位與查無紀錄邏輯正確！")
             if ("runners.index(" in history_clean or ".index(" in history_str) and
                ("名" in history_str or "完賽紀錄" in history_str or "+ 1" in history_str)
             else (False, "請安全查詢選手是否在名單中，在則輸出名次（index+1）否則輸出查無紀錄！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 8-5 學習成效自動評分檢驗報告")
    print(f"👤 學員姓名：{combined_display_name}")
    print(f"⏰ 檢驗時間：{timestamp_str}")
    print("=" * 72)

    for uid, qtype, name, pts, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception as e:
            ok, msg = False, f"評分邏輯執行異常：{e}"

        if ok:
            item_score = pts
            total_score += pts
            pass_count += 1
            print(f"✅ [{uid}] {qtype} - {name} ({pts}/{pts} 分)")
        else:
            item_score = 0
            print(f"❌ [{uid}] {qtype} - {name} (0/{pts} 分)")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通直接走訪、索引就地更新、雙軌走訪、in 成員查詢與 safe index() 樣板，走訪專家！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，串列走訪模式與安全查詢掌握純熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調 range 邊界與安全查詢順序！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "8-5",
        "unit_title": "串列走訪模式與成員存在性",
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
        log_filename = "score_log_unit_8_5.json"
        with open(log_filename, "w", encoding="utf-8") as lf:
            json.dump(log_data, lf, ensure_ascii=False, indent=2)
        print(f"💾 [本地存檔] 評分紀錄檔已生成：{log_filename}（可於左側檔案區下載備查）")
    except Exception as e:
        print(f"⚠️ 本地日誌寫入提示：{e}")

    # --------------------------------------------------------------------------
    # 📡 2. 雲端後台成績記錄
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
auto_grade_unit_8_5()
