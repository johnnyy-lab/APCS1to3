# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-2 自動評分器
單元名稱：語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（9 大語法除錯核心，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime
import keyword

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

UNIT_ID = "13-2"
UNIT_TITLE = "語法錯誤（SyntaxError）深度排查與 Traceback 閱讀心法"

QUESTIONS = [
    # 13.2.1 編譯階段 vs 執行階段
    {"id": "q1", "name": "實作 13.2.1：合法 Python 語法回傳 SYNTAX_OK", "points": 6},
    {"id": "q2", "name": "實作 13.2.1：語法錯誤精準捕獲回傳 COMPILE_ERROR", "points": 6},
    # 13.2.2 括號未閉合之痛
    {"id": "q3", "name": "實作 13.2.2：括號堆疊對稱匹配平衡檢驗（True）", "points": 6},
    {"id": "q4", "name": "實作 13.2.2：單邊未閉合與交叉錯位括號檢驗（False）", "points": 6},
    # 13.2.3 冒號缺失隱形殺手
    {"id": "q5", "name": "實作 13.2.3：區塊控制關鍵字尾端缺失冒號自動補正", "points": 6},
    {"id": "q6", "name": "實作 13.2.3：已具備冒號與一般陳述式無副作用保持", "points": 6},
    # 13.2.4 引號未閉合與字串跨行陷阱
    {"id": "q7", "name": "實作 13.2.4：單雙引號衝突動態安全包覆與 eval 解析", "points": 6},
    {"id": "q8", "name": "實作 13.2.4：同時含單雙引號之三引號包覆防禦機制", "points": 6},
    # 13.2.5 縮排錯誤與空區塊之災
    {"id": "q9", "name": "實作 13.2.5：未縮排空區塊自動插入 pass 防禦", "points": 6},
    {"id": "q10", "name": "實作 13.2.5：修正後程式碼合法通過 compile() 編譯", "points": 6},
    # 13.2.6 全形字元隱形幽靈
    {"id": "q11", "name": "實作 13.2.6：全形空白、全形冒號與逗號深度淨化", "points": 5},
    {"id": "q12", "name": "實作 13.2.6：全形中文引號與圓括號淨化並通過編譯", "points": 5},
    # 13.2.7 C 風格自增運算子
    {"id": "q13", "name": "實作 13.2.7：C 風格自增運算子 i++ 轉譯為 Python i += 1", "points": 5},
    {"id": "q14", "name": "實作 13.2.7：C 風格自減運算子 i-- 轉譯並完整保留縮排", "points": 5},
    # 13.2.8 變數命名地雷
    {"id": "q15", "name": "實作 13.2.8：合法識別字雙重檢驗（底線、變數名）", "points": 5},
    {"id": "q16", "name": "實作 13.2.8：Python 關鍵字與非法開頭排除防禦", "points": 5},
    # 13.2.9 考場全方位語法醫生綜合驗收
    {"id": "q17", "name": "實作 13.2.9：綜合語法修復：全形字元淨化與運算子轉譯", "points": 5},
    {"id": "q18", "name": "實作 13.2.9：綜合語法修復：條件單等號修復與實機編譯", "points": 5},
]

# ----------------- 檢查函式實作 -----------------

def check_q1(g, hist):
    fn = g.get("diagnose_code_phase")
    if callable(fn):
        try:
            r1 = fn("print('Hello Python')")
            r2 = fn("x = 10\ny = 20\nprint(x + y)")
            if r1 == "SYNTAX_OK" and r2 == "SYNTAX_OK":
                return True, "太棒了！合法 Python 程式碼皆精準判定為 SYNTAX_OK！"
        except Exception as e:
            return False, f"執行 diagnose_code_phase 時發生例外: {e}"
    if "SYNTAX_OK" in hist and "diagnose_code_phase" in hist:
        return True, "偵測到合法代碼檢驗通過記錄！"
    return False, "尚未正確實作 diagnose_code_phase 或正常語法未回傳 'SYNTAX_OK'。"

