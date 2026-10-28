# ==============================================================================
# 🧪 《PythAPCS123》單元 14-8：七言對聯（平仄規則判定與字串輸出） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_14_8.py
# 版權宣告：PythAPCS123 教材團隊版權所有
# ==============================================================================
#
# 🕵️‍♂️【給順藤摸瓜找到這裡的程式冒險者 —— 一封來自教材團隊的良心提醒信】
#
# 嗨！聰明的同學：
# 如果你有本事一路順著 Colab 的程式碼追查到這裡，並打開了這份評分腳本，
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
import signal
import threading
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
# ------------------------------------------------------------------------------
# 🌐 雲端後台成績記錄端點（已綁定 Google 試算表 Webhook）
# ------------------------------------------------------------------------------
LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_14-8_couplet_apcs_g275.ipynb"
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

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# 🔬 隔離重跑：第 14 章變數名跨格同名時的取值方式
#
# 第 14 章的範例、填空、練習格大量重用 u、d、verse、line、ans 這類名字，
# 學生依序執行時後一格會覆蓋前一格，直接讀全域值會拿到別的題的答案。
# 黃金標竿做法：先用每格獨有的常數設定（marker）從 IPython 輸入歷史 _ih
# 定位學生實際執行的那一格，再在乾淨命名空間隔離重跑，取該格自己的結果。
# 這樣既不受跨格覆蓋影響，也不會因為範例格含同樣的寫法就放水。
# ------------------------------------------------------------------------------


def _isolated_cell(env, marker, names):
    """從 _ih 找最後一格含 marker 的程式碼，隔離重跑後回傳 {name: value}。

    回傳 None 表示找不到該格或該格無法執行。取不到的名字不在字典裡，
    checker 因此能分辨沒跑過與跑過但值不對。
    """
    raw = env.get("_ih") or env.get("In") or []
    if not isinstance(raw, list):
        return None
    src = None
    for item in reversed(raw):
        text = item if isinstance(item, str) else ""
        if marker and marker in text:
            src = text
            break
    if src is None:
        return None
    sandbox = {"__name__": "__grader_sandbox__"}
    try:
        exec(compile(src, "<cell>", "exec"), sandbox)
    except Exception:
        return None
    return {name: sandbox.get(name, "__MISSING__") for name in names}


# 🎯 對拍題專用：第 14、15 章真題解題函式比對
# 依 colab_notebook_generation_rules.md 第八節第五子節：
#   * 測資只用題目官方公開範例與筆記本內已教過的邊界，不另做隱藏大測資。
#   * 傳入可變物件前深拷貝，防止學生函式就地修改測資波及後續比對。
#   * 以 try...except Exception 包裹，遇 RecursionError 或例外給中文提示，
#     絕不拋出未處理例外讓評分儲存格崩潰。
#   * 失敗只回報第一筆不符：輸入、學生回傳、預期回傳。
# ------------------------------------------------------------------------------
import copy



def _run_solve(fn, args):
    """呼叫學生函式，回傳 (成功與否, 回傳值或中文錯誤訊息)。"""
    has_alarm = hasattr(signal, "alarm") and hasattr(signal, "SIGALRM")
    is_main = threading.current_thread() is threading.main_thread()
    can_alarm = has_alarm and is_main
    old_handler = None
    if can_alarm:
        try:
            old_handler = signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("函式執行逾時（可能陷入死迴圈）")))
            signal.alarm(2)
        except (ValueError, OSError):
            can_alarm = False
    try:
        if isinstance(args, (list, dict)):
            args = copy.deepcopy(args)
        return True, fn(*args)
    except RecursionError:
        return False, "函式執行超出遞迴深度上限，請檢查終止條件"
    except TimeoutError as te:
        return False, str(te)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        if can_alarm:
            try:
                signal.alarm(0)
                if old_handler is not None:
                    signal.signal(signal.SIGALRM, old_handler)
            except (ValueError, OSError):
                pass

