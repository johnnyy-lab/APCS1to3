# ==============================================================================
# 🧪 《PythAPCS123》單元 14-6：人力分配（二次函數極值） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_14_6.py
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
NOTEBOOK_FILE = "PythAPCS123_14-6_manpower_allocation_apcs_f312.ipynb"
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
# 第 14 章的範例、填空、練習格大量重用 n、x1、x2、A1、A2 這類名字，
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



def _check_q61(g):
    """14-6-1：以 marker 定位本格，隔離重跑取 fac1_num 與 fac2_num。"""
    got = _isolated_cell(g, "分配 {emp_total} 名員工的可能方案", ("fac1_num", "fac2_num")) or {}
    f1 = got.get("fac1_num", "__MISSING__")
    f2 = got.get("fac2_num", "__MISSING__")
    if f1 == 3 and f2 == 0:
        return True, "完美！range 終點填對了，最後一輪 fac1_num = 3、fac2_num = 0，剛好涵蓋到全去一廠！"
    if f1 == 2 or f2 == 1:
        return False, "差一陷阱！range 終點少填 1，fac1_num 最多只到 2。終點必須是 emp_total + 1 才能含到 emp_total 喔！"
    return False, "請在 14.6.1 填空題把兩個 ___ 填好（range 終點填 emp_total + 1，fac2_num 填 emp_total - fac1_num）並點擊播放鍵執行！"


def _check_q66(g):
    """14-6-6：全域值安全，但呼叫 audit_boundary 需包 try。"""
    fn = g.get("audit_boundary")
    tested = g.get("tested")
    is_safe = g.get("is_safe")
    if not callable(fn):
        return False, "找不到 audit_boundary，請在 14.6.6 填空題補齊 range 終點與長度判斷並執行！"
    try:
        covered = fn(5)
    except Exception:
        return False, "audit_boundary(5) 執行時發生例外，請檢查 range 終點是否正確！"
    if covered == [0, 1, 2, 3, 4, 5] and tested == [0, 1, 2, 3, 4, 5] and is_safe is True:
        return True, "邊界防守完美：audit_boundary(5) 涵蓋 0 到 5，is_safe 為 True！"
    return False, f"tested 目前是 {tested!r}、is_safe={is_safe!r}。range 終點與 len 判斷都要含到 n！"



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

def _check_solve_f312(g):
    """14-6-5 對拍：solve_f312(A1, B1, C1, A2, B2, C2, n) 回傳最大總收益。

    測資全部來自筆記本 14.6.5 與 14.6.6 的公開測試資料，不另做隱藏大測資。
    """
    fn = g.get("solve_f312")
    if not callable(fn):
        return False, "找不到解題函式 solve_f312，請在 14.6.5 填空題補齊四個 ___ 並點擊播放鍵執行！"

    cases = [
        # 官方範例 1（14.6.5 公開測試資料 1），預期 11
        ((2, -1, 3, 4, -5, 2, 2), 11),
        # 全虧損測資（14.6.5），預期 -41
        ((-1, -1, -10, -2, -3, -20, 3), -41),
        # 極小人力邊界 n = 1（14.6.6 公開測試資料 1），預期 9
        ((1, 2, 3, 3, 2, 1, 1), 9),
        # 對稱均分（14.6.6 公開測試資料 2 的已教形式），預期 -450
        ((-5, 0, -100, -5, 0, -100, 10), -450),
        # 最優解唯一落在 x1 = n 的邊界（14.6.6 挑戰題 cell31 測資 A 要求的
        # 「全部去一廠」形式，是筆記本已教過的邊界）。加這一組是因為上面四組
        # 官方範例的最適解都落在中段，差一陷阱（range 少 1）算出來同值，
        # 分不出來。這一組預期 -96，差一版會得 -100。
        ((1, 0, 0, -1, 0, -100, 2), -96),
    ]

    for args, expect in cases:
        ok, got = _run_solve(fn, args)
        if not ok:
            return False, got
        if got != expect:
            hint = (
                "請檢查：range 終點是否含 n？初始值是否設為 -float('inf')？"
                "兩廠收益都有算進來嗎？"
            )
            return False, (
                f"第一筆不符：輸入 {args}，你的回傳 {got!r}，預期 {expect}。" + "".join(hint)
            )

    return True, f"四組官方範例與邊界全數通過！最大總收益計算完全正確（最後一組 {got}）。"

