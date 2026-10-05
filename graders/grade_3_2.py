# ==============================================================================
# 🧪 《PythAPCS123》單元 3-2：字元與 ASCII 互轉（ord, chr） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_3_2.py
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

def auto_grade_unit_3_2():
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 3-2-1 ord() 字元身分證——探訪 ASCII 編碼與連續性特徵 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-1", "填空題", "ord() 查驗字元 ASCII 編碼 (ascii_code = 90)", 6,
         lambda g: (
             (True, "查驗成功：ord('Z') = 90！")
             if (g.get("ascii_code") == 90 and type(g.get("ascii_code")) is int)
             else (False, "找不到 ascii_code 或數值不為 90，請在空格填入 ord 並執行！")
         )),

        ("3-2-1", "練習題", "單一字元 ASCII 編碼取得並印出 (check_char)", 8,
         lambda g: (
             (True, f"字元 ASCII 編碼取得正確！(check_char='{g.get('check_char')}')")
             if ("check_char" in g and
                 (any(v in [77, 57] and type(v) is int for v in g.values()) or
                  (isinstance(g.get("check_char"), str) and len(g.get("check_char")) == 1 and
                   any(v == ord(g.get("check_char")) for v in g.values() if type(v) is int))))
             else (False, "找不到 check_char，請宣告單一字元並使用 ord() 計算其 ASCII 編碼！")
         )),

        ("3-2-1", "挑戰題", "計算字母 'g' 距基準 'a' 的相對距離 (6)", 6,
         lambda g: (
             (True, "字母距離計算正確：ord('g') - ord('a') = 6！")
             if any(v == 6 and type(v) is int for v in g.values()) or
                (g.get("target_letter") == "g" and any(v == 6 for v in g.values()))
             else (False, "請宣告 target_letter = 'g'，並計算 ord('g') - ord('a') 得到相對差距 6！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-2 chr() 編碼變身術——數字召喚字元 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-2", "填空題", "chr() 召喚字元 (secret_char = 'S')", 6,
         lambda g: (
             (True, "字元召喚成功：chr(83) = 'S'！")
             if (g.get("secret_char") == 'S')
             else (False, "找不到 secret_char 或字元不為 'S'，請在空格填入 chr 並執行！")
         )),

        ("3-2-2", "練習題", "整數編碼轉回對應字元 (ascii_number)", 8,
         lambda g: (
             (True, "數字召喚字元正確！")
             if ("ascii_number" in g and
                 (any(v in ['P', 'k'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("ascii_number"), int) and
                   any(v == chr(g.get("ascii_number")) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 ascii_number，請使用 chr(ascii_number) 將數值召喚回字元！")
         )),

        ("3-2-2", "挑戰題", "字母時光機下一個字元召喚 ('I')", 6,
         lambda g: (
             (True, "字母時光機召喚成功：chr(72 + 1) = 'I'！")
             if any(v == 'I' for v in g.values() if isinstance(v, str)) or
                (g.get("base_ascii") == 72 and any(v == 'I' for v in g.values()))
             else (False, "請宣告 base_ascii = 72，並使用 chr(base_ascii + 1) 召喚出緊鄰的字母 'I'！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-3 經典差值 32（0x20）——純手工大小寫無痛轉換 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-3", "填空題", "大寫手工加 32 轉小寫 (small_ch = 'k')", 6,
         lambda g: (
             (True, "大小寫轉換成功：chr(ord('K') + 32) = 'k'！")
             if (g.get("small_ch") == 'k')
             else (False, "找不到 small_ch 或數值不為 'k'，請在空格填入 32 並執行！")
         )),

        ("3-2-3", "練習題", "大寫字母手工轉小寫 (upper_input)", 8,
         lambda g: (
             (True, "大寫轉小寫運算正確！")
             if ("upper_input" in g and
                 (any(v in ['g', 'w'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("upper_input"), str) and len(g.get("upper_input")) == 1 and
                   any(v == chr(ord(g.get("upper_input")) + 32) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 upper_input，請以 chr(ord(upper_input) + 32) 完成手工小寫轉換！")
         )),

        ("3-2-3", "挑戰題", "小寫字母手工減 32 逆向轉大寫 ('R')", 6,
         lambda g: (
             (True, "小寫轉大寫逆向變身成功：chr(ord('r') - 32) = 'R'！")
             if any(v == 'R' for v in g.values() if isinstance(v, str)) or
                (g.get("small_input") == 'r' and any(v == 'R' for v in g.values()))
             else (False, "請宣告 small_input = 'r'，以 chr(ord(small_input) - 32) 轉為大寫 'R'！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-4 字母相對索引 ord(c) - ord('A')——26 個字母計數器起手式 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-4", "填空題", "大寫字母相對索引 0 起算 (letter_idx = 7)", 6,
         lambda g: (
             (True, "相對索引計算成功：ord('H') - ord('A') = 7！")
             if (g.get("letter_idx") == 7 and type(g.get("letter_idx")) is int)
             else (False, "找不到 letter_idx 或數值不為 7，請在空格填入 'A' 並執行！")
         )),

        ("3-2-4", "練習題", "字母在 26 字母表中的序號 (target_ch)", 8,
         lambda g: (
             (True, "字母序號計算正確！")
             if ("target_ch" in g and
                 (any(v in [3, 12] and type(v) is int for v in g.values()) or
                  (isinstance(g.get("target_ch"), str) and len(g.get("target_ch")) == 1 and
                   any(v == ord(g.get("target_ch")) - ord('A') for v in g.values() if type(v) is int))))
             else (False, "找不到 target_ch，請使用 ord(target_ch) - ord('A') 計算其 0 起算索引！")
         )),

        ("3-2-4", "挑戰題", "小寫字母相對序號計算 ('e' ➔ 4)", 6,
         lambda g: (
             (True, "小寫字母序號計算成功：ord('e') - ord('a') = 4！")
             if any(v == 4 and type(v) is int for v in g.values()) or
                (g.get("sample_lower") == 'e' and any(v == 4 for v in g.values()))
             else (False, "請宣告 sample_lower = 'e'，以 ord(sample_lower) - ord('a') 算出相對序號 4！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-5 凱撒密碼位移——字元循環輪替加密小魔法 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-5", "填空題", "字元位移加密 (encrypted_ch = 'J')", 6,
         lambda g: (
             (True, "字元加密成功：chr(ord('F') + 4) = 'J'！")
             if (g.get("encrypted_ch") == 'J')
             else (False, "找不到 encrypted_ch 或不為 'J'，請在空格依序填入 chr 與 ord！")
         )),

        ("3-2-5", "練習題", "字母位移加密運算 (plain_text, shift_val)", 8,
         lambda g: (
             (True, "凱撒密碼字元位移計算正確！")
             if ("plain_text" in g and "shift_val" in g and
                 (any(v in ['D', 'H'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("plain_text"), str) and isinstance(g.get("shift_val"), int) and
                   any(v == chr(ord(g.get("plain_text")) + g.get("shift_val")) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 plain_text 或 shift_val，請以 chr(ord(plain_text) + shift_val) 算出加密字元！")
         )),

        ("3-2-5", "挑戰題", "密碼倒退 5 步還原明文 ('F')", 6,
         lambda g: (
             (True, "密碼還原成功：chr(ord('K') - 5) = 'F'！")
             if any(v == 'F' for v in g.values() if isinstance(v, str)) or
                (g.get("secret_msg") == 'K' and any(v == 'F' for v in g.values()))
             else (False, "請宣告 secret_msg = 'K'，以 chr(ord(secret_msg) - 5) 倒退還原明文 'F'！")
         )),
    ]

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 3-2：字元與 ASCII 互轉（ord, chr） —— 自動評分報告")
    print(f" 👤 學員自填姓名：{declared_name}")
    if google_email:
        print(f" 🔑 Google 帳號認證：{google_email}（暱稱：{final_google_name}）")
    else:
        print(f" 📧 登記信箱：{final_email}")
    print(f" ⏰ 送交時間：{timestamp_str}")
    print("=" * 72)

    pass_count = 0
    item_results = []

    for uid, qtype, name, pts, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception as e:
            ok, msg = False, f"執行檢驗時發生異常：{e}"

        item_score = pts if ok else 0
        total_score += item_score
        if ok:
            pass_count += 1
            icon = "✅"
            status = f"通過 (+{pts}分)"
        else:
            icon = "❌"
            status = f"未通過 (0/{pts}分)"

        print(f"{icon} [{uid} {qtype}] {name:<32} ➔ {status}")
        if not ok:
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 ord 與 chr 互轉密技，ASCII 編碼與差值 32 運用自如！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，字元與數值編碼互逆轉換觀念扎實！"
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
        "unit": "3-2",
        "unit_title": "字元與 ASCII 互轉（ord, chr）",
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
        log_filename = "score_log_unit_3_2.json"
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
auto_grade_unit_3_2()
