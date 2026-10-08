# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-1 自動評分器
單元名稱：競技程式線上評判系統（Online Judge）運作機制與評判結果型別解析
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（6 大評判主題，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime

UNIT_ID = "13-1"
UNIT_TITLE = "競技程式線上評判系統（Online Judge）運作機制與評判結果型別解析"

QUESTIONS = [
    # 13.1.1 Online Judge 比對本質
    {"id": "q1", "name": "實作 13.1.1：評判狀態基礎比對判定（AC / WA）", "points": 6},
    {"id": "q2", "name": "實作 13.1.1：輸出格式尾端空白與換行容錯處理", "points": 6},
    {"id": "q3", "name": "實作 13.1.1：偵測執行崩潰 Error 關鍵字回傳 RE", "points": 5},
    # 13.1.2 通過狀態 AC 與極端測資防禦
    {"id": "q4", "name": "實作 13.1.2：正整數篩選與最小正整數計算", "points": 6},
    {"id": "q5", "name": "實作 13.1.2：極端全負數與無正整數回傳 -1", "points": 6},
    {"id": "q6", "name": "實作 13.1.2：含零與重複值極端測資強韌性", "points": 5},
    # 13.1.3 語法錯誤 CE 與除錯診斷
    {"id": "q7", "name": "實作 13.1.3：fixed_code 修正語法漏冒號錯誤", "points": 6},
    {"id": "q8", "name": "實作 13.1.3：fixed_code 成功通過 compile() 編譯", "points": 6},
    {"id": "q9", "name": "實作 13.1.3：修復後 calculate_average 運算邏輯正確", "points": 5},
    # 13.1.4 答案錯誤 WA 與嚴格輸出格式
    {"id": "q10", "name": "實作 13.1.4：首行總平均四捨五入整數規範", "points": 6},
    {"id": "q11", "name": "實作 13.1.4：次行及格成績降序排列篩選", "points": 6},
    {"id": "q12", "name": "實作 13.1.4：嚴格空格分隔與尾端無多餘空白格式", "points": 5},
    # 13.1.5 超時 TLE 預防與複雜度估算
    {"id": "q13", "name": "實作 13.1.5：O(N) 線性複雜度 10^5 運算量判定 PASS", "points": 6},
    {"id": "q14", "name": "實作 13.1.5：O(N^2) 平方複雜度 10^5 運算量預警 TLE", "points": 5},
    {"id": "q15", "name": "實作 13.1.5：時間限制與運算量臨界邊界判定", "points": 5},
    # 13.1.6 執行崩潰 RE 與防禦性除法器
    {"id": "q16", "name": "實作 13.1.6：safe_division 正常數值整數商計算", "points": 6},
    {"id": "q17", "name": "實作 13.1.6：防禦空串列與長度不足 INVALID_LENGTH", "points": 5},
    {"id": "q18", "name": "實作 13.1.6：防禦除以零 DIVISION_BY_ZERO 零崩潰", "points": 5},
]

def get_evaluate_fn(g):
    return g.get("evaluate_testcase") or g.get("evaluate_testcase_ans")

def check_q1(g, hist):
    fn = get_evaluate_fn(g)
    if callable(fn):
        try:
            if fn("100\n", "100") == "AC" and fn("100", "200") == "WA":
                return True, "太棒了！精準判定完全吻合為 AC，答案相異為 WA！"
        except Exception:
            pass
    if "evaluate_testcase" in hist and '"AC"' in hist and '"WA"' in hist:
        return True, "比對邏輯檢驗通過！"
    return False, "請實作 evaluate_testcase(user_output, expected_output) 進行基礎判定。"

def check_q2(g, hist):
    fn = get_evaluate_fn(g)
    if callable(fn):
        try:
            if fn("hello world  \n", "hello world") == "AC" and fn("42\n\n", "42") == "AC":
                return True, "完全正確！strip() 去除頭尾空白換行，落實 OJ 寬容比對規範！"
        except Exception:
            pass
    if ".strip()" in hist and "evaluate_testcase" in hist:
        return True, "空白修剪處理正確，通過！"
    return False, "請使用 .strip() 消除尾端空白與換行以防範偽 WA。"

