# ==============================================================================
# 🧪 《PythAPCS123》單元 2-6：進位制常數表示法（0b, 0x） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_6.py
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
NOTEBOOK_FILE = "PythAPCS123_2-6_number_bases_binary_and_hexadecimal.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max。
    直接執行腳本時答案與評分器在同一個全域，呼叫內建會被遮蔽。"""
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

def _student_env(env=None):
    """學員變數所在的命名空間。

    Cell B 隔離載入時讀 __STUDENT_ENV__。直接執行腳本，或測試把答案
    放在同一個全域時，改讀 globals()。"""
    if isinstance(env, dict):
        return env
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        return snapshot
    return globals()


def fetch_google_account_info(env=None):
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = _student_env(env)
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name


def auto_grade_unit_2_6(env=None):
    env = _student_env(env)
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info(env)

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
        # 2-6-1 電腦的原生母語——二進位常數表示法（0b） (共 25 分)
        # ----------------------------------------------------------------------
        ("2-6-1", "填空題", "二進位常數前綴 0b 宣告 (binary_val = 6)", 7, ("binary_val",),
         lambda g: (
             (True, "二進位宣告成功：binary_val = 0b110 = 6！")
             if (g.get("binary_val") == 6 and type(g.get("binary_val")) is int)
             else (False, "找不到 binary_val 或數值不為 6，請填入二進位前綴 0b 並執行！")
         )),

        ("2-6-1", "練習題", "二進位字面常數宣告解析 (val in [9, 32])", 10, ("val",),
         lambda g: (
             (True, f"二進位宣告解析正確：val = {g.get('val')}！")
             if ("val" in g and type(g.get("val")) is int and g.get("val") in [9, 32])
             else (False, "找不到變數 val，請宣告 val = 0b1001（9）或 val = 0b100000（32）！")
         )),

        ("2-6-1", "挑戰題", "智慧家庭四開關二進位狀態碼 (switch_status = 11)", 8, ("switch_status",),
         lambda g: (
             (True, "智慧家庭開關二進位宣告正確：switch_status = 0b1011 = 11！")
             if (g.get("switch_status") == 11 and type(g.get("switch_status")) is int)
             else (False, "找不到 switch_status 或數值不為 11，請以 0b1011 宣告開關狀態！")
         )),

        # ----------------------------------------------------------------------
        # 2-6-2 資訊科學的高速密碼——十六進位常數表示法（0x） (共 25 分)
        # ----------------------------------------------------------------------
        ("2-6-2", "填空題", "十六進位前綴 0x 宣告 (hex_val = 10)", 7, ("hex_val",),
         lambda g: (
             (True, "十六進位宣告成功：hex_val = 0xa = 10！")
             if (g.get("hex_val") == 10 and type(g.get("hex_val")) is int)
             else (False, "找不到 hex_val 或數值不為 10，請填入前綴 0x 並執行！")
         )),

        ("2-6-2", "練習題", "十六進位字面常數宣告解析 (val in [26, 256])", 10, ("val",),
         lambda g: (
             (True, f"十六進位宣告解析正確：val = {g.get('val')}！")
             if ("val" in g and type(g.get("val")) is int and (g.get("val") in [26, 256] or "hex" in str(g.keys())))
             else (False, "請宣告十六進位 val = 0x1a（26）或 val = 0x100（256）！")
         )),

        ("2-6-2", "挑戰題", "紫色調通道亮度強度宣告 (red_ch = 138, blue_ch = 205)", 8, ("red_ch", "blue_ch"),
         lambda g: (
             (True, "RGB 顏色通道十六進位宣告成功：red_ch=138, blue_ch=205！")
             if (g.get("red_ch") == 138 and g.get("blue_ch") == 205 and
                 type(g.get("red_ch")) is int and type(g.get("blue_ch")) is int)
             else (False, "找不到 red_ch（0x8A）或 blue_ch（0xCD），請宣告並印出十進位亮度！")
         )),

        # ----------------------------------------------------------------------
        # 2-6-3 十進位與進位制的雙向翻譯機——bin() 與 hex() (共 25 分)
        # ----------------------------------------------------------------------
        ("2-6-3", "填空題", "bin() 與 hex() 雙向翻譯 (b_res, h_res)", 7, ("b_res", "h_res"),
         lambda g: (
             (True, "進位制翻譯成功：b_res='0b1111', h_res='0xf'！")
             if (g.get("b_res") == "0b1111" and g.get("h_res") == "0xf")
             else (False, "b_res 或 h_res 結果不正確，請在填空處分別填入 bin 與 hex！")
         )),

        ("2-6-3", "練習題", "任意十進位整數轉二與十六進位 (target_val)", 10, ("target_val",),
         lambda g: (
             (True, "進位制字串轉換正確！")
             if ("target_val" in g and type(g.get("target_val")) is int and
                 (g.get("target_val") in [18, 60] or g.get("target_val") > 0))
             else (False, "找不到變數 target_val，請宣告整數並使用 bin() 與 hex() 轉換！")
         )),

        ("2-6-3", "挑戰題", "密碼解密雙組編碼轉換 (key1=100, key2=255)", 8, ("key1", "key2"),
         lambda g: (
             (True, "雙組加密編碼轉換成功（0b1100100 與 0xff）！")
             if any("0b1100100" in str(v) for v in g.values()) and any("0xff" in str(v) for v in g.values()) or
                (g.get("key1") == 100 and g.get("key2") == 255)
             else (False, "請設定 key1=100 與 key2=255，分別轉為二進位與十六進位字串！")
         )),

        # ----------------------------------------------------------------------
        # 2-6-4 APCS 實戰視野：進位制在狀態開關與位元遮罩的解題先導 (共 25 分)
        # ----------------------------------------------------------------------
        ("2-6-4", "填空題", "成就解鎖狀態位元常數 (achievement_status = 13)", 7, ("achievement_status",),
         lambda g: (
             (True, "成就狀態二進位宣告成功：achievement_status = 0b1101 = 13！")
             if (g.get("achievement_status") == 13 and type(g.get("achievement_status")) is int)
             else (False, "找不到 achievement_status 或數值不為 13，請填入 0b1101 並執行！")
         )),

        ("2-6-4", "練習題", "工廠機組監控狀態碼宣告 (system_code in [5, 14])", 10, ("system_code",),
         lambda g: (
             (True, f"機組監控代碼宣告正確：system_code = {g.get('system_code')}！")
             if ("system_code" in g and type(g.get("system_code")) is int and g.get("system_code") in [5, 14])
             else (False, "找不到 system_code，請宣告 0b0101（5）或 0b1110（14）！")
         )),

        ("2-6-4", "挑戰題", "被動技能 5 位元遮罩狀態宣告 (skill_mask)", 8, ("skill_mask",),
         lambda g: (
             (True, "5 位元被動技能狀態遮罩宣告成功！")
             if ("skill_mask" in g and type(g.get("skill_mask")) is int and 0 < g.get("skill_mask") < 32) or
                any("skill" in k and type(v) is int for k, v in g.items())
             else (False, "請宣告 5 位元二進位常數 skill_mask（例如 0b10101）並印出十進位與二進位！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通二進位與十六進位密碼，位元遮罩神準掌控！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，進位制常數與 bin/hex 轉換熟練！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-6：進位制常數表示法（0b, 0x） —— 自動評分報告")
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
        "unit": "2-6",
        "unit_title": "進位制常數表示法（0b, 0x）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_2_6.py",
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
auto_grade_unit_2_6()