def _check_q81(g):
    """14-8-1 填空題：計算上聯中平聲與仄聲的數量 ping_count = u.count(0), ze_count = u.count(1)。"""
    got = _isolated_cell(g, "平聲個數:", ("ping_count", "ze_count")) or {}
    p_cnt = got.get("ping_count", "__MISSING__")
    z_cnt = got.get("ze_count", "__MISSING__")
    if p_cnt == 4 and z_cnt == 3:
        return True, "平仄計數完全正確：平聲 ping_count = 4，仄聲 ze_count = 3！"
    if p_cnt != "__MISSING__" or z_cnt != "__MISSING__":
        return False, f"目前 ping_count={p_cnt!r}, ze_count={z_cnt!r}，預期為 4 與 3。平聲填 0，仄聲填 1！"
    return False, "請在 14.8.1 填空題補齊兩個 ___（分別統計 0 與 1）並點擊播放鍵執行！"


def _check_q82(g):
    """14-8-2 填空題：補齊關鍵字位索引 w2 = verse[1], w4 = verse[3], w6 = verse[5], w7 = verse[6]。"""
    got = _isolated_cell(g, "w2=", ("w2", "w4", "w6", "w7")) or {}
    w2 = got.get("w2", "__MISSING__")
    w4 = got.get("w4", "__MISSING__")
    w6 = got.get("w6", "__MISSING__")
    w7 = got.get("w7", "__MISSING__")
    if w2 == 1 and w4 == 0 and w6 == 1 and w7 == 1:
        return True, "關鍵字位索引提取正確：第 2, 4, 6, 7 字分別為 1, 0, 1, 1！"
    if w2 != "__MISSING__" or w4 != "__MISSING__" or w6 != "__MISSING__" or w7 != "__MISSING__":
        return False, f"目前提取結果為 ({w2}, {w4}, {w6}, {w7})，預期 (1, 0, 1, 1)。Python 索引從 0 起算，第 k 字為 index k-1！"
    return False, "請在 14.8.2 填空題補齊四個索引 ___（填入 1, 3, 5, 6）並點擊播放鍵執行！"


def _check_q83(g):
    """14-8-3 填空題：補齊規則 A 邏輯運算式 is_ok = (line[1] != line[3]) and (line[1] == line[5])。"""
    got = _isolated_cell(g, "此句符合規則 A 嗎？", ("is_ok",)) or {}
    is_ok = got.get("is_ok", "__MISSING__")
    if is_ok is True:
        return True, "規則 A 邏輯運算式判定正確：二四不同且二六同，is_ok 為 True！"
    if is_ok is False:
        return False, "is_ok 為 False。請比對二四字是否不同（!=）且二六字是否相同（==）！"
    if is_ok != "__MISSING__":
        return False, f"is_ok 目前是 {is_ok!r}，預期為 True。"
    return False, "請在 14.8.3 填空題補齊兩個 ___（填入 != 與 ==）並點擊播放鍵執行！"


def _check_q84(g):
    """14-8-4 填空題：補齊末字平仄檢查 valid_B = (u[6] == 1) and (d[6] == 0)。"""
    got = _isolated_cell(g, "是否符合仄起平收？", ("valid_B",)) or {}
    valid = got.get("valid_B", "__MISSING__")
    if valid is True:
        return True, "規則 B 仄起平收檢驗正確：上聯末仄(1)且下聯末平(0)，valid_B 為 True！"
    if valid is False:
        return False, "valid_B 為 False。請確認上聯末字為 1 且下聯末字為 0！"
    if valid != "__MISSING__":
        return False, f"valid_B 目前是 {valid!r}，預期為 True。"
    return False, "請在 14.8.4 填空題補齊兩個 ___（分別填入 1 與 0）並點擊播放鍵執行！"


def _check_q86(g):
    """14-8-6 填空題：補齊全合格輸出 None 判定 output = 'None'。"""
    got = _isolated_cell(g, "輸出結果:", ("output",)) or {}
    out_val = got.get("output", "__MISSING__")
    if out_val == "None":
        return True, "全合格字串輸出判定正確：output = 'None'！"
    if out_val is None:
        return False, "output 是 Python 內建物件 None，但考場輸出必須是字串 'None' 喔！"
    if out_val != "__MISSING__":
        return False, f"output 目前是 {out_val!r}，預期為字串 'None'。"
    return False, "請在 14.8.6 填空題補齊 ___（填入 'None' 字串）並點擊播放鍵執行！"


