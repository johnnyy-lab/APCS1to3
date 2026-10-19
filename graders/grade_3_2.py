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
import unicodedata
from datetime import datetime, timezone, timedelta
import logging

# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_3-2_character_and_ascii_ord_chr.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max，
    評分器與學員程式共用同一個全域，呼叫內建會被學員變數遮蔽。"""
    total = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total


def _pad(text, width):
    """以顯示寬度為基準補齊空白，讓全形題名在終端也能對齊。"""
    gap = width - _disp_width(text)
    if gap > 0:
        return text + " " * gap
    return text


def _student_value(env, names):
    """各題學生實際值，截斷到 80 字元，方便分辨 7 與 7.0。"""
    parts = []
    for name in names:
        if name in env:
            parts.append(f"{name}={env.get(name)!r}")
        else:
            parts.append(f"{name}=缺")
    return ", ".join(parts)[:80]

def fetch_google_account_info():
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = globals()
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name


def auto_grade_unit_3_2():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info()

    # 3. 整合身分識別欄位（區分 Colab 雲端認證與本機免登入自評）
    is_colab = False
    try:
        import google.colab
        is_colab = True
    except ImportError:
        is_colab = False

    if google_email:
        final_email = google_email
        final_google_name = google_name if google_name else declared_name
        combined_display_name = f"{declared_name} (Google: {final_google_name})"
    elif not is_colab:
        final_email = "本機"
        final_google_name = "本機"
        combined_display_name = f"{declared_name} (本機)"
    else:
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未綁定 Google"
        final_google_name = "訪客"
        combined_display_name = declared_name

    tw_tz = timezone(timedelta(hours=8))
    timestamp_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    test_cases = [
        # ----------------------------------------------------------------------
        # 3-2-1 ord() 字元身分證——探訪 ASCII 編碼與連續性特徵 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-1", "填空題", "ord() 查驗字元 ASCII 編碼 (ascii_code = 90)", 6, ("ascii_code",),
         lambda g: (
             (True, "查驗成功：ord('Z') = 90！")
             if (g.get("ascii_code") == 90 and type(g.get("ascii_code")) is int)
             else (False, "找不到 ascii_code 或數值不為 90，請在空格填入 ord 並執行！")
         )),

        ("3-2-1", "練習題", "單一字元 ASCII 編碼取得並印出 (check_char)", 8, ("check_char",),
         lambda g: (
             (True, f"字元 ASCII 編碼取得正確！(check_char='{g.get('check_char')}')")
             if ("check_char" in g and
                 (any(v in [77, 57] and type(v) is int for v in g.values()) or
                  (isinstance(g.get("check_char"), str) and len(g.get("check_char")) == 1 and
                   any(v == ord(g.get("check_char")) for v in g.values() if type(v) is int))))
             else (False, "找不到 check_char，請宣告單一字元並使用 ord() 計算其 ASCII 編碼！")
         )),

        ("3-2-1", "挑戰題", "計算字母 'g' 距基準 'a' 的相對距離 (6)", 6, ("target_letter",),
         lambda g: (
             (True, "字母距離計算正確：ord('g') - ord('a') = 6！")
             if any(v == 6 and type(v) is int for v in g.values()) or
                (g.get("target_letter") == "g" and any(v == 6 for v in g.values()))
             else (False, "請宣告 target_letter = 'g'，並計算 ord('g') - ord('a') 得到相對差距 6！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-2 chr() 編碼變身術——數字召喚字元 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-2", "填空題", "chr() 召喚字元 (secret_char = 'S')", 6, ("secret_char",),
         lambda g: (
             (True, "字元召喚成功：chr(83) = 'S'！")
             if (g.get("secret_char") == 'S')
             else (False, "找不到 secret_char 或字元不為 'S'，請在空格填入 chr 並執行！")
         )),

        ("3-2-2", "練習題", "整數編碼轉回對應字元 (ascii_number)", 8, ("ascii_number",),
         lambda g: (
             (True, "數字召喚字元正確！")
             if ("ascii_number" in g and
                 (any(v in ['P', 'k'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("ascii_number"), int) and
                   any(v == chr(g.get("ascii_number")) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 ascii_number，請使用 chr(ascii_number) 將數值召喚回字元！")
         )),

        ("3-2-2", "挑戰題", "字母時光機下一個字元召喚 ('I')", 6, ("base_ascii",),
         lambda g: (
             (True, "字母時光機召喚成功：chr(72 + 1) = 'I'！")
             if any(v == 'I' for v in g.values() if isinstance(v, str)) or
                (g.get("base_ascii") == 72 and any(v == 'I' for v in g.values()))
             else (False, "請宣告 base_ascii = 72，並使用 chr(base_ascii + 1) 召喚出緊鄰的字母 'I'！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-3 經典差值 32（0x20）——純手工大小寫無痛轉換 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-3", "填空題", "大寫手工加 32 轉小寫 (small_ch = 'k')", 6, ("small_ch",),
         lambda g: (
             (True, "大小寫轉換成功：chr(ord('K') + 32) = 'k'！")
             if (g.get("small_ch") == 'k')
             else (False, "找不到 small_ch 或數值不為 'k'，請在空格填入 32 並執行！")
         )),

        ("3-2-3", "練習題", "大寫字母手工轉小寫 (upper_input)", 8, ("upper_input",),
         lambda g: (
             (True, "大寫轉小寫運算正確！")
             if ("upper_input" in g and
                 (any(v in ['g', 'w'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("upper_input"), str) and len(g.get("upper_input")) == 1 and
                   any(v == chr(ord(g.get("upper_input")) + 32) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 upper_input，請以 chr(ord(upper_input) + 32) 完成手工小寫轉換！")
         )),

        ("3-2-3", "挑戰題", "小寫字母手工減 32 逆向轉大寫 ('R')", 6, ("small_input",),
         lambda g: (
             (True, "小寫轉大寫逆向變身成功：chr(ord('r') - 32) = 'R'！")
             if any(v == 'R' for v in g.values() if isinstance(v, str)) or
                (g.get("small_input") == 'r' and any(v == 'R' for v in g.values()))
             else (False, "請宣告 small_input = 'r'，以 chr(ord(small_input) - 32) 轉為大寫 'R'！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-4 字母相對索引 ord(c) - ord('A')——26 個字母計數器起手式 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-4", "填空題", "大寫字母相對索引 0 起算 (letter_idx = 7)", 6, ("letter_idx",),
         lambda g: (
             (True, "相對索引計算成功：ord('H') - ord('A') = 7！")
             if (g.get("letter_idx") == 7 and type(g.get("letter_idx")) is int)
             else (False, "找不到 letter_idx 或數值不為 7，請在空格填入 'A' 並執行！")
         )),

        ("3-2-4", "練習題", "字母在 26 字母表中的序號 (target_ch)", 8, ("target_ch",),
         lambda g: (
             (True, "字母序號計算正確！")
             if ("target_ch" in g and
                 (any(v in [3, 12] and type(v) is int for v in g.values()) or
                  (isinstance(g.get("target_ch"), str) and len(g.get("target_ch")) == 1 and
                   any(v == ord(g.get("target_ch")) - ord('A') for v in g.values() if type(v) is int))))
             else (False, "找不到 target_ch，請使用 ord(target_ch) - ord('A') 計算其 0 起算索引！")
         )),

        ("3-2-4", "挑戰題", "小寫字母相對序號計算 ('e' ➔ 4)", 6, ("sample_lower",),
         lambda g: (
             (True, "小寫字母序號計算成功：ord('e') - ord('a') = 4！")
             if any(v == 4 and type(v) is int for v in g.values()) or
                (g.get("sample_lower") == 'e' and any(v == 4 for v in g.values()))
             else (False, "請宣告 sample_lower = 'e'，以 ord(sample_lower) - ord('a') 算出相對序號 4！")
         )),

        # ----------------------------------------------------------------------
        # 3-2-5 凱撒密碼位移——字元循環輪替加密小魔法 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-2-5", "填空題", "字元位移加密 (encrypted_ch = 'J')", 6, ("encrypted_ch",),
         lambda g: (
             (True, "字元加密成功：chr(ord('F') + 4) = 'J'！")
             if (g.get("encrypted_ch") == 'J')
             else (False, "找不到 encrypted_ch 或不為 'J'，請在空格依序填入 chr 與 ord！")
         )),

        ("3-2-5", "練習題", "字母位移加密運算 (plain_text, shift_val)", 8, ("plain_text", "shift_val"),
         lambda g: (
             (True, "凱撒密碼字元位移計算正確！")
             if ("plain_text" in g and "shift_val" in g and
                 (any(v in ['D', 'H'] for v in g.values() if isinstance(v, str)) or
                  (isinstance(g.get("plain_text"), str) and isinstance(g.get("shift_val"), int) and
                   any(v == chr(ord(g.get("plain_text")) + g.get("shift_val")) for v in g.values() if isinstance(v, str)))))
             else (False, "找不到 plain_text 或 shift_val，請以 chr(ord(plain_text) + shift_val) 算出加密字元！")
         )),

        ("3-2-5", "挑戰題", "密碼倒退 5 步還原明文 ('F')", 6, ("secret_msg",),
         lambda g: (
             (True, "密碼還原成功：chr(ord('K') - 5) = 'F'！")
             if any(v == 'F' for v in g.values() if isinstance(v, str)) or
                (g.get("secret_msg") == 'K' and any(v == 'F' for v in g.values()))
             else (False, "請宣告 secret_msg = 'K'，以 chr(ord(secret_msg) - 5) 倒退還原明文 'F'！")
         )),
    ]

    pass_count = 0
    item_results = []
    item_outputs = []

    for uid, qtype, name, pts, watch, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception:
            ok, msg = False, "執行檢驗時發生異常，請確認程式碼是否可正常執行"

        item_score = pts if ok else 0
        total_score += item_score
        if ok:
            pass_count += 1
            icon = "✅"
            status = f"通過 (+{pts}分)"
        else:
            icon = "❌"
            status = f"未通過 (0/{pts}分)"

        out_lines = [f"{icon} [{uid} {qtype}] {_pad(name, 44)} ➔ {status}"]
        if not ok:
            out_lines.append(f"   💡 提示：{msg}")
        item_outputs.append(out_lines)

        item_results.append({
            "uid": uid,
            "type": qtype,
            "name": name,
            "passed": ok,
            "score": item_score,
            "max_score": pts,
            "message": msg,
            "student_value": _student_value(env, watch)
        })

    if total_score >= 90:
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 ord 與 chr 互轉密技，ASCII 編碼與差值 32 運用自如！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，字元與數值編碼互逆轉換觀念扎實！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 3-2：字元與 ASCII 互轉（ord, chr） —— 自動評分報告")
    print("=" * 72)
    print(f" 📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f" 🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)
    print(f" 👤 學員姓名：{declared_name}")
    print(f" 🆔 學號座號：{declared_id}")
    if google_email:
        print(f" 🔑 Google 帳號認證：{google_email}（暱稱：{final_google_name}）")
    elif not is_colab:
        print(f" 💻 執行環境：本機環境（免登入自評）")
    else:
        print(f" 📧 登記信箱：{final_email}")
    print(f" ⏰ 送交時間：{timestamp_str}")
    print("=" * 72)
    print(" 📝 題目作答細項檢驗：")
    for lines in item_outputs:
        for line in lines:
            print(line)
    print("=" * 72)

    # 試算表姓名、學號用學生輸入原值。暱稱與 email 在本機填「本機測試」。
    if google_email:
        sheet_google_name = google_name if google_name else declared_name
        sheet_google_email = google_email
    elif not is_colab:
        sheet_google_name = "本機測試"
        sheet_google_email = "本機測試"
    else:
        sheet_google_name = "未認證"
        sheet_google_email = "未認證"

    score_fingerprint = ",".join(
        f"{item['uid']}:{item['type']}:{'1' if item['passed'] else '0'}"
        for item in item_results
    )

    # --------------------------------------------------------------------------
    # 📡 雲端後台成績記錄（Google Apps Script 試算表 Webhook）
    # 欄位拆開送出。相同成績是否寫入由 Apps Script 判斷，這裡只讀回應。
    # 鐵律：絕不產生任何本地日誌暫存檔。
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "3-2",
        "unit_title": "字元與 ASCII 互轉（ord, chr）",
        "declared_name": declared_name,
        "declared_id": declared_id,
        "google_name": sheet_google_name,
        "google_email": sheet_google_email,
        "student_name": declared_name,
        "student_id": declared_id,
        "name": declared_name,
        "id": declared_id,
        "student_email": sheet_google_email,
        "email": sheet_google_email,
        "timestamp": timestamp_str,
        "total_score": total_score,
        "max_score": max_score,
        "pass_count": pass_count,
        "total_count": len(test_cases),
        "badge": badge,
        "details": item_results,
        "grader_version": GRADER_VERSION,
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_3_2.py",
        "notebook_file": NOTEBOOK_FILE,
        "score_fingerprint": score_fingerprint
    }

    if LOG_WEBHOOK_URL:
        try:
            req_data = json.dumps(log_data, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_body = response.read().decode("utf-8", errors="replace").strip()
            status = ""
            if raw_body:
                try:
                    payload = json.loads(raw_body)
                    if isinstance(payload, dict):
                        status = str(payload.get("status", "")).strip().lower()
                except json.JSONDecodeError:
                    status = ""
            if status == "duplicate":
                print("📡 [雲端回報] 成績與上次相同，未重複登錄（本機成績仍有效）。\n")
            else:
                print("📡 [雲端回報] 成績已成功上傳並登錄至授課試算表！\n")
        except Exception:
            # 離線測試或連線逾時溫和提示，絕不噴出紅色例外
            if not is_colab:
                print("📡 [本機模式] 成績已於本機評分完成（雲端試算表未連線）。\n")
            else:
                print("📡 [離線模式] 暫時無法連線至雲端試算表，但本機評分已完成。\n")

    if total_score < 100:
        print("\n💡 小技巧：若有題目顯示 ❌ 未通過，請回到上方對應題目的儲存格修改程式碼，")
        print("   並務必重新點擊該題的『▶ 播放鍵』執行，再回來執行此評分儲存格就可以刷新成績與紀錄囉！")
        print("=" * 72)


# 執行評分
auto_grade_unit_3_2()
