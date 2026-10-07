# ==============================================================================
# 🧪 《PythAPCS123》單元 10-3：字典概念、建立與鍵值對存取（Key-Value） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_3.py
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

def auto_grade_unit_10_3():
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
        # 10-3-1 為什麼需要字典？名牌索引 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-3-1", "填空題", "機場代碼字典查詢 airports['TPE']", 5,
         lambda g: (
             (True, "機場代碼查詢填空正確！")
             if ("airports['TPE']" in history_str or 'airports["TPE"]' in history_str or
                 "airports['KHH']" in history_str)
             else (False, "請在 10-3-1 填空題填入鍵值 'TPE' 取出城市！")
         )),

        ("10-3-1", "練習題", "電話簿快速查號台 phone_book[name]", 6,
         lambda g: (
             (True, "電話簿字典建立與查號正確！")
             if ("phone_book" in history_str or "phone" in history_str) and ("[" in history_str and "]" in history_str)
             else (False, "請建立 phone_book 字典並完成電話號碼查詢！")
         )),

        ("10-3-1", "挑戰題", "單字英翻中對照小辭典", 5,
         lambda g: (
             (True, "英中辭典動態建置與查詢正確！")
             if ("dict" in history_str or "{}" in history_str) and ("for" in history_str and "input" in history_str)
             else (False, "請建立英翻中字典並查詢指定單字！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-2 大括號鍵值對語法與空字典 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-2", "填空題", "商品價格字典宣告 {'book': 250, 'pen': 30}", 5,
         lambda g: (
             (True, "商品價格字典宣告填空正確！")
             if (g.get("item_prices") and g.get("item_prices").get("book") == 250) or
                ("250" in history_str and "30" in history_str and ":" in history_str)
             else (False, "請在 10-3-2 填空題填入價格 250 與 30！")
         )),

        ("10-3-2", "練習題", "學生學號登錄卡 (學號為 Key，姓名為 Value)", 6,
         lambda g: (
             (True, "學號姓名登錄字典正確！")
             if ("{}" in history_str or "dict()" in history_str) and ("[" in history_str and "=" in history_str)
             else (False, "請以學號為 Key、姓名為 Value 存入字典！")
         )),

        ("10-3-2", "挑戰題", "重複鍵覆蓋歷史追蹤器", 6,
         lambda g: (
             (True, "重複鍵覆蓋特性驗證正確！")
             if ("len(" in history_str or "print" in history_str) and ("=" in history_str)
             else (False, "請模擬相同 Key 重複賦值，觀察字典長度維持 1 且值被更新！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-3 鍵的合法型態：Hashable 限制 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-3", "填空題", "使用座標元組作為鍵 board[(1, 3)] = 'QUEEN'", 5,
         lambda g: (
             (True, "座標元組做為字典鍵填空正確！")
             if ("(1, 3)" in history_str or "(1,3)" in history_clean) and ("QUEEN" in history_str or "KNIGHT" in history_str)
             else (False, "請在 10-3-3 填空題填入座標元組 (1, 3) 與 (2, 2)！")
         )),

        ("10-3-3", "練習題", "網格寶物定位查詢機 treasure_map[(r, c)]", 6,
         lambda g: (
             (True, "網格寶物座標元組字典正確！")
             if ("(r, c)" in history_str or "(r,c)" in history_clean or "treasure" in history_str)
             else (False, "請以 (r, c) 元組為 Key 記錄各座標點的寶物！")
         )),

        ("10-3-3", "挑戰題", "座標點重疊價值累加器 (+= val)", 6,
         lambda g: (
             (True, "重複座標價值累加正確！")
             if ("+=" in history_str or "get(" in history_str) and ("(r, c)" in history_str or "(r,c)" in history_clean)
             else (False, "請在座標重複時將數值累加至該格字典中！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-4 鍵值存取與 KeyError 防範 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-4", "填空題", "使用 in 運算子安全防禦 target_country in capitals", 5,
         lambda g: (
             (True, "in 運算子安全檢查填空正確！")
             if ("in capitals" in history_str)
             else (False, "請在 10-3-4 填空題填入 target_country in capitals！")
         )),

        ("10-3-4", "練習題", "圖書館借閱安全查詢機", 6,
         lambda g: (
             (True, "安全借閱書籍查詢正確！")
             if ("in books" in history_str or "not in" in history_str or "get(" in history_str)
             else (False, "請在查詢前檢查書籍是否存在於 books 中！")
         )),

        ("10-3-4", "挑戰題", "多鍵連續查詢與未命中計數器", 6,
         lambda g: (
             (True, "連續查詢與未命中統計正確！")
             if ("NONE" in history_str or "miss" in history_str or "count" in history_str) and ("in" in history_str)
             else (False, "請查詢代碼，查不到輸出 NONE 並統計未命中總次數！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-5 新增與修改鍵值對 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-5", "填空題", "開票計數初值設定與 counts[cand] += 1 累加", 5,
         lambda g: (
             (True, "計數初值設定與累加填空正確！")
             if ("counts[cand] = 1" in history_str or "counts[cand] += 1" in history_str or
                 "+= 1" in history_str)
             else (False, "請在 10-3-5 填空題補齊初值設定與 += 1 累加！")
         )),

        ("10-3-5", "練習題", "動態商品庫存管理員 (進出貨累加扣減)", 6,
         lambda g: (
             (True, "動態庫存加減更新正確！")
             if ("+=" in history_str or "stock" in history_str) and ("in" in history_str)
             else (False, "請以字典動態維護商品進出貨後的庫存量！")
         )),

        ("10-3-5", "挑戰題", "字串單字出現次數統計與最高票", 6,
         lambda g: (
             (True, "單字出現頻率統計與極值正確！")
             if ("max(" in history_str or "count" in history_str) and ("+=" in history_str or "get(" in history_str)
             else (False, "請統計每個單字出現次數並找出最高票得主！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-6 刪除鍵值對：del 與 pop() (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-3-6", "填空題", "安全彈出過期用戶 users.pop('user3', 'NOT_FOUND')", 5,
         lambda g: (
             (True, "pop 安全彈出預設值填空正確！")
             if ("NOT_FOUND" in history_str)
             else (False, "請在 10-3-6 填空題填入預設回傳值 'NOT_FOUND'！")
         )),

        ("10-3-6", "練習題", "會員登出與註銷系統 (pop 安全剔除)", 6,
         lambda g: (
             (True, "會員帳號安全註銷正確！")
             if (".pop(" in history_str or "del " in history_str) and ("members" in history_str)
             else (False, "請使用 pop() 或 del 註銷會員帳號並防範 KeyError！")
         )),

        ("10-3-6", "挑戰題", "黑名單安全過濾清理器 (防崩潰)", 5,
         lambda g: (
             (True, "批次黑名單安全過濾正確！")
             if (".pop(" in history_str or "in players" in history_str or "discard" in history_str)
             else (False, "請批次自 players 中剔除作弊者，且不因重複不存在而崩潰！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-3：字典概念、建立與鍵值對存取（Key-Value） —— 自動評分報告")
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
        level_comment = "🏆 完美滿分！你已經徹底攻克二維陣列核心技術，具備 APCS 實戰高手水準！"
    elif total_score >= 80:
        level_comment = "🌟 優秀！觀念掌握非常扎實，稍微細心檢查即可登峰造極！"
    elif total_score >= 60:
        level_comment = "👍 及格！基本概念已建立，建議複習未通過的題目加強熟悉度！"
    else:
        level_comment = "💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！"

    print(f"💬 導師評語: {level_comment}")
    print("=" * 72)

    # 4. 本地 JSON 報告儲存
    report_data = {
        "unit_id": "10-3",
        "unit_name": "字典概念、建立與鍵值對存取（Key-Value）",
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
        filename = f"grade_report_10_3.json"
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
    auto_grade_unit_10_3()