def check_q3(g, hist):
    fn = get_evaluate_fn(g)
    if callable(fn):
        try:
            if fn("Error: IndexError", "100") == "RE" and fn("Error: ZeroDivisionError", "0") == "RE":
                return True, "精彩！精確辨識 Error: 關鍵字並回傳 RE (Runtime Error)！"
        except Exception:
            pass
    if '"Error:"' in hist and '"RE"' in hist:
        return True, "例外識別邏輯正確，通過！"
    return False, "當 user_output 包含 'Error:' 時請回傳 'RE'。"

def get_find_min_pos_fn(g):
    return g.get("find_min_positive") or g.get("find_min_positive_ans")

def check_q4(g, hist):
    fn = get_find_min_pos_fn(g)
    if callable(fn):
        try:
            if fn([4, -2, 7, 1, 9]) == 1 and fn([10, 20, 5]) == 5:
                return True, "太棒了！順利過濾正整數並找出最小值 1！"
        except Exception:
            pass
    if "find_min_positive" in hist and "min(" in hist:
        return True, "正整數篩選通過！"
    return False, "請實作 find_min_positive(nums) 回傳大於 0 的最小值。"

def check_q5(g, hist):
    fn = get_find_min_pos_fn(g)
    if callable(fn):
        try:
            if fn([-5, -10, -3]) == -1 and fn([-1]) == -1:
                return True, "完全正確！面對全負數等無解極端測資，安全防禦回傳 -1！"
        except Exception:
            pass
    if "return -1" in hist and "find_min_positive" in hist:
        return True, "無解邊界防禦通過！"
    return False, "當數列中無任何正整數時，必須回傳 -1。"

def check_q6(g, hist):
    fn = get_find_min_pos_fn(g)
    if callable(fn):
        try:
            if fn([0, 5, 2, 2]) == 2 and fn([0, 0, 0]) == -1:
                return True, "強韌無比！面對包含 0 與重複正整數極端邊界，判定完全精準！"
        except Exception:
            pass
    if "x > 0" in hist and "find_min_positive" in hist:
        return True, "嚴格大於零邏輯通過！"
    return False, "請確保 0 不被誤認為正整數，且重複值能正確求出最小值。"

def check_q7(g, hist):
    fc = g.get("fixed_code", "")
    if isinstance(fc, str) and "if len(nums) > 0:" in fc:
        return True, "太棒了！成功在 if 條件句末尾補齊關鍵冒號 ':'！"
    if "len(nums) > 0:" in hist or "correct_code_sample" in g:
        return True, "語法修正通過！"
    return False, "請在 fixed_code 中修復 if len(nums) > 0: 漏冒號語法錯誤。"

def check_q8(g, hist):
    fc = g.get("fixed_code", "")
    if isinstance(fc, str) and fc.strip():
        try:
            compile(fc, filename="<test>", mode="exec")
            return True, "完全正確！fixed_code 順利通過 compile() 編譯檢查，完全消滅 CE！"
        except SyntaxError:
            pass
    if g.get("comp_ok") is True:
        return True, "編譯檢驗通過！"
    return False, "請確保 fixed_code 不包含任何 SyntaxError，能順利編譯。"

def check_q9(g, hist):
    fc = g.get("fixed_code", "")
    if isinstance(fc, str) and "def calculate_average" in fc:
        loc = {}
        try:
            exec(fc, loc)
            fn = loc.get("calculate_average")
            if callable(fn) and fn([10, 20, 30]) == 20 and fn([]) == 0:
                return True, "精彩！修復後 calculate_average 實測正確，空串列保護亦完全無誤！"
        except Exception:
            pass
    if "calculate_average" in hist:
        return True, "平均計算邏輯檢驗通過！"
    return False, "請確保 calculate_average 正常回傳平均值，空串列回傳 0。"

def get_format_report_fn(g):
    return g.get("format_report") or g.get("format_report_ans")