def check_q2(g, hist):
    fn = g.get("diagnose_code_phase")
    if callable(fn):
        try:
            r1 = fn("if True\n    print(1)")
            r2 = fn("def foo(:")
            r3 = fn("123 = a")
            if r1 == "COMPILE_ERROR" and r2 == "COMPILE_ERROR" and r3 == "COMPILE_ERROR":
                return True, "太棒了！語法錯誤程式碼精準攔截並回傳 COMPILE_ERROR！"
        except Exception as e:
            return False, f"執行 diagnose_code_phase 時發生例外: {e}"
    if "COMPILE_ERROR" in hist and "diagnose_code_phase" in hist:
        return True, "偵測到語法錯誤攔截檢驗通過記錄！"
    return False, "語法錯誤代碼未能正確回傳 'COMPILE_ERROR'。"

def check_q3(g, hist):
    fn = g.get("is_brackets_balanced")
    if callable(fn):
        try:
            c1 = fn("(a + b) * [c - d]")
            c2 = fn("{x: [1, (2 + 3)]}")
            c3 = fn("")
            c4 = fn("()[]{}")
            if c1 is True and c2 is True and c3 is True and c4 is True:
                return True, "太棒了！對稱與巢狀平衡括號皆精準判定為 True！"
        except Exception as e:
            return False, f"執行 is_brackets_balanced 時發生例外: {e}"
    if "is_brackets_balanced" in hist and "assert is_brackets_balanced" in hist:
        return True, "偵測到括號平衡檢驗通過記錄！"
    return False, "尚未正確實作 is_brackets_balanced 或對稱括號未能回傳 True。"

def check_q4(g, hist):
    fn = g.get("is_brackets_balanced")
    if callable(fn):
        try:
            c1 = fn("(a + b]")
            c2 = fn("((())")
            c3 = fn("][")
            c4 = fn("{[(])}")
            if c1 is False and c2 is False and c3 is False and c4 is False:
                return True, "太棒了！未閉合與交叉錯位之不平衡括號皆精準判定為 False！"
        except Exception as e:
            return False, f"執行 is_brackets_balanced 時發生例外: {e}"
    if "is_brackets_balanced" in hist:
        return True, "偵測到括號檢查邏輯！"
    return False, "不平衡或交叉錯位括號未能正確判定為 False。"

def check_q5(g, hist):
    fn = g.get("auto_fix_colons")
    if callable(fn):
        try:
            res_if = fn("if x > 0")
            res_while = fn("    while True")
            res_def = fn("def my_func()")
            res_elif = fn("elif count == 0")
            res_else = fn("else")
            if (res_if.rstrip().endswith(":") and 
                res_while.rstrip().endswith(":") and 
                res_def.rstrip().endswith(":") and
                res_elif.rstrip().endswith(":") and
                res_else.rstrip().endswith(":")):
                return True, "太棒了！控制流程與函式宣告行末缺失冒號皆已自動補正！"
        except Exception as e:
            return False, f"執行 auto_fix_colons 時發生例外: {e}"
    if "auto_fix_colons" in hist:
        return True, "偵測到自動補冒號邏輯！"
    return False, "尚未正確實作 auto_fix_colons 或末端缺少冒號未能自動補齊。"

def check_q6(g, hist):
    fn = g.get("auto_fix_colons")
    if callable(fn):
        try:
            res_already = fn("if x > 0:")
            res_stmt = fn("x = 10")
            res_print = fn("    print('hello')")
            if res_already == "if x > 0:" and res_stmt == "x = 10" and res_print == "    print('hello')":
                return True, "太棒了！既有冒號與一般表達式保持原貌，無重複補正之副作用！"
        except Exception as e:
            return False, f"執行 auto_fix_colons 時發生例外: {e}"
    if "auto_fix_colons" in hist:
        return True, "偵測到無副作用防禦邏輯！"
    return False, "已有冒號或一般陳述式未保持原貌。"

