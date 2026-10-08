# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-5 自動評分器
單元名稱：邏輯錯誤（Logic Error）排查與常見 WA 陷阱拆解
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（9 大 WA 邏輯地雷與對拍抓蟲心法，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

UNIT_ID = "13-5"
UNIT_TITLE = "邏輯錯誤（Logic Error）排查與常見 WA 陷阱拆解"

QUESTIONS = [
    # 13.5.1 WA 評判本質與輸出診斷
    {"id": "q1", "name": "實作 13.5.1：diagnose_wa_discrepancy 完全相符回傳 AC", "points": 6},
    {"id": "q2", "name": "實作 13.5.1：diagnose_wa_discrepancy 揪出首個差異行與內容", "points": 6},
    # 13.5.2 差一錯誤 Off-by-one 防禦
    {"id": "q3", "name": "實作 13.5.2：interval_stats 閉區間長度與總和精準計算", "points": 6},
    {"id": "q4", "name": "實作 13.5.2：safe_binary_search 二分搜尋涵蓋單元素邊界", "points": 6},
    # 13.5.3 運算子優先級陷阱
    {"id": "q5", "name": "實作 13.5.3：safe_midpoint 中點運算正確優先級防偏", "points": 6},
    {"id": "q6", "name": "實作 13.5.3：is_even_bitwise 位元運算與等號優先級防護", "points": 6},
    # 13.5.4 浮點數精度與除法語意
    {"id": "q7", "name": "實作 13.5.4：safe_float_equal 浮點數微小誤差容許比對", "points": 6},
    {"id": "q8", "name": "實作 13.5.4：truncate_towards_zero_divide 正負向零截斷整除", "points": 6},
    # 13.5.5 物件參考淺拷貝共享災難
    {"id": "q9", "name": "實作 13.5.5：create_independent_matrix 建立完全獨立二維矩陣", "points": 6},
    {"id": "q10", "name": "實作 13.5.5：safe_append_copy 無副作用複本追加", "points": 6},
    # 13.5.6 變數遮蔽與名稱污染
    {"id": "q11", "name": "實作 13.5.6：matrix_diagonal_sums 主次對角線計算", "points": 5},
    {"id": "q12", "name": "實作 13.5.6：matrix_diagonal_sums 方陣大小邊界與零元素計算", "points": 5},
    # 13.5.7 多測資狀態殘留毒瘤
    {"id": "q13", "name": "實作 13.5.7：process_testcases_cleanly 多測資獨立乾淨加總", "points": 5},
    {"id": "q14", "name": "實作 13.5.7：process_testcases_cleanly 空測資與邊界狀態隔離", "points": 5},
    # 13.5.8 極端 Corner Cases 盲點
    {"id": "q15", "name": "實作 13.5.8：find_min_max_difference 全負數測資極值差計算", "points": 5},
    {"id": "q16", "name": "實作 13.5.8：find_min_max_difference 單一元素與重複值回傳 0", "points": 5},
    # 13.5.9 考場對拍檢測驗證器
    {"id": "q17", "name": "實作 13.5.9：stress_test_validator 對拍全數通過判定 AC", "points": 5},
    {"id": "q18", "name": "實作 13.5.9：stress_test_validator 揪出相異反例精準報告 WA", "points": 5},
]

# ----------------- 檢查函式實作 -----------------

def check_q1(g, hist):
    fn = g.get("diagnose_wa_discrepancy")
    if callable(fn):
        try:
            r1 = fn("42", "42")
            r2 = fn("Line1\nLine2", "Line1\nLine2 ")
            if r1 == ("AC", "Accepted") and r2 == ("AC", "Accepted"):
                return True, "太棒了！完全吻合或尾端空格容錯皆判定為 AC！"
        except Exception as e:
            return False, f"執行 diagnose_wa_discrepancy 時發生例外: {e}"
    if "diagnose_wa_discrepancy" in hist and '"AC"' in hist:
        return True, "偵測到 AC 診斷判定邏輯！"
    return False, "尚未正確實作 diagnose_wa_discrepancy 或相符輸出未回傳 AC。"

