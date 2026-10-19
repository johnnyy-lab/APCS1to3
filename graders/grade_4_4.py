# ==============================================================================
# 🧪 《PythAPCS123》單元 4-4：變數與運算式綜合輸出 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_4.py
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
NOTEBOOK_FILE = "PythAPCS123_4-4_variable_and_expression_output.ipynb"

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


def auto_grade_unit_4_4():
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

    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""

    test_cases = [
        # ----------------------------------------------------------------------
        # 4-4-1 字串標籤與變數混合輸出——變數名牌 vs 字串引號的本質區別 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-1", "填空題", "天體日誌與視星等數值混合輸出 (star_name, magnitude)", 6, ("star_name", "magnitude"),
         lambda g: (
             (True, "字串標籤與變數填寫正確：成功輸出恆星名稱與視星等！")
             if (("star_name" in history_str and "magnitude" in history_str) or
                 (g.get("star_name") == "天狼星" and g.get("magnitude") == -1.46))
             else (False, "請在 4-4-1 填空題空格依序填入 star_name 與 magnitude 並執行！")
         )),

        ("4-4-1", "練習題", "校慶田徑賽選手成績看板 (athlete, event, score)", 8, ("athlete", "event", "score"),
         lambda g: (
             (True, f"選手成績單行混合輸出成功：{g.get('athlete')} {g.get('event')} {g.get('score')}！")
             if (("athlete" in g and "event" in g and "score" in g) and
                 ("選手：" in history_str or "公尺" in history_str))
             else (False, "請宣告 athlete, event, score 並使用單一行 print() 混合輸出文字標籤與變數！")
         )),

        ("4-4-1", "挑戰題", "深空探測船監控儀表板 (probe_name, distance_au, battery_pct)", 6, ("probe_name", "distance_au", "battery_pct"),
         lambda g: (
             (True, "探測船狀態代號與距地數據排版輸出成功！")
             if (("probe_name" in g and "distance_au" in g and "battery_pct" in g) and
                 ("探測船" in history_str or "AU" in history_str))
             else (False, "請宣告 probe_name, distance_au, battery_pct 變數，並撰寫兩行 print() 正確嵌入標籤！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-2 在 print() 中即時運算——算式先求值後輸出的精簡美學 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-2", "填空題", "披薩平分整除與取餘數即時運算 (// 與 %)", 6, ("total_slices",),
         lambda g: (
             (True, "即時運算填寫正確：成功使用 // 整除與 % 取餘數！")
             if (("//" in history_str and "%" in history_str) and
                 ("total_slices" in history_str or g.get("total_slices") == 26))
             else (False, "請在 4-4-2 填空題空格填入 // 與 % 運算子並執行儲存格！")
         )),

        ("4-4-2", "練習題", "圓周長與圓面積即時運算輸出 (r)", 8, ("r",),
         lambda g: (
             (True, f"圓幾何數值即時計算輸出成功：半徑={g.get('r')}！")
             if (("r" in g) and
                 ("3.14" in history_str) and
                 ("周長" in history_str and "面積" in history_str))
             else (False, "請宣告半徑 r，並在 print() 內部直接計算圓周長與圓面積！")
         )),

        ("4-4-2", "挑戰題", "打工薪資即時計算系統 (hourly_wage, normal_hours, overtime_hours)", 6, ("hourly_wage", "normal_hours", "overtime_hours"),
         lambda g: (
             (True, "工資計算邏輯與優先權運算正確！")
             if (("hourly_wage" in g and "normal_hours" in g and "overtime_hours" in g) and
                 ("1.5" in history_str or "平日" in history_str or "加班" in history_str))
             else (False, "請宣告 hourly_wage, normal_hours, overtime_hours 變數，並在 print() 中即時運算！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-3 消除文字與數值突兀間隔——利用 sep='' 實現中文字詞與單位無縫貼合 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-3", "填空題", "氣溫與濕度無縫貼合 (sep='')", 6, ("city",),
         lambda g: (
             (True, "字詞無縫貼合設定正確：sep=''！")
             if (("sep=''" in history_str or 'sep=""' in history_str) and
                 ("高雄市" in history_str or g.get("city") == "高雄市"))
             else (False, "請在 4-4-3 填空題末尾填入 sep='' 並執行儲存格！")
         )),

        ("4-4-3", "練習題", "跑步距離與時間單位無縫貼合 (km, mins, secs, sep='')", 8, ("km", "mins", "secs"),
         lambda g: (
             (True, f"運動報告單位貼合成功：{g.get('km')}公里，{g.get('mins')}分{g.get('secs')}秒！")
             if (("km" in g and "mins" in g and "secs" in g) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 km, mins, secs 變數，並使用 sep='' 消除空格貼合單位輸出！")
         )),

        ("4-4-3", "挑戰題", "暴擊戰鬥日誌現場無縫算式 (attacker, skill, base_damage, multiplier)", 6, ("attacker", "skill", "base_damage", "multiplier"),
         lambda g: (
             (True, "暴擊戰鬥日誌無縫輸出成功！")
             if (("attacker" in g and "skill" in g and "base_damage" in g and "multiplier" in g) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告戰鬥變數，並使用 sep='' 搭配現場傷害算式印出戰報！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-4 連續跨行與接續排版——結合 end 參數建構連貫算式與計算歷程 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-4", "填空題", "連乘算式不換行留空格 (end=' ')", 6, ("x",),
         lambda g: (
             (True, "算式接續設定正確：end=' '！")
             if (("end=' '" in history_str or 'end=" "' in history_str) and
                 ("算式" in history_str or g.get("x") == 3))
             else (False, "請在 4-4-4 填空題空格填入 end=' ' 並執行儲存格！")
         )),

        ("4-4-4", "練習題", "糖果盒裝商數餘數單行連貫接續 (candies, box, end=' ')", 8, ("candies", "box"),
         lambda g: (
             (True, f"糖果盒裝連貫輸出成功：{g.get('candies')} 顆每 {g.get('box')} 顆裝一盒！")
             if (("candies" in g and "box" in g) and
                 ("end=' '" in history_str or 'end=" "' in history_str or "//" in history_str))
             else (False, "請宣告 candies, box 變數，並分兩次 print() 接續輸出裝盒結果！")
         )),

        ("4-4-4", "挑戰題", "畢氏定理斜邊推導歷程單行組裝 (leg_a, leg_b)", 6, ("leg_a", "leg_b"),
         lambda g: (
             (True, f"畢氏定理推導歷程組裝完成：兩股={g.get('leg_a')}, {g.get('leg_b')}！")
             if (("leg_a" in g and "leg_b" in g) and
                 ("斜邊" in history_str or "根號" in history_str or "**2" in history_str))
             else (False, "請宣告 leg_a, leg_b 變數，並分三步接續在同一行輸出幾何推導歷程！")
         )),

        # ----------------------------------------------------------------------
        # 4-4-5 實戰全能儀表板——變數、即時運算、sep 與 end 的終極融合 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-4-5", "填空題", "成績單內建函數 round 與 max (round, max)", 6, ("chinese",),
         lambda g: (
             (True, "內建函數填寫正確：round 與 max！")
             if (("round" in history_str and "max" in history_str) and
                 ("學生段考成績單" in history_str or g.get("chinese") == 92))
             else (False, "請在 4-4-5 填空題空格填入 round 與 max 函數名稱並執行！")
         )),

        ("4-4-5", "練習題", "直角三角形幾何分析儀全能排版 (a, b, c, sep='')", 8, ("a", "b"),
         lambda g: (
             (True, f"幾何工程分析儀輸出成功：兩股={g.get('a')}, {g.get('b')}！")
             if (("a" in g and "b" in g) and
                 ("直角三角形兩股" in history_str) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 a, b 變數，並結合即時運算與 sep='' 輸出直角三角形幾何報告！")
         )),

        ("4-4-5", "挑戰題", "智慧家庭夏月用電計費儀表板 (billing_month, kwh_used, rate_per_kwh, base_fee)", 6, ("billing_month", "kwh_used", "rate_per_kwh", "base_fee"),
         lambda g: (
             (True, "電費帳單儀表板排版與計算完成！")
             if (("billing_month" in g and "kwh_used" in g and "rate_per_kwh" in g and "base_fee" in g) and
                 ("電費通知單" in history_str or "用電" in history_str))
             else (False, "請宣告電費變數，並在 print() 內部現場計算流動電費與應繳總額！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美融合變數、即時運算、sep 與 end！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-4：變數與運算式綜合輸出 —— 自動評分報告")
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
        "unit": "4-4",
        "unit_title": "變數與運算式綜合輸出",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_4.py",
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
auto_grade_unit_4_4()
