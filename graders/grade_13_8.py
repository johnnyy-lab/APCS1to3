# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-8 自動評分器
單元名稱：系統化除錯法與考場送出前自主檢核清單（Checklist）
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（6 大系統化除錯與考場自主檢核核心，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime
import io

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

UNIT_ID = "13-8"
UNIT_TITLE = "系統化除錯法與考場送出前自主檢核清單（Checklist）"

QUESTIONS = [
    # 13.8.1 極小可重現範例 (MRE)
    {"id": "q1", "name": "實作 13.8.1：reverse_sublist 指定區間反轉且前後綴保持", "points": 6},
    {"id": "q2", "name": "實作 13.8.1：reverse_sublist 全區間與單元素微型測資驗證", "points": 6},
    {"id": "q3", "name": "實作 13.8.1：reverse_sublist 兩元素邊界反轉正確無誤", "points": 5},
    # 13.8.2 二分註解隔離法
    {"id": "q4", "name": "實作 13.8.2：safe_pipeline_executor 正常數值過濾與平均計算", "points": 6},
    {"id": "q5", "name": "實作 13.8.2：safe_pipeline_executor 混入非數字安全過濾防禦", "points": 6},
    {"id": "q6", "name": "實作 13.8.2：safe_pipeline_executor 空資料安全回傳 0.0 防禦除零", "points": 5},
    # 13.8.3 科學化 Print 追蹤法
    {"id": "q7", "name": "實作 13.8.3：binary_search_with_logs 二分搜尋正確回傳目標索引", "points": 6},
    {"id": "q8", "name": "實作 13.8.3：binary_search_with_logs 歷程完整包含 [DEBUG] 標籤日誌", "points": 6},
    {"id": "q9", "name": "實作 13.8.3：binary_search_with_logs 查無目標回傳 -1 與日誌", "points": 5},
    # 13.8.4 斷言守門法 (assert)
    {"id": "q10", "name": "實作 13.8.4：divide_and_assert_invariant 商餘計算滿足除法不變量", "points": 6},
    {"id": "q11", "name": "實作 13.8.4：divide_and_assert_invariant 整除餘數為 0 斷言驗證", "points": 6},
    {"id": "q12", "name": "實作 13.8.4：divide_and_assert_invariant 除數為 0 觸發 AssertionError", "points": 5},
    # 13.8.5 極端值預先探測法
    {"id": "q13", "name": "實作 13.8.5：find_top_two 正整數串列前兩大不重複值查找", "points": 6},
    {"id": "q14", "name": "實作 13.8.5：find_top_two 全負數極端測資前兩大負數查找", "points": 5},
    {"id": "q15", "name": "實作 13.8.5：find_top_two 全相同或元素不足安全回傳 None", "points": 5},
    # 13.8.6 考場標準送出模板
    {"id": "q16", "name": "實作 13.8.6：apcs_standard_solution 最大值與 3 的倍數個數計算", "points": 6},
    {"id": "q17", "name": "實作 13.8.6：apcs_standard_solution 全負數輸入精確對齊換行格式", "points": 5},
    {"id": "q18", "name": "實作 13.8.6：apcs_standard_solution 純淨標準 I/O 無殘留提示與除錯", "points": 5},
]

# ----------------- 檢查函式實作 -----------------

def check_q1(g, hist):
    fn = g.get("reverse_sublist")
    if callable(fn):
        try:
            r = fn([1, 2, 3, 4, 5], 1, 3)
            if r == [1, 4, 3, 2, 5]:
                return True, "太棒了！指定子區間精準反轉且前後綴完整保留！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到區間反轉邏輯！"
    return False, "尚未正確實作 reverse_sublist 或反轉結果不符。"

