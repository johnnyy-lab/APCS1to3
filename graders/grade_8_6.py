# ==============================================================================
# 🧪 《PythAPCS123》單元 8-6：串列參照與淺拷貝 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_6.py
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

def auto_grade_unit_8_6():
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
        # 8-6-1 變數賦值的大陷阱：b = a 只是共用同一張標籤 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-6-1", "填空題", "串列參照賦值共用 (shared_cart = cart)", 6,
         lambda g: (
             (True, "shared_cart = cart 參照賦值正確！")
             if ("shared_cart=cart" in history_clean or "shared_cart = cart" in history_str) and
                ("滑鼠" in history_str)
             else (False, "請在 8-6-1 填空題空格將 cart 賦值給 shared_cart！")
         )),

        ("8-6-1", "練習題", "別名共用污染首尾修改印出 a (b = a 修改輸出)", 9,
         lambda g: (
             (True, "b = a 別名共用污染驗證輸出正確！")
             if ("b = a" in history_str or "b=a" in history_clean) and
                ("[100, 2, 99]" in history_str or "[100, 6, 7, 99]" in history_str or ("b[0] = 100" in history_str and "b[-1] = 99" in history_str))
             else (False, "請設定 b = a，修改 b 的首尾元素並印出受到連動影響的 a！")
         )),

        ("8-6-1", "挑戰題", "被污染的遊戲存檔情境模擬 (backup = player_stats)", 5,
         lambda g: (
             (True, "遊戲存檔共用參照污染情境模擬正確！")
             if ("player_stats" in history_str and "backup" in history_str and "-= 40" in history_str) or
                ("[60, 50]" in history_str)
             else (False, "請模擬 backup = player_stats，扣除血量後輸出被污染的 backup！")
         )),

        # ----------------------------------------------------------------------
        # 8-6-2 身分證驗證：id() 函式與 is 運算子 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-6-2", "填空題", "is 運算子與 == 運算子身分對決填空", 6,
         lambda g: (
             (True, "== 內容比對與 is 物件身分同一性填空正確！")
             if ("list1 == list2" in history_str or "list1==list2" in history_clean) and
                ("list1 is list2" in history_str or "list1islist2" in history_clean)
             else (False, "請在 8-6-2 填空題依序填入 == 與 is 運算子！")
         )),

        ("8-6-2", "練習題", "同一物件性判定印出 (p is q 為 True, p is r 為 False)", 9,
         lambda g: (
             (True, "p is q (True) 與 p is r (False) 印出正確！")
             if ("p is q" in history_str and "p is r" in history_str) or
                ("True\nFalse" in history_str)
             else (False, "請分別印出 p is q 與 p is r 的布林值結果！")
         )),

        ("8-6-2", "挑戰題", "別名與獨立拷貝三變數檢驗 (alias is True, clone is False)", 5,
         lambda g: (
             (True, "alias (同一物件) 與 clone (內容相同身分相異) 檢驗成功！")
             if ("items is alias" in history_str or "items is clone" in history_str or "clone" in history_str)
             else (False, "請宣告 alias 與 clone，驗證 items is alias 與 items == clone！")
         )),

        # ----------------------------------------------------------------------
        # 8-6-3 製作真正的獨立副本：copy() 方法 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-6-3", "填空題", "呼叫 copy() 方法建立獨立副本 (safe_cart)", 6,
         lambda g: (
             (True, "使用 .copy() 建立獨立副本成功！")
             if ("original_cart.copy()" in history_clean) or
                (g.get("safe_cart") == ["牛奶", "麵包", "蘋果"] and "糖果" in g.get("original_cart", []))
             else (False, "請在 8-6-3 填空題空格填入方法名稱 copy！")
         )),

        ("8-6-3", "練習題", "獨立副本調分輸出 (scores.copy() 加分獨立不連動)", 9,
         lambda g: (
             (True, "copy() 調分副本與原成績單雙軌輸出正確！")
             if ("scores.copy()" in history_clean and ("+= 10" in history_str or "+10" in history_clean)) or
                ("[70, 80, 90]\n[80, 90, 100]" in history_str or "[50, 60]\n[60, 70]" in history_str)
             else (False, "請使用 copy() 建立副本並為副本加 10 分，依序印出兩份成績！")
         )),

        ("8-6-3", "挑戰題", "商品調價模擬器 (promo_prices = original_prices.copy())", 5,
         lambda g: (
             (True, "獨立調價副本建構與八折計算正確！")
             if ("original_prices.copy()" in history_clean and ("* 8 // 10" in history_str or "*8//10" in history_clean)) or
                ("[100, 200, 320]" in history_str)
             else (False, "請建立 copy() 副本 promo_prices 並將 > 200 商品打八折輸出！")
         )),

        # ----------------------------------------------------------------------
        # 8-6-4 切片複製經典技法：b = a[:] (共 20 分)
        # ----------------------------------------------------------------------
        ("8-6-4", "填空題", "全範圍切片複製語法 words[:]", 6,
         lambda g: (
             (True, "全範圍切片 words[:] 複製完全正確！")
             if ("words[:]" in history_clean) or
                (g.get("new_words") == ["PYTHON", "rocks"] and g.get("words") == ["python", "rocks"])
             else (False, "請在 8-6-4 填空題中括號內填入冒號 : 完成全範圍切片複製！")
         )),

        ("8-6-4", "練習題", "切片複製獨立性與 pop 移除印出長度", 9,
         lambda g: (
             (True, "nums[:] 切片副本與 pop() 長度驗證正確！")
             if ("nums[:]" in history_clean and "filtered_nums.pop()" in history_clean) or
                ("長度: 4" in history_str and "長度: 3" in history_str)
             else (False, "請使用 nums[:] 複製副本，從副本 pop 末位並印出兩者內容與長度！")
         )),

        ("8-6-4", "挑戰題", "參照、copy() 與 [:] 三重同一性驗證", 5,
         lambda g: (
             (True, "b=a、copy() 與 [:] 三重身分驗證完整！")
             if ("a is b" in history_str and "a is c" in history_str and "a is d" in history_str) or
                ("True\nFalse\nFalse" in history_str)
             else (False, "請分別輸出 a is b, a is c, a is d 的布林值結果！")
         )),

        # ----------------------------------------------------------------------
        # 8-6-5 淺拷貝（Shallow Copy）的核心本質與防禦實踐 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-6-5", "填空題", "list() 型態建構函式淺拷貝 (independent_tags)", 6,
         lambda g: (
             (True, "使用 list(original_tags) 建構式拷貝成功！")
             if ("list(original_tags)" in history_clean) or
                ("apcs" in g.get("independent_tags", []) and "apcs" not in g.get("original_tags", []))
             else (False, "請在 8-6-5 填空題空格填入型態名稱 list！")
         )),

        ("8-6-5", "練習題", "副本清空測試 (test_stock.clear() 原始長度不受影響)", 9,
         lambda g: (
             (True, "副本清空與原庫存長度保留輸出正確！")
             if ("test_stock.clear()" in history_clean or "test_stock[:] = []" in history_str) and
                ("原始長度:" in history_str and "副本長度:" in history_str) or
                ("原始長度: 3\n副本長度: 0" in history_str or "原始長度: 1\n副本長度: 0" in history_str)
             else (False, "請以 copy() 建立副本並清空，輸出原始長度與副本長度！")
         )),

        ("8-6-5", "挑戰題", "模擬資料防護系統 (加獎勵積分 100 原總和保持 60)", 5,
         lambda g: (
             (True, "安全副本資料防護與總和比對正確！")
             if ("working_points" in history_str and ".copy(" in history_str and "sum(" in history_str) or
                ("60" in history_str and "160" in history_str)
             else (False, "請在安全副本中加 100 分，驗證原串列總和仍保持為 60！")
         ))
    ]

    # 4. 逐題進行驗證與計分
    item_results = []
    pass_count = 0

    print("=" * 72)
    print(f"📊 《PythAPCS123》單元 8-6 學習成效自動評分檢驗報告")
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通串列參照共用、id() 記憶體門牌、is 與 == 對決、copy() 與 [:] 淺拷貝，防禦工程宗師！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，串列參照大陷阱與獨立副本原理掌握精準！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調 is 運算子與 copy() 呼叫！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print(f"📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f"🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)

    # --------------------------------------------------------------------------
    # 📝 1. 本地日誌記錄
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "8-6",
        "unit_title": "串列參照與淺拷貝",
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
        log_filename = "score_log_unit_8_6.json"
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
auto_grade_unit_8_6()
