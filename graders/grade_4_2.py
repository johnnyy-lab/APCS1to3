# ==============================================================================
# 🧪 《PythAPCS123》單元 4-2：print() 分隔符號參數 sep —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_2.py
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
NOTEBOOK_FILE = "PythAPCS123_4-2_print_separator_sep.ipynb"

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


def auto_grade_unit_4_2(env=None):
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
        # 4-2-1 認識分隔參數 sep——揭開預設半形空格的秘密 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-2-1", "填空題", "認識 sep 參數與預設空格 (sep=' ')", 6, ("name1",),
         lambda g: (
             (True, "sep 參數填寫正確：成功使用 sep=' ' 輸出學生姓名！")
             if (("sep=' '" in history_str or 'sep=" "' in history_str) and
                 ("name1" in history_str or "王小明" in history_str or g.get("name1") == "王小明"))
             else (False, "請在 4-2-1 填空題空格填入 sep=' ' 並執行儲存格！")
         )),

        ("4-2-1", "練習題", "接力選手號碼牌 (num1, num2, num3, sep=' ')", 8, ("num1", "num2", "num3"),
         lambda g: (
             (True, f"選手號碼牌輸出正確：{g.get('num1')}, {g.get('num2')}, {g.get('num3')}！")
             if (("num1" in g and "num2" in g and "num3" in g) and
                 (("sep=' '" in history_str or 'sep=" "' in history_str) or
                  ("print(num1, num2, num3" in history_str.replace(" ", ""))))
             else (False, "請宣告 num1, num2, num3 並使用 print(num1, num2, num3, sep=' ') 輸出！")
         )),

        ("4-2-1", "挑戰題", "三科成績與總分計算輸出 (chinese, english, math, total_score)", 6, ("chinese", "english", "math", "total_score"),
         lambda g: (
             (True, f"成績單計算與輸出完成：總分={g.get('total_score')} 分！")
             if (("chinese" in g and "english" in g and "math" in g) and
                 (g.get("total_score") == g.get("chinese", 0) + g.get("english", 0) + g.get("math", 0)) and
                 ("sep=' '" in history_str or 'sep=" "' in history_str or "total_score" in history_str))
             else (False, "請建立 chinese, english, math 與 total_score 總分變數，並使用 sep=' ' 印出！")
         )),

        # ----------------------------------------------------------------------
        # 4-2-2 自訂常用標點符號分隔——逗號、連字號與斜線 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-2-2", "填空題", "活動日期斜線分隔 (sep='/')", 6, ("event_year",),
         lambda g: (
             (True, "日期分隔符號設定正確：sep='/'！")
             if (("sep='/'" in history_str or 'sep="/"' in history_str) and
                 ("event_year" in history_str or "2026" in history_str or g.get("event_year") == 2026))
             else (False, "請在 4-2-2 填空題空格填入 sep='/' 並執行儲存格！")
         )),

        ("4-2-2", "練習題", "衝線成績冒號分隔 (h, m, s, sep=':')", 8, ("h", "m", "s"),
         lambda g: (
             (True, f"計時成績格式化完成：{g.get('h')}:{g.get('m')}:{g.get('s')}！")
             if (("h" in g and "m" in g and "s" in g) and
                 ("sep=':'" in history_str or 'sep=":"' in history_str))
             else (False, "請宣告 h, m, s 變數，並使用 print(h, m, s, sep=':') 輸出！")
         )),

        ("4-2-2", "挑戰題", "零件識別標籤連字號分隔 (factory_code, machine_id, batch_no)", 6, ("factory_code", "machine_id", "batch_no"),
         lambda g: (
             (True, f"零件標籤產製成功：{g.get('factory_code')}-{g.get('machine_id')}-{g.get('batch_no')}！")
             if (("factory_code" in g and "machine_id" in g and "batch_no" in g) and
                 ("sep='-'" in history_str or 'sep="-"' in history_str))
             else (False, "請建立 factory_code, machine_id, batch_no 變數，並使用 sep='-' 串接輸出！")
         )),

        # ----------------------------------------------------------------------
        # 4-2-3 消除間隔的無縫緊密黏合——空字串 sep='' (共 20 分)
        # ----------------------------------------------------------------------
        ("4-2-3", "填空題", "超商結帳金額緊密貼合 (sep='')", 6, ("total",),
         lambda g: (
             (True, "無縫貼合設定正確：sep=''！")
             if (("sep=''" in history_str or 'sep=""' in history_str) and
                 ("NT$" in history_str or "total" in history_str or g.get("total") == 250))
             else (False, "請在 4-2-3 填空題空格填入空字串 sep='' 並執行儲存格！")
         )),

        ("4-2-3", "練習題", "郵遞區號與行政區緊密輸出 (zip_code, area, sep='')", 8, ("zip_code", "area"),
         lambda g: (
             (True, f"郵遞地址緊密合併成功：{g.get('zip_code')}{g.get('area')}！")
             if (("zip_code" in g and "area" in g) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 zip_code 與 area 變數，並使用 print(zip_code, area, sep='') 緊密輸出！")
         )),

        ("4-2-3", "挑戰題", "密碼箱通關金鑰無縫組合 (lock_a, lock_b, lock_c)", 6, ("lock_a", "lock_b", "lock_c"),
         lambda g: (
             (True, "寶箱通關金鑰產製成功：KEY735！")
             if (("lock_a" in g and "lock_b" in g and "lock_c" in g) and
                 ("KEY" in history_str) and
                 ("sep=''" in history_str or 'sep=""' in history_str))
             else (False, "請宣告 lock_a, lock_b, lock_c 變數，並使用 print('KEY', ..., sep='') 緊密輸出金鑰！")
         )),

        # ----------------------------------------------------------------------
        # 4-2-4 趣味多字元與文字字串分隔——流程箭頭與對戰排版 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-2-4", "填空題", "羽球對決看板文字分隔 (sep=' vs ')", 6, ("team1",),
         lambda g: (
             (True, "對決分隔字串設定正確：sep=' vs '！")
             if (("sep=' vs '" in history_str or 'sep=" vs "' in history_str or " vs " in history_str) and
                 ("team1" in history_str or "team2" in history_str or g.get("team1") == "旗美猛虎隊"))
             else (False, "請在 4-2-4 填空題空格填入包含前後空格的對決字串 ' vs ' 並執行儲存格！")
         )),

        ("4-2-4", "練習題", "高雄歷史文化路線箭頭串聯 (s1, s2, s3, sep=' -> ')", 8, ("s1", "s2", "s3"),
         lambda g: (
             (True, "旅遊景點箭頭路線圖輸出完成！")
             if (("s1" in g and "s2" in g and "s3" in g) and
                 ("->" in history_str))
             else (False, "請宣告 s1, s2, s3 景點變數，並使用 sep=' -> ' 串聯輸出！")
         )),

        ("4-2-4", "挑戰題", "專題三階段進度條雙箭頭 (phase1, phase2, phase3, sep=' ==> ')", 6, ("phase1", "phase2", "phase3"),
         lambda g: (
             (True, "專題進度條雙箭頭看板輸出成功！")
             if (("phase1" in g and "phase2" in g and "phase3" in g) and
                 ("==>" in history_str))
             else (False, "請宣告 phase1, phase2, phase3 變數，並使用 sep=' ==> ' 串接輸出！")
         )),

        # ----------------------------------------------------------------------
        # 4-2-5 特殊跳脫分隔符號——換行符號 sep='\n' 與跳格 sep='\t' (共 20 分)
        # ----------------------------------------------------------------------
        ("4-2-5", "填空題", "機器人狀態換行跳脫字元 (sep='\\n')", 6, ("status1",),
         lambda g: (
             (True, "換行分隔跳脫字元設定正確：sep='\\n'！")
             if (("sep='\\n'" in history_str or 'sep="\\n"' in history_str or "sep=\\n" in history_str) and
                 ("status1" in history_str or "status2" in history_str or g.get("status1") == "核心電源正常"))
             else (False, "請在 4-2-5 填空題空格填入反斜線換行跳脫字元 '\\n' 並執行儲存格！")
         )),

        ("4-2-5", "練習題", "商數、餘數、絕對值垂直輸出 (quotient, remainder, abs_val, sep='\\n')", 8, ("quotient", "remainder", "abs_val"),
         lambda g: (
             (True, f"運算結果分行垂直輸出正確：商數={g.get('quotient')}、餘數={g.get('remainder')}、絕對值={g.get('abs_val')}！")
             if (("quotient" in g and "remainder" in g and "abs_val" in g) and
                 ("sep='\\n'" in history_str or 'sep="\\n"' in history_str or "sep=\\n" in history_str))
             else (False, "請宣告 quotient, remainder, abs_val 變數，並使用 sep='\\n' 垂直一行印出！")
         )),

        ("4-2-5", "挑戰題", "APCS 數值分析三部曲單行輸出 (val_sum, val_diff, val_div, sep='\\n')", 6, ("val_sum", "val_diff", "val_div"),
         lambda g: (
             (True, f"數值分析三部曲計算正確：總和={g.get('val_sum')}、差值={g.get('val_diff')}、商數={g.get('val_div')}！")
             if (("val_sum" in g and "val_diff" in g and "val_div" in g) and
                 (g.get("val_sum") == 37 and g.get("val_diff") == 21 and g.get("val_div") == 3) and
                 ("sep='\\n'" in history_str or 'sep="\\n"' in history_str or "sep=\\n" in history_str))
             else (False, "請依題意計算出 val_sum(37)、val_diff(21)、val_div(3)，並用單一行 print() 搭配 sep='\\n' 輸出！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美解鎖 print() 分隔符號 sep 所有技巧！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-2：print() 分隔符號參數 sep —— 自動評分報告")
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
        "unit": "4-2",
        "unit_title": "print() 分隔符號參數 sep",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_2.py",
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
auto_grade_unit_4_2()
