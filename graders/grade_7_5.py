# ==============================================================================
# 🧪 《PythAPCS123》單元 7-5：字串切片與反轉 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_7_5.py
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

def auto_grade_unit_7_5():
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
        # 7-5-1 左閉右開基礎切片 s[start:stop] (共 20 分)
        # ----------------------------------------------------------------------
        ("7-5-1", "填空題", "左閉右開基礎切片 code[1:5] (sub_code)", 6,
         lambda g: (
             (True, "基礎切片 code[1:5] 提取 '1234' 完全正確！")
             if g.get("sub_code") == "1234" or
                ("code[1:5]" in history_clean)
             else (False, "請在 7-5-1 填空題空格填入起點 1 與終點 5！")
         )),

        ("7-5-1", "練習題", "生日年月日字串解析器 (Year, Month, Day)", 9,
         lambda g: (
             (True, "生日 8 碼切片解析西元、月份與日期輸出正確！")
             if (("[:4]" in history_str or "[0:4]" in history_str) and
                 ("[4:6]" in history_str) and
                 ("[6:8]" in history_str or "[6:]" in history_str)) or
                ("Year: 2008, Month: 05, Day: 12" in history_str or "Year: 2011, Month: 10, Day: 09" in history_str)
             else (False, "請使用切片分別截取前 4 碼、中 2 碼與後 2 碼並依格式輸出！")
         )),

        ("7-5-1", "挑戰題", "子字串雷達滑動切片比對 (Count: 3)", 5,
         lambda g: (
             (True, "滑動切片 s[i:i+3] 子字串次數統計正確！")
             if ("[i:i+3]" in history_clean or "[i:i+len(" in history_clean) and
                ("Count:" in history_str or "target" in history_str)
             else (False, "請以迴圈搭配滑動切片 s[i:i+3] 統計 target 出現次數！")
         )),

        # ----------------------------------------------------------------------
        # 7-5-2 省略起點或終點的俐落切片 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-5-2", "填空題", "省略終點之截取切片 url[8:] (domain)", 6,
         lambda g: (
             (True, "省略終點之切片 url[8:] 提取成功！")
             if g.get("domain") == "apcs.tw" or
                ("url[8:]" in history_clean)
             else (False, "請在 7-5-2 填空題填入起點 8 截取到字串結尾！")
         )),

        ("7-5-2", "練習題", "身分資訊遮罩產生器 (id_str[:2] + '*****' + id_str[7:])", 9,
         lambda g: (
             (True, "身分代號前後保留與中間星號遮罩拼接正確！")
             if (("[:2]" in history_str or "[0:2]" in history_str) and
                 ("*****" in history_str) and
                 ("[7:]" in history_str or "[-3:]" in history_str)) or
                ("A1*****789" in history_str or "B9*****321" in history_str)
             else (False, "請以切片保留前 2 碼與後 3 碼，中間替換為 ***** 輸出！")
         )),

        ("7-5-2", "挑戰題", "前後截斷對齊器 (前 k 與後 k 字元以 --- 串接)", 5,
         lambda g: (
             (True, "前 k 個字元與後 k 個字元截取與 --- 拼接正確！")
             if ("[:k]" in history_str or "[: k]" in history_str) and
                ("[-k:]" in history_str or "[len(s)-k:]" in history_clean) and
                ("---" in history_str)
             else (False, "請截取 s 前 k 個字元與後 k 個字元，以 --- 連接輸出！")
         )),

        # ----------------------------------------------------------------------
        # 7-5-3 步進切片 s[start:stop:step] (共 20 分)
        # ----------------------------------------------------------------------
        ("7-5-3", "填空題", "奇數索引跳躍步進切片 secret[1::2] (real_info)", 6,
         lambda g: (
             (True, "步進切片 secret[1::2] 解鎖情報成功！")
             if g.get("real_info") == "APCS!" or
                ("secret[1::2]" in history_clean)
             else (False, "請在 7-5-3 填空題空格填入起點 1 與步進值 2！")
         )),

        ("7-5-3", "練習題", "雙軌字串分離器 (Track A [::2] 與 Track B [1::2])", 9,
         lambda g: (
             (True, "偶數軌 [::2] 與奇數軌 [1::2] 雙軌分離輸出正確！")
             if ("[::2]" in history_str and "[1::2]" in history_str and
                 ("Track A:" in history_str and "Track B:" in history_str)) or
                ("1234" in history_str and "abcd" in history_str)
             else (False, "請分別以 s[::2] 與 s[1::2] 輸出 Track A 與 Track B！")
         )),

        ("7-5-3", "挑戰題", "APCS 經典秘密差計算 (abs(odd_sum - even_sum))", 5,
         lambda g: (
             (True, "奇偶位步進切片取和與 abs() 差值計算正確！")
             if ("abs(" in history_str and ("[1::2]" in history_str or "[::2]" in history_str)) or
                ("Secret Diff:" in history_str)
             else (False, "請利用切片分別求奇偶位數字和，並以 abs() 印出秘密差！")
         )),

        # ----------------------------------------------------------------------
        # 7-5-4 步進為負之字串全反轉 s[::-1] (共 20 分)
        # ----------------------------------------------------------------------
        ("7-5-4", "填空題", "全字串反轉切片 word[::-1] (dessert)", 6,
         lambda g: (
             (True, "字串全反轉 word[::-1] 成功將 stressed 翻轉為 desserts！")
             if g.get("dessert") == "desserts" or
                ("word[::-1]" in history_clean)
             else (False, "請在 7-5-4 填空題空格填入 ::-1 進行全字串反轉！")
         )),

        ("7-5-4", "練習題", "整數反轉相加器 (n + int(n[::-1]))", 9,
         lambda g: (
             (True, "數字字串反轉 [::-1] 與整數總和計算正確！")
             if (("[::-1]" in history_str and "int(" in history_str and "+" in history_str)) or
                ("444" in history_str or "606" in history_str)
             else (False, "請讀入數字字串 n，以 [::-1] 反轉後轉為整數計算兩者總和！")
         )),

        ("7-5-4", "挑戰題", "前半段保持後半段反轉拼接 (s[:mid] + s[mid:][::-1])", 5,
         lambda g: (
             (True, "中點分割與後半段反轉拼裝輸出正確！")
             if ("// 2" in history_str or "//2" in history_clean) and
                ("[:" in history_str and "[::-1]" in history_str)
             else (False, "請將單字對半切分，前半段保持、後半段反轉後拼裝印出！")
         )),

        # ----------------------------------------------------------------------
        # 7-5-5 迴文判定（Palindrome）與進階應用 (共 20 分)
        # ----------------------------------------------------------------------
        ("7-5-5", "填空題", "切片迴文快速判定 candidate == candidate[::-1] (verdict)", 6,
         lambda g: (
             (True, "candidate[::-1] 迴文比對判定正確！")
             if g.get("verdict") == "YES" or
                ("candidate[::-1]" in history_clean)
             else (False, "請在 7-5-5 填空題中括號內填入 ::-1！")
         )),

        ("7-5-5", "練習題", "迴文判定與長度通報 (YES [len] / NO [len])", 9,
         lambda g: (
             (True, "迴文檢測與字串長度格式通報正確！")
             if (("[::-1]" in history_str or "==" in history_str) and
                 ("YES" in history_str or "NO" in history_str) and "len(" in history_str) or
                ("YES 5" in history_str or "NO 5" in history_str)
             else (False, "請檢測單字是否為迴文，依規格輸出 YES [長度] 或 NO [長度]！")
         )),

        ("7-5-5", "挑戰題", "最少追加字元構造迴文 (ALREADY / Palindrome)", 5,
         lambda g: (
             (True, "經典最少字元構造迴文邏輯判斷完整！")
             if ("ALREADY PALINDROME" in history_str or "Palindrome:" in history_str) or
                ("s[1:]" in history_clean and "[::-1]" in history_str)
             else (False, "請檢驗 s 及 s[1:] 是否為迴文，構造出最短迴文字串！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 7-5 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通左閉右開切片、步進提取、[::-1] 反轉與迴文演算法，字串刀客！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，切片起訖與步進思維清晰敏銳！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調切片索引與左閉右開邊界！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "7-5",
        "unit_title": "字串切片與反轉",
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
        log_filename = "score_log_unit_7_5.json"
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
auto_grade_unit_7_5()
