# ==============================================================================
# 🧪 《PythAPCS123》單元 2-2：整數基本算術運算與優先級 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_2.py
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

# ------------------------------------------------------------------------------
# 🌐 雲端後台成績記錄端點（已綁定 Google 試算表 Webhook）
# ------------------------------------------------------------------------------
LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_2-2_integer_arithmetic_and_precedence.ipynb"

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


def auto_grade_unit_2_2(env=None):
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

    # 4. 強制換算台灣時間（GMT+8）
    tw_tz = timezone(timedelta(hours=8))
    timestamp_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    # 5. 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 觀察變數, 檢驗邏輯)
    # 所有題目配分加總必須剛好等於 100 分！
    # 變數一律只認題幹指定的專屬名稱。
    # 五個挑戰題只認 hp、stationery_total、picnic_total、table_total、final_damage，不接受其他名稱。
    # 絕不收 ans、res、temp 等通用路人名（詳見 AGYRules/colab_notebook_grade_rules.md 第三節）。
    test_cases = [
        # ----------------------------------------------------------------------
        # 2-2-1 整數加法與減法（+、-）——數值增減與負數運算 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-1", "填空題", "零用錢增減計算 (fnl_wllt = 275)", 6, ("fnl_wllt",),
         lambda g: (
             (True, "加減運算成功：fnl_wllt = 275！")
             if (g.get("fnl_wllt") == 275 and type(g.get("fnl_wllt")) is int)
             else (False, "找不到變數 fnl_wllt 或數值不為 275，請確認 wallet - lunch + reward 並執行！")
         )),

        ("2-2-1", "練習題", "前後氣溫溫差變化量 (temp_yesterday, temp_today)", 8, ("temp_yesterday", "temp_today"),
         lambda g: (
             (True, f"溫差變化計算正確：昨天 {g.get('temp_yesterday')} 度，今天 {g.get('temp_today')} 度（變化量 {g.get('temp_today') - g.get('temp_yesterday')}）")
             if ("temp_yesterday" in g and "temp_today" in g and
                 type(g.get("temp_yesterday")) is int and type(g.get("temp_today")) is int and
                 g.get("temp_today") - g.get("temp_yesterday") in [8, -8])
             else (False, "找不到 temp_yesterday 或 temp_today，請依練習題宣告氣溫變數並印出差值！")
         )),

        ("2-2-1", "挑戰題", "勇者地底迷宮生命值結算 (base_hp = 80)", 6, ("hp",),
         lambda g: (
             (True, f"勇者生命值計算完成：hp = {g.get('hp')}")
             if ("hp" in g and type(g.get("hp")) is int and g.get("hp") > 0)
             else (False, "請依挑戰題用 base_hp = 80 搭配恢復 45、扣除 30 與扣減 20，把最終生命值存入 hp 並執行！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-2 整數乘法（*）與代數陷阱——星號連乘與嚴禁省略乘號 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-2", "填空題", "操場長寬相乘面積計算 (area = 96)", 6, ("area",),
         lambda g: (
             (True, "乘法運算成功：area = length * width = 96！")
             if (g.get("area") == 96 and type(g.get("area")) is int)
             else (False, "找不到變數 area 或數值不為 96，請在空格填入乘號 * 並點擊播放鍵執行！")
         )),

        ("2-2-2", "練習題", "營養午餐便當總額 (unit_price, quantity)", 8, ("unit_price", "quantity"),
         lambda g: (
             (True, f"便當總額計算正確：{g.get('unit_price')} * {g.get('quantity')} = {g.get('unit_price') * g.get('quantity')}")
             if ("unit_price" in g and "quantity" in g and
                 type(g.get("unit_price")) is int and type(g.get("quantity")) is int and
                 (g.get("unit_price") * g.get("quantity") in [340, 1800] or g.get("unit_price") * g.get("quantity") > 0))
             else (False, "找不到變數 unit_price 或 quantity，請依練習題說明計算單價乘以數量！")
         )),

        ("2-2-2", "挑戰題", "開學特賣文具結帳總金額計算", 6, ("stationery_total",),
         lambda g: (
             (True, f"文具結帳金額計算成功：stationery_total = {g.get('stationery_total')}")
             if ("stationery_total" in g and type(g.get("stationery_total")) is int and g.get("stationery_total") > 0)
             else (False, "請依挑戰題宣告鉛筆、筆記本、橡皮擦數量，用乘法與加法計算總金額並存入專屬變數 stationery_total！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-3 運算子優先級鐵則——先乘後加減與由左至右結合性 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-3", "填空題", "打工日薪先乘後加 (tot_slry = 1100)", 6, ("tot_slry",),
         lambda g: (
             (True, "日薪計算正確：tot_slry = 200 + 180 * 5 = 1100！")
             if (g.get("tot_slry") == 1100 and type(g.get("tot_slry")) is int)
             else (False, "找不到 tot_slry 或數值不為 1100，請填入乘號 * 並執行！")
         )),

        ("2-2-3", "練習題", "計程車跳表總車資 (base_fare, rate_per_km, extra_km)", 8, ("base_fare", "rate_per_km", "extra_km"),
         lambda g: (
             (True, f"車資先乘後加正確：基本費 {g.get('base_fare')} + 單價 {g.get('rate_per_km')} * 里程 {g.get('extra_km')}")
             if ("base_fare" in g and "rate_per_km" in g and "extra_km" in g and
                 type(g.get("base_fare")) is int and type(g.get("rate_per_km")) is int and type(g.get("extra_km")) is int and
                 g.get("base_fare") + g.get("rate_per_km") * g.get("extra_km") in [205, 400])
             else (False, "找不到 base_fare, rate_per_km, extra_km，請依練習題說明計算總車資！")
         )),

        ("2-2-3", "挑戰題", "野餐採購先乘後加減折價券 (picnic_total = 700)", 6, ("picnic_total",),
         lambda g: (
             (True, "野餐採購總額計算正確：150 + 8*45 + 8*30 - 50 = 700！")
             if (g.get("picnic_total") == 700 and type(g.get("picnic_total")) is int)
             else (False, "請依挑戰題設計 150 + 8*45 + 8*30 - 50 的一行算式，把應付總額存入專屬變數 picnic_total！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-4 運算順序的王牌指揮官——小括號 (...) 搶先執行權 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-4", "填空題", "禮物與包裝分攤小括號 (each_pay = 200)", 6, ("each_pay",),
         lambda g: (
             (True, "小括號搶先加總成功：each_pay = (500 + 100) // 3 = 200！")
             if (g.get("each_pay") == 200 and type(g.get("each_pay")) is int)
             else (False, "找不到 each_pay 或數值不為 200，請在 gift + wrap 外圍加上小括號 () 並執行！")
         )),

        ("2-2-4", "練習題", "梯形上底加下底乘高 (top, bottom, height)", 8, ("top", "bottom", "height"),
         lambda g: (
             (True, f"梯形公式小括號運算正確：({g.get('top')} + {g.get('bottom')}) * {g.get('height')} = {(g.get('top') + g.get('bottom')) * g.get('height')}")
             if ("top" in g and "bottom" in g and "height" in g and
                 type(g.get("top")) is int and type(g.get("bottom")) is int and type(g.get("height")) is int and
                 (g.get("top") + g.get("bottom")) * g.get("height") in [50, 200])
             else (False, "找不到 top, bottom, height，請使用小括號 (top + bottom) * height 計算並印出！")
         )),

        ("2-2-4", "挑戰題", "好友同行特惠小括號結算 (table_total = 900)", 6, ("table_total",),
         lambda g: (
             (True, f"好友同行金額計算成功：table_total = (180 + 45) * 4 = {g.get('table_total')}")
             if ("table_total" in g and type(g.get("table_total")) is int and g.get("table_total") == 900)
             else (False, "請用小括號把單人消費 (main_meal + drink) 先加起來，再乘以同行人數 friend_count，把結果存入 table_total！")
         )),

        # ----------------------------------------------------------------------
        # 2-2-5 多重巢狀小括號與括號大忌——由內而外層層拆解 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-2-5", "填空題", "禁絕中括號改用合法小括號 (mth_frml = 150)", 6, ("mth_frml",),
         lambda g: (
             (True, "合法小括號運算成功：mth_frml = 5 * ((10 - 2) * 3 + 6) = 150！")
             if (g.get("mth_frml") == 150 and type(g.get("mth_frml")) is int)
             else (False, "找不到 mth_frml 或數值不為 150，請在外層填入合法小括號 () 並執行！")
         )),

        ("2-2-5", "練習題", "五變數雙層巢狀小括號 ((v1+v2)*v3 - v4)*v5", 8, ("v1", "v2", "v3", "v4", "v5"),
         lambda g: (
             (True, f"雙層巢狀小括號運算正確：(({g.get('v1')}+{g.get('v2')})*{g.get('v3')} - {g.get('v4')})*{g.get('v5')} = {((g.get('v1')+g.get('v2'))*g.get('v3') - g.get('v4'))*g.get('v5')}")
             if ("v1" in g and "v2" in g and "v3" in g and "v4" in g and "v5" in g and
                 type(g.get("v1")) is int and type(g.get("v2")) is int and type(g.get("v3")) is int and
                 type(g.get("v4")) is int and type(g.get("v5")) is int and
                 ((g.get('v1')+g.get('v2'))*g.get('v3') - g.get('v4'))*g.get('v5') in [36, 50])
             else (False, "找不到變數 v1, v2, v3, v4, v5，請依練習題宣告並計算 ((v1+v2)*v3 - v4)*v5！")
         )),

        ("2-2-5", "挑戰題", "戰略遊戲傷害結算雙重小括號一行整合 (final_damage)", 6, ("final_damage", "attack", "weapon", "critical_rate", "element_rate"),
         lambda g: (
             (True, f"戰略遊戲最終傷害計算成功：final_damage = {g.get('final_damage')}")
             if ("final_damage" in g and type(g.get("final_damage")) in [int, float] and g.get("final_damage") > 0)
             else (
                 (False, "請把三步驟結合成一行雙重小括號算式，並把最終傷害存入專屬變數 final_damage！")
                 if any(k in g for k in ["attack", "weapon", "critical_rate", "element_rate"])
                 else (False, "請依挑戰題宣告 attack、weapon、critical_rate、defense、element_rate 五個變數並計算 final_damage！")
             )
         )),
    ]

    # 6. 前置遍歷評分運算（結論先行前置計算）
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

    # 7. 計算榮譽等級徽章
    if total_score >= 90:
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通四則運算優先級與小括號統御力！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，算術與優先級觀念扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    # 8. 三段式頂部資訊排版（結論先行，防範 VS Code 終端折疊截斷）
    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-2：整數基本算術運算與優先級 —— 自動評分報告")
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
        for l in lines:
            print(l)
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
        "unit": "2-2",
        "unit_title": "整數基本算術運算與優先級",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_2_2.py",
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
auto_grade_unit_2_2()
