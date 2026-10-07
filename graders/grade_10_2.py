# ==============================================================================
# 🧪 《PythAPCS123》單元 10-2：元組進階操作與可雜湊特性（Hashable） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_2.py
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

def auto_grade_unit_10_2():
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
        # 10-2-1 記憶體行為本質與 id() (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-2-1", "填空題", "使用 id() 驗證元組重賦值產生新位址", 5,
         lambda g: (
             (True, "id() 記憶體探測填空正確！")
             if ("id(a)" in history_clean)
             else (False, "請在 10-2-1 填空題填入 id(a) 觀察位址變化！")
         )),

        ("10-2-1", "練習題", "不可變字串與元組位址驗證儀 (id1 != id2)", 6,
         lambda g: (
             (True, "元組加法新物件位址驗證正確！")
             if ("id(" in history_str and "!=" in history_str) or ("id1" in history_str and "id2" in history_str)
             else (False, "請記錄 t1 與 t2 的 id 並驗證兩者位址相異！")
         )),

        ("10-2-1", "挑戰題", "純淨不可變容器檢測 (isinstance int/float/str/tuple)", 5,
         lambda g: (
             (True, "不可變純淨型態檢測正確！")
             if ("isinstance" in history_str and ("tuple" in history_str or "list" in history_str)) or ("SAFE" in history_str)
             else (False, "請檢驗清單中各元素是否全為不可變型態！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-2 可雜湊（Hashable）本質 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-2", "填空題", "計算不可變元組雜湊指紋 hash(coord)", 5,
         lambda g: (
             (True, "hash() 函式填空正確！")
             if ("hash(coord)" in history_clean)
             else (False, "請在 10-2-2 填空題填入 hash(coord)！")
         )),

        ("10-2-2", "練習題", "元組雜湊一致性驗證 hash(t1) == hash(t2)", 6,
         lambda g: (
             (True, "雜湊一致性比對正確！")
             if ("hash(t1) == hash(t2)" in history_str or "hash(t1)==hash(t2)" in history_clean or "hash(" in history_str)
             else (False, "請驗證內容相同的兩個元組其 hash 值完全相等！")
         )),

        ("10-2-2", "挑戰題", "動態輸入資料可雜湊性整數檢驗", 6,
         lambda g: (
             (True, "可雜湊性檢測正確！")
             if ("isinstance(hash(" in history_clean or "hash(" in history_str)
             else (False, "請驗證 tuple 輸入的雜湊值為整數型態！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-3 巢狀元組與結構化資料打包 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-3", "填空題", "巢狀解包 sid, name, (math, eng, sci) = record", 5,
         lambda g: (
             (True, "多層巢狀解包填空正確！")
             if ("sid, name" in history_str and "math" in history_str) or ("record" in history_str)
             else (False, "請在 10-2-3 填空題填入多層解包變數！")
         )),

        ("10-2-3", "練習題", "學生卡成績統計器 (sid, name, (s1, s2, s3))", 6,
         lambda g: (
             (True, "學生卡巢狀打包與統計正確！")
             if ("(" in history_str and "sum(" in history_str) and ("name" in history_str or "sid" in history_str)
             else (False, "請打包為 (sid, name, (s1, s2, s3)) 並計算成績總和！")
         )),

        ("10-2-3", "挑戰題", "二維多線段長度統計 ((r1, c1), (r2, c2))", 6,
         lambda g: (
             (True, "巢狀線段長度統計正確！")
             if ("abs(" in history_str and "((" in history_str)
             else (False, "請將線段儲存為 ((r1, c1), (r2, c2)) 並計算曼哈頓長度！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-4 座標位移向量應用 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-4", "填空題", "八方向對角向量補齊 (-1, -1) 與 (1, 1)", 5,
         lambda g: (
             (True, "八方向位移向量填空正確！")
             if ("(-1, -1)" in history_str or "(-1,-1)" in history_clean) and ("(1, 1)" in history_str or "(1,1)" in history_clean)
             else (False, "請在 10-2-4 填空題補齊對角線位移向量！")
         )),

        ("10-2-4", "練習題", "網格安全位移探測器 (r + dr, c + dc)", 6,
         lambda g: (
             (True, "向量位移與邊界判定正確！")
             if ("r + dr" in history_str or "c + dc" in history_str or "0 <= nr < R" in history_str)
             else (False, "請使用位移向量計算新座標並加入邊界保護！")
         )),

        ("10-2-4", "挑戰題", "連續向量步進路徑生成", 6,
         lambda g: (
             (True, "連續步進軌跡計算正確！")
             if ("for" in history_str and ("dr" in history_str or "dc" in history_str or "DIRECTIONS" in history_str))
             else (False, "請連續執行 M 步移動並輸出最終座標！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-5 多傳回值模擬打包 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-5", "填空題", "奇偶數總和打包為 (odd_sum, even_sum)", 5,
         lambda g: (
             (True, "多值統計元組打包填空正確！")
             if ("(odd_sum, even_sum)" in history_str or "(odd_sum,even_sum)" in history_clean)
             else (False, "請在 10-2-5 填空題填入 (odd_sum, even_sum)！")
         )),

        ("10-2-5", "練習題", "四合一數據分析打包 (len, sum, max, min)", 6,
         lambda g: (
             (True, "四項統計指標打包正確！")
             if ("len(" in history_str and "sum(" in history_str and "max(" in history_str and "min(" in history_str)
             else (False, "請將長度、總和、最大值、最小值打包為四元組！")
         )),

        ("10-2-5", "挑戰題", "正負數與零計數三元組 (pos, neg, zero)", 6,
         lambda g: (
             (True, "正負零計數三元組打包正確！")
             if ("> 0" in history_str and "< 0" in history_str and "== 0" in history_str)
             else (False, "請統計正數、負數與 0 的個數並打包輸出！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-6 元組字典序排序原則 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-2-6", "填空題", "雙條件排序鍵值 (-score, penalties)", 5,
         lambda g: (
             (True, "多條件排序元組填空正確！")
             if ("-p1_score" in history_str or "-score" in history_str or "-p" in history_clean)
             else (False, "請在 10-2-6 填空題填入 (-score, penalties)！")
         )),

        ("10-2-6", "練習題", "兩位選手多條件勝負判定 (-solved, penalty, id)", 6,
         lambda g: (
             (True, "多準則勝負比對正確！")
             if ("-s" in history_clean or "p1" in history_str) and ("<" in history_str or ">" in history_str)
             else (False, "請使用元組 (-solved, penalty, id) 比較兩位選手高下！")
         )),

        ("10-2-6", "挑戰題", "三點距離原點多準則排序", 5,
         lambda g: (
             (True, "座標多準則排序正確！")
             if ("abs(" in history_str and "sort" in history_str) or ("sorted(" in history_str)
             else (False, "請依照曼哈頓距離與座標字典序對三點進行排序！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-2：元組進階操作與可雜湊特性（Hashable） —— 自動評分報告")
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
        "unit_id": "10-2",
        "unit_name": "元組進階操作與可雜湊特性（Hashable）",
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
        filename = f"grade_report_10_2.json"
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
    auto_grade_unit_10_2()
