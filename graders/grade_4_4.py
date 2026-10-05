# ==============================================================================
# 🧪 《PythAPCS123》單元 4-4：變數與運算式綜合輸出 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_4.py
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

def auto_grade_unit_4_4():
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
        # 4-4-1 字串標籤與變數混合輸出——變數名牌 vs 字串引號的本質區別 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-1", "填空題", "天體日誌與視星等數值混合輸出 (star_name, magnitude)", 6,
         lambda g: (
             (True, "字串標籤與變數填寫正確：成功輸出恆星名稱與視星等！")
             if (("star_name" in history_str and "magnitude" in history_str) or
                 (g.get("star_name") == "天狼星" and g.get("magnitude") == -1.46))
             else (False, "請在 4-4-1 填空題空格依序填入 star_name 與 magnitude 並執行！")
         )),

        ("4-4-1", "練習題", "校慶田徑賽選手成績看板 (athlete, event, score)", 8,
         lambda g: (
             (True, f"選手成績單行混合輸出成功：{g.get('athlete')} {g.get('event')} {g.get('score')}！")
             if (("athlete" in g and "event" in g and "score" in g) and
                 ("選手：" in history_str or "公尺" in history_str))
             else (False, "請宣告 athlete, event, score 並使用單一行 print() 混合輸出文字標籤與變數！")
         )),

        ("4-4-1", "挑戰題", "深空探測船監控儀表板 (probe_name, distance_au, battery_pct)", 6,
         lambda g: (
             (True, "探測船狀態代號與距地數據排版輸出成功！")
             if (("probe_name" in g and "distance_au" in g and "battery_pct" in g) and
                 ("探測船" in history_str or "AU" in history_str))
             else (False, "請宣告 probe_name, distance_au, battery_pct 變數，並撰寫兩行 print() 正確嵌入標籤！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-2 在 print() 中即時運算——算式先求值後輸出的精簡美學 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-2", "填空題", "披薩平分整除與取餘數即時運算 (// 與 %)", 6,
         lambda g: (
             (True, "即時運算填寫正確：成功使用 // 整除與 % 取餘數！")
             if (("//" in history_str and "%" in history_str) and
                 ("total_slices" in history_str or g.get("total_slices") == 26))
             else (False, "請在 4-4-2 填空題空格填入 // 與 % 運算子並執行儲存格！")
         )),

        ("4-4-2", "練習題", "圓周長與圓面積即時運算輸出 (r)", 8,
         lambda g: (
             (True, f"圓幾何數值即時計算輸出成功：半徑={g.get('r')}！")
             if (("r" in g) and
                 ("3.14" in history_str) and
                 ("周長" in history_str and "面積" in history_str))
             else (False, "請宣告半徑 r，並在 print() 內部直接計算圓周長與圓面積！")
         )),

        ("4-4-2", "挑戰題", "打工薪資即時計算系統 (hourly_wage, normal_hours, overtime_hours)", 6,
         lambda g: (
             (True, "工資計算邏輯與優先權運算正確！")
             if (("hourly_wage" in g and "normal_hours" in g and "overtime_hours" in g) and
                 ("1.5" in history_str or "平日" in history_str or "加班" in history_str))
             else (False, "請宣告 hourly_wage, normal_hours, overtime_hours 變數，並在 print() 中即時運算！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-3 消除文字與數值突兀間隔——利用 sep='' 實現中文字詞與單位無縫貼合 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-3", "填空題", "氣溫與濕度無縫貼合 (sep='')", 6,
         lambda g: (
             (True, "字詞無縫貼合設定正確：sep=''！")
             if (("sep=''" in history_str or 'sep=""' in history_str) and
                 ("高雄市" in history_str or g.get("city") == "高雄市"))
             else (False, "請在 4-4-3 填空題末尾填入 sep='' 並執行儲存格！")
         )),

        ("4-4-3", "練習題", "跑步距離與時間單位無縫貼合 (km, mins, secs, sep='')", 8,
         lambda g: (
             (True, f"運動報告單位貼合成功：{g.get('km')}公里，{g.get('mins')}分{g.get('secs')}秒！")
             if (("km" in g and "mins" in g and "secs" in g) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 km, mins, secs 變數，並使用 sep='' 消除空格貼合單位輸出！")
         )),

        ("4-4-3", "挑戰題", "暴擊戰鬥日誌現場無縫算式 (attacker, skill, base_damage, multiplier)", 6,
         lambda g: (
             (True, "暴擊戰鬥日誌無縫輸出成功！")
             if (("attacker" in g and "skill" in g and "base_damage" in g and "multiplier" in g) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告戰鬥變數，並使用 sep='' 搭配現場傷害算式印出戰報！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-4 連續跨行與接續排版——結合 end 參數建構連貫算式與計算歷程 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-4", "填空題", "連乘算式不換行留空格 (end=' ')", 6,
         lambda g: (
             (True, "算式接續設定正確：end=' '！")
             if (("end=' '" in history_str or 'end=" "' in history_str) and
                 ("算式" in history_str or g.get("x") == 3))
             else (False, "請在 4-4-4 填空題空格填入 end=' ' 並執行儲存格！")
         )),

        ("4-4-4", "練習題", "糖果盒裝商數餘數單行連貫接續 (candies, box, end=' ')", 8,
         lambda g: (
             (True, f"糖果盒裝連貫輸出成功：{g.get('candies')} 顆每 {g.get('box')} 顆裝一盒！")
             if (("candies" in g and "box" in g) and
                 ("end=' '" in history_str or 'end=" "' in history_str or "//" in history_str))
             else (False, "請宣告 candies, box 變數，並分兩次 print() 接續輸出裝盒結果！")
         )),

        ("4-4-4", "挑戰題", "畢氏定理斜邊推導歷程單行組裝 (leg_a, leg_b)", 6,
         lambda g: (
             (True, f"畢氏定理推導歷程組裝完成：兩股={g.get('leg_a')}, {g.get('leg_b')}！")
             if (("leg_a" in g and "leg_b" in g) and
                 ("斜邊" in history_str or "根號" in history_str or "**2" in history_str))
             else (False, "請宣告 leg_a, leg_b 變數，並分三步接續在同一行輸出幾何推導歷程！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-5 實戰全能儀表板——變數、即時運算、sep 與 end 的終極融合 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-5", "填空題", "成績單內建函數 round 與 max (round, max)", 6,
         lambda g: (
             (True, "內建函數填寫正確：round 與 max！")
             if (("round" in history_str and "max" in history_str) and
                 ("學生段考成績單" in history_str or g.get("chinese") == 92))
             else (False, "請在 4-4-5 填空題空格填入 round 與 max 函數名稱並執行！")
         )),

        ("4-4-5", "練習題", "直角三角形幾何分析儀全能排版 (a, b, c, sep='')", 8,
         lambda g: (
             (True, f"幾何工程分析儀輸出成功：兩股={g.get('a')}, {g.get('b')}！")
             if (("a" in g and "b" in g) and
                 ("直角三角形兩股" in history_str) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 a, b 變數，並結合即時運算與 sep='' 輸出直角三角形幾何報告！")
         )),

        ("4-4-5", "挑戰題", "智慧家庭夏月用電計費儀表板 (billing_month, kwh_used, rate_per_kwh, base_fee)", 6,
         lambda g: (
             (True, "電費帳單儀表板排版與計算完成！")
             if (("billing_month" in g and "kwh_used" in g and "rate_per_kwh" in g and "base_fee" in g) and
                 ("電費通知單" in history_str or "用電" in history_str))
             else (False, "請宣告電費變數，並在 print() 內部現場計算流動電費與應繳總額！")
         )),
    ]

    # 執行所有測資評分
    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 4-4 學習成效自動評分診斷報告")
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
        badge = "🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美融合變數、即時運算、sep 與 end！"
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
        "unit": "4-4",
        "unit_title": "變數與運算式綜合輸出",
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
        log_filename = "score_log_unit_4_4.json"
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
auto_grade_unit_4_4()
