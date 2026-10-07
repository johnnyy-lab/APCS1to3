# ==============================================================================
# 🧪 《PythAPCS123》單元 7-3：f-string 格式化與排版對齊 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_3.py
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

def auto_grade_unit_7_3():
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
        # 7-3-1 f-string 核心語法與大括號插值 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-3-1", "填空題", "變數插值填空 (f\"{player} 剩下 {hp} 點生命\")", 6,
         lambda g: (
             (True, "f-string 變數插值填寫正確！")
             if ("f\"" in history_str or "f'" in history_str) and
                ("{player}" in history_str and "{hp}" in history_str and "剩下" in history_str)
             else (False, "請在 7-3-1 填空題空格填入 {player} 與 {hp}！")
         )),

        ("7-3-1", "練習題", "同學成績單句子格式化 (同學 小華 考了 88 分)", 9,
         lambda g: (
             (True, "姓名與分數 f-string 句子輸出格式正確！")
             if ("同學" in history_str and "考了" in history_str and "分" in history_str and
                 ("f\"" in history_str or "f'" in history_str or "name" in history_str)) or
                ("同學 小華 考了 88 分" in history_str or "同學 阿凱 考了 100 分" in history_str)
             else (False, "請使用 f-string 輸出「同學 [name] 考了 [score] 分」！")
         )),

        ("7-3-1", "挑戰題", "自我介紹車票排版 (class_name, seat, nickname)", 5,
         lambda g: (
             (True, "班級、座號與暱稱 f-string 車票印出成功！")
             if ("f\"" in history_str or "f'" in history_str) and
                ("class_name" in history_str or "seat" in history_str or "nickname" in history_str)
             else (False, "請使用單一 f-string 印出包含班級、座號與暱稱的字串！")
         )),

        # ----------------------------------------------------------------------
        # 7-3-2 大括號內直接嵌入表達式運算 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-3-2", "填空題", "大括號嵌入相減算式 (f\"差是 {a - b}\")", 6,
         lambda g: (
             (True, "大括號內嵌入減法運算子 a - b 正確！")
             if ("{a - b}" in history_str or "{a-b}" in history_clean) and "差是" in history_str
             else (False, "請在 7-3-2 填空題大括號內填入 a - b！")
         )),

        ("7-3-2", "練習題", "計算總價並以 round 留一位 (總價是 結果 元)", 9,
         lambda g: (
             (True, "大括號內乘法計算與 round 四捨五入輸出正確！")
             if ("總價是" in history_str and "元" in history_str and
                 ("unit_price" in history_str or "round(" in history_str or "50.0" in history_str or "6.5" in history_str))
             else (False, "請在 f-string 大括號內嵌入 round(unit_price * quantity, 1) 印出總價！")
         )),

        ("7-3-2", "挑戰題", "三科分數與平均嵌入算式", 5,
         lambda g: (
             (True, "三科成績與平均運算式嵌入正確！")
             if ("f\"" in history_str or "f'" in history_str) and
                ("chinese" in history_str or "math" in history_str or "english" in history_str or "round" in history_str)
             else (False, "請在一個 f-string 內印出三科分數及在大括號內計算平均！")
         )),

        # ----------------------------------------------------------------------
        # 7-3-3 浮點數精度控制：{:.2f} 格式化 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-3-3", "填空題", "浮點數固定兩位小數格式 (:2f / :.2f)", 6,
         lambda g: (
             (True, "格式化規格 :.2f 填寫正確！")
             if (":.2f" in history_str or ":.2f}" in history_clean or ":.2f}" in history_str)
             else (False, "請在 7-3-3 填空題冒號後填入 .2f！")
         )),

        ("7-3-3", "練習題", "除法精確兩位小數 (num_x / num_y: {:.2f})", 9,
         lambda g: (
             (True, "除法計算與 {:.2f} 兩位小數輸出正確！")
             if (":.2f" in history_str and ("num_x" in history_str or "/" in history_str)) or
                ("3.33" in history_str or "3.50" in history_str)
             else (False, "請讀入或定義 num_x 與 num_y，以 {:.2f} 格式印出除法結果！")
         )),

        ("7-3-3", "挑戰題", "台幣換美金匯率換算精確兩位小數", 5,
         lambda g: (
             (True, "匯率換算除法與 {:.2f} 美金格式輸出正確！")
             if (":.2f" in history_str and ("exchange_rate" in history_str or "ntd_amount" in history_str or "31.85" in history_str)) or
                ("ntd_amount" in g and "exchange_rate" in g)
             else (False, "請以單斜線除法換算美金，並以 {:.2f} 印出包含兩位小數的美金金額！")
         )),

        # ----------------------------------------------------------------------
        # 7-3-4 整數寬度與靠右對齊：{:4d} (共 20 分)
        # ----------------------------------------------------------------------
        ("7-3-4", "填空題", "整數寬度 4 格格式化 (:4d)", 6,
         lambda g: (
             (True, "整數寬度格式化 :4d 填寫正確！")
             if (":4d" in history_str or ":4d}" in history_clean)
             else (False, "請在 7-3-4 填空題冒號後填入 4d！")
         )),

        ("7-3-4", "練習題", "變數 n 之 {:4d} 排版輸出", 9,
         lambda g: (
             (True, "變數 n 以 {:4d} 寬度靠右對齊輸出正確！")
             if (":4d" in history_str and ("n" in history_str or "print" in history_str)) or
                ("n" in g and ":4d" in history_str)
             else (False, "請使用 f-string 配合 {:4d} 格式印出變數 n！")
         )),

        ("7-3-4", "挑戰題", "三行數字 {:5d} 個位數直排對齊", 5,
         lambda g: (
             (True, "三行整數 {:5d} 對齊排版成功！")
             if (":5d" in history_str and ("1" in history_str and "12" in history_str and "123" in history_str))
             else (False, "請分別用三行 print 以 {:5d} 印出 1、12 與 123！")
         )),

        # ----------------------------------------------------------------------
        # 7-3-5 f-string 常見陷阱與引號使用 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-3-5", "填空題", "引號前方補齊 f 標記 (f\"城市：{city}\")", 6,
         lambda g: (
             (True, "成功補齊 f 前綴標記！")
             if ('f"城市：{city}"' in history_clean or "f'城市：{city}'" in history_clean or
                 'f"城市:{city}"' in history_clean or 'f"城市：' in history_str)
             else (False, "請在 7-3-5 填空題字串前綴補上 f！")
         )),

        ("7-3-5", "練習題", "輸出「答案是 [answer]」f-string", 9,
         lambda g: (
             (True, "答案標籤與變數插值 f-string 輸出正確！")
             if ("答案是" in history_str and ("{answer}" in history_str or "answer" in history_str)) or
                ("答案是 42" in history_str or "答案是 7" in history_str)
             else (False, "請使用 f-string 印出「答案是 」加上 answer 的值！")
         )),

        ("7-3-5", "挑戰題", "外雙內單引號 message 包裹插值", 5,
         lambda g: (
             (True, "雙引號外層嵌入單引號變數 message 正確！")
             if (("speaker" in history_str or "老師" in history_str) and
                 ("message" in history_str or "記得存檔" in history_str) and
                 ("f\"" in history_str or "f'" in history_str))
             else (False, "請在外層雙引號 f-string 中，以單引號包裹 {message} 並正確印出！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-3 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 f-string 語法、運算式嵌入、{:.2f} 精度與 {:4d} 對齊排版，字串格式化宗師！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，f-string 大括號運算與格式化參數運用純熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調 f 前綴與對齊規格！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-3",
        "unit_title": "f-string 格式化與排版對齊",
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
        log_filename = "score_log_unit_7_3.json"
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
auto_grade_unit_7_3()
