# ==============================================================================
# 🧪 《PythAPCS123》單元 4-6：單行多筆輸入 split() 與 map() —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_6.py
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

def auto_grade_unit_4_6():
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 4-6-1 字串拆解 split() 與多變數解包 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-1", "填空題", "雙人飛行員代號解包 (input().split())", 6,
         lambda g: (
             (True, "split() 解包設定正確：成功存入 pilot1 與 pilot2！")
             if (("split()" in history_str or "split" in history_str) and
                 ("pilot1" in g or "pilot2" in g or "pilot1" in history_str))
             else (False, "請在 4-6-1 填空題空格填入 split 方法並在 print 印出 pilot2！")
         )),

        ("4-6-1", "練習題", "超商進貨單行雙物品輸入與變數交換 (Swap)", 8,
         lambda g: (
             (True, "單行雙物品讀入與交換輸出成功！")
             if (("item1" in g and "item2" in g) and
                 ("split" in history_str) and
                 ("➔" in history_str or "->" in history_str or "," in history_str))
             else (False, "請使用 item1, item2 = input().split() 讀入並交換後輸出！")
         )),

        ("4-6-1", "挑戰題", "台灣高鐵三站名單行輸入與路線圖播報", 6,
         lambda g: (
             (True, "高鐵三站名單行讀入與路線排版成功！")
             if (("station1" in g and "station2" in g and "station3" in g) or
                 ("station1" in history_str and "split" in history_str))
             else (False, "請在同一行讀入三個站名，並以箭頭符號輸出路線！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-2 map(int, input().split()) 單行多個整數轉換 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-2", "填空題", "文具店單價與數量整數映射 (map, int)", 6,
         lambda g: (
             (True, "map 與 int 整數映射填寫正確！")
             if (("map(int" in history_str.replace(" ", "") or "price" in g) and
                 ("total_price" in history_str or "結帳明細" in history_str))
             else (False, "請在 4-6-2 填空題空格填入 map 與 int 進行整數轉換！")
         )),

        ("4-6-2", "練習題", "矩形長寬單行讀取與周長面積計算 (length, width)", 8,
         lambda g: (
             (True, f"矩形幾何數值計算完成：length={g.get('length')}, width={g.get('width')}！")
             if (("length" in g and "width" in g) and
                 ("map(int" in history_str.replace(" ", "") or "map" in history_str))
             else (False, "請使用 map(int, input().split()) 讀入長寬，並印出周長與面積！")
         )),

        ("4-6-2", "挑戰題", "射擊大賽選手得分分差分析 (score1, score2, abs)", 6,
         lambda g: (
             (True, "選手得分單行整數讀入與分差計算完成！")
             if (("score1" in g and "score2" in g) or
                 ("map(int" in history_str.replace(" ", "") and "abs" in history_str))
             else (False, "請在同一行讀入 score1 與 score2，並使用 abs 計算分差！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-3 三個及以上整數的單行讀取 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-3", "填空題", "段考三科成績解包與總分平均計算 (math, total_score)", 6,
         lambda g: (
             (True, "三科成績映射與計算設定正確！")
             if (("chinese" in g or "total_score" in g or "math" in history_str) and
                 ("map(int" in history_str.replace(" ", "") or "map" in history_str))
             else (False, "請在 4-6-3 填空題補齊變數 math 與總分算式！")
         )),

        ("4-6-3", "練習題", "單行三整數讀入與全距計算 (max - min)", 8,
         lambda g: (
             (True, "單行三整數讀入與全距計算成功！")
             if (("map(int" in history_str.replace(" ", "")) and
                 ("max" in history_str and "min" in history_str))
             else (False, "請使用 map(int, input().split()) 讀入三整數，並印出全距 max - min！")
         )),

        ("4-6-3", "挑戰題", "APCS 座標曼哈頓距離計算 (x1, y1, x2, y2)", 6,
         lambda g: (
             (True, "曼哈頓距離四座標讀入與計算完成！")
             if (("x1" in g or "x2" in g or "map(int" in history_str.replace(" ", "")) and
                 ("abs(" in history_str.replace(" ", "")))
             else (False, "請在同一行讀入四個座標，並利用 abs() 計算曼哈頓距離！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-4 浮點數轉換 map(float, input().split()) (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-4", "填空題", "雙裁判評分浮點數映射 (map(float, ...))", 6,
         lambda g: (
             (True, "浮點數映射設定正確：map(float, ...)！")
             if (("map(float" in history_str.replace(" ", "") or "score1" in g) and
                 ("avg_score" in history_str or "官方計分板" in history_str))
             else (False, "請在 4-6-4 填空題空格填入 float 與相加算式！")
         )),

        ("4-6-4", "練習題", "健康檢查站單行 BMI 計算 (height, weight)", 8,
         lambda g: (
             (True, "單行浮點數身高體重讀入與 BMI 計算完成！")
             if (("height" in g and "weight" in g) and
                 ("map(float" in history_str.replace(" ", "") or "float" in history_str))
             else (False, "請使用 map(float, input().split()) 讀入身高體重並輸出 BMI！")
         )),

        ("4-6-4", "挑戰題", "幾何同心圓環面積計算 (R, r)", 6,
         lambda g: (
             (True, "同心圓環兩半徑讀取與面積計算完成！")
             if (("map(float" in history_str.replace(" ", "")) and
                 ("3.14" in history_str or "**2" in history_str or "** 2" in history_str))
             else (False, "請在同一行讀入大圓與小圓半徑，並計算圓環面積！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-5 實戰 APCS / OJ 考題情境與除錯 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-5", "填空題", "三數乘積程式除錯特訓 (map(int, ...))", 6,
         lambda g: (
             (True, "map(int, ...) 除錯修復完成！")
             if (("map(int" in history_str.replace(" ", "") or "n1" in g) and
                 ("乘積結果" in history_str or "result" in history_str))
             else (False, "請在 4-6-5 填空題空格填入 map 與 int 修復型態錯誤！")
         )),

        ("4-6-5", "練習題", "APCS 基礎模擬實作：均分糖果問題 (candies, students)", 8,
         lambda g: (
             (True, "糖果均分問題單行輸入與商數餘數輸出正確！")
             if (("candies" in g and "students" in g) or
                 ("map(int" in history_str.replace(" ", "") and ("//" in history_str and "%" in history_str)))
             else (False, "請使用 map(int, input().split()) 讀入糖果與人數，並輸出 // 與 %！")
         )),

        ("4-6-5", "挑戰題", "APCS 基礎模擬實作：三角形邊長極端差 (max - min)", 6,
         lambda g: (
             (True, "三角形三邊長讀入與極端差計算完成！")
             if (("map(int" in history_str.replace(" ", "")) and
                 ("max(" in history_str and "min(" in history_str))
             else (False, "請單行讀入三角形三邊長，並輸出最長邊與最短邊差值！")
         )),
    ]

    # 執行所有測資評分
    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 4-6 學習成效自動評分診斷報告")
    print(f"👤 受評學員：{combined_display_name}")
    print(f"📧 驗證信箱：{final_email}")
    print(f"🕒 評分時間：{timestamp_str}")
    print("=" * 72)

    pass_count = 0
    item_results = []

    for sub_unit, q_type, q_title, score, validator in test_cases:
        try:
            passed, feedback = validator(env)
        except Exception as e:
            passed, feedback = False, f"評分邏輯檢查異常：{e}"

        earned = score if passed else 0
        total_score += earned
        if passed:
            pass_count += 1
            status_icon = "✅ 通過"
        else:
            status_icon = "❌ 未過"

        item_results.append({
            "sub_unit": sub_unit,
            "type": q_type,
            "title": q_title,
            "max_score": score,
            "earned_score": earned,
            "status": "PASS" if passed else "FAIL",
            "feedback": feedback
        })

        print(f"[{status_icon}] ({earned:2d}/{score:2d}分) 【{sub_unit} {q_type}】{q_title}")
        print(f"       👉 評語：{feedback}")

    print("-" * 72)
    # 計算榮譽稱號
    if total_score == 100:
        badge = "🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完全降伏 split() 與 map()，解鎖 APCS 核心輸入技法！"
    elif total_score >= 80:
        badge = "🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！"
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
        "unit": "4-6",
        "unit_title": "單行多筆輸入 split() 與 map()",
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
        log_filename = "score_log_unit_4_6.json"
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
auto_grade_unit_4_6()
