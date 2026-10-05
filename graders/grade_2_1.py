# ==============================================================================
# 🧪 《PythAPCS123》單元 2-1：數值型態分類（整數與浮點數） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_1.py
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
        # 非 Colab 環境、無網路或學生略過授權
        return None, None

def auto_grade_unit_2_1():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生在表單自行輸入之姓名（中文全名或學號）
    declared_name = str(env.get("student_name", "")).strip()
    if not declared_name or declared_name == "自學冒險者":
        declared_name = "自學冒險者（未填姓名）"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info()

    # 3. 整合身分識別欄位
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 2-1-1 數字世界的兩大宗族——整數積木（int）與浮點果汁（float） (共 24 分)
        # ----------------------------------------------------------------------
        ("2-1-1", "填空題", "整數與浮點數外觀宣告 (my_int, my_float)", 7,
         lambda g: (
             (True, "成功建立整數積木 my_int=10 與浮點果汁 my_float=10.0！")
             if (g.get("my_int") == 10 and type(g.get("my_int")) is int and
                 g.get("my_float") == 10.0 and type(g.get("my_float")) is float)
             else (
                 (False, "my_float 必須是帶有小數點的浮點數 10.0，目前型態為整數 int 喔！")
                 if (g.get("my_int") == 10 and type(g.get("my_float")) is int)
                 else (False, "找不到變數 my_int=10 或 my_float=10.0，請在底線填入 10.0 並點擊播放鍵執行！")
             )
         )),

        ("2-1-1", "練習題", "價格與重量變數 (price_int, weight_float)", 10,
         lambda g: (
             (True, f"型態正確：price_int={g.get('price_int')} (int), weight_float={g.get('weight_float')} (float)")
             if ("price_int" in g and "weight_float" in g and
                 type(g.get("price_int")) is int and type(g.get("weight_float")) is float and
                 (g.get("price_int") in [85, 120] or g.get("price_int") > 0) and
                 (g.get("weight_float") in [2.5, 0.75] or g.get("weight_float") > 0))
             else (
                 (False, "price_int 必須是純整數（int），請勿加上小數點！")
                 if ("price_int" in g and type(g.get("price_int")) is float)
                 else (
                     (False, "weight_float 必須是帶有小數點的浮點數（float）！")
                     if ("weight_float" in g and type(g.get("weight_float")) is int)
                     else (False, "找不到變數 price_int 或 weight_float，請依練習題說明宣告並設定數值！")
                 )
             )
         )),

        ("2-1-1", "挑戰題", "圓周率與半徑宣告 (pi, r)", 7,
         lambda g: (
             (True, f"常數宣告正確：pi={g.get('pi')} (float), r={g.get('r')} (int)")
             if ("pi" in g and "r" in g and
                 type(g.get("pi")) is float and 3.14 <= g.get("pi") <= 3.1416 and
                 type(g.get("r")) is int and g.get("r") == 5)
             else (
                 (False, "半徑 r 題目指定為整數 5，請勿寫成浮點數 5.0！")
                 if ("r" in g and type(g.get("r")) is float)
                 else (
                     (False, "圓周率 pi 必須是浮點數（如 3.14159）！")
                     if ("pi" in g and type(g.get("pi")) is int)
                     else (False, "找不到變數 pi=3.14159 或 r=5，請依挑戰題說明宣告並執行！")
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-2 查驗身分的照妖鏡——認識內建型態檢查工具 type() (共 24 分)
        # ----------------------------------------------------------------------
        ("2-1-2", "填空題", "type() 照妖鏡檢驗浮點數 num", 7,
         lambda g: (
             (True, f"照妖鏡檢驗成功：num={g.get('num')} 身分型態為 <class 'float'>！")
             if ("num" in g and g.get("num") == 99.9 and type(g.get("num")) is float)
             else (False, "找不到變數 num=99.9，請確認在填空處填入 type 並執行！")
         )),

        ("2-1-2", "練習題", "自訂數值型態檢驗 sample_val", 10,
         lambda g: (
             (True, f"成功建立數值 sample_val={g.get('sample_val')}，其型態為 {type(g.get('sample_val')).__name__}！")
             if ("sample_val" in g and type(g.get("sample_val")) in [int, float])
             else (False, "找不到數值變數 sample_val，請建立整數或浮點數 sample_val（如 7 或 7.0）！")
         )),

        ("2-1-2", "挑戰題", "三數型態對比 (v1=0, v2=0.0, v3=-50)", 7,
         lambda g: (
             (True, f"三數型態透視成功：v1=0 (int), v2=0.0 (float), v3=-50 (int)！")
             if ("v1" in g and "v2" in g and "v3" in g and
                 g.get("v1") == 0 and type(g.get("v1")) is int and
                 g.get("v2") == 0.0 and type(g.get("v2")) is float and
                 g.get("v3") == -50 and type(g.get("v3")) is int)
             else (
                 (False, "v2 必須是帶小數點的浮點數 0.0，不可省略小數點！")
                 if ("v2" in g and type(g.get("v2")) is int)
                 else (
                     (False, "v1 必須是純整數 0，請勿寫成 0.0！")
                     if ("v1" in g and type(g.get("v1")) is float)
                     else (False, "找不到變數 v1=0, v2=0.0, v3=-50，請依挑戰題說明宣告並執行！")
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-3 染紅效應——整數與浮點數混合運算自動晉升為浮點數 (共 26 分)
        # ----------------------------------------------------------------------
        ("2-1-3", "填空題", "整數乘以 1.0 自動染紅晉升 (val = 8.0)", 7,
         lambda g: (
             (True, "染紅成功！8 * 1.0 晉升為浮點數 val = 8.0（<class 'float'>）")
             if ("val" in g and g.get("val") == 8.0 and type(g.get("val")) is float)
             else (
                 (False, "val 目前是整數 8，請在填空處乘以浮點數 1.0 觸發晉升為 8.0！")
                 if ("val" in g and g.get("val") == 8 and type(g.get("val")) is int)
                 else (False, "找不到變數 val，請在填空處填入 1.0 並點擊播放鍵執行！")
             )
         )),

        ("2-1-3", "練習題", "整數與浮點數混合相加 sum_val", 11,
         lambda g: (
             (True, f"混合相加染紅成功：sum_val = {g.get('sum_val')}（<class 'float'>）")
             if ("sum_val" in g and type(g.get("sum_val")) is float and
                 "a" in g and "b" in g and type(g.get("a")) is int and type(g.get("b")) is float and
                 abs(g.get("sum_val") - (g.get("a") + g.get("b"))) < 1e-9)
             else (
                 (False, "變數 b 必須是浮點數（例如 0.5 或 5.0），才能示範染紅晉升效應喔！")
                 if ("b" in g and type(g.get("b")) is int)
                 else (
                     (False, "變數 a 必須是純整數（int，例如 10 或 20）！")
                     if ("a" in g and type(g.get("a")) is float)
                     else (False, "找不到變數 a, b 或 sum_val，請宣告 a 與 b 並將 a + b 存入 sum_val！")
                 )
             )
         )),

        ("2-1-3", "挑戰題", "三數混合連加染紅 (ans_float = 10.0)", 8,
         lambda g: (
             (True, "三數連加染紅成功：ans_float = 10.0（整數 5 與 3 被 2.0 染紅為 float）！")
             if ("ans_float" in g and g.get("ans_float") == 10.0 and type(g.get("ans_float")) is float)
             else (
                 (True, "三數連加染紅成功：ans = 10.0（整數 5 與 3 被 2.0 染紅為 float）！")
                 if ("ans" in g and g.get("ans") == 10.0 and type(g.get("ans")) is float)
                 else (
                     (False, "檢測到變數 ans 被 2-1-4 填空題覆蓋為 5！在 2-1-3 挑戰題建議將變數命名為 ans_float = 5 + 3 + 2.0 避免覆蓋喔！")
                     if ("ans_float" not in g and g.get("ans") == 5)
                     else (
                         (False, "計算結果目前是純整數 10，算式中請包含 2.0 浮點數讓結果自動晉升為 10.0！")
                         if (g.get("ans_float") == 10 or g.get("ans") == 10)
                         else (False, "找不到變數 ans_float（或 ans=10.0），請寫出 5 + 3 + 2.0 計算並存入 ans_float！")
                     )
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-4 APCS 考場的致命失分陷阱——4.0 與 4 大不相同 (共 26 分)
        # ----------------------------------------------------------------------
        ("2-1-4", "填空題", "修正 3.0 為純整數 3 避免 WA (ans = 5)", 7,
         lambda g: (
             (True, "修正成功！ans = 3 + 2 得到純整數 5（<class 'int'>），成功避開 5.0 WA 陷阱！")
             if ("ans" in g and g.get("ans") == 5 and type(g.get("ans")) is int)
             else (
                 (False, "變數 ans 目前為浮點數 5.0！請將 3.0 修改為純整數 3，確保輸出為純整數 5！")
                 if ("ans" in g and (g.get("ans") == 5.0 or (g.get("ans") == 5 and type(g.get("ans")) is float)))
                 else (
                     (False, "變數 ans 目前仍為 10.0，請至 2-1-4 填空題執行 ans = 3 + 2 並點擊播放鍵！")
                     if ("ans" in g and g.get("ans") == 10.0)
                     else (False, "找不到變數 ans 或數值不為 5，請填入純整數 3 並點擊播放鍵執行！")
                 )
             )
         )),

        ("2-1-4", "練習題", "長寬與周長純整數運算 (length, width)", 11,
         lambda g: (
             (True, f"長寬與周長計算正確：length={g.get('length')}, width={g.get('width')}（周長 {(g.get('length')+g.get('width'))*2}，純整數）")
             if ("length" in g and "width" in g and
                 type(g.get("length")) is int and type(g.get("width")) is int and
                 g.get("length") > 0 and g.get("width") > 0 and
                 not any(isinstance(g.get(k), float) for k in ["perimeter", "peri", "ans_p"] if k in g))
             else (
                 (False, "題目要求輸入都是整數，length 與 width 必須是純整數（int），請勿加上小數點！")
                 if (("length" in g and type(g.get("length")) is float) or ("width" in g and type(g.get("width")) is float))
                 else (
                     (False, "檢測到周長變數為浮點數，在 APCS 輸出帶小數點會被判 WA 喔！請確保計算過程不使用浮點數！")
                     if any(isinstance(g.get(k), float) for k in ["perimeter", "peri", "ans_p"] if k in g)
                     else (False, "找不到變數 length 或 width，請依題目宣告長度與寬度純整數！")
                 )
             )
         )),

        ("2-1-4", "挑戰題", "破除 100.0 浮點陷阱維持整數 score", 8,
         lambda g: (
             (True, "完美修正！score = 100 為純正整數（<class 'int'>），成功避開 APCS 考場的 100.0 WA 陷阱！")
             if ("score" in g and g.get("score") == 100 and type(g.get("score")) is int)
             else (
                 (False, "變數 score 目前仍是浮點數 100.0！請不要乘以 1.0，改用純整數 100 * 1 或 score = 100，確保輸出為純整數！")
                 if ("score" in g and (g.get("score") == 100.0 or (g.get("score") == 100 and type(g.get("score")) is float)))
                 else (False, "找不到變數 score 或數值不為 100，請設定純整數 score = 100 並點擊播放鍵執行！")
             )
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-1：數值型態分類（整數與浮點數） —— 自動評分報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通整數與浮點數本質，考場零 WA！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，型態觀念清晰扎實！"
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
        "unit": "2-1",
        "unit_title": "數值型態分類（整數與浮點數）",
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
        log_filename = f"score_log_unit_2_1.json"
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
auto_grade_unit_2_1()
