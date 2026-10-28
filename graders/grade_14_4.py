# ==============================================================================
# 🧪 《PythAPCS123》單元 14-4：籃球比賽（雙場比分與勝負三分支） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_14_4.py
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
import io
import json
import contextlib
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
NOTEBOOK_FILE = "PythAPCS123_14-4_basketball_game_apcs_e286.ipynb"
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
# 第 14 章的範例、填空、練習格大量重用 sh1、sa1、sh2、sa2、wins 這類名字，
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

def _capture_print(fn, args):
    """呼叫會印出結果的學生函式，回傳 (成功與否, 輸出文字或中文錯誤訊息)。"""
    buf = io.StringIO()
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
        with contextlib.redirect_stdout(buf):
            fn(*args)
        return True, buf.getvalue()
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

def _check_q41(g):
    """14-4-1 填空題：雙場加總與勝負初探 s_h1, s_a1, res = Lose。"""
    got = _isolated_cell(g, "g1_h = [20, 20, 20, 20]", ("s_h1", "s_a1", "game_result")) or {}
    h1 = got.get("s_h1", "__MISSING__")
    a1 = got.get("s_a1", "__MISSING__")
    res = got.get("game_result", "__MISSING__")
    if h1 == 80 and a1 == 100 and res == "Lose":
        return True, "雙場加總與勝負初探判定正確：80:100，勝負為 Lose！"
    if h1 != "__MISSING__" or a1 != "__MISSING__" or res != "__MISSING__":
        return False, f"目前 s_h1={h1!r}, s_a1={a1!r}, res={res!r}，預期 80, 100, 'Lose'。請檢查 sum 與勝場判定！"
    return False, "請在 14.4.1 填空題補齊 sum 與勝場三分支（Win/Lose/Tie）並點擊播放鍵執行！"


def _check_q42(g):
    """14-4-2 練習題：系列賽評估函式 evaluate_series(h1, a1, h2, a2)。"""
    fn = g.get("evaluate_series")
    if not callable(fn):
        return False, "找不到函式 evaluate_series，請在 14.4.2 練習題儲存格（cell#5）點擊播放鍵執行！"
    cases = [
        (([25, 25, 25, 25], [20, 20, 20, 20], [20, 20, 20, 20], [25, 25, 25, 25]), "100:80\n80:100\nTie"),
        (([30, 30, 30, 30], [20, 20, 20, 20], [30, 30, 30, 30], [20, 20, 20, 20]), "120:80\n120:80\nWin"),
    ]
    for args, expect in cases:
        ok, got = _capture_print(fn, args)
        if not ok:
            return False, f"執行時發生例外：{got}"
        if got.strip().splitlines() != expect.splitlines():
            return False, f"輸出不符：預期 {expect.splitlines()!r}，你的輸出 {got.strip().splitlines()!r}。"
    return True, "系列賽評估函式 evaluate_series 輸出格式與判定完全正確！"


def _check_q43(g):
    """14-4-3 練習題：四行輸入解析函式 parse_four_lines(lines)。"""
    fn = g.get("parse_four_lines")
    if not callable(fn):
        return False, "找不到函式 parse_four_lines，請在 14.4.3 練習題儲存格（cell#10）點擊播放鍵執行！"
    cases = [
        (["1 2 3 4", "5 6 7 8", "9 10 11 12", "13 14 15 16"],
         ([1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16])),
    ]
    for lines, expect in cases:
        ok, got = _run_solve(fn, (lines,))
        if not ok:
            return False, f"執行時發生例外：{got}"
        if got != expect:
            return False, f"輸入 {lines} 回傳 {got!r}，預期 {expect!r}。請將每行文字轉為整數串列！"
    return True, "四行輸入解析函式 parse_four_lines 驗證全數通過！"


def _check_q44(g):
    """14-4-4 練習題：比分輸出函式 print_scores(sh1, sa1, sh2, sa2)。"""
    fn = g.get("print_scores")
    if not callable(fn):
        return False, "找不到函式 print_scores，請在 14.4.4 練習題儲存格（cell#20）點擊播放鍵執行！"
    ok, got = _capture_print(fn, (104, 100, 95, 90))
    if not ok:
        return False, f"執行時發生例外：{got}"
    if got.strip().splitlines() != ["104:100", "95:90"]:
        return False, f"print_scores 輸出格式不符：預期 ['104:100', '95:90']，你的輸出 {got.strip().splitlines()!r}。"
    return True, "比分輸出函式 print_scores 兩行格式化輸出正確！"


