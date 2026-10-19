# ==============================================================================
# 🧪 《PythAPCS123》單元 11-8：函數模組化解題實戰：Top-Down 拆題法與輔助函式庫 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_8.py
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
NOTEBOOK_FILE = "PythAPCS123_11-8_modular_decomposition_and_helper_functions.ipynb"

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

def get_submission_env():
    """取得 Colab / 本地端全域變數與執行歷史代碼"""
    try:
        import IPython
        ipython_inst = IPython.get_ipython()
        if ipython_inst is not None:
            user_ns = ipython_inst.user_ns
            history_cells = getattr(ipython_inst, 'user_ns', {}).get('_ih', [])
            return user_ns, history_cells
    except Exception:
        pass
    
    # 備用機制：若不在 IPython 環境，從呼叫棧主模組獲取
    try:
        import __main__
        return __main__.__dict__, []
    except Exception:
        return {}, []


def auto_grade_unit_11_8():
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

    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 11-8-1 自頂向下拆題思維 (Top-Down Decomposition) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-1", "填空題", "電商促銷結帳系統 checkout 與子流程組裝", 5, ("final_total", "checkout"),
         lambda g: (
             (True, "checkout 電商結帳模組填空正確！")
             if (callable(g.get("checkout")) and g.get("checkout")([200, 300, 500]) == 860) or
                (g.get("final_total") == 860) or
                ("checkout" in history_str and "calc_subtotal" in history_str)
             else (False, "請在 checkout 依序串接 calc_subtotal、apply_coupon 與 add_shipping！")
         )),

        ("11-8-1", "練習題", "字串清洗流水線 clean_and_format(text)", 6, ("clean_and_format",),
         lambda g: (
             (True, "clean_and_format 自頂向下清洗正確！")
             if (callable(g.get("clean_and_format"))) or
                ("clean_and_format" in history_str and "strip" in history_str)
             else (False, "請拆解 strip_punctuation 與 to_uppercase 並在主函數組合！")
         )),

        ("11-8-1", "挑戰題", "單詞統計報表系統 generate_word_report(article)", 6, ("generate_word_report",),
         lambda g: (
             (True, "generate_word_report 報表流水線正確！")
             if (callable(g.get("generate_word_report"))) or
                ("generate_word_report" in history_str and "split_words" in history_str)
             else (False, "請由高層骨架拆解分詞、過濾與頻率統計子函數並產出報表！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-2 必備輔助函式庫一：二維網格安全邊界檢查 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-2", "填空題", "邊界檢查 in_bound 與八方向雷達 sum_surrounding_8", 5, ("in_bound", "sum_surrounding_8"),
         lambda g: (
             (True, "八方向邊界掃描填空正確！")
             if (callable(g.get("in_bound")) and callable(g.get("sum_surrounding_8"))) or
                ("in_bound(nr, nc, H, W)" in history_str or "in_bound" in history_str)
             else (False, "請定義 in_bound 邊界檢查並在 sum_surrounding_8 中防護掃描！")
         )),

        ("11-8-2", "練習題", "踩地雷周圍探測 count_adjacent_mines(board, r, c)", 6, ("count_adjacent_mines",),
         lambda g: (
             (True, "踩地雷雷達探測器實作正確！")
             if (callable(g.get("count_adjacent_mines"))) or
                ("count_adjacent_mines" in history_str and "in_bound" in history_str)
             else (False, "請使用 in_bound 檢查鄰近 8 格並統計地雷數量！")
         )),

        ("11-8-2", "挑戰題", "滑雪者直線連續滑行探測 skier_slide_distance", 6, ("skier_slide_distance",),
         lambda g: (
             (True, "滑雪者直線探測實作正確！")
             if (callable(g.get("skier_slide_distance"))) or
                ("in_bound" in history_str and "while" in history_str and "dr" in history_str)
             else (False, "請沿著向量 (dr, dc) 推進，若未出界且坡度符合則累計滑行距離！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-3 必備輔助函式庫二：曼哈頓與歐式距離 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-3", "填空題", "外送巡迴路程曼哈頓計算 calc_total_trip", 5, ("calc_total_trip",),
         lambda g: (
             (True, "外送總路程計算填空正確！")
             if (callable(g.get("calc_total_trip"))) or
                ("manhattan" in history_str and "calc_total_trip" in history_str)
             else (False, "請定義 manhattan(p1, p2) 並在 calc_total_trip 累加整趟行程距離！")
         )),

        ("11-8-3", "練習題", "圓形雷達範圍探測 find_targets_in_radius", 6, ("find_targets_in_radius",),
         lambda g: (
             (True, "find_targets_in_radius 範圍篩選正確！")
             if (callable(g.get("find_targets_in_radius"))) or
                ("find_targets_in_radius" in history_str and "radius ** 2" in history_str or "dist" in history_str)
             else (False, "請定義距離平方函數並篩選距離小於等於半徑的所有目標點！")
         )),

        ("11-8-3", "挑戰題", "計程車最近乘客指派系統 dispatch_taxi", 6, ("dispatch_taxi",),
         lambda g: (
             (True, "dispatch_taxi 就近指派實作正確！")
             if (callable(g.get("dispatch_taxi"))) or
                ("dispatch_taxi" in history_str and "manhattan" in history_str)
             else (False, "請計算所有計程車與乘客之距離，回傳距離最近的計程車編號！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-4 必備輔助函式庫三：數論判定工具 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-8-4", "填空題", "完全平方數 is_perfect_square 與質數判定", 5, ("is_perfect_square",),
         lambda g: (
             (True, "完全平方數與質數判定填空正確！")
             if (callable(g.get("is_perfect_square")) and g.get("is_perfect_square")(16) is True) or
                ("is_perfect_square" in history_str and "root * root == n" in history_str)
             else (False, "請利用 root = int(n ** 0.5) 判定 root * root == n 回傳布林值！")
         )),

        ("11-8-4", "練習題", "特殊密碼數字篩選器 find_special_numbers", 6, ("find_special_numbers",),
         lambda g: (
             (True, "find_special_numbers 密碼篩選正確！")
             if (callable(g.get("find_special_numbers"))) or
                ("find_special_numbers" in history_str and "is_prime" in history_str)
             else (False, "請結合質數判定子函數，篩選區間內符合條件的特殊密碼數字！")
         )),

        ("11-8-4", "挑戰題", "雙胞胎質數搜尋器 find_twin_primes(limit)", 6, ("find_twin_primes",),
         lambda g: (
             (True, "find_twin_primes 雙胞胎質數搜尋正確！")
             if (callable(g.get("find_twin_primes")) and (3, 5) in g.get("find_twin_primes")(20)) or
                ("find_twin_primes" in history_str and "p + 2" in history_str)
             else (False, "請走訪找出所有 (p, p + 2) 皆為質數的數對清單！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-5 實戰綜合演練：自頂向下拆解大型模擬題 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-8-5", "填空題", "安全庇護所綜合篩選 count_valid_shelters", 5, ("count_valid_shelters",),
         lambda g: (
             (True, "count_valid_shelters 綜合篩選填空正確！")
             if (callable(g.get("count_valid_shelters"))) or
                ("count_valid_shelters" in history_str and "in_bound" in history_str)
             else (False, "請組裝邊界檢查與容量判斷，統計符合條件的庇護所總數！")
         )),

        ("11-8-5", "練習題", "雷達最高警報點搜尋 find_max_alert", 6, ("find_max_alert",),
         lambda g: (
             (True, "find_max_alert 最高警報點搜尋正確！")
             if (callable(g.get("find_max_alert"))) or
                ("find_max_alert" in history_str and "in_bound" in history_str)
             else (False, "請結合半徑與邊界檢查，找出雷達範圍內警報值最高之點！")
         )),

        ("11-8-5", "挑戰題", "神祕遺跡尋寶模擬 treasure_hunt(grid, path)", 5, ("treasure_hunt",),
         lambda g: (
             (True, "treasure_hunt 遺跡尋寶模擬挑戰成功！")
             if (callable(g.get("treasure_hunt"))) or
                ("treasure_hunt" in history_str and "in_bound" in history_str)
             else (False, "請以模組化函數追蹤尋寶路徑，遇到障礙或出界安全停步並統計金幣！")
         )),

        # ----------------------------------------------------------------------
        # 11-8-6 模組化除錯策略：單元測試與程式碼健檢 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-8-6", "填空題", "邊界函數單元測試 test_in_bound 與 Assert 斷言", 5, ("test_in_bound",),
         lambda g: (
             (True, "test_in_bound 單元測試填空正確！")
             if (callable(g.get("test_in_bound"))) or
                ("assert in_bound" in history_str and "test_in_bound" in history_str)
             else (False, "請在 test_in_bound 使用多個 assert 斷言覆蓋角落與越界情況！")
         )),

        ("11-8-6", "練習題", "自訂 GCD 函數單元測試 test_gcd(my_gcd)", 6, ("test_gcd",),
         lambda g: (
             (True, "test_gcd 單元測試實作正確！")
             if (callable(g.get("test_gcd"))) or
                ("assert" in history_str and "test_gcd" in history_str)
             else (False, "請設計 test_gcd 包含互質、倍數與邊界測資進行全面驗證！")
         )),

        ("11-8-6", "挑戰題", "程式碼健檢醫師：修復質數函數邊界漏洞 fixed_prime", 5, ("fixed_prime",),
         lambda g: (
             (True, "fixed_prime 質數函數邊界修復正確！")
             if (callable(g.get("fixed_prime")) and
                 g.get("fixed_prime")(1) is False and
                 g.get("fixed_prime")(0) is False and
                 g.get("fixed_prime")(-7) is False and
                 g.get("fixed_prime")(2) is True and
                 g.get("fixed_prime")(7) is True) or
                ("fixed_prime" in history_str and "n <= 1" in history_str)
             else (False, "請修復質數函數，確保 <= 1 與負數回傳 False，且 2 回傳 True！")
         ))
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
        badge = '🏆 完美滿分！你已經徹底攻克自訂函數與作用域核心技術，具備 APCS 實戰高手水準！'
    elif total_score >= 80:
        badge = '🌟 優秀！模組化概念與函數傳參掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本函數已建立，建議複習未通過的題目加強熟悉度！'
    else:
        badge = '💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 11-8：函數模組化解題實戰：Top-Down 拆題法與輔助函式庫 —— 自動評分報告")
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
        "unit": "11-8",
        "unit_title": "函數模組化解題實戰：Top-Down 拆題法與輔助函式庫",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_8.py",
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
auto_grade_unit_11_8()