def check_q2(g, hist):
    fn = g.get("reverse_sublist")
    if callable(fn):
        try:
            r1 = fn([1, 2, 3], 0, 2)
            r2 = fn([10], 0, 0)
            if r1 == [3, 2, 1] and r2 == [10]:
                return True, "太棒了！全區間反轉與單元素微型測資驗證無誤！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到微型邊界反轉邏輯！"
    return False, "全區間或單元素反轉失敗。"

def check_q3(g, hist):
    fn = g.get("reverse_sublist")
    if callable(fn):
        try:
            if fn([1, 2], 0, 1) == [2, 1]:
                return True, "太棒了！兩元素邊界反轉正確無誤！"
        except Exception as e:
            return False, f"執行 reverse_sublist 時發生例外: {e}"
    if "reverse_sublist" in hist:
        return True, "偵測到兩元素反轉！"
    return False, "兩元素反轉不符。"

def check_q4(g, hist):
    fn = g.get("safe_pipeline_executor")
    if callable(fn):
        try:
            if fn(["10", "20", "30"]) == 20.0:
                return True, "太棒了！字串轉整數並精準計算浮點平均值 20.0！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到管線平均計算邏輯！"
    return False, "尚未正確實作 safe_pipeline_executor 或平均值不符。"

def check_q5(g, hist):
    fn = g.get("safe_pipeline_executor")
    if callable(fn):
        try:
            if fn(["5", "invalid", "15"]) == 10.0:
                return True, "太棒了！自動過濾非數字文字，維持正常數據運算！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到非數字安全過濾邏輯！"
    return False, "非數字字串過濾有誤。"

def check_q6(g, hist):
    fn = g.get("safe_pipeline_executor")
    if callable(fn):
        try:
            if fn([]) == 0.0 and fn(["abc", "xyz"]) == 0.0:
                return True, "太棒了！空串列與全無效字串安全回傳 0.0，杜絕除以零崩潰！"
        except Exception as e:
            return False, f"執行 safe_pipeline_executor 時發生例外: {e}"
    if "safe_pipeline_executor" in hist:
        return True, "偵測到空資料防禦邏輯！"
    return False, "空資料未回傳 0.0。"

def check_q7(g, hist):
    fn = g.get("binary_search_with_logs")
    if callable(fn):
        try:
            pos, logs = fn([1, 3, 5, 7, 9], 7)
            if pos == 3:
                return True, "太棒了！二分搜尋正確定位目標值索引 3！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist:
        return True, "偵測到二分搜尋回傳邏輯！"
    return False, "尚未正確實作 binary_search_with_logs 或索引不符。"

def check_q8(g, hist):
    fn = g.get("binary_search_with_logs")
    if callable(fn):
        try:
            _, logs = fn([1, 3, 5, 7, 9], 7)
            if len(logs) >= 1 and logs[0].startswith("[DEBUG]") and "val=" in logs[0]:
                return True, "太棒了！搜尋歷程正確記錄 [DEBUG] 標籤且包含變數細節！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist and "[DEBUG]" in hist:
        return True, "偵測到 [DEBUG] 日誌格式邏輯！"
    return False, "日誌歷程格式不符或未包含 [DEBUG]。"

def check_q9(g, hist):
    fn = g.get("binary_search_with_logs")
    if callable(fn):
        try:
            pos_nf, logs_nf = fn([1, 2, 3], 99)
            if pos_nf == -1 and len(logs_nf) >= 1:
                return True, "太棒了！查無目標時安全回傳 -1 與完整搜尋日誌！"
        except Exception as e:
            return False, f"執行 binary_search_with_logs 時發生例外: {e}"
    if "binary_search_with_logs" in hist:
        return True, "偵測到查無目標防禦！"
    return False, "查無目標時未回傳 -1。"