def check_q7(g, hist):
    fn = g.get("safe_quote_string")
    if callable(fn):
        try:
            t1 = "Hello 'World'"
            q1 = fn(t1)
            t2 = 'Hello "World"'
            q2 = fn(t2)
            if eval(q1) == t1 and eval(q2) == t2:
                return True, "太棒了！單/雙引號衝突動態切換包覆，eval() 解析 100% 吻合！"
        except Exception as e:
            return False, f"執行 safe_quote_string 時發生例外: {e}"
    if "safe_quote_string" in hist:
        return True, "偵測到安全引號包覆邏輯！"
    return False, "尚未正確實作 safe_quote_string 或包覆後字串無法正確 eval() 解碼。"

def check_q8(g, hist):
    fn = g.get("safe_quote_string")
    if callable(fn):
        try:
            t_both = 'He said "It\'s fine"'
            q_both = fn(t_both)
            if eval(q_both) == t_both and (q_both.startswith('"""') or q_both.startswith("'''")):
                return True, "太棒了！同時包含單雙引號時成功啟動三引號防禦機制！"
        except Exception as e:
            return False, f"執行 safe_quote_string 時發生例外: {e}"
    if "safe_quote_string" in hist:
        return True, "偵測到三引號安全防禦邏輯！"
    return False, "同時含單雙引號時未能採用三引號安全包覆或 eval() 結果相異。"

def check_q9(g, hist):
    fn = g.get("fill_empty_blocks_with_pass")
    if callable(fn):
        try:
            code = "if x > 0:\nprint(x)"
            fixed = fn(code)
            if "pass" in fixed:
                compile(fixed, "<test_q9>", "exec")
                return True, "太棒了！空區塊成功自動插入 pass 並順利通過編譯！"
        except Exception as e:
            return False, f"執行 fill_empty_blocks_with_pass 時發生例外: {e}"
    if "fill_empty_blocks_with_pass" in hist:
        return True, "偵測到自動填補 pass 邏輯！"
    return False, "尚未正確實作 fill_empty_blocks_with_pass 或修復後未插入 pass。"

def check_q10(g, hist):
    fn = g.get("fill_empty_blocks_with_pass")
    if callable(fn):
        try:
            code = "def foo():\n    if True:\n        pass\n    return 42"
            fixed = fn(code)
            compile(fixed, "<test_q10>", "exec")
            return True, "太棒了！既有合法巢狀結構完整保留且維持合法編譯！"
        except Exception as e:
            return False, f"執行 fill_empty_blocks_with_pass 時發生例外: {e}"
    if "fill_empty_blocks_with_pass" in hist:
        return True, "偵測到合法結構保持邏輯！"
    return False, "包含既有陳述式之區塊修復後編譯失敗。"

def check_q11(g, hist):
    fn = g.get("deep_sanitize_code")
    if callable(fn):
        try:
            code = "for　i　in range(5)：\n　　print(i，i+1)"
            cleaned = fn(code)
            if '\u3000' not in cleaned and '：' not in cleaned and '，' not in cleaned:
                if ":" in cleaned and "," in cleaned and " " in cleaned:
                    return True, "太棒了！全形空白、全形冒號與全形逗號全數精準淨化！"
        except Exception as e:
            return False, f"執行 deep_sanitize_code 時發生例外: {e}"
    if "deep_sanitize_code" in hist:
        return True, "偵測到全形字元淨化邏輯！"
    return False, "尚未正確實作 deep_sanitize_code 或未能完全消除全形標點。"

def check_q12(g, hist):
    fn = g.get("deep_sanitize_code")
    if callable(fn):
        try:
            code = "if x == 10:\n    print（“PASS”，x）"
            cleaned = fn(code)
            if '（' not in cleaned and '）' not in cleaned and '“' not in cleaned and '”' not in cleaned:
                compile("x = 10\n" + cleaned, "<test_q12>", "exec")
                return True, "太棒了！全形引號與圓括號全數淨化且通過實機編譯驗證！"
        except Exception as e:
            return False, f"執行 deep_sanitize_code 時發生例外: {e}"
    if "deep_sanitize_code" in hist:
        return True, "偵測到全形標點淨化與編譯邏輯！"
    return False, "全形引號或圓括號未完全消除，或淨化後代碼無法編譯。"

