# ==============================================================================
# 🧪 《PythAPCS123》單元 6-8：EOF 與串流輸入模式 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_8.py
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

def auto_grade_unit_6_8():
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
        # 6-8-1 預知次數的輸入走訪 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-1", "填空題", "讀取首行 T 並走訪 T 次 (T, total_processed)", 4,
         lambda g: (
             (True, "預知筆數 T 與 for 迴圈結構填寫正確！")
             if (g.get("total_processed") == 3 or
                 (("range(T)" in history_clean or "range(int(simulated_first_line))" in history_clean) and
                  ("total_processed" in g or "total_processed" in history_str)))
             else (False, "請在 6-8-1 填空題空格填入 T 與正確的 range 走訪次數！")
         )),

        ("6-8-1", "練習題", "固定 N 筆加總與筆數統計 (total_sum = 100, count = 4)", 4,
         lambda g: (
             (True, "固定 N 筆輸入與累加統計輸出正確！")
             if (g.get("total_sum") == 100 and g.get("count") == 4) or
                (("total_sum" in g or "total_sum" in history_str) and
                 ("assert count == 4 and total_sum == 100" in history_str or
                  "assertcount==4andtotal_sum==100" in history_clean))
             else (False, "請撰寫 for 迴圈讀取 N 筆數值，計算 total_sum 與筆數 count！")
         )),

        ("6-8-1", "挑戰題", "櫃檯提款哨兵值 0 終止 (customer_count = 3, total_withdraw = 400)", 5,
         lambda g: (
             (True, "提款哨兵終止邏輯與金額結算完全正確！")
             if (g.get("customer_count") == 3 and g.get("total_withdraw") == 400) or
                (("customer_count" in g or "customer_count" in history_str) and
                 ("assert customer_count == 3 and total_withdraw == 400" in history_str or
                  "assertcustomer_count==3andtotal_withdraw==400" in history_clean))
             else (False, "請使用 while True 搭配哨兵值 0 判定退出，統計人數與總提款額！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-2 預知筆數標準走訪與底線慣例 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-2", "填空題", "底線 _ 慣例走訪 N 次 (for _ in range(N))", 4,
         lambda g: (
             (True, "底線 _ 慣用法與 range(N) 填寫正確！")
             if "for_inrange(N)" in history_clean or "for _ in range(N)" in history_str or "for _ in range(" in history_str
             else (False, "請在 6-8-2 填空題使用底線 _ 與 range(N) 走訪 N 輪！")
         )),

        ("6-8-2", "練習題", "N 筆成績統計及格人數與最高分 (pass_count = 2, max_score = 80)", 4,
         lambda g: (
             (True, "N 筆成績及格計數與極值更新邏輯正確！")
             if (g.get("pass_count") == 2 and g.get("max_score") == 80) or
                (("pass_count" in g or "pass_count" in history_str) and
                 ("assert pass_count == 2 and max_score == 80" in history_str or
                  "assertpass_count==2andmax_score==80" in history_clean))
             else (False, "請撰寫 for 迴圈走訪 N 筆成績，統計 pass_count 與 max_score！")
         )),

        ("6-8-2", "挑戰題", "雙層巢狀多測資框架加總 (grand_total = 66)", 5,
         lambda g: (
             (True, "多組測資雙層 for 迴圈累加總和正確！")
             if g.get("grand_total") == 66 or
                (("grand_total" in g or "grand_total" in history_str) and
                 ("assert grand_total == 66" in history_str or "assertgrand_total==66" in history_clean))
             else (False, "請撰寫雙層 for 迴圈（外層 T、內層 N），計算全組別總和 grand_total！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-3 特殊哨兵值終止模式 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-3", "填空題", "while True 與哨兵 -1 煞車 (while True / break)", 4,
         lambda g: (
             (True, "while True 永動迴圈與哨兵 -1 煞車語法填寫正確！")
             if ("while True" in history_str or "whileTrue" in history_clean) and
                ("val == -1" in history_str or "val==-1" in history_clean) and
                "break" in history_str
             else (False, "請在 6-8-3 填空題補齊 while True 與 val == -1: break！")
         )),

        ("6-8-3", "練習題", "哨兵 0 終止體重累加與平均 (count = 3, avg_weight = 70)", 4,
         lambda g: (
             (True, "哨兵終止體重統計與平均值計算正確！")
             if (g.get("avg_weight") == 70 or g.get("total_weight") == 210 or
                 (g.get("count") == 3 and "weight" in history_clean) or
                 (("avg_weight" in g or "avg_weight" in history_str) and
                  ("assert count == 3 and avg_weight == 70" in history_str or
                   "assertcount==3andavg_weight==70" in history_clean)))
             else (False, "請使用 while 迴圈在遇到 0 時中斷，計算人數 count 與平均體重 avg_weight！")
         )),

        ("6-8-3", "挑戰題", "雙哨兵 (0, 0) 曼哈頓距離加總 (valid_points = 3, total_manhattan = 21)", 5,
         lambda g: (
             (True, "雙哨兵 (0, 0) 複合條件中斷與曼哈頓距離累加正確！")
             if (g.get("total_manhattan") == 21 or
                 (g.get("valid_points") == 3 and "manhattan" in history_clean) or
                 (("total_manhattan" in g or "total_manhattan" in history_str) and
                  ("assert valid_points == 3 and total_manhattan == 21" in history_str or
                   "assertvalid_points==3andtotal_manhattan==21" in history_clean)))
             else (False, "請檢查 x == 0 and y == 0 結束標記，並計算有效點曼哈頓距離總和！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-4 什麼是 EOF (共 13 分)
        # ----------------------------------------------------------------------
        ("6-8-4", "填空題", "Windows 與 Linux/Mac EOF 快捷鍵認知", 4,
         lambda g: (
             (True, "EOF 系統快捷鍵觀念理解正確（Ctrl+Z / Ctrl+D）！")
             if ("z" in str(g.get("win_eof_key", "")).lower() and
                 "d" in str(g.get("unix_eof_key", "")).lower()) or
                ("win_eof_key" in history_clean and "unix_eof_key" in history_clean and
                 ("ctrl+z" in history_clean.lower() or "ctrl-z" in history_clean.lower()))
             else (False, "請填入 Windows (Ctrl+Z) 與 Unix (Ctrl+D) 的 EOF 模擬快捷鍵！")
         )),

        ("6-8-4", "練習題", "模擬 None 串流末端字串長度加總 (total_chars = 14)", 4,
         lambda g: (
             (True, "None 結尾偵測與字串長度累加正確！")
             if g.get("total_chars") == 14 or
                (("total_chars" in g or "total_chars" in history_str) and
                 ("assert total_chars == 14" in history_str or "asserttotal_chars==14" in history_clean))
             else (False, "請使用 while True 讀取字串，偵測到 None 時 break 並統計 total_chars！")
         )),

        ("6-8-4", "挑戰題", "逐行整數讀取至 EOF 總和與行數 (total_lines = 4, grand_sum = 120)", 5,
         lambda g: (
             (True, "EOF 逐行整數統計行數與總和輸出完全正確！")
             if (g.get("grand_sum") == 120 or g.get("total_lines") == 4) or
                (("grand_sum" in g or "grand_sum" in history_str) and
                 ("assert total_lines == 4 and grand_sum == 120" in history_str or
                  "asserttotal_lines==4andgrand_sum==120" in history_clean))
             else (False, "請在讀取到 None 前累加整數至 grand_sum，並計算 total_lines！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-5 sys.stdin 自然走訪 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-5", "填空題", "sys.stdin 自然走訪語法 (for line in sys.stdin:)", 4,
         lambda g: (
             (True, "for line in sys.stdin 自然走訪語法填寫正確！")
             if "forlineinsys.stdin" in history_clean or "for line in sys.stdin" in history_str
             else (False, "請在 6-8-5 填空題填入走訪 sys.stdin 的 for 迴圈關鍵字！")
         )),

        ("6-8-5", "練習題", "自然迭代偶數平方和 (count = 2, even_sq_sum = 52)", 4,
         lambda g: (
             (True, "串流迭代偶數篩選與平方和統計輸出正確！")
             if g.get("even_sq_sum") == 52 or
                (g.get("count") == 2 and "even_sq_sum" in history_clean) or
                (("even_sq_sum" in g or "even_sq_sum" in history_str) and
                 ("assert count == 2 and even_sq_sum == 52" in history_str or
                  "assertcount==2andeven_sq_sum==52" in history_clean))
             else (False, "請走訪數列，篩選偶數累加平方和 even_sq_sum 與個數 count！")
         )),

        ("6-8-5", "挑戰題", "單行多值解包求矩形最大面積 (max_area = 16)", 4,
         lambda g: (
             (True, "單行多值解包與極值面積比對完全正確！")
             if g.get("max_area") == 16 or
                (("max_area" in g or "max_area" in history_str) and
                 ("assert max_area == 16" in history_str or "assertmax_area==16" in history_clean))
             else (False, "請走訪每行字串，使用 map(int, line.split()) 解包並更新 max_area！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-6 while True + try-except EOFError (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-6", "填空題", "try-except 攔截 EOFError 骨架 (try: / except EOFError:)", 4,
         lambda g: (
             (True, "try-except EOFError 例外攔截語法填寫正確！")
             if ("try:" in history_str or "try" in history_str) and
                ("except EOFError" in history_str or "exceptEOFError" in history_clean)
             else (False, "請在 6-8-6 填空題補齊 try 與 except EOFError 關鍵字！")
         )),

        ("6-8-6", "練習題", "try-except 平方和連續累加 (sum_squares = 93)", 4,
         lambda g: (
             (True, "例外攔截串流平方和計算正確！")
             if g.get("sum_squares") == 93 or
                (("sum_squares" in g or "sum_squares" in history_str) and
                 ("assert sum_squares == 93" in history_str or "assertsum_squares==93" in history_clean))
             else (False, "請使用 try-except 攔截 EOFError 並計算平方和 sum_squares！")
         )),

        ("6-8-6", "挑戰題", "EOF 氣溫極值更新與全距 (max_t = 31, min_t = 18, range_t = 13)", 4,
         lambda g: (
             (True, "串流氣溫極值即時更新與全距計算正確！")
             if (g.get("max_t") == 31 and g.get("min_t") == 18 and g.get("range_t") == 13) or
                (("range_t" in g or "range_t" in history_str) and
                 ("assert max_t == 31 and min_t == 18 and range_t == 13" in history_str or
                  "assertmax_t==31andmin_t==18andrange_t==13" in history_clean))
             else (False, "請使用 try-except 在退出時計算 range_t = max_t - min_t！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-7 空間複雜度 O(1) 串流即時縮減心法 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-7", "填空題", "串流即時維護最小值 (min_val = 7)", 4,
         lambda g: (
             (True, "最小值初值與即時比對更新填寫正確！")
             if g.get("min_val") == 7 or
                ("min_val" in history_clean and ("data < min_val" in history_str or "data<min_val" in history_clean))
             else (False, "請在 6-8-7 填空題完成 min_val 初值與條件更新！")
         )),

        ("6-8-7", "練習題", "氣溫串流統計與全距 (count_t = 5, sum_t = 110, temp_range = 15)", 4,
         lambda g: (
             (True, "空間 O(1) 氣溫串流統計與全距輸出正確！")
             if (g.get("count_t") == 5 and g.get("sum_t") == 110 and g.get("temp_range") == 15) or
                (("temp_range" in g or "temp_range" in history_str) and
                 ("assert count_t == 5 and sum_t == 110 and temp_range == 15" in history_str or
                  "assertcount_t==5andsum_t==110andtemp_range==15" in history_clean))
             else (False, "請以純純量維護總和、筆數、極值，並計算 temp_range！")
         )),

        ("6-8-7", "挑戰題", "串流及格率統計 (total_players = 6, pass_players = 4, pass_rate = 66)", 4,
         lambda g: (
             (True, "串流及格率整數百分比運算正確！")
             if (g.get("total_players") == 6 and g.get("pass_players") == 4 and g.get("pass_rate") == 66) or
                (("pass_rate" in g or "pass_rate" in history_str) and
                 ("assert total_players == 6 and pass_players == 4 and pass_rate == 66" in history_str or
                  "asserttotal_players==6andpass_players==4andpass_rate==66" in history_clean))
             else (False, "請統計 total_players 與 pass_players，計算 pass_rate = pass_players * 100 // total_players！")
         )),

        # ----------------------------------------------------------------------
        # 6-8-8 單行多值拆解與 APCS 實戰總結 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-8-8", "填空題", "單行多值整數映射語法 (map(int, line_str.split()))", 4,
         lambda g: (
             (True, "map 與 split 單行解包語法填寫正確！")
             if g.get("total") == 60 or
                ("map(int,line_str.split())" in history_clean or "map(int, line_str.split())" in history_str or "split()" in history_clean)
             else (False, "請在 6-8-8 填空題填入 map(int, line_str.split())！")
         )),

        ("6-8-8", "練習題", "連續兩行向量內積計算 (dot = 26)", 4,
         lambda g: (
             (True, "兩行向量解析與內積計算輸出正確！")
             if g.get("dot") == 26 or
                (("dot" in g or "dot" in history_str) and
                 ("assert dot == 26" in history_str or "assertdot==26" in history_clean))
             else (False, "請分別解包兩行座標，計算向量內積 dot = x1*x2 + y1*y2！")
         )),

        ("6-8-8", "挑戰題", "APCS 多組門檻過濾累加 (total_qualified = 4, all_groups_sum = 305)", 4,
         lambda g: (
             (True, "雙組測資合格門檻加總與計數完全正確！")
             if (g.get("total_qualified") == 4 and g.get("all_groups_sum") == 305) or
                (("all_groups_sum" in g or "all_groups_sum" in history_str) and
                 ("assert total_qualified == 4 and all_groups_sum == 305" in history_str or
                  "asserttotal_qualified==4andall_groups_sum==305" in history_clean))
             else (False, "請走訪雙組測資，統計高於門檻數字個數 total_qualified 與數值總和 all_groups_sum！")
         ))
    ]

    print("\n" + "=" * 70)
    print("📋 《PythAPCS123》單元 6-8：EOF 與串流輸入模式 —— 學習評量診斷報告")
    print(f"👤 學生姓名：{combined_display_name}")
    print(f"📧 帳號識別：{final_email}")
    print(f"⏰ 檢測時間：{timestamp_str}")
    print("=" * 70 + "\n")

    current_subunit = ""
    for subunit, q_type, q_desc, weight, check_fn in test_cases:
        if subunit != current_subunit:
            current_subunit = subunit
            print(f"\n【子單元 {current_subunit} 測驗項目】")

        passed, feedback = check_fn(env)
        if passed:
            score_earned = weight
            total_score += score_earned
            status_icon = "✅ 通過"
        else:
            score_earned = 0
            status_icon = "❌ 未達標"

        print(f"  [{status_icon}] ({score_earned}/{weight}分) {q_type} - {q_desc}")
        print(f"         回饋：{feedback}")

    # 計算總評
    print("\n" + "=" * 70)
    print(f"🎯 結算總得分：{total_score} / {max_score} 分")
    
    if total_score == 100:
        badge = "🏆【全章大滿貫榮譽徽章】串流與輸入處理大師！APCS 實作題破關神手！"
    elif total_score >= 80:
        badge = "🥇【優秀晉級徽章】對 EOF 與串流輸入已有相當敏銳的掌握度！"
    elif total_score >= 60:
        badge = "🥈【及格認證徽章】掌握基本輸入模式，多加練習即可更加熟練！"
    else:
        badge = "💡【尚在探索徽章】別氣餒！仔細觀察迴圈終止條件與 map 解包語法，再次挑戰吧！"
    
    print(f"🎖️ 榮譽評價：{badge}")
    print("=" * 70 + "\n")

    # 4. 準備傳送雲端試算表記錄
    log_data = {
        "unit": "Unit 6-8: EOF 與串流輸入模式",
        "student_name": declared_name,
        "google_email": final_email,
        "google_name": final_google_name,
        "score": total_score,
        "max_score": max_score,
        "badge": badge,
        "timestamp": timestamp_str
    }

    # 本地備份
    try:
        with open("score_log_unit_6_8.json", "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 雲端傳送
    try:
        json_bytes = json.dumps(log_data).encode("utf-8")
        req = urllib.request.Request(
            LOG_WEBHOOK_URL,
            data=json_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            resp_text = response.read().decode("utf-8")
            print("🚀 成績已同步回報至教學系統後台資料庫！")
    except Exception:
        print("ℹ️ 本地評分已完成（若在離線環境，成績已存至本地日誌）。")

if __name__ == "__main__":
    auto_grade_unit_6_8()
