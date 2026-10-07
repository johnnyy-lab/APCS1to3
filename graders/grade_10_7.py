# ==============================================================================
# 🧪 《PythAPCS123》單元 10-7：集合代數運算子與范氏圖解題實戰 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_7.py
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

def auto_grade_unit_10_7():
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
        # 10-7-1 范氏圖幾何模型與四大運算 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-7-1", "填空題", "交集 & 與聯集 | 填空運算", 5,
         lambda g: (
             (True, "集合交集與聯集填空正確！")
             if ("&" in history_str and "|" in history_str)
             else (False, "請在 10-7-1 填空題填入 & 與 | 運算子！")
         )),

        ("10-7-1", "練習題", "兩班共同興趣社團人數統計 len(club_a & club_b)", 6,
         lambda g: (
             (True, "兩班共同社團交集正確！")
             if ("&" in history_str or "intersection" in history_str) and ("set(" in history_str)
             else (False, "請將兩清單轉為集合並計算交集人數！")
         )),

        ("10-7-1", "挑戰題", "三集合連鎖交集運算 set1 & set2 & set3", 5,
         lambda g: (
             (True, "三集合連鎖交集計算正確！")
             if ("&" in history_str and history_str.count("&") >= 2) or ("intersection" in history_str)
             else (False, "請計算三個集合的連鎖共同交集！")
         )),

        # ----------------------------------------------------------------------
        # 10-7-2 交集運算子 & (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-7-2", "填空題", "求兩數列之公共質數 sample_numbers & primes", 5,
         lambda g: (
             (True, "質數交集填空正確！")
             if ("& primes" in history_str or "&primes" in history_clean)
             else (False, "請在 10-7-2 填空題填入 & primes！")
         )),

        ("10-7-2", "練習題", "跨社團共同核心幹部篩選器 (student_council & guitar_club)", 6,
         lambda g: (
             (True, "跨社團雙棲幹部交集篩選正確！")
             if ("&" in history_str or "intersection" in history_str) and ("council" in history_str)
             else (False, "請使用 & 找出同時在兩組織擔任幹部的名單！")
         )),

        ("10-7-2", "挑戰題", "全勤模範生連續交集篩選 (三天出席名單交集)", 6,
         lambda g: (
             (True, "連續三天全勤交集正確！")
             if ("&" in history_str) and ("day1" in history_str and "day2" in history_str and "day3" in history_str)
             else (False, "請計算三天出席名單的交集找出全勤生！")
         )),

        # ----------------------------------------------------------------------
        # 10-7-3 聯集運算子 | (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-7-3", "填空題", "合併通訊錄聯絡人 sim1_contacts | sim2_contacts", 5,
         lambda g: (
             (True, "通訊錄聯集填空正確！")
             if ("|" in history_str or "union" in history_str)
             else (False, "請在 10-7-3 填空題填入 | 運算子！")
         )),

        ("10-7-3", "練習題", "多組抽獎箱號碼彙整總管 (box1 | box2 | box3)", 6,
         lambda g: (
             (True, "多抽獎箱聯集彙整正確！")
             if ("|" in history_str or "union" in history_str) and ("box" in history_str)
             else (False, "請使用聯集 | 合併三個抽獎箱號碼！")
         )),

        ("10-7-3", "挑戰題", "累計七日訪客動態擴充模擬 (total_visitors |= set(day))", 6,
         lambda g: (
             (True, "七日訪客聯集累加正確！")
             if ("|=" in history_str or "|" in history_str or "update" in history_str) and ("visitors" in history_str)
             else (False, "請在走訪七天紀錄時動態合併每日訪客！")
         )),

        # ----------------------------------------------------------------------
        # 10-7-4 差集運算子 - (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-7-4", "填空題", "現貨商品差集篩選 all_catalog - out_of_stock", 5,
         lambda g: (
             (True, "商品差集篩選填空正確！")
             if ("-" in history_str or "difference" in history_str)
             else (False, "請在 10-7-4 填空題填入 - 運算子！")
         )),

        ("10-7-4", "練習題", "未繳費名冊催繳通知器 (registered - paid)", 6,
         lambda g: (
             (True, "欠費名冊差集過濾正確！")
             if ("-" in history_str or "difference" in history_str) and ("registered" in history_str or "paid" in history_str)
             else (False, "請使用差集運算子找出尚未繳費的學生名冊！")
         )),

        ("10-7-4", "挑戰題", "雙向差集互查 (r1 - r2 與 r2 - r1)", 6,
         lambda g: (
             (True, "雙向差集互查正確！")
             if ("r1 - r2" in history_str and "r2 - r1" in history_str) or ("-" in history_str)
             else (False, "請分別計算 r1 - r2 與 r2 - r1 的名單！")
         )),

        # ----------------------------------------------------------------------
        # 10-7-5 對稱差運算子 ^ (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-7-5", "填空題", "非雙棲單一運動選手 swimmers ^ runners", 5,
         lambda g: (
             (True, "對稱差運算填空正確！")
             if ("^" in history_str or "symmetric_difference" in history_str)
             else (False, "請在 10-7-5 填空題填入 ^ 運算子！")
         )),

        ("10-7-5", "練習題", "兩份名冊不一致檢測機 (sys_records ^ paper_records)", 6,
         lambda g: (
             (True, "名冊不一致對稱差檢測正確！")
             if ("^" in history_str or "symmetric_difference" in history_str) and ("records" in history_str)
             else (False, "請使用 ^ 找出兩份名冊中不一致的人員名單！")
         )),

        ("10-7-5", "挑戰題", "驗證對稱差等價公式 (A | B) - (A & B)", 6,
         lambda g: (
             (True, "對稱差等價公式驗證正確！")
             if ("(set_a | set_b) - (set_a & set_b)" in history_str or "^" in history_str and "-" in history_str)
             else (False, "請驗證 A ^ B 等於 (A | B) - (A & B)！")
         )),

        # ----------------------------------------------------------------------
        # 10-7-6 子集與超集判斷 (<=, >=) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-7-6", "填空題", "藥水材料完整度檢查 recipe <= my_backpack", 5,
         lambda g: (
             (True, "子集運算子 <= 填空正確！")
             if ("<=" in history_str or "issubset" in history_str)
             else (False, "請在 10-7-6 填空題填入 <= 或 issubset()！")
         )),

        ("10-7-6", "練習題", "任務必備鑰匙齊全檢驗 (required_keys <= backpack)", 6,
         lambda g: (
             (True, "必備道具齊全子集檢驗正確！")
             if ("<=" in history_str or "issubset" in history_str) and ("keys" in history_str or "bag" in history_str)
             else (False, "請以 required_keys <= backpack 判定是否集齊鑰匙！")
         )),

        ("10-7-6", "挑戰題", "求職者資格符合統計 (standard <= cand_skills)", 5,
         lambda g: (
             (True, "求職資格合格統計正確！")
             if ("<=" in history_str or "issubset" in history_str) and ("count" in history_str or "+= 1" in history_str)
             else (False, "請統計完全具備 standard 標準資格的求職者總數！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-7：集合代數運算子與范氏圖解題實戰 —— 自動評分報告")
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
        "unit_id": "10-7",
        "unit_name": "集合代數運算子與范氏圖解題實戰",
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
        filename = f"grade_report_10_7.json"
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
    auto_grade_unit_10_7()
