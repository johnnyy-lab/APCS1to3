# ==============================================================================
# 🧪 《PythAPCS123》單元 11-8：函數模組化解題實戰：Top-Down 拆題法與輔助函式庫 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_8.py
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

def auto_grade_unit_11_8(student_name=""):
    """
    單元 11-8：函數模組化解題實戰：Top-Down 拆題法與輔助函式庫 自動評分主程式
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
        # 11-8-1 自頂向下拆題思維 (Top-Down Decomposition) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-1", "填空題", "電商促銷結帳系統 checkout 與子流程組裝", 5,
         lambda g: (
             (True, "checkout 電商結帳模組填空正確！")
             if (callable(g.get("checkout")) and g.get("checkout")([200, 300, 500]) == 860) or
                (g.get("final_total") == 860) or
                ("checkout" in history_str and "calc_subtotal" in history_str)
             else (False, "請在 checkout 依序串接 calc_subtotal、apply_coupon 與 add_shipping！")
         )),

        ("11-8-1", "練習題", "字串清洗流水線 clean_and_format(text)", 6,
         lambda g: (
             (True, "clean_and_format 自頂向下清洗正確！")
             if (callable(g.get("clean_and_format"))) or
                ("clean_and_format" in history_str and "strip" in history_str)
             else (False, "請拆解 strip_punctuation 與 to_uppercase 並在主函數組合！")
         )),

        ("11-8-1", "挑戰題", "單詞統計報表系統 generate_word_report(article)", 6,
         lambda g: (
             (True, "generate_word_report 報表流水線正確！")
             if (callable(g.get("generate_word_report"))) or
                ("generate_word_report" in history_str and "split_words" in history_str)
             else (False, "請由高層骨架拆解分詞、過濾與頻率統計子函數並產出報表！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-2 必備輔助函式庫一：二維網格安全邊界檢查 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-2", "填空題", "邊界檢查 in_bound 與八方向雷達 sum_surrounding_8", 5,
         lambda g: (
             (True, "八方向邊界掃描填空正確！")
             if (callable(g.get("in_bound")) and callable(g.get("sum_surrounding_8"))) or
                ("in_bound(nr, nc, H, W)" in history_str or "in_bound" in history_str)
             else (False, "請定義 in_bound 邊界檢查並在 sum_surrounding_8 中防護掃描！")
         )),

        ("11-8-2", "練習題", "踩地雷周圍探測 count_adjacent_mines(board, r, c)", 6,
         lambda g: (
             (True, "踩地雷雷達探測器實作正確！")
             if (callable(g.get("count_adjacent_mines"))) or
                ("count_adjacent_mines" in history_str and "in_bound" in history_str)
             else (False, "請使用 in_bound 檢查鄰近 8 格並統計地雷數量！")
         )),

        ("11-8-2", "挑戰題", "滑雪者直線連續滑行探測 skier_slide_distance", 6,
         lambda g: (
             (True, "滑雪者直線探測實作正確！")
             if (callable(g.get("skier_slide_distance"))) or
                ("in_bound" in history_str and "while" in history_str and "dr" in history_str)
             else (False, "請沿著向量 (dr, dc) 推進，若未出界且坡度符合則累計滑行距離！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-3 必備輔助函式庫二：曼哈頓與歐式距離 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-3", "填空題", "外送巡迴路程曼哈頓計算 calc_total_trip", 5,
         lambda g: (
             (True, "外送總路程計算填空正確！")
             if (callable(g.get("calc_total_trip"))) or
                ("manhattan" in history_str and "calc_total_trip" in history_str)
             else (False, "請定義 manhattan(p1, p2) 並在 calc_total_trip 累加整趟行程距離！")
         )),

        ("11-8-3", "練習題", "圓形雷達範圍探測 find_targets_in_radius", 6,
         lambda g: (
             (True, "find_targets_in_radius 範圍篩選正確！")
             if (callable(g.get("find_targets_in_radius"))) or
                ("find_targets_in_radius" in history_str and "radius ** 2" in history_str or "dist" in history_str)
             else (False, "請定義距離平方函數並篩選距離小於等於半徑的所有目標點！")
         )),

        ("11-8-3", "挑戰題", "計程車最近乘客指派系統 dispatch_taxi", 6,
         lambda g: (
             (True, "dispatch_taxi 就近指派實作正確！")
             if (callable(g.get("dispatch_taxi"))) or
                ("dispatch_taxi" in history_str and "manhattan" in history_str)
             else (False, "請計算所有計程車與乘客之距離，回傳距離最近的計程車編號！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-4 必備輔助函式庫三：數論判定工具 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-4", "填空題", "完全平方數 is_perfect_square 與質數判定", 5,
         lambda g: (
             (True, "完全平方數與質數判定填空正確！")
             if (callable(g.get("is_perfect_square")) and g.get("is_perfect_square")(16) is True) or
                ("is_perfect_square" in history_str and "root * root == n" in history_str)
             else (False, "請利用 root = int(n ** 0.5) 判定 root * root == n 回傳布林值！")
         )),

        ("11-8-4", "練習題", "特殊密碼數字篩選器 find_special_numbers", 6,
         lambda g: (
             (True, "find_special_numbers 密碼篩選正確！")
             if (callable(g.get("find_special_numbers"))) or
                ("find_special_numbers" in history_str and "is_prime" in history_str)
             else (False, "請結合質數判定子函數，篩選區間內符合條件的特殊密碼數字！")
         )),

        ("11-8-4", "挑戰題", "雙胞胎質數搜尋器 find_twin_primes(limit)", 6,
         lambda g: (
             (True, "find_twin_primes 雙胞胎質數搜尋正確！")
             if (callable(g.get("find_twin_primes")) and (3, 5) in g.get("find_twin_primes")(20)) or
                ("find_twin_primes" in history_str and "p + 2" in history_str)
             else (False, "請走訪找出所有 (p, p + 2) 皆為質數的數對清單！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-5 實戰綜合演練：自頂向下拆解大型模擬題 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-8-5", "填空題", "安全庇護所綜合篩選 count_valid_shelters", 5,
         lambda g: (
             (True, "count_valid_shelters 綜合篩選填空正確！")
             if (callable(g.get("count_valid_shelters"))) or
                ("count_valid_shelters" in history_str and "in_bound" in history_str)
             else (False, "請組裝邊界檢查與容量判斷，統計符合條件的庇護所總數！")
         )),

        ("11-8-5", "練習題", "雷達最高警報點搜尋 find_max_alert", 6,
         lambda g: (
             (True, "find_max_alert 最高警報點搜尋正確！")
             if (callable(g.get("find_max_alert"))) or
                ("find_max_alert" in history_str and "in_bound" in history_str)
             else (False, "請結合半徑與邊界檢查，找出雷達範圍內警報值最高之點！")
         )),

        ("11-8-5", "挑戰題", "神祕遺跡尋寶模擬 treasure_hunt(grid, path)", 5,
         lambda g: (
             (True, "treasure_hunt 遺跡尋寶模擬挑戰成功！")
             if (callable(g.get("treasure_hunt"))) or
                ("treasure_hunt" in history_str and "in_bound" in history_str)
             else (False, "請以模組化函數追蹤尋寶路徑，遇到障礙或出界安全停步並統計金幣！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-6 模組化除錯策略：單元測試與程式碼健檢 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-8-6", "填空題", "邊界函數單元測試 test_in_bound 與 Assert 斷言", 5,
         lambda g: (
             (True, "test_in_bound 單元測試填空正確！")
             if (callable(g.get("test_in_bound"))) or
                ("assert in_bound" in history_str and "test_in_bound" in history_str)
             else (False, "請在 test_in_bound 使用多個 assert 斷言覆蓋角落與越界情況！")
         )),

        ("11-8-6", "練習題", "自訂 GCD 函數單元測試 test_gcd(my_gcd)", 6,
         lambda g: (
             (True, "test_gcd 單元測試實作正確！")
             if (callable(g.get("test_gcd"))) or
                ("assert" in history_str and "test_gcd" in history_str)
             else (False, "請設計 test_gcd 包含互質、倍數與邊界測資進行全面驗證！")
         )),

        ("11-8-6", "挑戰題", "程式碼健檢醫師：修復質數函數邊界漏洞 fixed_prime", 5,
         lambda g: (
             (True, "fixed_prime 質數函數邊界修復正確！")
             if (callable(g.get("fixed_prime")) and
                 g.get("fixed_prime")(1) is False and
                 g.get("fixed_prime")(0) is False and
                 g.get("fixed_prime")(-7) is False and
                 g.get("fixed_prime")(2) is True and
                 g.get("fixed_prime")(7) is True) or
                ("fixed_prime" in history_str and "n <= 1" in history_str)
             else (False, "請修復質數函數，確保 <= 1 與負數回傳 False，且 2 回傳 True！")
         ))
    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 11-8：函數模組化解題實戰：Top-Down 拆題法與輔助函式庫 —— 自動評分報告")
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
        "unit_id": "11-8",
        "unit_name": "函數模組化解題實戰：Top-Down 拆題法與輔助函式庫",
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
        filename = f"grade_report_11_8.json"
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
    auto_grade_unit_11_8()
