# ==============================================================================
# 🧪 《PythAPCS123》單元 4-1：標準輸出 print() 基本語法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_1.py
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

def auto_grade_unit_4_1():
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
        # 4-1-1 print() 的初體驗——電腦的發聲大喇叭與字串輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-1-1", "填空題", "print() 字串輸出廣播歡迎語", 6,
         lambda g: (
             (True, "字串輸出指令正確：print('旗美廣播社早安，祝大家學習愉快！')！")
             if ("旗美廣播社" in history_str or
                 any("旗美廣播社" in str(v) for v in g.values()) or
                 g.get("radio_ok") is True)
             else (False, "請在 4-1-1 填空題空格填入 print 函數並點擊播放鍵執行！")
         )),

        ("4-1-1", "練習題", "社團口號變數宣告與輸出 (slogan)", 8,
         lambda g: (
             (True, f"口號變數宣告正確：slogan='{g.get('slogan')}'！")
             if ("slogan" in g and isinstance(g.get("slogan"), str) and len(g.get("slogan").strip()) > 0)
             else (False, "找不到變數 slogan，請將口號文字（如 'Coding is fun!'）賦值給 slogan 並印出！")
         )),

        ("4-1-1", "挑戰題", "數位名片座右銘變數與輸出 (my_motto)", 6,
         lambda g: (
             (True, f"數位名片座右銘設定完成：my_motto='{g.get('my_motto')}'！")
             if ("my_motto" in g and isinstance(g.get("my_motto"), str) and len(g.get("my_motto").strip()) > 0) or
                any(isinstance(v, str) and len(v) > 2 for k, v in g.items() if "motto" in k)
             else (False, "請宣告 my_motto 變數儲存激勵自己的座右銘，並使用 print() 印出！")
         )),

        # ----------------------------------------------------------------------
        # 4-1-2 print() 輸出數值與即時算術——讓喇叭播報運算結果 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-1-2", "填空題", "即時算術計算剩餘金額 (245)", 6,
         lambda g: (
             (True, "即時算術正確：500 - 85 * 3 = 245 元！")
             if ("pocket_money" in g and "book_price" in g and "books_count" in g and
                 g.get("pocket_money") - g.get("book_price") * g.get("books_count") == 245) or
                (any(v == 245 for v in g.values() if isinstance(v, (int, float)))) or
                ("pocket_money - book_price * books_count" in history_str)
             else (False, "請在 4-1-2 填空題空格處依序填入減號 - 與乘號 * 並執行！")
         )),

        ("4-1-2", "練習題", "文具特賣單價與數量乘積計算 (total_cost)", 8,
         lambda g: (
             (True, "文具總花費乘積計算正確！")
             if ("unit_price" in g and "quantity" in g and
                 isinstance(g.get("unit_price"), (int, float)) and
                 isinstance(g.get("quantity"), (int, float)) and
                 (any(v in [140, 360] for v in g.values() if isinstance(v, (int, float))) or
                  any(v == g['unit_price'] * g['quantity'] for v in g.values() if isinstance(v, (int, float))) or
                  "total_cost" in g))
             else (False, "找不到 unit_price 或 quantity，請計算 unit_price * quantity 並印出！")
         )),

        ("4-1-2", "挑戰題", "花圃矩形周長與面積純整數輸出 (length=18, width=7)", 6,
         lambda g: (
             (True, "花圃幾何計算正確：周長 50、面積 126！")
             if ("length" in g and "width" in g and g.get("length") == 18 and g.get("width") == 7) or
                (any(v == 50 for v in g.values() if isinstance(v, (int, float))) and
                 any(v == 126 for v in g.values() if isinstance(v, (int, float)))) or
                ("18" in history_str and "7" in history_str and "50" in history_str)
             else (False, "請宣告 length=18, width=7，分別印出周長 (18+7)*2=50 與面積 18*7=126！")
         )),

        # ----------------------------------------------------------------------
        # 4-1-3 逗號 `,` 串聯多個項目——預設單一空格隔開的神奇魔術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-1-3", "填空題", "逗號串聯模範生資料 (seat_num, student_name, award)", 6,
         lambda g: (
             (True, "逗號串聯成功：'座號', 12, '小美', '榮獲', '熱心服務獎'！")
             if (g.get("seat_num") == 12 and g.get("award") == "熱心服務獎") or
                ("熱心服務獎" in history_str and "," in history_str)
             else (False, "請在 4-1-3 填空題空格處填入半形逗號 , 分隔各引數並執行！")
         )),

        ("4-1-3", "練習題", "計分板兩隊名稱與比分 (team_a, score_a, team_b, score_b)", 8,
         lambda g: (
             (True, "比賽計分板各項目以逗號串聯印出正確！")
             if (all(k in g for k in ["team_a", "score_a", "team_b", "score_b"]) and
                 (g.get("score_a") in [88, 105] and g.get("score_b") in [79, 102])) or
                ("team_a, score_a, team_b, score_b" in history_str)
             else (False, "請宣告主客隊名稱與分數，並以逗號隔開在同一個 print() 中印出！")
         )),

        ("4-1-3", "挑戰題", "海圖座標與曼哈頓距離串聯輸出 (dist = 14)", 6,
         lambda g: (
             (True, "航海地圖座標與曼哈頓距離計算正確（距離 14 浬）！")
             if (all(k in g for k in ["x1", "y1", "x2", "y2"]) and
                 (abs(g['x1'] - g['x2']) + abs(g['y1'] - g['y2']) == 14)) or
                any(v == 14 for v in g.values() if isinstance(v, (int, float))) or
                ("寶藏座標" in history_str and "14" in history_str)
             else (False, "請宣告寶藏 (15, 20) 與海盜船 (9, 12)，計算曼哈頓距離 14 並以逗號串聯印出！")
         )),

        # ----------------------------------------------------------------------
        # 4-1-4 print() 的自動換行特質——每喊一次話就移至新的一行 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-1-4", "填空題", "連續三次 print() 垂直輸出遊戲選單", 6,
         lambda g: (
             (True, "連續換行成功：分行輸出遊戲主畫面三項選單！")
             if ("冒險王國選單" in history_str or
                 any("冒險王國選單" in str(v) for v in g.values()) or
                 g.get("menu_ok") is True)
             else (False, "請在 4-1-4 填空題空格填入 print 函數並點擊播放鍵執行！")
         )),

        ("4-1-4", "練習題", "商品明細分三行輸出 (item_name, item_price, discount)", 8,
         lambda g: (
             (True, "商品明細分行輸出變數設置正確！")
             if (all(k in g for k in ["item_name", "item_price", "discount"]) and
                 g.get("item_price") in [45, 38]) or
                ("巧克力餅乾" in history_str and "85折" in history_str)
             else (False, "請宣告商品名稱、單價與折數，並使用三個 print() 分行輸出！")
         )),

        ("4-1-4", "挑戰題", "三層星號階梯圖案 ASCII 輸出 (*, **, ***)", 6,
         lambda g: (
             (True, "三層向右星號階梯輸出正確！")
             if ("*" in history_str and "**" in history_str and "***" in history_str) or
                any(v in ["*", "**", "***"] for v in g.values()) or
                g.get("stars_ok") is True
             else (False, "請使用恰好 3 次 print()，垂直印出 *、**、*** 三層階梯！")
         )),

        # ----------------------------------------------------------------------
        # 4-1-5 不帶引數的 print()——空白行與段落視覺排版術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-1-5", "填空題", "不帶引數的 print() 空白行排版", 6,
         lambda g: (
             (True, "空行排版成功：print() 不帶引數產生乾淨間隔！")
             if ("歡迎登入 APCS" in history_str or
                 any("歡迎登入 APCS" in str(v) for v in g.values()) or
                 g.get("blank_line_ok") is True)
             else (False, "請在 4-1-5 填空題填入 print() 產生空白行並執行！")
         )),

        ("4-1-5", "練習題", "兩組公告訊息與中間空行分隔 (msg_top, msg_bottom)", 8,
         lambda g: (
             (True, "兩組公告與空行間隔輸出設定正確！")
             if ("msg_top" in g and "msg_bottom" in g and
                 isinstance(g.get("msg_top"), str) and isinstance(g.get("msg_bottom"), str)) or
                ("今日圖書館" in history_str and "大掃除" in history_str)
             else (False, "請宣告 msg_top 與 msg_bottom，並在兩次 print 之間插入一行 print()！")
         )),

        ("4-1-5", "挑戰題", "通關結算卡片視覺排版輸出", 6,
         lambda g: (
             (True, "通關結算卡片版面輸出成功！")
             if ("通關第 4-1 單元" in history_str or "通關" in history_str or
                 any("通關" in str(v) for v in g.values()) or
                 g.get("card_ok") is True)
             else (False, "請使用 print() 裝飾線、標題、空行 print() 與挑戰者資訊印出通關卡片！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-1：標準輸出 print() 基本語法 —— 自動評分報告")
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

        print(f"{icon} [{uid} {qtype}] {name:<32} ➔ {status}")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 print() 標準輸出，逗號串聯與空白行排版無懈可擊！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，print() 基本語法與版面分行邏輯清晰！"
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
        "unit": "4-1",
        "unit_title": "標準輸出 print() 基本語法",
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
        log_filename = "score_log_unit_4_1.json"
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
auto_grade_unit_4_1()
