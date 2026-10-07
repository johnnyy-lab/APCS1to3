# ==============================================================================
# 🧪 《PythAPCS123》單元 7-1：字串表示法與跳脫字元 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_1.py
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

def auto_grade_unit_7_1():
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
        # 7-1-1 單引號與雙引號宣告 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-1-1", "填空題", "成對引號字串宣告 (potion_name, spell_incantation)", 6,
         lambda g: (
             (True, "成對引號宣告完全正確：potion_name 與 spell_incantation 正確賦值！")
             if (g.get("potion_name") == "Healing Potion" and g.get("spell_incantation") == "Abracadabra") or
                ('"Healing Potion"' in history_str and "'Abracadabra'" in history_str)
             else (False, "請在 7-1-1 填空題空格填入成對的單引號或雙引號並點擊播放鍵 ▶ 執行！")
         )),

        ("7-1-1", "練習題", "冒險者公會身份卡格式輸出 (Adventurer, Rank)", 9,
         lambda g: (
             (True, "冒險者代號與等級輸出格式正確！")
             if ("Adventurer:" in history_str and "Rank:" in history_str) or
                ("Adventurer" in history_str and "code_name" in history_str)
             else (False, "請讀入 code_name 與 level，並依格式輸出 Adventurer: [代號], Rank: [等級]！")
         )),

        ("7-1-1", "挑戰題", "城市密碼驗證器 (Avalon / MagicPass)", 5,
         lambda g: (
             (True, "城市與密碼雙重比對條件式撰寫正確！")
             if (("Avalon" in history_str and "MagicPass" in history_str) and
                 ("ACCESS GRANTED" in history_str or "ACCESS DENIED" in history_str)) or
                ("city" in g and "password" in g and "ACCESS" in history_str)
             else (False, "請輸入 city 與 password，當 city=='Avalon' 且 password=='MagicPass' 時輸出 ACCESS GRANTED！")
         )),

        # ----------------------------------------------------------------------
        # 7-1-2 引號互套免跳脫（外單內雙、外雙內單） (共 20 分)
        # ----------------------------------------------------------------------
        ("7-1-2", "填空題", "引號互套無衝突賦值 (sentence1, sentence2)", 6,
         lambda g: (
             (True, "外單內雙與外雙內單引號互套成功！")
             if (g.get("sentence1") == "It's time to level up!" and g.get("sentence2") == 'He shouted: "Victory!"') or
                ("It's time to level up!" in history_str and 'He shouted: "Victory!"' in history_str)
             else (False, "請在 7-1-2 填空題外部填入合適的外雙內單或外單內雙引號！")
         )),

        ("7-1-2", "練習題", "歷史名人名言錄引述雙引號排版", 9,
         lambda g: (
             (True, "名人座右銘雙引號包裹輸出正確！")
             if ('"Keep moving forward."' in history_str or 'Keep moving forward.' in history_str) and
                ("once said:" in history_str)
             else (False, "請輸入 speaker 並輸出 [speaker] once said: \"Keep moving forward.\"！")
         )),

        ("7-1-2", "挑戰題", "英文日記造句機 (Today's, I'm 單引號處理)", 5,
         lambda g: (
             (True, "英文縮寫單引號造句輸出正確！")
             if ("Today's" in history_str and "I'm" in history_str) or
                ("Today\'s" in history_str and "I\'m" in history_str)
             else (False, "請處理包含 Today's 與 I'm 的造句字串並正確輸出！")
         )),

        # ----------------------------------------------------------------------
        # 7-1-3 常用跳脫字元：換行 \n 與跳格 \t (共 20 分)
        # ----------------------------------------------------------------------
        ("7-1-3", "填空題", "跳脫字元表格卡片排版 (card 包含 \\t 與 \\n)", 6,
         lambda g: (
             (True, "正確運用 \\t 水平跳格與 \\n 換行排版！")
             if g.get("card") == "Name\tAlice\nScore\t95" or
                (r"\t" in history_str and r"\n" in history_str and "Alice" in history_str)
             else (False, "請在 7-1-3 填空題空格處正確填入 \\t 與 \\n！")
         )),

        ("7-1-3", "練習題", "自動收據生成器兩行跳格排版 (Item, Price)", 9,
         lambda g: (
             (True, "收據項目與價格換行及跳格排版正確！")
             if ("Item:" in history_str and "Price:" in history_str and (r"\t" in history_str or "\t" in history_str or r"\n" in history_str)) or
                ("price1" in g or "price2" in g or "item1" in g)
             else (False, "請讀入兩組項目與價格，以 \\n 換行與 \\t 跳格輸出收據清單！")
         )),

        ("7-1-3", "挑戰題", "倒數計時多行告示牌 (跳格 \\t 與換行 GO!)", 5,
         lambda g: (
             (True, "倒數數字 \\t 間隔與 GO! 結尾設計正確！")
             if ("GO!" in history_str and (r"\t" in history_str or "\t" in history_str or "end=" in history_str)) or
                ("range(" in history_str and "GO!" in history_str)
             else (False, "請由 n 倒數至 1，以 \\t 分隔輸出，最後換行輸出 GO!！")
         )),

        # ----------------------------------------------------------------------
        # 7-1-4 特殊跳脫：反斜線 \\ 與同類引號 \" (共 20 分)
        # ----------------------------------------------------------------------
        ("7-1-4", "填空題", "雙引號與反斜線跳脫字元 (quote_text)", 6,
         lambda g: (
             (True, "雙引號 \\\" 與反斜線 \\\\ 跳脫完全符合要求！")
             if g.get("quote_text") == 'He said: "It\'s cool!" \\(^_^)/' or
                (r'\"' in history_str and r'\\' in history_str and "cool" in history_str)
             else (False, "請在 7-1-4 填空題空格填入 \\\" 與 \\\\ 完成跳脫！")
         )),

        ("7-1-4", "練習題", "系統完整檔案路徑反斜線拼裝", 9,
         lambda g: (
             (True, "Windows 路徑反斜線與雙引號狀態訊息正確！")
             if (r"\Projects\APCS" in history_str or r":\Projects" in history_str or "Projects\\APCS" in history_str) and
                ("Status: File" in history_str or "ready!" in history_str)
             else (False, "請讀入 disk 與 filename，組裝 Windows 反斜線路徑並輸出 Status 訊息！")
         )),

        ("7-1-4", "挑戰題", "屋頂小房子 ASCII 圖案輸出", 5,
         lambda g: (
             (True, "ASCII 小房子幾何圖案繪製完整！")
             if ("/\\" in history_str or "/  \\" in history_str or "\\\\\"" in history_str or
                 ("| \"\" |" in history_str or "|____|" in history_str) or
                 ("\\" in history_str and "|" in history_str))
             else (False, "請使用 print() 輸出包含屋頂與窗戶的小房子 ASCII 藝術圖形！")
         )),

        # ----------------------------------------------------------------------
        # 7-1-5 三引號多行字串：保留完整排版 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-1-5", "填空題", "三引號多行公告文字 (announcement)", 6,
         lambda g: (
             (True, "三引號多行公告宣告成功！")
             if (isinstance(g.get("announcement"), str) and
                 "【公會公告】" in g.get("announcement") and "維護時間" in g.get("announcement")) or
                ('"""' in history_str and "【公會公告】" in history_str)
             else (False, "請在 7-1-5 填空題前後空格填入連續 3 個引號（\"\"\" 或 \'''）！")
         )),

        ("7-1-5", "練習題", "冒險餐館當日菜單三引號排版 (TODAY'S MENU)", 9,
         lambda g: (
             (True, "三引號菜單多行格式排版輸出正確！")
             if ("TODAY'S MENU" in history_str or "TODAY\'S MENU" in history_str) and
                ("Special:" in history_str and "Price:" in history_str)
             else (False, "請讀入 dish 與 price，以多行三引號字串輸出 TODAY'S MENU 菜單！")
         )),

        ("7-1-5", "挑戰題", "懸賞通緝令多行海報排版 (WANTED 海報)", 5,
         lambda g: (
             (True, "WANTED 懸賞通緝令多行海報設計完整！")
             if ("WANTED" in history_str and ("target_name" in history_str or "bounty" in history_str or '"""' in history_str)) or
                ("WANTED" in history_str and ("target_name" in g or "bounty" in g))
             else (False, "請以多行字串設計包含 WANTED 標題、代號與賞金的通緝海報！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-1 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通字串表示法、引號互套、跳脫字元與三引號排版，文字塑形功力超群！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，跳脫字元與多行排版思維清晰敏銳！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調引號與跳脫細節！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-1",
        "unit_title": "字串表示法與跳脫字元",
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
        log_filename = "score_log_unit_7_1.json"
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
auto_grade_unit_7_1()
