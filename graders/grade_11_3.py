# ==============================================================================
# 🧪 《PythAPCS123》單元 11-3：參數傳遞機制與副作用防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_3.py
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
NOTEBOOK_FILE = "PythAPCS123_11-3_parameter_passing_and_side_effects.ipynb"

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

def get_submission_env():
    """取得學員全域與執行歷史。Cell B 隔離載入時優先讀 __STUDENT_ENV__。"""
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        history_cells = snapshot.get("_ih", snapshot.get("In", []))
        if not isinstance(history_cells, list):
            history_cells = []
        return snapshot, history_cells
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


def auto_grade_unit_11_3(env=None):
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

    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 11-3-1 不可變物件傳遞與外部接收 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-1", "填空題", "調薪函數不可變數值傳遞 give_raise 與 return", 5, ("current_salary", "give_raise"),
         lambda g: (
             (True, "give_raise 填空正確！")
             if (callable(g.get("give_raise")) and g.get("give_raise")(40000, 5000) == 45000) or
                (g.get("current_salary") == 45000) or
                ("return new_salary" in history_str or "give_raise(current_salary" in history_str)
             else (False, "請在 give_raise 內 return new_salary 並在主程式接收回傳值！")
         )),

        ("11-3-1", "練習題", "商品折扣計算 apply_discount(price, rate)", 6, ("apply_discount",),
         lambda g: (
             (True, "apply_discount 折扣計算實作正確！")
             if (callable(g.get("apply_discount")) and
                 g.get("apply_discount")(1000, 0.8) == 800 and
                 g.get("apply_discount")(250, 0.75) == 187) or
                ("apply_discount" in history_str and "int(" in history_str)
             else (False, "請定義 apply_discount 計算 int(price * rate) 並回傳折後價！")
         )),

        ("11-3-1", "挑戰題", "安全字串加密 caesar_shift(text, shift)", 6, ("caesar_shift",),
         lambda g: (
             (True, "凱薩位移加密函數實作正確！")
             if (callable(g.get("caesar_shift")) and
                 g.get("caesar_shift")("ABC", 3) == "DEF" and
                 g.get("caesar_shift")("XYZ", 3) == "ABC") or
                ("caesar_shift" in history_str and "ord(" in history_str and "chr(" in history_str)
             else (False, "請實作 caesar_shift 回傳全新位移字串且原字串不受影響！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-2 可變物件傳遞：串列與字典原地修改 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-2", "填空題", "活動簽到簿原地追加 check_in 與 append", 5, ("check_in",),
         lambda g: (
             (True, "check_in 串列追加填空正確！")
             if (callable(g.get("check_in"))) or
                ("attendees.append" in history_str)
             else (False, "請在 check_in 內呼叫 attendees.append(student_id) 就地修改！")
         )),

        ("11-3-2", "練習題", "字典庫存原地更新 update_inventory(stock_dict, item, amount)", 6, ("update_inventory",),
         lambda g: (
             (True, "update_inventory 字典原地更新正確！")
             if (callable(g.get("update_inventory"))) or
                ("update_inventory" in history_str and "stock_dict" in history_str)
             else (False, "請定義 update_inventory 就地累加或新增指定項目的庫存量！")
         )),

        ("11-3-2", "挑戰題", "遊戲血量原地扣減結算 apply_damage(team_hp_list, damage)", 6, ("apply_damage",),
         lambda g: (
             (True, "apply_damage 串列原地扣減血量正確！")
             if (callable(g.get("apply_damage"))) or
                ("apply_damage" in history_str and "team_hp_list" in history_str)
             else (False, "請定義 apply_damage 就地扣減隊員血量且不低於 0！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-3 賦值遮蔽 vs 就地清空 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-3", "填空題", "辨析重新指向與原地清空 reset_scores 與 clear", 5, ("reset_scores",),
         lambda g: (
             (True, "reset_scores 原地清空填空正確！")
             if (callable(g.get("reset_scores"))) or
                ("scores.clear()" in history_str)
             else (False, "請在 reset_scores 使用 scores.clear() 而非 scores = []！")
         )),

        ("11-3-3", "練習題", "重新賦值與原地翻倍 double_by_reassign 與 double_in_place", 6, ("double_by_reassign", "double_in_place"),
         lambda g: (
             (True, "重新賦值與原地翻倍函數實作正確！")
             if (callable(g.get("double_by_reassign")) or callable(g.get("double_in_place"))) or
                ("double_by_reassign" in history_str and "double_in_place" in history_str)
             else (False, "請定義 double_by_reassign 與 double_in_place 對比重新賦值與就地翻倍！")
         )),

        ("11-3-3", "挑戰題", "切片賦值原地過濾正數 filter_positive_in_place(nums)", 6, ("filter_positive_in_place",),
         lambda g: (
             (True, "filter_positive_in_place 切片賦值原地更新正確！")
             if (callable(g.get("filter_positive_in_place"))) or
                ("filter_positive_in_place" in history_str and "nums[:]" in history_str)
             else (False, "請使用切片賦值 nums[:] 原處更新串列！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-4 防禦性複製：.copy() 阻斷副作用 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-3-4", "填空題", "成績截尾總和與防禦性複製 trimmed_sum 與 copy()", 5, ("trimmed_sum",),
         lambda g: (
             (True, "trimmed_sum copy() 填空正確！")
             if (callable(g.get("trimmed_sum"))) or
                ("arr.copy()" in history_str)
             else (False, "請在 trimmed_sum 內使用 arr.copy() 阻斷對外部串列的影響！")
         )),

        ("11-3-4", "練習題", "安全負數過濾器 remove_negatives_safe(nums)", 6, ("remove_negatives_safe",),
         lambda g: (
             (True, "remove_negatives_safe 安全過濾實作正確！")
             if (callable(g.get("remove_negatives_safe"))) or
                ("remove_negatives_safe" in history_str and "copy()" in history_str)
             else (False, "請使用 .copy() 複製串列後過濾負數並回傳新串列！")
         )),

        ("11-3-4", "挑戰題", "字典防禦性特價處理 apply_store_discount(catalog, discount_rate)", 6, ("apply_store_discount",),
         lambda g: (
             (True, "apply_store_discount 字典防禦性複製特價處理正確！")
             if (callable(g.get("apply_store_discount"))) or
                ("apply_store_discount" in history_str and "catalog.copy()" in history_str)
             else (False, "請使用 catalog.copy() 複製字典並回傳特價字典！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-5 參數預設值 (Default Parameters) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-3-5", "填空題", "自訂邊框文字預設參數 banner(text, border='*')", 5, ("banner",),
         lambda g: (
             (True, "banner 預設參數填空正確！")
             if (callable(g.get("banner"))) or
                ("border='*'" in history_str or "border = '*'" in history_str)
             else (False, "請為 banner 函數的 border 參數指定預設值 '*'！")
         )),

        ("11-3-5", "練習題", "次方計算預設參數 power(base, exp=2)", 6, ("power",),
         lambda g: (
             (True, "power 預設參數定義正確！")
             if (callable(g.get("power")) and
                 g.get("power")(5) == 25 and
                 g.get("power")(2, 3) == 8) or
                ("power" in history_str and "exp=2" in history_str)
             else (False, "請定義 power(base, exp=2) 使未給 exp 時預設求平方！")
         )),

        ("11-3-5", "挑戰題", "多重預設參數結帳計算 checkout(amount, discount=0.9, is_vip=False)", 5, ("checkout",),
         lambda g: (
             (True, "checkout 多重預設參數實作正確！")
             if (callable(g.get("checkout"))) or
                ("checkout" in history_str and "discount=0.9" in history_str)
             else (False, "請定義 checkout(amount, discount=0.9, is_vip=False)！")
         )),

        # ----------------------------------------------------------------------
        # 11-3-6 陷阱防範：避免可變物件預設參數與 None 慣用法 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-3-6", "填空題", "安全待辦清單 create_todo 與 todo_list=None", 5, ("create_todo",),
         lambda g: (
             (True, "None 慣用法填空正確！")
             if (callable(g.get("create_todo"))) or
                ("todo_list is None" in history_str or "todo_list=None" in history_str)
             else (False, "請使用 todo_list=None 預設值並在函數內判定建立新清單 []！")
         )),

        ("11-3-6", "練習題", "學生成績登記簿安全預設值 register_score(name, score, score_dict=None)", 6, ("register_score",),
         lambda g: (
             (True, "register_score 安全預設字典實作正確！")
             if (callable(g.get("register_score"))) or
                ("register_score" in history_str and "score_dict is None" in history_str)
             else (False, "請以 score_dict=None 作為預設參數，避免跨呼叫共享字典污染！")
         )),

        ("11-3-6", "挑戰題", "獨立文字收集器 collect_words(word, container=None)", 5, ("collect_words",),
         lambda g: (
             (True, "collect_words 獨立容器建立正確！")
             if (callable(g.get("collect_words"))) or
                ("collect_words" in history_str and "container is None" in history_str)
             else (False, "請定義 collect_words 驗證兩次預設呼叫產出的容器互不干擾！")
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
    print(" 📊 《PythAPCS123》單元 11-3：參數傳遞機制與副作用防禦 —— 自動評分報告")
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
        "unit": "11-3",
        "unit_title": "參數傳遞機制與副作用防禦",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_3.py",
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
auto_grade_unit_11_3()