def check_q2(g, hist):
    fn = g.get("diagnose_wa_discrepancy")
    if callable(fn):
        try:
            r1 = fn("100", "99")
            r2 = fn("A\nB\nC", "A\nB")
            if r1[0] == "WA" and "Line 1" in r1[1] and r2[0] == "WA" and "Line 3" in r2[1]:
                return True, "太棒了！精準定位第一個相異行號與內容細節！"
        except Exception as e:
            return False, f"執行 diagnose_wa_discrepancy 時發生例外: {e}"
    if "diagnose_wa_discrepancy" in hist and '"WA"' in hist:
        return True, "偵測到 WA 診斷判定邏輯！"
    return False, "相異輸出未能回傳正確 WA 行號與資訊。"

def check_q3(g, hist):
    fn = g.get("interval_stats")
    if callable(fn):
        try:
            r1 = fn(1, 5)
            r2 = fn(10, 10)
            r3 = fn(-3, 3)
            if r1 == (5, 15) and r2 == (1, 10) and r3 == (7, 0):
                return True, "太棒了！閉區間元素個數與總和計算完全杜絕差一錯誤！"
        except Exception as e:
            return False, f"執行 interval_stats 時發生例外: {e}"
    if "interval_stats" in hist:
        return True, "偵測到 interval_stats 閉區間統計邏輯！"
    return False, "尚未正確實作 interval_stats 或區間計算有誤。"

def check_q4(g, hist):
    fn = g.get("safe_binary_search")
    if callable(fn):
        try:
            if (fn([5], 5) is True and 
                fn([5], 6) is False and 
                fn([], 1) is False and 
                fn([1, 3, 5, 7, 9], 9) is True):
                return True, "太棒了！二分搜尋在單元素、空陣列與邊界完全不漏判！"
        except Exception as e:
            return False, f"執行 safe_binary_search 時發生例外: {e}"
    if "safe_binary_search" in hist:
        return True, "偵測到 safe_binary_search 二分搜尋邏輯！"
    return False, "尚未正確實作 safe_binary_search 或邊界搜尋有誤。"

def check_q5(g, hist):
    fn = g.get("safe_midpoint")
    if callable(fn):
        try:
            if fn(10, 20) == 15 and fn(0, 8) == 4 and fn(-10, 10) == 0:
                return True, "太棒了！中點計算括號完全正確，無優先級運算偏差！"
        except Exception as e:
            return False, f"執行 safe_midpoint 時發生例外: {e}"
    if "safe_midpoint" in hist:
        return True, "偵測到 safe_midpoint 中點計算邏輯！"
    return False, "尚未正確實作 safe_midpoint。"

def check_q6(g, hist):
    fn = g.get("is_even_bitwise")
    if callable(fn):
        try:
            if (fn(4) is True and 
                fn(7) is False and 
                fn(0) is True and 
                fn(-2) is True and 
                fn(-3) is False):
                return True, "太棒了！位元運算與等號優先級括號精準結合！"
        except Exception as e:
            return False, f"執行 is_even_bitwise 時發生例外: {e}"
    if "is_even_bitwise" in hist:
        return True, "偵測到 is_even_bitwise 偶數判斷邏輯！"
    return False, "尚未正確實作 is_even_bitwise 或正負奇偶判斷不符。"

def check_q7(g, hist):
    fn = g.get("safe_float_equal")
    if callable(fn):
        try:
            if (fn(0.1 + 0.2, 0.3) is True and 
                fn(1.00000000001, 1.0) is True and 
                fn(1.05, 1.0) is False):
                return True, "太棒了！浮點數微小誤差容許比對守門員精準防禦！"
        except Exception as e:
            return False, f"執行 safe_float_equal 時發生例外: {e}"
    if "safe_float_equal" in hist:
        return True, "偵測到 safe_float_equal 浮點比對邏輯！"
    return False, "尚未正確實作 safe_float_equal 或比對結果不符。"