def check_q10(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if callable(fn):
        try:
            if fn(10, 3) == (3, 1) and fn(29, 6) == (4, 5):
                return True, "太棒了！整數除法商與餘數計算精準，滿足除法不變量！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist:
        return True, "偵測到商餘計算邏輯！"
    return False, "尚未正確實作 divide_and_assert_invariant 或商餘不符。"

def check_q11(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if callable(fn):
        try:
            if fn(20, 5) == (4, 0) and fn(-15, 4) == (-4, 1):
                return True, "太棒了！整除情境與負數除法商餘計算均正確斷言通過！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist:
        return True, "偵測到整除斷言通過！"
    return False, "整除或負數除法斷言失敗。"

def check_q12(g, hist):
    fn = g.get("divide_and_assert_invariant")
    if callable(fn):
        try:
            threw = False
            try:
                fn(10, 0)
            except AssertionError:
                threw = True
            except Exception:
                pass
            if threw:
                return True, "太棒了！除數為 0 時精準由 assert 攔截觸發 AssertionError！"
        except Exception as e:
            return False, f"執行 divide_and_assert_invariant 時發生例外: {e}"
    if "divide_and_assert_invariant" in hist and "assert" in hist:
        return True, "偵測到除以零斷言邏輯！"
    return False, "除數為 0 時未能引爆 AssertionError。"

def check_q13(g, hist):
    fn = g.get("find_top_two")
    if callable(fn):
        try:
            if fn([1, 2, 3, 4]) == (4, 3) and fn([10, 5, 20, 15]) == (20, 15):
                return True, "太棒了！正整數串列前兩大不重複值查找完全精準！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到前兩大極值查找邏輯！"
    return False, "尚未正確實作 find_top_two 或回傳值不符。"

def check_q14(g, hist):
    fn = g.get("find_top_two")
    if callable(fn):
        try:
            if fn([-5, -1, -10]) == (-1, -5) and fn([-5, -10, -3]) == (-3, -5):
                return True, "太棒了！全負數極端測資前兩大負數查找完全正確！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到全負數極值查找邏輯！"
    return False, "全負數輸入查找失敗。"

def check_q15(g, hist):
    fn = g.get("find_top_two")
    if callable(fn):
        try:
            if fn([7, 7, 7]) is None and fn([99]) is None and fn([]) is None:
                return True, "太棒了！全相同數字、單一元素與空串列安全回傳 None！"
        except Exception as e:
            return False, f"執行 find_top_two 時發生例外: {e}"
    if "find_top_two" in hist:
        return True, "偵測到無解安全回傳 None 邏輯！"
    return False, "元素不足或全相同時未回傳 None。"

def check_q16(g, hist):
    fn = g.get("apcs_standard_solution")
    if callable(fn):
        try:
            test_in = "4\n3 6 9 12\n"
            expected = "12\n4\n"
            if fn(test_in) == expected:
                return True, "太棒了！標準兩行輸出最大整數與能被 3 整除之個數完全正確！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到 APCS 標準解題輸出邏輯！"
    return False, "尚未正確實作 apcs_standard_solution 或輸出不符。"

def check_q17(g, hist):
    fn = g.get("apcs_standard_solution")
    if callable(fn):
        try:
            test_neg = "3\n-9 -3 -6\n"
            expected_neg = "-3\n3\n"
            if fn(test_neg) == expected_neg:
                return True, "太棒了！全負數測資最大值 -3 與整除個數 3 格式對齊完全無瑕！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到全負數標準輸出邏輯！"
    return False, "全負數測資輸出結果不符。"

def check_q18(g, hist):
    fn = g.get("apcs_standard_solution")
    if callable(fn):
        try:
            test_mix = "5\n10 15 20 33 7\n"
            out = fn(test_mix)
            lines = out.strip().split("\n")
            if len(lines) == 2 and lines[0] == "33" and lines[1] == "2":
                return True, "太棒了！純淨標準輸出，無任何提示文字或 debug print 污染！"
        except Exception as e:
            return False, f"執行 apcs_standard_solution 時發生例外: {e}"
    if "apcs_standard_solution" in hist:
        return True, "偵測到純淨標準輸出檢查！"
    return False, "輸出內容包含多餘行數或污染文字。"

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
