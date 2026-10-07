# ==============================================================================
# 🧪 《PythAPCS123》單元 8-3：常用串列方法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_3.py
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

def auto_grade_unit_8_3():
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
        # 8-3-1 .append() 尾端動態追加元素 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-1", "填空題", "呼叫 append 方法依序追加 (a 包含 [100, 200])", 6,
         lambda g: (
             (True, "使用 .append(100) 與 .append(200) 動態追加成功！")
             if g.get("a") == [100, 200] or
                ("a.append(100)" in history_clean and "a.append(200)" in history_clean)
             else (False, "請在 8-3-1 填空題空格填入方法名稱 append！")
         )),

        ("8-3-1", "練習題", "及格名單過濾收集器 (passed_list.append(score))", 9,
         lambda g: (
             (True, "及格分數 append 收集與 print(*passed_list) 輸出正確！")
             if (".append(" in history_str and ">= 60" in history_str and "print(*" in history_str) or
                ("85 90" in history_str or "70 60 100" in history_str)
             else (False, "請讀入 n 筆成績，若 >= 60 則 append 進 passed_list 並以 print(*passed_list) 印出！")
         )),

        ("8-3-1", "挑戰題", "3 的倍數收集生成器 (multiples.append(i))", 5,
         lambda g: (
             (True, "迴圈中倍數過濾與 append 收集正確！")
             if ("% 3 == 0" in history_str and ".append(" in history_str) or
                ("3 6 9" in history_str)
             else (False, "請走訪 1 到 n，將 3 的倍數 append 入串列中並印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-2 .pop() 元素彈出與提取 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-2", "填空題", "呼叫 pop() 彈出末端元素 (last_item == 30)", 6,
         lambda g: (
             (True, "使用 .pop() 成功彈出並保存末端元素！")
             if (g.get("last_item") == 30 and g.get("nums") == [10, 20]) or
                ("nums.pop()" in history_clean)
             else (False, "請在 8-3-2 填空題空格填入方法名稱 pop！")
         )),

        ("8-3-2", "練習題", "堆疊出牌模擬器 (cards.pop() 與 Remaining 顯示)", 9,
         lambda g: (
             (True, "兩回合 cards.pop() 出牌與剩餘牌組輸出正確！")
             if ("cards.pop()" in history_clean and "Play card:" in history_str and "Remaining:" in history_str) or
                ("Diamond Q" in history_str and "Spade A" in history_str)
             else (False, "請連續呼叫 cards.pop() 出牌兩次，依序印出出的牌與剩餘牌組！")
         )),

        ("8-3-2", "挑戰題", "FIFO 佇列模擬器 (queue.pop(0) 叫號看診)", 5,
         lambda g: (
             (True, "佇列首位 queue.pop(0) 移出與狀態通報正確！")
             if ("queue.pop(0)" in history_clean and "Served:" in history_str) or
                ("Patient 1" in history_str and "Patient 2" in history_str)
             else (False, "請以迴圈呼叫 queue.pop(0) 看診 k 次並輸出服務病患！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-3 .insert(idx, val) 指定位置插入 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-3", "填空題", "呼叫 insert(1, 20) 完成中間插入", 6,
         lambda g: (
             (True, "使用 .insert(1, 20) 插入指定位置成功！")
             if g.get("nums") == [10, 20, 30] or
                ("nums.insert(1,20)" in history_clean or "nums.insert(1, 20)" in history_str)
             else (False, "請在 8-3-3 填空題空格填入方法名稱 insert！")
         )),

        ("8-3-3", "練習題", "哨兵隊長加頂儀 (a.insert(0, 0))", 9,
         lambda g: (
             (True, "最前端哨兵 a.insert(0, 0) 插入輸出正確！")
             if ("insert(0, 0)" in history_str or "insert(0,0)" in history_clean) or
                ("[0, 5, 10, 15]" in history_str or "[0, 99, 88, 77]" in history_str)
             else (False, "請讀入 3 個整數存入 a，並使用 a.insert(0, 0) 在首位插入哨兵 0！")
         )),

        ("8-3-3", "挑戰題", "保持遞增之排序插入模擬 (sorted_list.insert(i, x))", 5,
         lambda g: (
             (True, "遞增排序位置尋找與 insert(i, x) 插入正確！")
             if (".insert(" in history_str and ("append(" in history_str or "break" in history_str)) or
                ("10 20 25 30 40" in history_str)
             else (False, "請找出首個大於 x 的位置進行 insert(i, x) 保持數列遞增！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-4 .remove(val) 依數值精準刪除 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-4", "填空題", "呼叫 remove('Bob') 移除名冊成員", 6,
         lambda g: (
             (True, "使用 .remove('Bob') 精準移除元素成功！")
             if g.get("members") == ["Alice", "Charlie"] or
                ('members.remove("Bob")' in history_clean or "members.remove('Bob')" in history_clean)
             else (False, "請在 8-3-4 填空題空格填入方法名稱 remove！")
         )),

        ("8-3-4", "練習題", "瑕疵品批號剔除器 (if in 檢查搭配 batches.remove)", 9,
         lambda g: (
             (True, "瑕疵批號 in 存在檢查與 .remove() 剔除正確！")
             if ("in batches" in history_str and "batches.remove(" in history_str and "NOT FOUND" in history_str) or
                ("101 202 404 505" in history_str or "NOT FOUND" in history_str)
             else (False, "請檢查 defect_batch 是否在 batches 中，存在則 remove 否則印出 NOT FOUND！")
         )),

        ("8-3-4", "挑戰題", "重複值全數連根拔起 (while 2 in a: a.remove(2))", 5,
         lambda g: (
             (True, "while in 迴圈全數移除重複元素完全正確！")
             if ("while 2 in a:" in history_str or "while 2 in a" in history_str or "while2ina:" in history_clean) or
                ("[1, 3, 4, 5]" in history_str)
             else (False, "請使用 while 2 in a: 反覆呼叫 a.remove(2) 清理所有 2！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-5 .reverse() 原地就地反轉 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-5", "填空題", "呼叫 reverse() 原地反轉 (letters == ['C', 'B', 'A'])", 6,
         lambda g: (
             (True, "呼叫 .reverse() 完成原地就地反轉！")
             if g.get("letters") == ["C", "B", "A"] or
                ("letters.reverse()" in history_clean)
             else (False, "請在 8-3-5 填空題空格填入方法名稱 reverse！")
         )),

        ("8-3-5", "練習題", "逆序倒數就地計時器 (countdown.reverse())", 9,
         lambda g: (
             (True, "countdown.reverse() 就地反轉與 print(*countdown) 輸出正確！")
             if ("countdown.reverse()" in history_clean and "print(*countdown)" in history_clean) or
                ("4 3 2 1" in history_str or "40 30 20 10" in history_str)
             else (False, "請使用 countdown.reverse() 進行原地反轉並以 print(*countdown) 印出！")
         )),

        ("8-3-5", "挑戰題", "雙端操作模擬器 (append, insert, pop, reverse)", 5,
         lambda g: (
             (True, "四大串列方法四部曲模擬輸出正確！")
             if (".append(" in history_str and ".insert(" in history_str and ".pop(" in history_str and ".reverse(" in history_str) or
                ("30 20 10 0" in history_str)
             else (False, "請依序執行 append, insert, pop, reverse 四步操作並印出結果！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 8-3 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 append、pop、insert、remove 與 reverse 五大神兵方法，串列操控行雲流水！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，常用串列方法呼叫精準純熟！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調方法參數與佇列/堆疊邏輯！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "8-3",
        "unit_title": "常用串列方法",
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
        log_filename = "score_log_unit_8_3.json"
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
auto_grade_unit_8_3()