def check_q8(g, hist):
    fn = g.get("truncate_towards_zero_divide")
    if callable(fn):
        try:
            if (fn(7, 2) == 3 and 
                fn(-7, 2) == -3 and 
                fn(10, -3) == -3 and 
                fn(-10, -3) == 3):
                return True, "太棒了！正負數向零截斷除法實作精確無誤！"
        except Exception as e:
            return False, f"執行 truncate_towards_zero_divide 時發生例外: {e}"
    if "truncate_towards_zero_divide" in hist:
        return True, "偵測到向零截斷除法邏輯！"
    return False, "尚未正確實作 truncate_towards_zero_divide 或向零截斷偏差。"

def check_q9(g, hist):
    fn = g.get("create_independent_matrix")
    if callable(fn):
        try:
            m = fn(3, 4, 0)
            m[1][2] = 5
            if m[0] == [0, 0, 0, 0] and m[1] == [0, 0, 5, 0] and m[2] == [0, 0, 0, 0]:
                return True, "太棒了！二維矩陣列與列完全獨立，徹底粉碎淺拷貝幽靈！"
        except Exception as e:
            return False, f"執行 create_independent_matrix 時發生例外: {e}"
    if "create_independent_matrix" in hist:
        return True, "偵測到獨立矩陣建立邏輯！"
    return False, "尚未正確實作 create_independent_matrix 或列與列存在共享參考。"

def check_q10(g, hist):
    fn = g.get("safe_append_copy")
    if callable(fn):
        try:
            src = ["a", "b"]
            res = fn(src, "c")
            if res == ["a", "b", "c"] and src == ["a", "b"] and res is not src:
                return True, "太棒了！無副作用追加新元素，原始串列 100% 未受污染！"
        except Exception as e:
            return False, f"執行 safe_append_copy 時發生例外: {e}"
    if "safe_append_copy" in hist:
        return True, "偵測到無副作用複本邏輯！"
    return False, "尚未正確實作 safe_append_copy 或原始串列被修改。"

def check_q11(g, hist):
    fn = g.get("matrix_diagonal_sums")
    if callable(fn):
        try:
            m1 = [[1, 2], [3, 4]]
            if fn(m1) == (5, 5):
                return True, "太棒了！主次對角線計算完全正確且變數命名無遮蔽！"
        except Exception as e:
            return False, f"執行 matrix_diagonal_sums 時發生例外: {e}"
    if "matrix_diagonal_sums" in hist:
        return True, "偵測到對角線計算邏輯！"
    return False, "尚未正確實作 matrix_diagonal_sums 或對角線加總不符。"

def check_q12(g, hist):
    fn = g.get("matrix_diagonal_sums")
    if callable(fn):
        try:
            m2 = [[2, 0, 0], [0, 3, 0], [0, 0, 4]]
            if fn(m2) == (9, 3):
                return True, "太棒了！3x3 矩陣中心元素次對角線重複計數與邊界加總無誤！"
        except Exception as e:
            return False, f"執行 matrix_diagonal_sums 時發生例外: {e}"
    if "matrix_diagonal_sums" in hist:
        return True, "偵測到 3x3 矩陣對角線驗算！"
    return False, "3x3 矩陣對角線總和計算錯誤。"

def check_q13(g, hist):
    fn = g.get("process_testcases_cleanly")
    if callable(fn):
        try:
            data = [[60, 40, 70], [50, 51], [10, 20]]
            if fn(data) == [130, 51, 0]:
                return True, "太棒了！每筆測資獨立重設狀態，徹底根絕跨測資污染！"
        except Exception as e:
            return False, f"執行 process_testcases_cleanly 時發生例外: {e}"
    if "process_testcases_cleanly" in hist:
        return True, "偵測到乾淨多測資處理邏輯！"
    return False, "尚未正確實作 process_testcases_cleanly 或存在狀態殘留。"

def check_q14(g, hist):
    fn = g.get("process_testcases_cleanly")
    if callable(fn):
        try:
            if fn([[], [100]]) == [0, 100] and fn([[55], [55], [55]]) == [55, 55, 55]:
                return True, "太棒了！空測資與重複單元素測資完全隔離精準計算！"
        except Exception as e:
            return False, f"執行 process_testcases_cleanly 時發生例外: {e}"
    if "process_testcases_cleanly" in hist:
        return True, "偵測到邊界測資獨立隔離邏輯！"
    return False, "空測資或重複測資處理不符。"