def auto_grade_unit_14_6(env=None):
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
        # 14-6-1 員工分配列舉：range 終點必須含 emp_total，fac2_num = emp_total - fac1_num (共 18 分)
        # 以 marker 定位本格後隔離重跑取 fac1_num 與 fac2_num。
        # ----------------------------------------------------------------------
        ("14-6-1", "填空題", "員工分配列舉 range 含 emp_total 與互補關係", 18, (),
         lambda g: _check_q61(g)),

        # ----------------------------------------------------------------------
        # 14-6-2 工廠二收益公式：profit2 = 4*(2^2) + (-5)*(2) + 2 = 8 (共 18 分)
        # profit2 只出現在本格，全域值安全。
        # ----------------------------------------------------------------------
        ("14-6-2", "填空題", "工廠二收益公式 profit2 = 8", 18, ("profit2",),
         lambda g: (
             (True, "二次函數收益計算正確：profit2 = 8！")
             if g.get("profit2") == 8
             else (
                 (False, f"profit2 目前是 {g.get('profit2')!r}，預期是 8。檢查三個 ___：二次項要乘 x2 的平方、一次項乘 x2、最後補上常數項 C2！")
                 if "profit2" in g
                 else (False, "找不到 profit2，請在 14.6.2 填空題把公式補齊並點擊播放鍵執行！")
             )
         )),

        # ----------------------------------------------------------------------
        # 14-6-3 各方案總收益清單：[2, 2, 4] (共 18 分)
        # total_list 只出現在本格，全域值安全。
        # ----------------------------------------------------------------------
        ("14-6-3", "填空題", "各方案總收益清單 total_list = [2, 2, 4]", 18, ("total_list",),
         lambda g: (
             (True, "清單收集正確：[2, 2, 4]！")
             if (isinstance(g.get("total_list"), list) and g.get("total_list") == [2, 2, 4])
             else (
                 (False, f"total_list 目前是 {g.get('total_list')!r}，預期是 [2, 2, 4]。可能是差一陷阱：range 終點要是 n + 1，否則少算最後一組！")
                 if "total_list" in g
                 else (False, "找不到 total_list，請在 14.6.3 填空題把 range 終點與 x2 補齊並點擊播放鍵執行！")
             )
         )),

        # ----------------------------------------------------------------------
        # 14-6-4 全負數清單的最大值維護：best_val = -85 (共 18 分)
        # best_val 與 losses 只出現在本格，全域值安全。
        # ----------------------------------------------------------------------
        ("14-6-4", "填空題", "全負數清單最大值 best_val = -85", 18, ("best_val",),
         lambda g: (
             (True, "極值維護正確：best_val = -85，成功避開初始化為 0 的全負數地雷！")
             if g.get("best_val") == -85
             else (
                 (False, f"best_val 目前是 {g.get('best_val')!r}，預期是 -85。初始值要設成負無窮大 -float('inf')，再用 max() 逐一更新！")
                 if "best_val" in g
                 else (False, "找不到 best_val，請在 14.6.4 填空題把初始值與 max() 補齊並點擊播放鍵執行！")
             )
         )),

        # ----------------------------------------------------------------------
        # 14-6-6 差一陷阱邊界自我檢驗：audit_boundary(5) 含 0 與 5 (共 18 分)
        # audit_boundary、tested、is_safe 只出現在本格，全域值安全。
        # ----------------------------------------------------------------------
        ("14-6-6", "填空題", "邊界自我檢驗 audit_boundary 涵蓋 0 與 n", 18, ("tested", "is_safe"),
         lambda g: _check_q66(g)),

        # ----------------------------------------------------------------------
        # 14-6-5 對拍題：完整解題函式 solve_f312 (共 10 分)
        # 測資全部來自筆記本內已教過的官方範例與邊界，不另做隱藏大測資。
        # ----------------------------------------------------------------------
        ("14-6-5", "對拍題", "完整解題函式 solve_f312 對官方範例與邊界", 10, ("solve_f312",),
         lambda g: _check_solve_f312(g)),
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通整數與浮點數本質，考場零 WA！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，型態觀念清晰扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 14-6：人力分配（二次函數極值） —— 自動評分報告")
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
        "unit": "14-6",
        "unit_title": "人力分配（二次函數極值）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_14_6.py",
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


auto_grade_unit_14_6()