def _check_q45(g):
    """14-4-5 練習題：完整解題函式 solve_basketball(four_lines)。"""
    fn = g.get("solve_basketball")
    if not callable(fn):
        return False, "找不到函式 solve_basketball，請在 14.4.5 練習題儲存格（cell#25）點擊播放鍵執行！"
    cases = [
        (["20 20 20 20", "25 25 25 25", "20 20 20 20", "25 25 25 25"], ['80:100', '80:100', 'Lose']),
        (["25 25 25 25", "20 20 20 20", "20 20 20 20", "25 25 25 25"], ['100:80', '80:100', 'Tie']),
    ]
    for lines, expect in cases:
        ok, got = _run_solve(fn, (lines,))
        if not ok:
            return False, f"執行時發生例外：{got}"
        if got != expect:
            return False, f"輸入 {lines} 回傳 {got!r}，預期 {expect!r}。請回傳由三行字串組成的串列！"
    return True, "完整解題函式 solve_basketball 驗證全數通過！"


def _check_solve_e286(g):
    """14-4-8 對拍題：完整解題函式 solve_basketball(four_lines) 對官方範例與邊界。

    測資全部來自官方範例與邊界，不另做隱藏大測資。
    """
    fn = g.get("solve_basketball")
    if not callable(fn):
        return False, "找不到解題函式 solve_basketball，請在 14.4.5 練習題儲存格（cell#25）點擊播放鍵執行！"

    cases = [
        # 官方範例 1：主隊兩場皆勝 (Win)
        (["26 26 26 26", "25 25 25 25", "25 25 25 20", "25 20 25 20"], ["104:100", "95:90", "Win"]),
        # 官方範例 2：主隊兩場皆負 (Lose)
        (["20 20 20 20", "25 25 25 25", "20 20 20 20", "25 25 25 25"], ["80:100", "80:100", "Lose"]),
        # 官方範例 3：一勝一負平手 (Tie)
        (["25 25 25 25", "20 20 20 20", "20 20 20 20", "25 25 25 25"], ["100:80", "80:100", "Tie"]),
        # 極限狂勝 (Win)
        (["100 100 100 100", "0 0 0 0", "100 100 100 100", "0 0 0 0"], ["400:0", "400:0", "Win"]),
    ]

    for four_lines, expect in cases:
        ok, got = _run_solve(fn, (four_lines,))
        if not ok:
            return False, got
        if got != expect:
            hint = "請檢查：格式是否為 主隊:客隊（緊密無空白）？第三項是否為 Win、Lose 或 Tie？"
            return False, f"第一筆不符：輸入行 {four_lines}，你的輸出 {got!r}，預期 {expect!r}。{hint}"

    return True, f"四組官方範例與邊界全數通過！籃球系列賽比分與勝負三分支輸出完全正確（最後一組 {got}）。"


def auto_grade_unit_14_4(env=None):
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
        # 14-4-1 雙場加總與勝負初探：s_h1, s_a1, res (共 18 分)
        # ----------------------------------------------------------------------
        ("14-4-1", "填空題", "雙場加總與勝負初探 s_h1, s_a1, res = Lose", 18, (),
         lambda g: _check_q41(g)),

        # ----------------------------------------------------------------------
        # 14-4-2 系列賽評估：evaluate_series 輸出三行 (共 18 分)
        # ----------------------------------------------------------------------
        ("14-4-2", "練習題", "系列賽評估函式 evaluate_series 輸出三行", 18, ("evaluate_series",),
         lambda g: _check_q42(g)),

        # ----------------------------------------------------------------------
        # 14-4-3 四行輸入解析：parse_four_lines (共 18 分)
        # ----------------------------------------------------------------------
        ("14-4-3", "練習題", "四行輸入解析函式 parse_four_lines", 18, ("parse_four_lines",),
         lambda g: _check_q43(g)),

        # ----------------------------------------------------------------------
        # 14-4-4 比分兩行輸出：print_scores (共 18 分)
        # ----------------------------------------------------------------------
        ("14-4-4", "練習題", "比分兩行格式化輸出函式 print_scores", 18, ("print_scores",),
         lambda g: _check_q44(g)),

        # ----------------------------------------------------------------------
        # 14-4-5 完整解題函式：solve_basketball 回傳三行串列 (共 18 分)
        # ----------------------------------------------------------------------
        ("14-4-5", "練習題", "完整解題函式 solve_basketball 回傳字串串列", 18, ("solve_basketball",),
         lambda g: _check_q45(g)),

        # ----------------------------------------------------------------------
        # 14-4-8 對拍題：solve_basketball_series 對官方範例與邊界 (共 10 分)
        # ----------------------------------------------------------------------
        ("14-4-8", "對拍題", "完整解題函式 solve_basketball 對官方範例與邊界", 10, ("solve_basketball",),
         lambda g: _check_solve_e286(g)),
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通雙場比分統計與勝負分支，考場零 WA！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，比分加總與勝負三分支邏輯清晰扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 14-4：籃球比賽（雙場比分與勝負三分支） —— 自動評分報告")
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
        "unit": "14-4",
        "unit_title": "籃球比賽（雙場比分與勝負三分支）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_14_4.py",
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


auto_grade_unit_14_4()