def _check_solve_g275(g):
    """14-8-5 對拍題：採選項 A，用 marker 從 cell#38 隔離取出裸 solve 再呼叫。
    marker 取自 cell#38 的 '=== 8 大情境覆蓋率壓力測試 ==='。
    """
    got = _isolated_cell(g, "=== 8 大情境覆蓋率壓力測試 ===", ("solve",)) or {}
    fn = got.get("solve", "__MISSING__")
    if not callable(fn):
        return False, "找不到本節的解題函式 solve，請回到 14.8 的壓力測試範例格（cell#38）按下播放鍵執行！"

    cases = [
        # 官方範例一 (單首違規 AC)
        (([1, 0, 0, 0, 0, 1, 1], [0, 1, 0, 0, 1, 1, 0]), "AC"),
        # 官方範例二 首句 (None)
        (([0, 1, 0, 0, 0, 1, 1], [1, 0, 1, 1, 1, 0, 0]), "None"),
        # 官方範例二 次句 (AB)
        (([0, 1, 0, 1, 1, 1, 0], [1, 0, 0, 0, 0, 0, 1]), "AB"),
        # 官方範例二 第三句 (ABC)
        (([0, 1, 0, 0, 1, 1, 1], [1, 0, 0, 0, 0, 1, 1]), "ABC"),
        # 單一違規 B 邊界 (B)
        (([0, 1, 0, 0, 0, 1, 0], [1, 0, 1, 1, 1, 0, 0]), "B"),
    ]

    for args, expect in cases:
        ok, got_val = _run_solve(fn, args)
        if not ok:
            return False, got_val
        if str(got_val).strip() != expect:
            hint = "請檢查：規則 A（二四不同且二六同）、規則 B（仄起平收）、規則 C（同聯相對），全合格時輸出 'None'！"
            return False, f"第一筆不符：輸入對聯 {args}，你的回傳 {got_val!r}，預期 {expect!r}。{hint}"

    return True, f"五組官方範例與邊界全數通過！七言對聯平仄檢驗完全正確（最後一組 {got_val}）。"


def auto_grade_unit_14_8(env=None):
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
        # ----------------------------------------------------------------------
    test_cases = [
        # ----------------------------------------------------------------------
        # 14-8-1 平仄數量統計：ping_count 與 ze_count (共 18 分)
        # ----------------------------------------------------------------------
        ("14-8-1", "填空題", "平聲與仄聲數量統計 ping_count 與 ze_count", 18, (),
         lambda g: _check_q81(g)),

        # ----------------------------------------------------------------------
        # 14-8-2 關鍵字位索引：提取第 2, 4, 6, 7 字 (共 18 分)
        # ----------------------------------------------------------------------
        ("14-8-2", "填空題", "關鍵字位索引提取 w2, w4, w6, w7", 18, (),
         lambda g: _check_q82(g)),

        # ----------------------------------------------------------------------
        # 14-8-3 句內平仄規則 A：二四不同且二六同 (共 18 分)
        # ----------------------------------------------------------------------
        ("14-8-3", "填空題", "句內平仄規則 A：二四不同且二六同", 18, (),
         lambda g: _check_q83(g)),

        # ----------------------------------------------------------------------
        # 14-8-4 句尾平仄規則 B：仄起平收 (共 18 分)
        # ----------------------------------------------------------------------
        ("14-8-4", "填空題", "句尾平仄規則 B：仄起平收 valid_B", 18, (),
         lambda g: _check_q84(g)),

        # ----------------------------------------------------------------------
        # 14-8-6 全合格字串判定：output = 'None' (共 18 分)
        # ----------------------------------------------------------------------
        ("14-8-6", "填空題", "全合格字串輸出判定 output = 'None'", 18, (),
         lambda g: _check_q86(g)),

        # ----------------------------------------------------------------------
        # 14-8-8 對拍題：選項 A 隔離取出 cell#38 裸 solve 進行對拍 (共 10 分)
        # ----------------------------------------------------------------------
        ("14-8-8", "對拍題", "完整解題函式 solve 對官方範例與邊界", 10, (),
         lambda g: _check_solve_g275(g)),
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通七言對聯平仄檢驗與規則比對，考場零 WA！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，平仄規則與條件邏輯清晰扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 14-8：七言對聯（平仄規則判定與字串輸出） —— 自動評分報告")
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
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "14-8",
        "unit_title": "七言對聯（平仄規則判定與字串輸出）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_14_8.py",
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


auto_grade_unit_14_8()