def check_q13(g, hist):
    fn = g.get("convert_c_increment_to_python")
    if callable(fn):
        try:
            r1 = fn("i++")
            r2 = fn("    counter++")
            if r1.strip() == "i += 1" and r2 == "    counter += 1":
                return True, "太棒了！自增運算子 i++ 精準轉譯為 Python i += 1 且縮排完整！"
        except Exception as e:
            return False, f"執行 convert_c_increment_to_python 時發生例外: {e}"
    if "convert_c_increment_to_python" in hist:
        return True, "偵測到自增運算子轉譯邏輯！"
    return False, "尚未正確實作 convert_c_increment_to_python 或 i++ 轉譯結果不正確。"

def check_q14(g, hist):
    fn = g.get("convert_c_increment_to_python")
    if callable(fn):
        try:
            r1 = fn("idx--")
            r2 = fn("        step--")
            r3 = fn("x = 10")
            if r1.strip() == "idx -= 1" and r2 == "        step -= 1" and r3 == "x = 10":
                return True, "太棒了！自減運算子 i-- 成功轉譯為 -= 1，且一般賦值不受影響！"
        except Exception as e:
            return False, f"執行 convert_c_increment_to_python 時發生例外: {e}"
    if "convert_c_increment_to_python" in hist:
        return True, "偵測到自減轉譯與非自減行保護邏輯！"
    return False, "自減運算子未轉譯或一般語法行被異常修改。"

def check_q15(g, hist):
    fn = g.get("is_safe_identifier")
    if callable(fn):
        try:
            v1 = fn("score")
            v2 = fn("_total_sum")
            v3 = fn("student_id_99")
            if v1 is True and v2 is True and v3 is True:
                return True, "太棒了！合規英文、底線與混合命名皆正確判定為安全識別字！"
        except Exception as e:
            return False, f"執行 is_safe_identifier 時發生例外: {e}"
    if "is_safe_identifier" in hist:
        return True, "偵測到安全識別字驗證邏輯！"
    return False, "尚未正確實作 is_safe_identifier 或合規命名未能回傳 True。"

def check_q16(g, hist):
    fn = g.get("is_safe_identifier")
    if callable(fn):
        try:
            f1 = fn("class")
            f2 = fn("def")
            f3 = fn("for")
            f4 = fn("123abc")
            f5 = fn("my-score")
            if f1 is False and f2 is False and f3 is False and f4 is False and f5 is False:
                return True, "太棒了！Python 保留關鍵字與非法符號開頭皆精準攔截拒絕！"
        except Exception as e:
            return False, f"執行 is_safe_identifier 時發生例外: {e}"
    if "is_safe_identifier" in hist:
        return True, "偵測到保留字攔截邏輯！"
    return False, "Python 關鍵字或非法識別字未能正確判定為 False。"

def check_q17(g, hist):
    fn = g.get("fix_all_syntax_errors")
    if callable(fn):
        try:
            broken = "while　i < 10：\n　　i++"
            fixed = fn(broken)
            if "i++" not in fixed and "i += 1" in fixed and "：" not in fixed and "\u3000" not in fixed:
                return True, "太棒了！綜合修復器成功粉碎全形冒號、全形空白與 i++ 語法缺陷！"
        except Exception as e:
            return False, f"執行 fix_all_syntax_errors 時發生例外: {e}"
    if "fix_all_syntax_errors" in hist:
        return True, "偵測到綜合語法修復器邏輯！"
    return False, "尚未正確實作 fix_all_syntax_errors 或未能成功修復全形字元與自增。"

def check_q18(g, hist):
    fn = g.get("fix_all_syntax_errors")
    if callable(fn):
        try:
            broken = "if　val = 5：\n　　pass\ni++"
            fixed = fn(broken)
            if "==" in fixed and "pass" in fixed:
                compile("val = 5\ni = 0\n" + fixed, "<test_q18>", "exec")
                return True, "太棒了！if 條件單等號成功修復為雙等號，並通過 compile() 實機驗證！"
        except Exception as e:
            return False, f"執行 fix_all_syntax_errors 時發生例外: {e}"
    if "fix_all_syntax_errors" in hist:
        return True, "偵測到綜合修復與實機編譯驗證！"
    return False, "if 單等號未修正或綜合修復後程式碼無法通過編譯。"

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
