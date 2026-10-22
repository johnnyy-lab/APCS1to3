# ==============================================================================
# 🧪 《PythAPCS123》單元 3-1：數值與文字強制轉型（int, float, str） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_3_1.py
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
NOTEBOOK_FILE = "PythAPCS123_3-1_type_casting_int_float_str.ipynb"

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


def auto_grade_unit_3_1(env=None):
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
        # 3-1-1 int() 浮點數轉整數——無條件向零截斷（Truncation） (共 20 分)
        # ----------------------------------------------------------------------
        ("3-1-1", "填空題", "int() 浮點數向零截斷 (tm_rcrd = 13)", 6, ("tm_rcrd",),
         lambda g: (
             (True, "截斷成功：tm_rcrd = int(13.85) = 13（純整數 int）！")
             if (g.get("tm_rcrd") == 13 and type(g.get("tm_rcrd")) is int)
             else (
                 (False, "注意：請使用 int() 無條件向零截斷，勿使用 round() 四捨五入成 14 喔！")
                 if (g.get("tm_rcrd") == 14)
                 else (
                     (False, "tm_rcrd 目前仍為浮點數 13.85，請使用 int() 轉型！")
                     if (g.get("tm_rcrd") == 13.85)
                     else (False, "找不到變數 tm_rcrd 或數值不為 13，請在空格填入 int 並執行！")
                 )
             )
         )),

        ("3-1-1", "練習題", "圓面積計算並以 int() 截斷輸出 (area)", 8, ("radius", "area"),
         lambda g: (
             (True, f"圓面積無條件捨去整數計算正確！(radius={g.get('radius')})")
             if ("radius" in g and
                 (any(isinstance(v, int) and v in [78, 314] for v in g.values()) or
                  any(isinstance(v, (int, float)) and int(v) in [78, 314] for k, v in g.items() if "area" in k)))
             else (
                 (False, "題目要求無條件捨去小數點輸出純整數，請使用 int(area) 轉為 int 型態！")
                 if ("area" in g and type(g.get("area")) is float and not any(isinstance(v, int) and v in [78, 314] for v in g.values()))
                 else (False, "找不到 radius 或 area，請宣告半徑並計算圓面積後以 int() 截斷小數點！")
             )
         )),

        ("3-1-1", "挑戰題", "同樂會均攤金額無條件捨去取整 (actual_share = 84)", 6, ("actual_share", "total_expense"),
         lambda g: (
             (True, "均攤金額向零截斷成功：590 / 7 截斷整數為 84 元！")
             if (g.get("actual_share") == 84 and type(g.get("actual_share")) is int) or
                (g.get("total_expense") == 590 and any(v == 84 and type(v) is int for v in g.values()))
             else (
                 (False, "actual_share 必須為純整數 84，請使用 int(total_expense / students)！")
                 if any(abs(v - 84.2857) < 0.1 for v in g.values() if isinstance(v, float))
                 else (False, "請宣告 total_expense = 590 與 students = 7，並使用 int() 截斷計算 actual_share！")
             )
         )),

        # ----------------------------------------------------------------------
        # 3-1-2 int() 純整數字串轉整數——打破型態隔閡與致命的 ValueError 陷阱 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-1-2", "填空題", "字串轉整數相加避免拼接 (tot_pt = 190)", 6, ("tot_pt",),
         lambda g: (
             (True, "字串轉型成功：tot_pt = int('150') + int('40') = 190！")
             if (g.get("tot_pt") == 190 and type(g.get("tot_pt")) is int)
             else (
                 (False, "注意：直接相加會得到字串 '15040'，請使用 int() 轉為整數再相加！")
                 if (g.get("tot_pt") == "15040")
                 else (False, "找不到 tot_pt 或數值不為 190，請在兩處空格填入 int 並執行！")
             )
         )),

        ("3-1-2", "練習題", "純整數字串轉型乘積計算 (str_x, str_y)", 8, ("str_x", "str_y"),
         lambda g: (
             (True, "整數字串轉型相乘計算正確！")
             if ("str_x" in g and "str_y" in g and
                 (any(v in [60, 1000] and type(v) is int for v in g.values()) or
                  (g.get("str_x").isdigit() and g.get("str_y").isdigit() and
                   any(v == int(g.get("str_x")) * int(g.get("str_y")) for v in g.values() if type(v) is int))))
             else (False, "找不到 str_x 或 str_y，請將字串轉為 int() 後相乘並輸出！")
         )),

        ("3-1-2", "挑戰題", "出生年份字串轉整數計算實歲年齡 (age = 14)", 6, ("birth_year_str",),
         lambda g: (
             (True, "實歲年齡計算成功：2026 - int('2012') = 14 歲！")
             if any(v == 14 and type(v) is int for k, v in g.items() if "age" in k) or
                (g.get("birth_year_str") == "2012" and any(v == 14 and type(v) is int for v in g.values()))
             else (False, "請宣告 birth_year_str = '2012'，以 int() 轉型後用 current_year 減去算出年齡 14！")
         )),

        # ----------------------------------------------------------------------
        # 3-1-3 float() 轉型為浮點數——打造小數刻度與兩段式字串小數轉整數法 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-1-3", "填空題", "特價商品兩段式轉型 int(float(str)) (fnl_prc = 49)", 6, ("fnl_prc",),
         lambda g: (
             (True, "兩段式轉型成功：int(float('49.9')) = 49！")
             if (g.get("fnl_prc") == 49 and type(g.get("fnl_prc")) is int)
             else (
                 (False, "fnl_prc 目前為浮點數 49.9，請外層加上 int() 截斷小數點！")
                 if (g.get("fnl_prc") == 49.9)
                 else (False, "找不到 fnl_prc 或數值不為 49，請在空格依序填入 int 與 float！")
             )
         )),

        ("3-1-3", "練習題", "兩浮點數字串轉型總和 (float(str_x) + float(str_y))", 8, ("str_x", "str_y"),
         lambda g: (
             (True, "浮點數字串轉型相加正確！")
             if ("str_x" in g and "str_y" in g and
                 (any(isinstance(v, (int, float)) and abs(v - 7.7) < 1e-4 for v in g.values()) or
                  any(isinstance(v, (int, float)) and abs(v - 11.0) < 1e-4 for v in g.values()) or
                  any(isinstance(v, float) for k, v in g.items() if "sum" in k or "total" in k)))
             else (
                 (True, "浮點數字串轉型相加正確！")
                 if any(isinstance(v, (int, float)) and (abs(v - 7.7) < 1e-4 or abs(v - 11.0) < 1e-4) for v in g.values())
                 else (False, "找不到 str_x 或 str_y，請使用 float() 轉型後相加並印出！")
             )
         )),

        ("3-1-3", "挑戰題", "身高字串轉 float 計算 BMI 並取整數 (22)", 6, ("height_str",),
         lambda g: (
             (True, "BMI 計算與整數截斷成功（bmi 取整為 22）！")
             if any(v == 22 and type(v) is int for v in g.values()) or
                (g.get("height_str") == "1.75" and any(abs(v - 22.857) < 0.1 for v in g.values() if isinstance(v, float)))
             else (False, "請宣告 height_str='1.75'，以 float() 轉型後計算 weight / (h**2)，再以 int() 取整印出 22！")
         )),

        # ----------------------------------------------------------------------
        # 3-1-4 str() 轉型為文字字串——安全無縫拼接與格式輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-1-4", "填空題", "數值轉字串拼接學籍成績單 (report_card)", 6, ("report_card",),
         lambda g: (
             (True, "字串轉型拼接成功：report_card = '學生#101 得分:96'！")
             if (g.get("report_card") == "學生#101 得分:96" or
                 (isinstance(g.get("report_card"), str) and "101" in g.get("report_card") and "96" in g.get("report_card")))
             else (False, "找不到 report_card 或格式不符，請在兩處空格填入 str 函數！")
         )),

        ("3-1-4", "練習題", "時分整數轉字串組裝時鐘格式 (hours, minutes)", 8, ("hours", "minutes"),
         lambda g: (
             (True, "時鐘格式字串組裝正確！")
             if any(v in ["9h30m", "14h5m"] for v in g.values() if isinstance(v, str)) or
                ("hours" in g and "minutes" in g and
                 any(str(g.get("hours")) + "h" + str(g.get("minutes")) + "m" == v for v in g.values() if isinstance(v, str)))
             else (False, "找不到符合格式的時鐘字串（如 '9h30m'），請使用 str(hours) + 'h' + str(minutes) + 'm' 組合！")
         )),

        ("3-1-4", "挑戰題", "電競戰隊戰報字串格式化拼接", 6, ("team_name",),
         lambda g: (
             (True, "戰報字串格式化組裝成功（戰隊[閃電狼] 戰績 18勝-2敗）！")
             if any(isinstance(v, str) and "閃電狼" in v and "18勝-2敗" in v for v in g.values()) or
                (g.get("team_name") == "閃電狼" and any(isinstance(v, str) and "18" in v and "2" in v for v in g.values()))
             else (False, "請宣告 team_name='閃電狼', wins=18, losses=2，並組合成 '戰隊[閃電狼] 戰績 18勝-2敗'！")
         )),

        # ----------------------------------------------------------------------
        # 3-1-5 數值與文字強制轉型實務綜合應用——建立商品標籤與計費字串輸出 (共 20 分)
        # ----------------------------------------------------------------------
        ("3-1-5", "填空題", "文具店打折計算與收據明細 (total_pay = 108)", 6, ("unit_price", "total_pay", "msg"),
         lambda g: (
             (True, "綜合轉型成功：unit_price=24, total_pay=108，明細字串輸出正確！")
             if (g.get("unit_price") == 24 and g.get("total_pay") == 108 and
                 isinstance(g.get("msg"), str) and "108" in g.get("msg"))
             else (False, "請依序填入 int（轉單價）、int（轉結帳整數）、str（轉字串收據明細）！")
         )),

        ("3-1-5", "練習題", "遊樂場代幣兌換與找零格式化 (coins, change)", 8, ("coins", "change"),
         lambda g: (
             (True, "代幣兌換與找零計算正確！")
             if ((g.get("coins") == 33 and g.get("change") == 5) or
                 (g.get("coins") == 8 and g.get("change") == 0) or
                 any(isinstance(v, str) and "兌換代幣：" in v and "找零：" in v for v in g.values()))
             else (False, "找不到 coins 或 change，請以 // 計算代幣、% 計算找零，並以 str() 組合成字串！")
         )),

        ("3-1-5", "挑戰題", "影城團體訂票打折與手續費總額 (final_fee = 1065)", 6, ("final_fee",),
         lambda g: (
             (True, "影城團體訂票計算與明細字串組裝正確（實付總額：1065 元）！")
             if (g.get("final_fee") == 1065) or
                any(isinstance(v, str) and "1065" in v and "訂票" in v for v in g.values())
             else (False, "請計算 discounted_tickets = int(280 * 4 * 0.88)，加上手續費 80 得 final_fee = 1065 並印出！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通三大強制轉型神技，型態隔閡與 ValueError 全數瓦解！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，數值與文字轉型觀念清晰扎實！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 3-1：數值與文字強制轉型（int, float, str） —— 自動評分報告")
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
        "unit": "3-1",
        "unit_title": "數值與文字強制轉型（int, float, str）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_3_1.py",
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
auto_grade_unit_3_1()