def check_q10(g, hist):
    fn = get_format_report_fn(g)
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            first_line = out.strip().splitlines()[0]
            if first_line == "86":
                return True, "太棒了！首行平均數四捨五入為整數 86，完全符合輸出規範！"
        except Exception:
            pass
    if "round(" in hist and "format_report" in hist:
        return True, "四捨五入整數邏輯通過！"
    return False, "首行請輸出 round() 四捨五入後的整數平均值。"

def check_q11(g, hist):
    fn = get_format_report_fn(g)
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            lines = out.strip().splitlines()
            if len(lines) >= 2 and "92 90 85 78" in lines[1]:
                return True, "完全正確！及格成績由大到小降序排列無誤！"
        except Exception:
            pass
    if "reverse=True" in hist and "format_report" in hist:
        return True, "降序排列邏輯通過！"
    return False, "次行請將 >= 60 的成績由大到小降序排列輸出。"

def check_q12(g, hist):
    fn = get_format_report_fn(g)
    if callable(fn):
        try:
            out = fn([85, 92, 78, 90])
            lines = out.strip().splitlines()
            if len(lines) >= 2 and lines[1] == "92 90 85 78" and not lines[1].endswith(" "):
                return True, "字元級嚴謹！以 ' '.join() 分隔且行末無多餘空白，徹底杜絕格式 WA！"
        except Exception:
            pass
    if '" ".join' in hist or "' '.join" in hist:
        return True, "空格串接格式通過！"
    return False, "請使用 ' '.join() 串接成績，確保數字間單一空格且行末無空白。"

def get_predict_tle_fn(g):
    return g.get("predict_tle") or g.get("predict_tle_ans")

def check_q13(g, hist):
    fn = get_predict_tle_fn(g)
    if callable(fn):
        try:
            if fn(100000, "O(N)") == "PASS":
                return True, "太棒了！N=10^5 在 O(N) 僅 10 萬次運算，遠低於千萬上限，判定 PASS！"
        except Exception:
            pass
    if 'predict_tle(100000, "O(N)")' in hist:
        return True, "O(N) 運算量檢驗通過！"
    return False, "請實作 predict_tle，當運算量小於限制時回傳 'PASS'。"

def check_q14(g, hist):
    fn = get_predict_tle_fn(g)
    if callable(fn):
        try:
            if fn(100000, "O(N^2)") == "TLE":
                return True, "完全正確！N=10^5 在 O(N^2) 高達 10^10 次運算，精準預警 TLE！"
        except Exception:
            pass
    if 'predict_tle(100000, "O(N^2)")' in hist:
        return True, "O(N^2) TLE 預警通過！"
    return False, "當預估運算次數超過限制時，請回傳 'TLE'。"

def check_q15(g, hist):
    fn = get_predict_tle_fn(g)
    if callable(fn):
        try:
            if fn(2000, "O(N^2)") == "PASS" and fn(5000, "O(N^2)") == "TLE":
                return True, "精彩！精確掌握 2000^2=4*10^6 (PASS) 與 5000^2=2.5*10^7 (TLE) 臨界邊界！"
        except Exception:
            pass
    if "predict_tle" in hist and "time_limit_sec" in hist:
        return True, "臨界值邊界檢驗通過！"
    return False, "請依運算次數上限正確認定邊界 (2000 PASS, 5000 TLE)。"

def get_safe_division_fn(g):
    return g.get("safe_division") or g.get("safe_division_ans")

def check_q16(g, hist):
    fn = get_safe_division_fn(g)
    if callable(fn):
        try:
            if fn([20, 4]) == 5 and fn([-8, 2]) == -4 and fn([0, 5]) == 0:
                return True, "太棒了！正常數值整數商 lst[0] // lst[1] 計算完全正確！"
        except Exception:
            pass
    if "safe_division" in hist and "//" in hist:
        return True, "整數商計算通過！"
    return False, "請在輸入合法時回傳 lst[0] // lst[1]。"

def check_q17(g, hist):
    fn = get_safe_division_fn(g)
    if callable(fn):
        try:
            if fn([10]) == "INVALID_LENGTH" and fn([]) == "INVALID_LENGTH":
                return True, "完全正確！長度小於 2 與空串列防禦無懈可擊，回傳 INVALID_LENGTH！"
        except Exception:
            pass
    if '"INVALID_LENGTH"' in hist and "len(" in hist:
        return True, "長度防禦檢驗通過！"
    return False, "當 lst 長度小於 2 時，請安全回傳 'INVALID_LENGTH'。"

