# ==============================================================================
# 🧪 《PythAPCS123》單元 7-2：字串拼接與重複運算 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_2.py
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

def auto_grade_unit_7_2():
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
        # 7-2-1 加法拼接運算子 (+) 與型態轉型 str() (共 20 分)
        # ----------------------------------------------------------------------
        ("7-2-1", "填空題", "商品標價安全字串加法拼接 (price_tag)", 6,
         lambda g: (
             (True, "字串加法拼接與 str(item_price) 轉型成功！")
             if g.get("price_tag") == "Apple: $30" or
                ('price_tag' in g and "Apple: $30" in str(g.get("price_tag"))) or
                ("item_name" in history_str and "str(item_price)" in history_clean)
             else (False, "請在 7-2-1 填空題空格填入 + 號與 str(item_price)！")
         )),

        ("7-2-1", "練習題", "郵件地址拼接器 (username + '@' + domain)", 9,
         lambda g: (
             (True, "Email 帳號與網域名稱加法拼接正確！")
             if ("@" in history_str and "+" in history_str and ("username" in history_str or "domain" in history_str)) or
                ("apcs_student@test.edu.tw" in history_str or "coder123@gmail.com" in history_str)
             else (False, "請讀入 username 與 domain，以 + 號拼接成 [username]@[domain]！")
         )),

        ("7-2-1", "挑戰題", "遊戲存檔標籤生成器 (<title> HP:hp | GOLD:gold)", 5,
         lambda g: (
             (True, "遊戲角色屬性字串拼接格式正確！")
             if ("HP:" in history_str and "GOLD:" in history_str and "<" in history_str) or
                ("str(hp)" in history_clean or "str(gold)" in history_clean)
             else (False, "請讀入 title, hp, gold，使用加法拼接成 <title> HP:hp | GOLD:gold！")
         )),

        # ----------------------------------------------------------------------
        # 7-2-2 空字串初始化與 += 迴圈累加 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-2-2", "填空題", "空字串初始化與 += 迴圈累加 (pattern)", 6,
         lambda g: (
             (True, "空字串初始化與 += 數字累加完全正確！")
             if g.get("pattern") == "1-2-3-" or
                ('pattern = ""' in history_clean or "pattern=''" in history_clean) and "+=" in history_str
             else (False, "請在 7-2-2 填空題初始化為空字串 \"\" 並使用 += 累加！")
         )),

        ("7-2-2", "練習題", "連續字串黏合器 (text += word + '_')", 9,
         lambda g: (
             (True, "多單字底線分隔累加黏合輸出正確！")
             if ("+=" in history_str and "_" in history_str and ("word" in history_str or "text" in history_str)) or
                ("Iron_Man_Suit_" in history_str or "Super_Hero_" in history_str)
             else (False, "請讀入 n 筆單字，使用字串變數 text 累加所有單字並以底線分隔！")
         )),

        ("7-2-2", "挑戰題", "偶數與奇數標記拼接器 ([E:數字] 與 [O:數字])", 5,
         lambda g: (
             (True, "奇偶數標籤判斷與字串累加正確！")
             if ("[E:" in history_str and "[O:" in history_str) or
                ("% 2" in history_str and "+=" in history_str)
             else (False, "請走訪 1 到 n，偶數追加 [E:數字]，奇數追加 [O:數字]！")
         )),

        # ----------------------------------------------------------------------
        # 7-2-3 乘法重複運算子 (*) (共 20 分)
        # ----------------------------------------------------------------------
        ("7-2-3", "填空題", "星號乘法倍數生成指定長度 (line)", 6,
         lambda g: (
             (True, "字串乘法快速生成 10 顆星號成功！")
             if (g.get("line") == "**********" and len(g.get("line", "")) == 10) or
                ('"*"' in history_str and "* 10" in history_str) or
                ("'*'" in history_str and "*10" in history_clean)
             else (False, "請在 7-2-3 填空題填入 * 乘法運算子與倍數 10！")
         )),

        ("7-2-3", "練習題", "遊戲血條進度條繪製 ([####------])", 9,
         lambda g: (
             (True, "現有血量 '#' 與缺損血量 '-' 乘法繪製正確！")
             if ("#" in history_str and "-" in history_str and ("[" in history_str or "current_hp" in history_str)) or
                ("[####------]" in history_str or "[########]" in history_str)
             else (False, "請讀入 current_hp 與 max_hp，用 '#' 與 '-' 繪製血條進度條！")
         )),

        ("7-2-3", "挑戰題", "密碼遮罩產生器 (星號重複 len 次)", 5,
         lambda g: (
             (True, "密碼長度計算與星號遮罩產生正確！")
             if ("len(" in history_str and "*" in history_str and ("Masked:" in history_str or "password" in history_str)) or
                ("Masked:" in history_str and "Length:" in history_str)
             else (False, "請計算密碼長度，並印出長度相同的星號遮罩字串！")
         )),

        # ----------------------------------------------------------------------
        # 7-2-4 複合運算優先權與小括號 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-2-4", "填空題", "小括號強制加法優先於乘法 (wave)", 6,
         lambda g: (
             (True, "小括號強制包裹字串加法優先運算成功！")
             if g.get("wave") == "~*~~*~~*~" or
                ('("~" + "*" + "~") * 3' in history_clean or "('~'+'*'+'~')*3" in history_clean)
             else (False, "請在 7-2-4 填空題使用小括號將加法部分包裹：(\"~\" + \"*\" + \"~\") * 3！")
         )),

        ("7-2-4", "練習題", "連續燈泡序列產生器 (<--(*)...(*)-->)", 9,
         lambda g: (
             (True, "左右箭頭與 k 組燈泡單元排列正確！")
             if ("<--" in history_str and "-->" in history_str and "(*)" in history_str) or
                ("<--(*)(*)(*)-->" in history_str or "<--(*)-->" in history_str)
             else (False, "請輸入 k，輸出左右有箭頭且包含 k 組 (*) 的燈串！")
         )),

        ("7-2-4", "挑戰題", "棋盤格子花紋產生器 (n 行 m 組 #.)", 5,
         lambda g: (
             (True, "棋盤 pattern 單元乘法與多行迴圈輸出正確！")
             if ("#." in history_str and "for" in history_str and ("range(" in history_str or "*" in history_str)) or
                ("#.#.#.#." in history_str)
             else (False, "請輸入 n 與 m，使用迴圈輸出 n 行由 m 組 '#.' 組成的棋盤花紋！")
         )),

        # ----------------------------------------------------------------------
        # 7-2-5 字串乘法在 APCS 幾何圖形之應用 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-2-5", "填空題", "奇數星號對稱金字塔計算 (stars = '*' * (2*i - 1))", 6,
         lambda g: (
             (True, "奇數星號計算式 (2 * i - 1) 填寫正確！")
             if ("2 * i - 1" in history_str or "2*i-1" in history_clean or "2*i - 1" in history_str) and
                ("spaces" in history_str and "stars" in history_str)
             else (False, "請在 7-2-5 填空題空格填入奇數算式 2 * i - 1！")
         )),

        ("7-2-5", "練習題", "倒立靠左直角三角形 (單層迴圈字串乘法)", 9,
         lambda g: (
             (True, "倒立直角三角形星號遞減輸出正確！")
             if ("*" in history_str and "range(" in history_str and ("-1" in history_str or "n - i" in history_str or "n-i" in history_clean)) or
                ("****\n***\n**\n*" in history_str or "***\n**\n*" in history_str)
             else (False, "請輸入 n，使用單層迴圈搭配字串乘法印出倒立直角三角形！")
         )),

        ("7-2-5", "挑戰題", "數字沙漏對稱圖案 (# 縮排對稱展開)", 5,
         lambda g: (
             (True, "對稱沙漏圖形空格式縮排與展開設計完整！")
             if ("#" in history_str and "range(" in history_str and ("spaces" in history_str or " " in history_str)) or
                ("#####\n ###\n  #\n ###\n#####" in history_str)
             else (False, "請輸入奇數 n，以字串乘法與迴圈印出對稱沙漏圖形！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-2 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通字串加法拼接、+= 迴圈黏接、乘法重複與幾何圖形構造，字符魔術師！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，字串累加與圖案規律掌握紮實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調轉型與運算優先權！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-2",
        "unit_title": "字串拼接與重複運算",
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
        log_filename = "score_log_unit_7_2.json"
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
auto_grade_unit_7_2()
