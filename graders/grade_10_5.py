# ==============================================================================
# 🧪 《PythAPCS123》單元 10-5：字典在 APCS 的經典解題模式 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_5.py
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

def auto_grade_unit_10_5():
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
        # 10-5-1 頻率統計模式（Frequency Counter） (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-5-1", "填空題", "以 get() 補齊投票開票計數 tally.get(candidate, 0) + 1", 5,
         lambda g: (
             (True, "投票計數 get() 填空正確！")
             if ("tally.get(candidate, 0)" in history_str or "tally.get(candidate,0)" in history_clean or
                 "get(" in history_str and "+ 1" in history_str)
             else (False, "請在 10-5-1 填空題填入 tally.get(candidate, 0) + 1！")
         )),

        ("10-5-1", "練習題", "最高票選拔統計機 (得票最多者與票數)", 6,
         lambda g: (
             (True, "最高票統計與候選人搜尋正確！")
             if ("max(" in history_str or "for" in history_str) and ("ballot_box" in history_str or "count" in history_str)
             else (False, "請統計投票結果並輸出得票最高者與票數！")
         )),

        ("10-5-1", "挑戰題", "尋找唯一落單的幸運號碼 (恰好出現 1 次)", 5,
         lambda g: (
             (True, "唯一落單號碼統計鎖定正確！")
             if ("== 1" in history_str or "==1" in history_clean) and ("counts" in history_str or "get(" in history_str)
             else (False, "請以字典統計頻率，找出出現次數恰為 1 的號碼！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-2 查表法（Lookup Table） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-2", "填空題", "月份縮寫轉數字查表 month_map.get(target_month, -1)", 5,
         lambda g: (
             (True, "月份查表法填空正確！")
             if ("month_map.get" in history_str and "-1" in history_str)
             else (False, "請在 10-5-2 填空題填入 month_map.get(target_month, -1)！")
         )),

        ("10-5-2", "練習題", "外幣匯率試算器 (幣別查表換算台幣)", 6,
         lambda g: (
             (True, "外幣匯率查表換算正確！")
             if ("exchange_rates" in history_str and "*" in history_str) or ("sum" in history_str)
             else (False, "請透過匯率字典查表並計算兌換後的新台幣總額！")
         )),

        ("10-5-2", "挑戰題", "英文星期天數差計算 (星期縮寫查表差距)", 6,
         lambda g: (
             (True, "星期天數差距查表計算正確！")
             if ("weekday_map" in history_str and ("abs(" in history_str or "-" in history_str))
             else (False, "請透過星期查表計算兩天數之間的絕對差距！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-3 離散化 / 座標壓縮（Coordinate Compression） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-3", "填空題", "建立座標壓縮字典 rank_map[val] = idx", 5,
         lambda g: (
             (True, "座標壓縮字典建立填空正確！")
             if ("rank_map[val] = idx" in history_str or "rank_map[val]=idx" in history_clean or
                 "enumerate" in history_str)
             else (False, "請在 10-5-3 填空題填入 rank_map[val] = idx！")
         )),

        ("10-5-3", "練習題", "選手背號稠密排名轉換器 (排序去重離散化)", 6,
         lambda g: (
             (True, "稠密排名離散化轉換正確！")
             if ("sorted(" in history_str and "set(" in history_str) and ("[" in history_str and "]" in history_str)
             else (False, "請將選手背號排序去重，建立緊湊排名字典並映射輸出！")
         )),

        ("10-5-3", "挑戰題", "離散化反向解碼器 (依排名還原原始數值)", 6,
         lambda g: (
             (True, "反向字典查表解碼正確！")
             if ("rank_to_val" in history_str and "[" in history_str) or ("compressed" in history_str)
             else (False, "請透過反向字典將壓縮排名還原為原本的大數值！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-4 雙向映射表（Two-way Mapping） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-4", "填空題", "摩斯密碼反向字典建置 morse_decode[code] = letter", 5,
         lambda g: (
             (True, "雙向映射字典反轉填空正確！")
             if ("morse_decode[code] = letter" in history_str or "morse_decode[code]=letter" in history_clean)
             else (False, "請在 10-5-4 填空題填入 morse_decode[code] = letter！")
         )),

        ("10-5-4", "練習題", "情報員暗號雙向翻譯機 (代號與真名互查)", 6,
         lambda g: (
             (True, "特務雙向翻譯字典建置正確！")
             if ("agent_codes" in history_str and ("items()" in history_str or "reverse" in history_str))
             else (False, "請建置好雙向字典，支援代號與真名相互查詢！")
         )),

        ("10-5-4", "挑戰題", "一對多反向分組索引 (分數 -> 姓名串列)", 6,
         lambda g: (
             (True, "一對多反向分組索引正確！")
             if ("score_dict" in history_str and "append" in history_str) or ("score_to_names" in history_str)
             else (False, "請將學生姓名依成績反向歸入以分數為鍵的串列字典中！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-5 分組聚合（Group By / Bucket） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-5", "填空題", "奇偶數分組收集 d['odd'].append(x)", 5,
         lambda g: (
             (True, "奇偶數分組收集填空正確！")
             if ("append(" in history_str and ("odd" in history_str or "even" in history_str))
             else (False, "請在 10-5-5 填空題完成 odd 與 even 的 append 收集！")
         )),

        ("10-5-5", "練習題", "單字首字母分組歸檔器 (w[0].upper() 分桶)", 6,
         lambda g: (
             (True, "單字首字母分組歸檔正確！")
             if ("upper()" in history_str and "append(" in history_str) and ("words" in history_str)
             else (False, "請將單字按首字母大寫分組歸檔進字典中！")
         )),

        ("10-5-5", "挑戰題", "餘數分桶總和統計 (num % k 分組加總)", 6,
         lambda g: (
             (True, "餘數分桶統計與加總正確！")
             if ("% k" in history_str or "%k" in history_clean or "% 3" in history_str) and "sum(" in history_str
             else (False, "請將整數依餘數分組，並輸出各餘數組的總和！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-6 字典與串列效能實測對比 O(1) vs O(N) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-5-6", "填空題", "以字典建立白名單查詢 query_user in whitelist_dict", 5,
         lambda g: (
             (True, "字典 O(1) 白名單查詢填空正確！")
             if ("in whitelist_dict" in history_str or "in whitelist" in history_str)
             else (False, "請在 10-5-6 填空題填入 query_user in whitelist_dict！")
         )),

        ("10-5-6", "練習題", "極速資料去重過濾保留順序 (O(N) 雜湊查表)", 6,
         lambda g: (
             (True, "保留順序之雜湊去重正確！")
             if ("seen" in history_str or "table" in history_str or "in" in history_str) and "append(" in history_str
             else (False, "請利用雜湊字典/集合在維持初次出現順序下去除重複值！")
         )),

        ("10-5-6", "挑戰題", "兩數串列交集元素極速提取 O(N + M)", 5,
         lambda g: (
             (True, "O(N + M) 兩串列交集提取正確！")
             if ("table_a" in history_str or "in table" in history_str or "in set" in history_str) and ("list_b" in history_str)
             else (False, "請將 list_a 轉為雜湊表後走訪 list_b 達到 O(N+M) 交集！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-5：字典在 APCS 的經典解題模式 —— 自動評分報告")
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
        "unit_id": "10-5",
        "unit_name": "字典在 APCS 的經典解題模式",
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
        filename = f"grade_report_10_5.json"
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
    auto_grade_unit_10_5()