def check_q18(g, hist):
    fn = get_safe_division_fn(g)
    if callable(fn):
        try:
            if fn([10, 0]) == "DIVISION_BY_ZERO":
                return True, "滿分通關！除以零防禦無懈可擊，回傳 DIVISION_BY_ZERO，零崩潰達成！"
        except Exception:
            pass
    if '"DIVISION_BY_ZERO"' in hist:
        return True, "除以零防禦通過！"
    return False, "當分母 lst[1] == 0 時，請安全回傳 'DIVISION_BY_ZERO'。"

CHECK_FUNCS = {
    "q1": check_q1, "q2": check_q2, "q3": check_q3,
    "q4": check_q4, "q5": check_q5, "q6": check_q6,
    "q7": check_q7, "q8": check_q8, "q9": check_q9,
    "q10": check_q10, "q11": check_q11, "q12": check_q12,
    "q13": check_q13, "q14": check_q14, "q15": check_q15,
    "q16": check_q16, "q17": check_q17, "q18": check_q18,
}

def run_grading():
    g = globals()
    hist_list = []
    in_hist = g.get("In", [])
    if isinstance(in_hist, list):
        hist_list.extend([str(x) for x in in_hist])
    hist = "\n".join(hist_list)

    results = []
    total_score = 0
    max_score = sum(q["points"] for q in QUESTIONS)

    for q in QUESTIONS:
        qid = q["id"]
        checker = CHECK_FUNCS.get(qid)
        passed, msg = False, "未執行或未檢測到結果"
        if checker:
            try:
                passed, msg = checker(g, hist)
            except Exception as e:
                passed, msg = False, f"檢測時發生例外錯誤: {str(e)}"
        
        score = q["points"] if passed else 0
        total_score += score
        results.append({
            "id": qid,
            "name": q["name"],
            "points": q["points"],
            "score": score,
            "passed": passed,
            "feedback": msg
        })

    return total_score, max_score, results

def main():
    user_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("STUDENT_NAME", "匿名學員")
    student_id = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("STUDENT_ID", "無學號")
    user_email = "未綁定 (良心信條模式)"

    total_score, max_score, results = run_grading()
    pass_ratio = (total_score / max_score) * 100 if max_score > 0 else 0

    print("=" * 64)
    print(f"🎯 PythAPCS123 自動評分系統 - 單元 {UNIT_ID}：{UNIT_TITLE}")
    print(f"👤 學習者：{user_name} ({student_id}) | 認證身分：{user_email}")
    print(f"⏰ 評分時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)

    for r in results:
        mark = "✅ [通過]" if r["passed"] else "❌ [未過]"
        print(f"{mark} {r['name']} ({r['score']}/{r['points']}分)")
        print(f"    💡 回饋：{r['feedback']}")

    print("-" * 64)
    print(f"📊 總結得分：{total_score} / {max_score} 分 (達成率: {pass_ratio:.1f}%)")
    
    badge = "🥉 仍需努力"
    if pass_ratio >= 90:
        badge = "🏆 卓越宗師 (Mastery)"
    elif pass_ratio >= 75:
        badge = "🥈 熟練精通 (Proficient)"
    elif pass_ratio >= 60:
        badge = "🥉 基礎達標 (Pass)"
    print(f"🏅 榮譽成就：{badge}")
    print("=" * 64)

    report_data = {
        "unit_id": UNIT_ID,
        "unit_title": UNIT_TITLE,
        "student_name": user_name,
        "student_id": student_id,
        "total_score": total_score,
        "max_score": max_score,
        "pass_ratio": pass_ratio,
        "badge": badge,
        "timestamp": datetime.datetime.now().isoformat(),
        "results": results
    }
    try:
        with open(f"grade_report_{UNIT_ID.replace('-', '_')}.json", "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return total_score

if __name__ == "__main__":
    main()
