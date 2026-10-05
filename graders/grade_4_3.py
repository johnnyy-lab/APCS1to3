# ==============================================================================
# 🧪 《PythAPCS123》單元 4-3：print() 結尾符號參數 end —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_3.py
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

def auto_grade_unit_4_3():
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
        # 4-3-1 認識結尾參數 end——揭開自動換行 \n 的秘密 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-1", "填空題", "認識 end 參數與預設換行 (end='\\n')", 6,
         lambda g: (
             (True, "end 參數填寫正確：成功設定 end='\\n' 輸出天文觀測通知！")
             if (("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str) and
                 ("msg1" in history_str or "火星衝" in history_str or g.get("msg1") is not None))
             else (False, "請在 4-3-1 填空題空格填入 end='\\n' 並執行儲存格！")
         )),

        ("4-3-1", "練習題", "運動會賽程上午與下午換行輸出 (morning_event, afternoon_event)", 8,
         lambda g: (
             (True, "校慶賽程換行公告完成！")
             if (("morning_event" in g and "afternoon_event" in g) and
                 ("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str))
             else (False, "請宣告 morning_event, afternoon_event 並在第一次 print() 加上 end='\\n' 輸出！")
         )),

        ("4-3-1", "挑戰題", "氣象站今明兩天氣溫逐日通報 (temp_today, temp_tomorrow)", 6,
         lambda g: (
             (True, f"氣溫通報設定完成：今天={g.get('temp_today')}度、明天={g.get('temp_tomorrow')}度！")
             if (("temp_today" in g and "temp_tomorrow" in g) and
                 ("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str))
             else (False, "請建立 temp_today, temp_tomorrow 變數，並在第一次輸出加上 end='\\n'！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-2 取消換行緊密相連——空字串 end='' 接續輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-2", "填空題", "取消換行接續輸出金額 (end='')", 6,
         lambda g: (
             (True, "取消換行設定正確：end=''！")
             if (("end=''" in history_str or 'end=""' in history_str) and
                 ("應付總額" in history_str or "total_price" in history_str or g.get("total_price") == 360))
             else (False, "請在 4-3-2 填空題空格填入 end='' 取消換行並執行儲存格！")
         )),

        ("4-3-2", "練習題", "經驗值接續輸出 (exp_points, end='')", 8,
         lambda g: (
             (True, f"經驗值接續輸出成功：exp_points={g.get('exp_points')}！")
             if (("exp_points" in g) and
                 ("end=''" in history_str or 'end=""' in history_str) and
                 ("獲得經驗值" in history_str))
             else (False, "請宣告 exp_points 變數，並使用 print('獲得經驗值: +', end='') 接續輸出！")
         )),

        ("4-3-2", "挑戰題", "密碼三片段單行拼裝 (part_a, part_b, part_c)", 6,
         lambda g: (
             (True, "密碼三片段使用 end='' 拼裝成功！")
             if (("part_a" in g and "part_b" in g and "part_c" in g) and
                 ("FLAG" in str(g.get("part_a", "")) or "FLAG" in history_str) and
                 ("end=''" in history_str or 'end=""' in history_str))
             else (False, "請建立 part_a, part_b, part_c 變數，並呼叫三次 print() 搭配 end='' 拼裝！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-3 自訂結尾間隔符號——空格 end=' ' 與標點符號收尾 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-3", "填空題", "選手背號單行空格間隔 (end=' ')", 6,
         lambda g: (
             (True, "結尾空格設定正確：end=' '！")
             if (("end=' '" in history_str or 'end=" "' in history_str) and
                 ("winner1" in history_str or g.get("winner1") == 15))
             else (False, "請在 4-3-3 填空題空格填入 end=' ' 並執行儲存格！")
         )),

        ("4-3-3", "練習題", "捷運語音路線箭頭串聯 (st1, st2, st3, end=' -> ')", 8,
         lambda g: (
             (True, "捷運廣播路線單行箭頭串接完成！")
             if (("st1" in g and "st2" in g and "st3" in g) and
                 ("end=' -> '" in history_str or 'end=" -> "' in history_str or "->" in history_str))
             else (False, "請宣告 st1, st2, st3 變數，並使用 print(..., end=' -> ') 串接輸出！")
         )),

        ("4-3-3", "挑戰題", "三關金幣累加算式接續拼裝 (coin1, coin2, coin3)", 6,
         lambda g: (
             (True, f"金幣累加算式輸出正確：{g.get('coin1')} + {g.get('coin2')} + {g.get('coin3')}！")
             if (("coin1" in g and "coin2" in g and "coin3" in g) and
                 ("+" in history_str and "=" in history_str))
             else (False, "請建立 coin1, coin2, coin3 變數，並利用 end 參數組裝出金幣累加算式！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-4 結尾的雙重換行與段落拉開——end='\n\n' 大段落排版術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-4", "填空題", "標題下方雙換行空行排版 (end='\\n\\n')", 6,
         lambda g: (
             (True, "雙換行排版設定正確：end='\\n\\n'！")
             if (("end='\\n\\n'" in history_str or 'end="\\n\\n"' in history_str or "end=\\n\\n" in history_str) and
                 ("headline" in history_str or g.get("headline") is not None))
             else (False, "請在 4-3-4 填空題空格填入 end='\\n\\n' 並執行儲存格！")
         )),

        ("4-3-4", "練習題", "兩則重要公告段落拉開 (notice1, notice2, end='\\n\\n')", 8,
         lambda g: (
             (True, "兩則公告段落分離排版完成！")
             if (("notice1" in g and "notice2" in g) and
                 ("end='\\n\\n'" in history_str or 'end="\\n\\n"' in history_str or "end=\\n\\n" in history_str))
             else (False, "請宣告 notice1, notice2 並使用 end='\\n\\n' 達成段落分離！")
         )),

        ("4-3-4", "挑戰題", "資安警告分隔線包覆排版 (alert_title, alert_action)", 6,
         lambda g: (
             (True, "資安警報卡分隔線包覆排版完成！")
             if (("alert_title" in g and "alert_action" in g) and
                 ("-" in history_str or "---" in str(g.get("alert_title")) or "end=" in history_str))
             else (False, "請宣告 alert_title, alert_action 變數，並在印出標題時以 end 包含換行與橫線！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-5 綜合雙劍合璧——sep 與 end 同時登場的精密排版術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-5", "填空題", "風速連字號與單位結尾雙參數 (sep='-', end=' km/h\\n')", 6,
         lambda g: (
             (True, "雙參數設定正確：sep='-' 搭配 end=' km/h\\n'！")
             if (("sep='-'" in history_str or 'sep="-"' in history_str) and
                 ("km/h" in history_str or "end=" in history_str) and
                 ("v1" in history_str or g.get("v1") == 12))
             else (False, "請在 4-3-5 填空題空格依序填入 sep 與 end 關鍵字名稱並執行！")
         )),

        ("4-3-5", "練習題", "機器人三軸座標精密排版 (x, y, z, sep=', ', end=']\\n')", 8,
         lambda g: (
             (True, f"機器人三軸座標排版完成：[{g.get('x')}, {g.get('y')}, {g.get('z')}]！")
             if (("x" in g and "y" in g and "z" in g) and
                 ("Robot Pos" in history_str) and
                 ("sep=" in history_str and "end=" in history_str))
             else (False, "請宣告 x, y, z 並使用 end='' 前導字串搭配 sep=', ', end=']\\n' 輸出！")
         )),

        ("4-3-5", "挑戰題", "戰艦雷達目標掃描儀表板 (target1, target2, target3)", 6,
         lambda g: (
             (True, f"雷達掃描狀態儀表板輸出成功：{g.get('target1')} ~ {g.get('target2')} ~ {g.get('target3')}！")
             if (("target1" in g and "target2" in g and "target3" in g) and
                 ("雷達目標掃描" in history_str) and
                 ("sep=" in history_str and "end=" in history_str))
             else (False, "請宣告 target1, target2, target3 變數，同時使用 sep 與 end 參數精密排版！")
         )),
    ]

    # 執行所有測資評分
    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 4-3 學習成效自動評分診斷報告")
    print(f"👤 受評學員：{combined_display_name}")
    print(f"📧 驗證信箱：{final_email}")
    print(f"🕒 評分時間：{timestamp_str}")
    print("=" * 72)

    pass_count = 0
    item_results = []

    for sub_unit, q_type, q_title, score, validator in test_cases:
        try:
            passed, feedback = validator(env)
        except Exception as e:
            passed, feedback = False, f"評分邏輯檢查異常：{e}"

        earned = score if passed else 0
        total_score += earned
        if passed:
            pass_count += 1
            status_icon = "✅ 通過"
        else:
            status_icon = "❌ 未過"

        item_results.append({
            "sub_unit": sub_unit,
            "type": q_type,
            "title": q_title,
            "max_score": score,
            "earned_score": earned,
            "status": "PASS" if passed else "FAIL",
            "feedback": feedback
        })

        print(f"[{status_icon}] ({earned:2d}/{score:2d}分) 【{sub_unit} {q_type}】{q_title}")
        print(f"       👉 評語：{feedback}")

    print("-" * 72)
    # 計算榮譽稱號
    if total_score == 100:
        badge = "🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美駕馭 print() 結尾參數 end 與雙劍合璧！"
    elif total_score >= 80:
        badge = "🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！"
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
        "unit": "4-3",
        "unit_title": "print() 結尾符號參數 end",
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
        log_filename = "score_log_unit_4_3.json"
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
auto_grade_unit_4_3()