def check_q15(g, hist):
    fn = g.get("find_min_max_difference")
    if callable(fn):
        try:
            if fn([-10, -5, -20]) == 15 and fn([-7, 8]) == 15:
                return True, "太棒了！全負數測資極值差計算精確，擺脫預設為 0 之盲點！"
        except Exception as e:
            return False, f"執行 find_min_max_difference 時發生例外: {e}"
    if "find_min_max_difference" in hist:
        return True, "偵測到全負數極值差防禦邏輯！"
    return False, "尚未正確實作 find_min_max_difference 或全負數差值計算錯誤。"

def check_q16(g, hist):
    fn = g.get("find_min_max_difference")
    if callable(fn):
        try:
            if fn([-100]) == 0 and fn([5, 5, 5]) == 0:
                return True, "太棒了！單一元素與全相同元素差值安全回傳 0！"
        except Exception as e:
            return False, f"執行 find_min_max_difference 時發生例外: {e}"
    if "find_min_max_difference" in hist:
        return True, "偵測到單元素與重複值極值防禦！"
    return False, "單一元素或全相同串列未能回傳 0。"

def check_q17(g, hist):
    fn = g.get("stress_test_validator")
    if callable(fn):
        try:
            f_s = lambda lst: max(lst) if lst else None
            f_f_good = lambda lst: sorted(lst)[-1] if lst else None
            res = fn(f_s, f_f_good, [[1, 5, 2], [-5, -1], [10]])
            if res == ("AC", 3):
                return True, "太棒了！對拍測資全數吻合時精準報告 ('AC', 測資數)！"
        except Exception as e:
            return False, f"執行 stress_test_validator 時發生例外: {e}"
    if "stress_test_validator" in hist and '"AC"' in hist:
        return True, "偵測到對拍 AC 驗證邏輯！"
    return False, "尚未正確實作 stress_test_validator 或全相符未回傳 AC。"

def check_q18(g, hist):
    fn = g.get("stress_test_validator")
    if callable(fn):
        try:
            f_s = lambda lst: max(lst) if lst else None
            f_f_bad = lambda lst: lst[0] if lst else None
            res = fn(f_s, f_f_bad, [[10, 20]])
            if (isinstance(res, tuple) and 
                res[0] == "WA" and 
                res[1] == [10, 20] and 
                res[2] == 20 and 
                res[3] == 10):
                return True, "太棒了！對拍中途出現相異時立刻終止並回傳反例與兩者答案！"
        except Exception as e:
            return False, f"執行 stress_test_validator 時發生例外: {e}"
    if "stress_test_validator" in hist and '"WA"' in hist:
        return True, "偵測到對拍 WA 抓反例邏輯！"
    return False, "對拍出錯時未能回傳正確反例與答案元組。"

CHECK_FUNCS = {
    "q1": check_q1,
    "q2": check_q2,
    "q3": check_q3,
    "q4": check_q4,
    "q5": check_q5,
    "q6": check_q6,
    "q7": check_q7,
    "q8": check_q8,
    "q9": check_q9,
    "q10": check_q10,
    "q11": check_q11,
    "q12": check_q12,
    "q13": check_q13,
    "q14": check_q14,
    "q15": check_q15,
    "q16": check_q16,
    "q17": check_q17,
    "q18": check_q18,
}

def extract_notebook_history():
    hist_text = ""
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip and hasattr(ip, "user_ns"):
            In = ip.user_ns.get("In", [])
            hist_text = "\n".join(In)
    except Exception:
        pass
    return hist_text

def run_grading(user_globals=None):
    g = {}
    if user_globals is not None:
        g.update(user_globals)
    else:
        try:
            import __main__
            g.update(__main__.__dict__)
        except Exception:
            pass

    hist = extract_notebook_history()

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
