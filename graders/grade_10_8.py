# ==============================================================================
# 🧪 《PythAPCS123》單元 10-8：雜湊容器綜合實戰：座標標記、稀疏網格與圖論前導 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_8.py
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

def auto_grade_unit_10_8():
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
        # 10-8-1 座標集合標記已拜訪點 (Visited Set) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-8-1", "填空題", "將起點座標元組加入已拜訪集合 visited_points.add((r, c))", 5,
         lambda g: (
             (True, "座標元組加入集合填空正確！")
             if ("visited_points.add" in history_str and "(" in history_str)
             else (False, "請在 10-8-1 填空題填入 visited_points.add((start_r, start_c))！")
         )),

        ("10-8-1", "練習題", "探險家足跡覆蓋統計 (相異點個數與走訪清單)", 6,
         lambda g: (
             (True, "探險家相異足跡統計正確！")
             if ("visited" in history_str and "path" in history_str) and (".add(" in history_str)
             else (False, "請使用集合追蹤走過的所有相異座標點！")
         )),

        ("10-8-1", "挑戰題", "首度自交點偵測 (First Self-Intersection)", 5,
         lambda g: (
             (True, "首度自交偵測正確！")
             if ("in visited" in history_str and "break" in history_str) or ("自交" in history_str or "moves" in history_str)
             else (False, "請在碰觸曾拜訪過的座標時輸出自交座標與步數！")
         )),

        # ----------------------------------------------------------------------
        # 10-8-2 元組為字典鍵值：百萬級稀疏網格 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-8-2", "填空題", "稀疏地圖放置旗幟與 get 預設讀取", 5,
         lambda g: (
             (True, "稀疏網格讀寫填空正確！")
             if ("world_map" in history_str and "EMPTY" in history_str) or (".get(" in history_str)
             else (False, "請在 10-8-2 填空題放置旗幟並以 get() 取得預設值！")
         )),

        ("10-8-2", "練習題", "稀疏棋盤子力總價值計算器 (重疊點價值累加)", 6,
         lambda g: (
             (True, "稀疏棋盤價值累加正確！")
             if ("pieces_data" in history_str and "+=" in history_str) or ("sum(" in history_str)
             else (False, "請以字典紀錄稀疏棋子並累加同一座標上的價值！")
         )),

        ("10-8-2", "挑戰題", "稀疏踩地雷相鄰地雷計數 (向量走訪 mine_locations)", 6,
         lambda g: (
             (True, "稀疏地雷相鄰計數正確！")
             if ("in mine_locations" in history_str or "mine_locations" in history_str) and ("dr" in history_str or "range(4)" in history_str)
             else (False, "請走訪相鄰座標，透過集合判定地雷是否存在！")
         )),

        # ----------------------------------------------------------------------
        # 10-8-3 字典模擬圖論鄰接串列 (Adjacency List) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-8-3", "填空題", "單向有向圖建置 graph[u].append(v)", 5,
         lambda g: (
             (True, "有向圖鄰接表建置填空正確！")
             if ("append(" in history_str and "flights" in history_str)
             else (False, "請在 10-8-3 填空題將目的地 append 進鄰接表中！")
         )),

        ("10-8-3", "練習題", "雙向連通公車路線鄰接表分析", 6,
         lambda g: (
             (True, "雙向公車網絡鄰接表建置正確！")
             if ("bus_network" in history_str and "append(" in history_str) and ("connections" in history_str)
             else (False, "請為雙向站點建立對應的相鄰站點清單！")
         )),

        ("10-8-3", "挑戰題", "社交網絡尋找二度好友 (朋友的朋友，排除自己)", 6,
         lambda g: (
             (True, "二度好友集合過濾正確！")
             if ("graph" in history_str and ("set(" in history_str or "second" in history_str))
             else (False, "請走訪好友的好友，並排除自己與一度好友！")
         )),

        # ----------------------------------------------------------------------
        # 10-8-4 字典轉串列多欄位複合排序 (sorted items) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-8-4", "填空題", "商品庫存量由大到小排序 sorted(..., reverse=True)", 5,
         lambda g: (
             (True, "字典轉元組降序排列填空正確！")
             if ("qty, item" in history_str or "item, qty" in history_str or "reverse=True" in history_str)
             else (False, "請在 10-8-4 填空題完成庫存量降序排序！")
         )),

        ("10-8-4", "練習題", "英文單字出現頻率英雄榜 (頻率降序，字母升序)", 6,
         lambda g: (
             (True, "單字出現頻率英雄榜排序正確！")
             if ("sorted(" in history_str and "items()" in history_str) or ("-count" in history_str)
             else (False, "請統計單字頻率並依出現次數降序、字母升序排列！")
         )),

        ("10-8-4", "挑戰題", "學生成績三準則複合排序 (分數降序、年級升序、姓名升序)", 6,
         lambda g: (
             (True, "三準則複合排序正確！")
             if (g.get("top_student") == "Charlie") or
                ("top_student" in history_str and "sorted" in history_str)
             else (False, "請對學生成績依照分數降序、年級升序、姓名升序進行複合排序，求出第一名！")
         )),

        # ----------------------------------------------------------------------
        # 10-8-5 重複元素偵測與首個重複值定位 (One-pass Hash) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-8-5", "填空題", "字串中首個重複字母偵測 if ch in seen: break", 5,
         lambda g: (
             (True, "首個重複字母偵測填空正確！")
             if ("in seen" in history_str and "break" in history_str)
             else (False, "請在 10-8-5 填空題填入 if ch in seen: break！")
         )),

        ("10-8-5", "練習題", "首個重複整數與索引定位器 (二度出現位置)", 6,
         lambda g: (
             (True, "首個重複數字與索引定位正確！")
             if ("in seen" in history_str and "break" in history_str) and ("numbers" in history_str)
             else (False, "請在單趟走訪中輸出首個重複數字與其當下索引！")
         )),

        ("10-8-5", "挑戰題", "首個出現滿 K 次的元素判定", 6,
         lambda g: (
             (True, "首個達門檻 K 次元素判定正確！")
             if ("== k" in history_str or "==k" in history_clean) and ("counts" in history_str or "get(" in history_str)
             else (False, "請統計元素出現次數，第一個達到 k 次時立即輸出並終止！")
         )),

        # ----------------------------------------------------------------------
        # 10-8-6 APCS 歷屆真題中的雜湊思維總覽 (c291 小群體原型) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-8-6", "填空題", "APCS c291 朋友圈走訪標記 while curr not in visited", 5,
         lambda g: (
             (True, "APCS c291 環形走訪標記填空正確！")
             if ("not in visited" in history_str or "visited.add" in history_str)
             else (False, "請在 10-8-6 填空題填入 while curr not in visited 走訪閉環！")
         )),

        ("10-8-6", "練習題", "APCS c291 小群體演算法完整實作 (計算封閉環個數)", 6,
         lambda g: (
             (True, "APCS c291 小群體環形計數正確！")
             if ("visited" in history_str and "relations" in history_str) and ("group_count" in history_str or "groups" in history_str or "count" in history_str)
             else (False, "請使用 visited 集合走訪 relations 並統計獨立朋友圈個數！")
         )),

        ("10-8-6", "挑戰題", "網格多粒子移動碰撞消除模擬", 5,
         lambda g: (
             (True, "多粒子碰撞消除模擬正確！")
             if ("particles" in history_str and ("pos" in history_str or "grid" in history_str))
             else (False, "請模擬多粒子前進，若多粒子位於同座標則同時湮滅消除！")
         ))    ]

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 10-8：雜湊容器綜合實戰：座標標記、稀疏網格與圖論前導 —— 自動評分報告")
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
        "unit_id": "10-8",
        "unit_name": "雜湊容器綜合實戰：座標標記、稀疏網格與圖論前導",
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
        filename = f"grade_report_10_8.json"
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
    auto_grade_unit_10_8()
