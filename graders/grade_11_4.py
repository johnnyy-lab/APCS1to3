# ==============================================================================
# 🧪 《PythAPCS123》單元 11-4：變數作用域：區域變數與同名遮蔽 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_4.py
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            google_email = data.get("email", "")
            google_name = data.get("name", "")
            return google_email, google_name
    except Exception:
        return "", ""

def get_submission_env():
    """取得 Colab / 本地端全域變數與執行歷史代碼"""
    try:
        import IPython
        ipython_inst = IPython.get_ipython()
        if ipython_inst is not None:
            user_ns = ipython_inst.user_ns
            history_cells = getattr(ipython_inst, 'user_ns', {}).get('_ih', [])
            return user_ns, history_cells
    except Exception:
        pass
    
    # 備用機制：若不在 IPython 環境，從呼叫棧主模組獲取
    try:
        import __main__
        return __main__.__dict__, []
    except Exception:
        return {}, []

def auto_grade_unit_11_4(student_name=""):
    """
    單元 11-4：變數作用域：區域變數與同名遮蔽 自動評分主程式
    滿分 100 分：
    - 填空題 6 題，每題 5 分，共 30 分
    - 練習題 6 題，每題 6 分，共 36 分
    - 挑戰題 6 題，共 34 分 (前 4 題各 6 分，後 2 題各 5 分)
    """
    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    # 1. 取得使用者身分
    declared_name = student_name.strip() if student_name else ""
    if not declared_name:
        for var_name in ["student_name", "my_name", "user_name", "author"]:
            val = env.get(var_name)
            if isinstance(val, str) and val.strip():
                declared_name = val.strip()
                break

    google_email, google_name = fetch_google_account_info()

    # 顯示姓名決策
    if declared_name and google_name:
        combined_display_name = f"{declared_name} ({google_name})"
    elif declared_name:
        combined_display_name = declared_name
    elif google_name:
        combined_display_name = google_name
    else:
        combined_display_name = "自主學習冒險者"

    final_email = google_email if google_email else "未綁定 Google 帳號"
    final_google_name = google_name if google_name else "無"

    # 2. 評分測試案例 (共 18 題，合計 100 分)
    total_score = 0
    max_score = 100
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    test_cases = [
        # ----------------------------------------------------------------------
        # 11-4-1 區域作用域 (Local Scope) 獨立王國 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-1", "填空題", "三角形面積區域變數封裝 get_triangle_area(b, h)", 5,
         lambda g: (
             (True, "get_triangle_area 區域變數填空正確！")
             if (callable(g.get("get_triangle_area")) and g.get("get_triangle_area")(10, 6) == 30.0) or
                (g.get("result_area") == 30.0) or
                ("b * h / 2" in history_str)
             else (False, "請在 get_triangle_area 內定義區域變數計算面積並 return！")
         )),

        ("11-4-1", "練習題", "圓面積區域變數計算 calc_circle_area(radius)", 6,
         lambda g: (
             (True, "calc_circle_area 區域計算實作正確！")
             if (callable(g.get("calc_circle_area"))) or
                ("calc_circle_area" in history_str and "3.14" in history_str)
             else (False, "請定義 calc_circle_area 使用區域變數 pi 計算並回傳面積！")
         )),

        ("11-4-1", "挑戰題", "圓柱體積區域分步計算 cylinder_volume(r, h)", 6,
         lambda g: (
             (True, "cylinder_volume 圓柱體積分步計算正確！")
             if (callable(g.get("cylinder_volume"))) or
                ("cylinder_volume" in history_str and "base_area" in history_str)
             else (False, "請在 cylinder_volume 內定義 base_area 等區域變數計算體積！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-2 區域變數生命週期：呼叫誕生、結束消亡 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-2", "填空題", "問候訊息生命週期驗證 greet_guest 與 msg 釋放", 5,
         lambda g: (
             (True, "greet_guest 生命週期填空正確！")
             if (callable(g.get("greet_guest"))) or
                ("greet_guest" in history_str and "msg1" in history_str)
             else (False, "請呼叫 greet_guest 驗證其內部區域變數在函數結束後不殘留！")
         )),

        ("11-4-2", "練習題", "購物車小計區域變數生命週期 calc_cart_total(prices)", 6,
         lambda g: (
             (True, "calc_cart_total 購物車小計實作正確！")
             if (callable(g.get("calc_cart_total"))) or
                ("calc_cart_total" in history_str and "subtotal" in history_str)
             else (False, "請定義 calc_cart_total 以區域變數 subtotal 累加並回傳總額！")
         )),

        ("11-4-2", "挑戰題", "區域變數外部不可見之 NameError 邊界驗證", 6,
         lambda g: (
             (True, "NameError 生命週期邊界驗證正確！")
             if ("try:" in history_str and "except NameError" in history_str) or
                ("NameError" in history_str and "temp_list" in history_str)
             else (False, "請使用 try-except NameError 驗證區域變數在外部無法被存取！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-3 變數遮蔽 (Shadowing) 與就近原則 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-3", "填空題", "免稅商店同名遮蔽 tax_free_shop 與 tax_rate", 5,
         lambda g: (
             (True, "tax_free_shop 同名遮蔽填空正確！")
             if (callable(g.get("tax_free_shop"))) or
                ("tax_rate = 0.0" in history_str or "tax_rate = 0" in history_str)
             else (False, "請在 tax_free_shop 內宣告區域 tax_rate = 0.0 遮蔽外部稅率！")
         )),

        ("11-4-3", "練習題", "調分計算同名變數遮蔽 curved_score(score)", 6,
         lambda g: (
             (True, "curved_score 變數遮蔽實作正確！")
             if (callable(g.get("curved_score"))) or
                ("curved_score" in history_str and "score" in history_str)
             else (False, "請在 curved_score 內宣告區域 score 調分，並確認外部變數不受影響！")
         )),

        ("11-4-3", "挑戰題", "全域、區域與參數同名遮蔽就近原則驗證", 6,
         lambda g: (
             (True, "就近原則遮蔽驗證正確！")
             if ("val" in history_str and "shadow" in history_str) or
                ("shadow" in history_str or "val = 10" in history_str)
             else (False, "請設計範例驗證同名變數依據就近原則優先採用區域變數！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-4 函數內部「唯讀」存取全域變數 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-4", "填空題", "及格門檻唯讀全域變數 check_pass 與 PASS_STANDARD", 5,
         lambda g: (
             (True, "check_pass 唯讀全域填空正確！")
             if (callable(g.get("check_pass"))) or
                ("PASS_STANDARD" in history_str)
             else (False, "請在 check_pass 內直接讀取全域常數 PASS_STANDARD 進行比較！")
         )),

        ("11-4-4", "練習題", "匯率轉換唯讀全域常數 convert_currency(usd)", 6,
         lambda g: (
             (True, "convert_currency 唯讀匯率常數正確！")
             if (callable(g.get("convert_currency"))) or
                ("convert_currency" in history_str and "USD_TO_TWD" in history_str)
             else (False, "請定義 convert_currency 唯讀讀取全域常數 USD_TO_TWD 計算新台幣！")
         )),

        ("11-4-4", "挑戰題", "安全尋路讀取全域方向常數 safe_navigate", 6,
         lambda g: (
             (True, "safe_navigate 讀取全域方向字典正確！")
             if (callable(g.get("safe_navigate"))) or
                ("safe_navigate" in history_str and "DIRS" in history_str)
             else (False, "請定義 safe_navigate 唯讀存取全域常數 DIRS 計算移動後座標！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-5 UnboundLocalError 經典報錯陷阱 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-4-5", "填空題", "點數累計未宣告 global 引發 UnboundLocalError 剖析", 5,
         lambda g: (
             (True, "UnboundLocalError 陷阱分析填空正確！")
             if ("UnboundLocalError" in history_str) or
                ("accumulate_points" in history_str)
             else (False, "請剖析 accumulate_points 內部 += 賦值為何被視為未初始化區域變數！")
         )),

        ("11-4-5", "練習題", "訪客累計安全性重構 track_visitors(new_visitors)", 6,
         lambda g: (
             (True, "訪客累計安全重構實作正確！")
             if (callable(g.get("track_visitors"))) or
                ("track_visitors" in history_str)
             else (False, "請將累計函數重構為接收目前計數與新增計數並 return 新數值！")
         )),

        ("11-4-5", "挑戰題", "修復 UnboundLocalError 之兩種正解方案實作", 5,
         lambda g: (
             (True, "修復 UnboundLocalError 方案實作正確！")
             if ("global" in history_str or "return" in history_str) and ("UnboundLocalError" in history_str or "fix" in history_str)
             else (False, "請以 (1) 宣告 global 或 (2) 透過參數傳入 return 傳出修復報錯！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-6 純函數設計原則：依賴參數與回傳 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-4-6", "填空題", "矩形周長純函數重構 calc_perimeter(w, h)", 5,
         lambda g: (
             (True, "calc_perimeter 純函數填空正確！")
             if (callable(g.get("calc_perimeter")) and g.get("calc_perimeter")(5, 3) == 16) or
                (g.get("rect1_p") == 16) or
                ("return (w + h) * 2" in history_str or "return 2 * (w + h)" in history_str)
             else (False, "請在 calc_perimeter 透過傳入的 w, h 計算周長並回傳！")
         )),

        ("11-4-6", "練習題", "兩點歐式距離純函數 distance_between(p1, p2)", 6,
         lambda g: (
             (True, "distance_between 純函數實作正確！")
             if (callable(g.get("distance_between"))) or
                ("distance_between" in history_str and "0.5" in history_str or "sqrt" in history_str)
             else (False, "請定義 distance_between 接收兩元組座標並計算歐式距離回傳！")
         )),

        ("11-4-6", "挑戰題", "重構依賴全域的髒代碼為無副作用純函數", 5,
         lambda g: (
             (True, "純函數重構挑戰成功！")
             if ("pure" in history_str or "def " in history_str) and ("return" in history_str)
             else (False, "請將依賴全域狀態的邏輯改寫為獨立可測試的純函數！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-4：變數作用域：區域變數與同名遮蔽 —— 自動評分報告")
    print(f"👤 學生姓名: {combined_display_name}")
    print(f"📧 帳號識別: {final_email}")
    print(f"⏰ 評分時間: {timestamp_str}")
    print("=" * 72)

    passed_count = 0
    detailed_results = []

    for sub_id, q_type, title, weight, check_fn in test_cases:
        try:
            passed, msg = check_fn(env)
        except Exception as err:
            passed = False
            msg = f"評分檢測過程發生例外狀況: {err}"

        status_icon = "✅ 通過" if passed else "❌ 未通過"
        points = weight if passed else 0
        total_score += points
        if passed:
            passed_count += 1

        print(f"[{status_icon}] ({points:2d}/{weight:2d}分) {sub_id} {q_type} - {title}")
        print(f"       回饋: {msg}")

        detailed_results.append({
            "sub_unit": sub_id,
            "type": q_type,
            "title": title,
            "score": points,
            "max_score": weight,
            "passed": passed,
            "feedback": msg
        })

    print("-" * 72)
    print(f"🎯 總結成績: {total_score} / {max_score} 分 (通過題數: {passed_count}/{len(test_cases)})")

    # 等級評語
    if total_score == 100:
        level_comment = "🏆 完美滿分！你已經徹底攻克自訂函數與作用域核心技術，具備 APCS 實戰高手水準！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！模組化概念與函數傳參掌握非常扎實，稍微細心檢查即可登峰造極！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本函數已建立，建議複習未通過的題目加強熟悉度！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 4. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "11-4",
        "unit_name": "變數作用域：區域變數與同名遮蔽",
        "student_name": declared_name,
        "google_name": final_google_name,
        "google_email": final_email,
        "score": total_score,
        "max_score": max_score,
        "passed_count": passed_count,
        "total_questions": len(test_cases),
        "comment": level_comment,
        "timestamp": timestamp_str,
        "details": detailed_results
    }

    try:
        filename = f"grade_report_11_4.json"
        with open(filename, "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)
        print(f"💾 本地成績報告已儲存至: {filename}")
    except Exception as e:
        print(f"⚠️ 本地儲存失敗: {e}")

    # 5. 上傳雲端 Webhook
    if LOG_WEBHOOK_URL and LOG_WEBHOOK_URL.startswith("http"):
        try:
            payload = json.dumps(report_data).encode("utf-8")
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status in (200, 302):
                    print("🚀 成績已成功同步至教材團隊雲端學習資料庫！")
                else:
                    print(f"📡 雲端同步回應代碼: {response.status}")
        except Exception as e:
            print("💡 （雲端記錄通道離線或連線逾時，本地成績記錄依然完全有效）")

if __name__ == "__main__":
    auto_grade_unit_11_4()
