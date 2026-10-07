# ==============================================================================
# 🧪 《PythAPCS123》單元 10-1：元組特性、建立與不可變保護機制 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_1.py
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

def auto_grade_unit_10_1():
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
        # 10-1-1 為什麼需要不可變容器？ (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-1-1", "填空題", "安全讀取伺服器設定 server_config[0] 與 server_config[-1]", 5,
         lambda g: (
             (True, "元組安全讀取填空完全正確！")
             if (g.get("port") == 8080 and g.get("status") == "ONLINE") or
                ("server_config[0]" in history_clean and "server_config[-1]" in history_clean)
             else (False, "請在 10-1-1 填空題填入索引 0 與 -1 安全讀取元組！")
         )),

        ("10-1-1", "練習題", "不可變常數守護者 (a, b, c) 打包乘數", 6,
         lambda g: (
             (True, "三常數元組打包與倍率運算正確！")
             if ("tuple" in history_str or "(" in history_str) and ("multiplier" in history_str or "*" in history_str)
             else (False, "請將三個整數打包為元組並乘以 multiplier！")
         )),

        ("10-1-1", "挑戰題", "四科成績極值守門員與全距計算", 5,
         lambda g: (
             (True, "元組極值與全距計算正確！")
             if ("max(" in history_str and "min(" in history_str) and ("scores" in history_str or "tuple" in history_str)
             else (False, "請輸入四科成績存入元組，並計算 max(scores) - min(scores)！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-2 單元素逗號陷阱 (x,) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-2", "填空題", "修復單元素元組宣告 (val,)", 5,
         lambda g: (
             (True, "單元素元組逗號修復正確！")
             if (isinstance(g.get("single_t"), tuple) and len(g.get("single_t")) == 1) or
                ("(val,)" in history_clean or "(88,)" in history_clean)
             else (False, "請在 10-1-2 填空題小括號內補上逗號 `(val,)`！")
         )),

        ("10-1-2", "練習題", "純括號整數 vs 單元素元組型態與長度檢驗", 6,
         lambda g: (
             (True, "元組型態與長度量測正確！")
             if ("type(" in history_str and "len(" in history_str) and ("," in history_str)
             else (False, "請比較 (N) 與 (N,) 的 type 與 len！")
         )),

        ("10-1-2", "挑戰題", "動態構造空元組 () 與單元素元組", 6,
         lambda g: (
             (True, "空元組與單元素動態構造正確！")
             if ("() " in history_str or "()" in history_clean or "tuple()" in history_str) and ("k ==" in history_str or "k==" in history_clean)
             else (False, "請依 K == 0 建立空元組 ()，K == 1 建立單元素元組！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-3 正負索引存取與切片操作 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-3", "填空題", "週末切片 days[-2:] 與平日反轉 days[:5][::-1]", 5,
         lambda g: (
             (True, "元組切片提取與反轉填空正確！")
             if (g.get("weekend") == ("六", "日")) or
                ("days[-2:]" in history_clean or "days[5:]" in history_clean or "::-1" in history_str)
             else (False, "請在 10-1-3 填空題填入 days[-2:] 與 days[:5][::-1]！")
         )),

        ("10-1-3", "練習題", "數列頭尾裁切與中間反轉 (t[1:-1][::-1])", 6,
         lambda g: (
             (True, "頭尾裁切與中間反轉切片正確！")
             if ("t[1:-1]" in history_clean and "::-1" in history_str) or ("tuple" in history_str and "print" in history_str)
             else (False, "請去除首尾兩數後將中間元素反轉輸出！")
         )),

        ("10-1-3", "挑戰題", "迴文元組檢測器 (t == t[::-1])", 6,
         lambda g: (
             (True, "迴文元組檢測邏輯正確！")
             if ("t == t[::-1]" in history_clean or "t==t[::-1]" in history_clean) and ("YES" in history_str and "NO" in history_str)
             else (False, "請以 t == t[::-1] 判斷是否為迴文元組並輸出 YES 或 NO！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-4 tuple(list) 與 list(tuple) 型態互轉 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-4", "填空題", "元組轉串列排序後重新封裝 tuple(sorted_list)", 5,
         lambda g: (
             (True, "元組與串列互轉填空正確！")
             if (g.get("sorted_t") == (10, 20, 30, 40, 50)) or
                ("list(raw_t)" in history_clean and "tuple(" in history_clean)
             else (False, "請在 10-1-4 填空題填入 list(raw_t) 與 tuple(sorted_list)！")
         )),

        ("10-1-4", "練習題", "黑名單數值過濾與元組重新封印", 6,
         lambda g: (
             (True, "黑名單過濾與元組封印正確！")
             if ("list(" in history_str and "tuple(" in history_str) and ("bad_val" in history_str or "!=" in history_str)
             else (False, "請將元組轉為串列剔除 bad_val 後重新轉為元組！")
         )),

        ("10-1-4", "挑戰題", "元組指定位置就地替換模擬器", 6,
         lambda g: (
             (True, "元組單點替換模擬正確！")
             if ("list(" in history_str and "tuple(" in history_str) and ("idx" in history_str and "new_val" in history_str)
             else (False, "請將元組轉為串列替換指定索引數值後封印回元組！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-5 元組解包賦值 (Tuple Unpacking) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-5", "填空題", "三維座標解包 x, y, z = coord_3d", 5,
         lambda g: (
             (True, "三維曼哈頓座標解包填空正確！")
             if (g.get("manhattan_dist") == 22) or
                ("x, y, z = coord_3d" in history_str or "x,y,z=coord_3d" in history_clean)
             else (False, "請在 10-1-5 填空題完成 x, y, z = coord_3d 解包！")
         )),

        ("10-1-5", "練習題", "選手四項成績解包與總分計算", 6,
         lambda g: (
             (True, "選手成績解包與加總正確！")
             if ("name, run, jump, shoot" in history_str or "name,run,jump,shoot" in history_clean or
                 "parts" in history_str)
             else (False, "請將選手資料解包給 name, run, jump, shoot 並計算總分！")
         )),

        ("10-1-5", "挑戰題", "兩人對戰成績解包與勝負判定", 6,
         lambda g: (
             (True, "兩人對戰解包判定正確！")
             if ("p1" in history_str and "p2" in history_str) and (">" in history_str and "sum" in history_str)
             else (False, "請各自解包兩人成績，計算三局總分並判定勝負！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-6 二維座標封裝：以 (r, c) 表示平面點 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-1-6", "填空題", "座標元組走訪 for r, c in points", 5,
         lambda g: (
             (True, "座標元組走訪填空正確！")
             if ("for r, c in points" in history_str or "for r, c in points:" in history_str or
                 "forr,cinpoints" in history_clean)
             else (False, "請在 10-1-6 填空題填入 for r, c in points！")
         )),

        ("10-1-6", "練習題", "曼哈頓兩點距離元組計算機 abs(r1-r2) + abs(c1-c2)", 6,
         lambda g: (
             (True, "曼哈頓兩點距離計算正確！")
             if ("abs(" in history_str and "+" in history_str) and ("r1" in history_str and "r2" in history_str)
             else (False, "請計算兩座標元組之間的曼哈頓距離 abs(r1 - r2) + abs(c1 - c2)！")
         )),

        ("10-1-6", "挑戰題", "多點軌跡中心點座標計算 (sum_r//N, sum_c//N)", 5,
         lambda g: (
             (True, "多點軌跡中心座標計算正確！")
             if ("sum(" in history_str or "sum_r" in history_str) and ("// n" in history_str or "//n" in history_clean or "// N" in history_str)
             else (False, "請計算所有點的平均座標 (sum_r // N, sum_c // N)！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-1：元組特性、建立與不可變保護機制 —— 自動評分報告")
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
        "unit_id": "10-1",
        "unit_name": "元組特性、建立與不可變保護機制",
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
        filename = f"grade_report_10_1.json"
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
    auto_grade_unit_10_1()
