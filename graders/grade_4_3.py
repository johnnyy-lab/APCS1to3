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
NOTEBOOK_FILE = "PythAPCS123_4-3_print_end_parameter.ipynb"

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


def auto_grade_unit_4_3(env=None):
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

    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""

    test_cases = [
        # ----------------------------------------------------------------------
        # 4-3-1 認識結尾參數 end——揭開自動換行 \n 的秘密 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-1", "填空題", "認識 end 參數與預設換行 (end='\\n')", 6, ("msg1",),
         lambda g: (
             (True, "end 參數填寫正確：成功設定 end='\\n' 輸出天文觀測通知！")
             if (("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str) and
                 ("msg1" in history_str or "火星衝" in history_str or g.get("msg1") is not None))
             else (False, "請在 4-3-1 填空題空格填入 end='\\n' 並執行儲存格！")
         )),

        ("4-3-1", "練習題", "運動會賽程上午與下午換行輸出 (morning_event, afternoon_event)", 8, ("morning_event", "afternoon_event"),
         lambda g: (
             (True, "校慶賽程換行公告完成！")
             if (("morning_event" in g and "afternoon_event" in g) and
                 ("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str))
             else (False, "請宣告 morning_event, afternoon_event 並在第一次 print() 加上 end='\\n' 輸出！")
         )),

        ("4-3-1", "挑戰題", "氣象站今明兩天氣溫逐日通報 (temp_today, temp_tomorrow)", 6, ("temp_today", "temp_tomorrow"),
         lambda g: (
             (True, f"氣溫通報設定完成：今天={g.get('temp_today')}度、明天={g.get('temp_tomorrow')}度！")
             if (("temp_today" in g and "temp_tomorrow" in g) and
                 ("end='\\n'" in history_str or 'end="\\n"' in history_str or "end=\\n" in history_str))
             else (False, "請建立 temp_today, temp_tomorrow 變數，並在第一次輸出加上 end='\\n'！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-2 取消換行緊密相連——空字串 end='' 接續輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-2", "填空題", "取消換行接續輸出金額 (end='')", 6, ("total_price",),
         lambda g: (
             (True, "取消換行設定正確：end=''！")
             if (("end=''" in history_str or 'end=""' in history_str) and
                 ("應付總額" in history_str or "total_price" in history_str or g.get("total_price") == 360))
             else (False, "請在 4-3-2 填空題空格填入 end='' 取消換行並執行儲存格！")
         )),

        ("4-3-2", "練習題", "經驗值接續輸出 (exp_points, end='')", 8, ("exp_points",),
         lambda g: (
             (True, f"經驗值接續輸出成功：exp_points={g.get('exp_points')}！")
             if (("exp_points" in g) and
                 ("end=''" in history_str or 'end=""' in history_str) and
                 ("獲得經驗值" in history_str))
             else (False, "請宣告 exp_points 變數，並使用 print('獲得經驗值: +', end='') 接續輸出！")
         )),

        ("4-3-2", "挑戰題", "密碼三片段單行拼裝 (part_a, part_b, part_c)", 6, ("part_a", "part_b", "part_c"),
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
        ("4-3-3", "填空題", "選手背號單行空格間隔 (end=' ')", 6, ("winner1",),
         lambda g: (
             (True, "結尾空格設定正確：end=' '！")
             if (("end=' '" in history_str or 'end=" "' in history_str) and
                 ("winner1" in history_str or g.get("winner1") == 15))
             else (False, "請在 4-3-3 填空題空格填入 end=' ' 並執行儲存格！")
         )),

        ("4-3-3", "練習題", "捷運語音路線箭頭串聯 (st1, st2, st3, end=' -> ')", 8, ("st1", "st2", "st3"),
         lambda g: (
             (True, "捷運廣播路線單行箭頭串接完成！")
             if (("st1" in g and "st2" in g and "st3" in g) and
                 ("end=' -> '" in history_str or 'end=" -> "' in history_str or "->" in history_str))
             else (False, "請宣告 st1, st2, st3 變數，並使用 print(..., end=' -> ') 串接輸出！")
         )),

        ("4-3-3", "挑戰題", "三關金幣累加算式接續拼裝 (coin1, coin2, coin3)", 6, ("coin1", "coin2", "coin3"),
         lambda g: (
             (True, f"金幣累加算式輸出正確：{g.get('coin1')} + {g.get('coin2')} + {g.get('coin3')}！")
             if (("coin1" in g and "coin2" in g and "coin3" in g) and
                 ("+" in history_str and "=" in history_str))
             else (False, "請建立 coin1, coin2, coin3 變數，並利用 end 參數組裝出金幣累加算式！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-4 結尾的雙重換行與段落拉開——end='\n\n' 大段落排版術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-4", "填空題", "標題下方雙換行空行排版 (end='\\n\\n')", 6, ("headline",),
         lambda g: (
             (True, "雙換行排版設定正確：end='\\n\\n'！")
             if (("end='\\n\\n'" in history_str or 'end="\\n\\n"' in history_str or "end=\\n\\n" in history_str) and
                 ("headline" in history_str or g.get("headline") is not None))
             else (False, "請在 4-3-4 填空題空格填入 end='\\n\\n' 並執行儲存格！")
         )),

        ("4-3-4", "練習題", "兩則重要公告段落拉開 (notice1, notice2, end='\\n\\n')", 8, ("notice1", "notice2"),
         lambda g: (
             (True, "兩則公告段落分離排版完成！")
             if (("notice1" in g and "notice2" in g) and
                 ("end='\\n\\n'" in history_str or 'end="\\n\\n"' in history_str or "end=\\n\\n" in history_str))
             else (False, "請宣告 notice1, notice2 並使用 end='\\n\\n' 達成段落分離！")
         )),

        ("4-3-4", "挑戰題", "資安警告分隔線包覆排版 (alert_title, alert_action)", 6, ("alert_title", "alert_action"),
         lambda g: (
             (True, "資安警報卡分隔線包覆排版完成！")
             if (("alert_title" in g and "alert_action" in g) and
                 ("-" in history_str or "---" in str(g.get("alert_title")) or "end=" in history_str))
             else (False, "請宣告 alert_title, alert_action 變數，並在印出標題時以 end 包含換行與橫線！")
         )),

        # ----------------------------------------------------------------------
        # 4-3-5 綜合雙劍合璧——sep 與 end 同時登場的精密排版術 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-3-5", "填空題", "風速連字號與單位結尾雙參數 (sep='-', end=' km/h\\n')", 6, ("v1",),
         lambda g: (
             (True, "雙參數設定正確：sep='-' 搭配 end=' km/h\\n'！")
             if (("sep='-'" in history_str or 'sep="-"' in history_str) and
                 ("km/h" in history_str or "end=" in history_str) and
                 ("v1" in history_str or g.get("v1") == 12))
             else (False, "請在 4-3-5 填空題空格依序填入 sep 與 end 關鍵字名稱並執行！")
         )),

        ("4-3-5", "練習題", "機器人三軸座標精密排版 (x, y, z, sep=', ', end=']\\n')", 8, ("x", "y", "z"),
         lambda g: (
             (True, f"機器人三軸座標排版完成：[{g.get('x')}, {g.get('y')}, {g.get('z')}]！")
             if (("x" in g and "y" in g and "z" in g) and
                 ("Robot Pos" in history_str) and
                 ("sep=" in history_str and "end=" in history_str))
             else (False, "請宣告 x, y, z 並使用 end='' 前導字串搭配 sep=', ', end=']\\n' 輸出！")
         )),

        ("4-3-5", "挑戰題", "戰艦雷達目標掃描儀表板 (target1, target2, target3)", 6, ("target1", "target2", "target3"),
         lambda g: (
             (True, f"雷達掃描狀態儀表板輸出成功：{g.get('target1')} ~ {g.get('target2')} ~ {g.get('target3')}！")
             if (("target1" in g and "target2" in g and "target3" in g) and
                 ("雷達目標掃描" in history_str) and
                 ("sep=" in history_str and "end=" in history_str))
             else (False, "請宣告 target1, target2, target3 變數，同時使用 sep 與 end 參數精密排版！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美駕馭 print() 結尾參數 end 與雙劍合璧！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-3：print() 結尾符號參數 end —— 自動評分報告")
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
        "unit": "4-3",
        "unit_title": "print() 結尾符號參數 end",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_3.py",
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
auto_grade_unit_4_3()
