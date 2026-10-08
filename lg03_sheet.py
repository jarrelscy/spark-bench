"""LG-03 (v7.1, hard): spreadsheet formula engine.

Replaces the saturated JSON design-spec task (every model 0.76-0.88 on structure
checks). Single module, ~600-1200 lines of real logic: tokenizer, precedence
parser, error propagation, range functions, cycle detection that survives edits,
undo, dependents, CSV export, and a 3,000-cell chain (forbids naive recursion).

Every behaviour the hidden tests check is written in the prompt. The test inputs
and expected values live only here, not in the prompt.
"""

LG03_PROMPT = r'''Implement a spreadsheet formula engine in Python 3.11, standard library only, as ONE module named sheet.py. Output exactly one fenced python code block containing the complete module. Write all of it; no placeholders. No tools, files or project exist: answer only in this message.

API
- class Sheet with methods:
  - set(ref: str, raw: str) -> None. Stores raw text exactly as given. raw == "" clears the cell. A non-str raw raises TypeError. An invalid ref raises ValueError.
  - get_raw(ref) -> str | None. The stored raw text, or None for an empty cell.
  - get(ref) -> the evaluated value: float, str, bool, None (empty cell), or an error code string (below).
  - undo() -> bool. Reverts the most recent set() call (including clears). Returns False when there is nothing to undo. Every set() is one undo step.
  - dependents(ref) -> list[str]. Every formula cell that depends on ref directly or transitively, through references or ranges, as canonical refs sorted by (row, column). Excludes ref itself.
  - to_csv() -> str. See CSV below.

Cell references
- Column letters A..ZZ (case-insensitive) followed by a row number 1..9999, e.g. A1, b7, AA10, ZZ9999. Canonical form is upper-case letters. Column order: A..Z, then AA..AZ, BA..BZ, ... ZZ (Excel style). Anything else (e.g. "1A", "A0", "A10000", "AAA1", "") is invalid: set/get/get_raw/dependents raise ValueError for it.

Raw text
- Starts with "=": a formula (the rest is the expression).
- Otherwise, if the WHOLE text (surrounding whitespace allowed) is a number such as 3, -2.5, .5, 1e3, it is a float.
- Otherwise it is literal text, kept verbatim (including leading/trailing spaces).

Values and coercion
- Numbers are Python floats. Booleans are Python bools.
- Arithmetic coercion: number -> itself; bool -> 1.0/0.0; empty cell -> 0.0; text -> error #VALUE!.
- Text coercion (for & and CONCAT): text -> itself; empty -> ""; bool -> "TRUE"/"FALSE"; number -> if it is integral and abs < 1e15, no decimal point (3.0 -> "3", -2.0 -> "-2"), otherwise repr(float) (2.5 -> "2.5", 0.1+0.2 -> "0.30000000000000004").
- A formula whose result is an empty cell (e.g. "=Z99" with Z99 empty) evaluates to 0.0.

Expression grammar, lowest to highest precedence (all binary operators left-associative except ^):
  1. comparison: = <> < > <= >=
  2. concatenation: &
  3. additive: + -
  4. multiplicative: * /
  5. unary: - +   (so -2^2 = -4, and 2^-1 = 0.5)
  6. power: ^  (right-associative: 2^3^2 = 512)
  7. primary: number literal, "string" literal (a doubled "" inside means one quote), TRUE / FALSE (case-insensitive), cell reference, range (A1:B3, only valid as a function argument), function call NAME(arg, ...) with a case-insensitive name, or ( expression ).
- Whitespace is allowed between tokens.
- Anything that does not parse (unbalanced parentheses, dangling operator, unterminated string, an empty formula "=", a range used outside a function argument at the top level such as "=A1:A3" ... see errors) gives #PARSE! for a syntax error. "=A1:A3" parses but evaluates to #VALUE!.
- A reference-shaped token that is out of bounds (e.g. A10000 or AAA1 inside a formula) is not a syntax error: it evaluates to #REF!.
- An identifier that is not TRUE/FALSE, not reference-shaped and not followed by "(" (e.g. =foo+1) evaluates to #NAME?. A call to an unknown function evaluates to #NAME?.

Comparison
- Compares two numbers, or two texts (case-insensitive), or bools (treated as 1.0/0.0 numbers). An empty cell compares as 0.0 against a number and as "" against text. Comparing a number with text gives #VALUE!. The result is a bool.

Errors (get() returns these exact strings)
- "#DIV/0!" division by zero (also 0 raised to a negative power), AVERAGE of no numbers.
- "#VALUE!" wrong type (text in arithmetic, number-vs-text comparison, text as IF condition, wrong argument count, a range where a single value is needed, a non-finite numeric result such as overflow).
- "#REF!" reference out of bounds.
- "#NAME?" unknown function or bare identifier.
- "#PARSE!" formula syntax error.
- "#CYCLE!" circular reference (see below).
- Propagation: errors propagate left to right. A binary operation, comparison or function returns the FIRST error it meets while evaluating its operands/arguments in order, before applying its own rules. IF evaluates only its condition and the chosen branch (the other branch's error does not matter).

Functions (arguments may be ranges where noted)
- SUM, AVERAGE, MIN, MAX, COUNT: arguments are numbers, expressions, cells or ranges. Inside cells/ranges, only number values count; text, bools and empty cells are skipped. Directly given (non-reference) arguments: bools count as 1.0/0.0, an expression evaluating to empty counts as 0.0, text gives #VALUE!. Any error in a cell or argument is returned (first one wins), EXCEPT for COUNT, which skips errors and non-numbers and just counts numbers. MIN/MAX of no numbers is 0.0. AVERAGE of no numbers is #DIV/0!. All return floats.
- IF(cond, then [, else]): cond must be a number or bool (empty counts as 0.0/false); text -> #VALUE!. Missing else returns False. 1 or 4+ arguments -> #VALUE!.
- CONCAT(args...): text-coerces and joins every argument; ranges are read row by row, left to right, top to bottom.
- LEN(x): length of the text coercion of x, as float.
- ABS(x): absolute value.
- ROUND(x [, digits]): round half away from zero to `digits` decimals (default 0); digits is truncated to an integer and may be negative. Must be exact on decimal ties: ROUND(2.5) = 3.0, ROUND(-2.5) = -3.0, ROUND(1.005, 2) = 1.01, ROUND(1234.5, -2) = 1200.0.
- Ranges A1:B3 cover the rectangle between the two corners in either order (B3:A1 is the same rectangle).

Cycles
- A formula cell that is part of a circular reference, through references or ranges, gets "#CYCLE!". This includes a cell referring to itself (=A1+1 in A1) and a range that contains the cell itself (=SUM(A1:A3) in A2). Cells that only depend on a cyclic cell (but are not in the cycle) get "#CYCLE!" by propagation, as a normal error.
- Cycles must be re-evaluated after every edit: breaking a cycle by changing one of its cells makes all other cells compute normally again; undo() can recreate it. Results must never be stale: get() always reflects the current raw contents of every cell.

Scale
- A chain of at least 3,000 cells (A1 = 1, A2 = A1+1, A3 = A2+1, ...) must evaluate correctly; do not rely on deep Python recursion over cells. get() on a 200x10 block of formulas must take well under a second each.

CSV
- to_csv() covers the rectangle from A1 to the bottom-most row and right-most column that contain any non-empty cell (empty sheet -> ""). Rows are joined with "\n" (no trailing newline), fields with ",". Each field is the text coercion of get(); errors appear as their code; empty cells are empty fields. A field containing a comma, a double quote or a newline is wrapped in double quotes with inner quotes doubled.
'''


LG03_TESTS = r'''
import sys, time
passed = 0; total = 0; details = []
def t(name, fn):
    global passed, total
    total += 1
    try:
        fn(); passed += 1
    except Exception as e:
        details.append(f"{name}:{type(e).__name__}")
try:
    import sheet as M
    S = M.Sheet
except Exception as e:
    print("LG_RESULT 0/10"); print("LG_DETAIL import:", type(e).__name__, str(e)[:120]); sys.exit(0)

def mk(**cells):
    s = S()
    for k, v in cells.items(): s.set(k, v)
    return s
def eq(a, b):
    if isinstance(b, float):
        assert isinstance(a, float) and not isinstance(a, bool) and abs(a - b) < 1e-9, (a, b)
    else:
        assert a == b and type(a) is type(b), (a, b)

def test_literals():
    s = mk(A1="3", A2=" -2.5 ", A3=".5", A4="1e3", A5="hello", A6=" pad ")
    eq(s.get("A1"), 3.0); eq(s.get("A2"), -2.5); eq(s.get("A3"), 0.5); eq(s.get("A4"), 1000.0)
    eq(s.get("A5"), "hello"); eq(s.get("A6"), " pad "); eq(s.get("B9"), None); eq(s.get_raw("A2"), " -2.5 ")
def test_case_insensitive_refs():
    s = mk(a1="2"); s.set("B1", "=a1*3"); eq(s.get("b1"), 6.0); eq(s.get_raw("A1"), "2")
def test_invalid_refs_raise():
    s = S()
    for bad in ("1A", "A0", "A10000", "AAA1", "", "A"):
        try: s.set(bad, "1"); raise AssertionError(bad)
        except ValueError: pass
    try: s.get("A0"); raise AssertionError("get")
    except ValueError: pass
def test_set_type_error():
    try: S().set("A1", 5); raise AssertionError()
    except TypeError: pass
def test_precedence():
    s = mk(A1="=1+2*3", A2="=(1+2)*3", A3="=10-4-3", A4="=12/3/2", A5="=2^3^2", A6="=-2^2", A7="=2^-1", A8="=1+2&3")
    eq(s.get("A1"), 7.0); eq(s.get("A2"), 9.0); eq(s.get("A3"), 3.0); eq(s.get("A4"), 2.0)
    eq(s.get("A5"), 512.0); eq(s.get("A6"), -4.0); eq(s.get("A7"), 0.5); eq(s.get("A8"), "33")
def test_comparison_lowest():
    s = mk(A1="=1+1=2", A2="=3>2+2", A3="=\"a\"&\"b\"=\"AB\"")
    eq(s.get("A1"), True); eq(s.get("A2"), False); eq(s.get("A3"), True)
def test_whitespace_and_strings():
    s = mk(A1="=  1 +   2 ", A2='="say ""hi"""', A3='=LEN("")')
    eq(s.get("A1"), 3.0); eq(s.get("A2"), 'say "hi"'); eq(s.get("A3"), 0.0)
def test_text_coercion_numbers():
    s = mk(A1="=3&\"\"", A2="=2.5&\"x\"", A3="=(0.1+0.2)&\"\"", A4="=-2&\"\"", A5="=TRUE&\"\"")
    eq(s.get("A1"), "3"); eq(s.get("A2"), "2.5x"); eq(s.get("A3"), "0.30000000000000004"); eq(s.get("A4"), "-2"); eq(s.get("A5"), "TRUE")
def test_empty_refs():
    s = mk(A1="=Z99", A2="=Z99+1", A3="=Z99&\"x\"")
    eq(s.get("A1"), 0.0); eq(s.get("A2"), 1.0); eq(s.get("A3"), "x")
def test_bool_arithmetic():
    s = mk(A1="=TRUE+TRUE", A2="=true*5", A3="=FALSE-1")
    eq(s.get("A1"), 2.0); eq(s.get("A2"), 5.0); eq(s.get("A3"), -1.0)
def test_value_errors():
    s = mk(B1="abc", A1="=B1+1", A2="=1<\"a\"", A3="=IF(\"x\",1,2)", A4="=10^400")
    eq(s.get("A1"), "#VALUE!"); eq(s.get("A2"), "#VALUE!"); eq(s.get("A3"), "#VALUE!"); eq(s.get("A4"), "#VALUE!")
def test_div0():
    s = mk(A1="=1/0", A2="=0^-1", A3="=AVERAGE(Z1:Z5)", A4="=1/(2-2)")
    for c in ("A1", "A2", "A3", "A4"): eq(s.get(c), "#DIV/0!")
def test_parse_errors():
    s = mk(A1="=(1+2", A2="=1+", A3="=\"abc", A4="=", A5="=1 2", A6="=SUM(1,)")
    for c in ("A1", "A2", "A3", "A4", "A5", "A6"): eq(s.get(c), "#PARSE!")
def test_name_and_ref_errors():
    s = mk(A1="=foo+1", A2="=NOPE(1)", A3="=A10000", A4="=AAA1+1", A5="=A1:A3")
    eq(s.get("A1"), "#NAME?"); eq(s.get("A2"), "#NAME?"); eq(s.get("A3"), "#REF!"); eq(s.get("A4"), "#REF!"); eq(s.get("A5"), "#VALUE!")
def test_error_left_to_right():
    s = mk(A1="=1/0", A2="=foo", A3="=A1+A2", A4="=A2+A1", A5="=SUM(A2,A1)", A6="=A1&A2", A7="=A2>A1")
    eq(s.get("A3"), "#DIV/0!"); eq(s.get("A4"), "#NAME?"); eq(s.get("A5"), "#NAME?"); eq(s.get("A6"), "#DIV/0!"); eq(s.get("A7"), "#NAME?")
def test_if_lazy():
    s = mk(A1="=IF(1,5,1/0)", A2="=IF(0,1/0,6)", A3="=IF(FALSE,1)", A4="=IF(Z9,1,2)", A5="=IF(1)", A6="=IF(1,2,3,4)", A7="=IF(1/0,1,2)")
    eq(s.get("A1"), 5.0); eq(s.get("A2"), 6.0); eq(s.get("A3"), False); eq(s.get("A4"), 2.0)
    eq(s.get("A5"), "#VALUE!"); eq(s.get("A6"), "#VALUE!"); eq(s.get("A7"), "#DIV/0!")
def test_sum_range_skips():
    s = mk(A1="1", A2="x", A3="=TRUE", A4="4", B1="=SUM(A1:A5)", B2="=SUM(A1:A4,10,TRUE)", B3="=SUM(\"x\")")
    eq(s.get("B1"), 5.0); eq(s.get("B2"), 16.0); eq(s.get("B3"), "#VALUE!")
def test_range_any_corner_order():
    s = mk(A1="1", B1="2", A2="3", B2="4", C1="=SUM(B2:A1)", C2="=SUM(A2:B1)")
    eq(s.get("C1"), 10.0); eq(s.get("C2"), 10.0)
def test_min_max_average():
    s = mk(A1="4", A2="-2", A3="x", B1="=MIN(A1:A3)", B2="=MAX(A1:A3)", B3="=AVERAGE(A1:A3)", B4="=MIN(Z1:Z3)", B5="=MAX(Z1:Z3,-5)")
    eq(s.get("B1"), -2.0); eq(s.get("B2"), 4.0); eq(s.get("B3"), 1.0); eq(s.get("B4"), 0.0); eq(s.get("B5"), -5.0)
def test_count_skips_errors():
    s = mk(A1="1", A2="=1/0", A3="t", A4="2", B1="=COUNT(A1:A4)", B2="=SUM(A1:A4)", B3="=COUNT(A1:A4,\"x\",3)")
    eq(s.get("B1"), 2.0); eq(s.get("B2"), "#DIV/0!"); eq(s.get("B3"), 3.0)
def test_concat_range_order():
    s = mk(A1="a", B1="1", A2="=TRUE", B2="2.5", C1="=CONCAT(A1:B2,\"!\")")
    eq(s.get("C1"), "a1TRUE2.5!")
def test_len_abs():
    s = mk(A1="=LEN(12.5)", A2="=LEN(\"abc\"&1)", A3="=ABS(-3)", A4="=ABS(\"x\")", A5="=LEN(A1:A2)")
    eq(s.get("A1"), 4.0); eq(s.get("A2"), 4.0); eq(s.get("A3"), 3.0); eq(s.get("A4"), "#VALUE!"); eq(s.get("A5"), "#VALUE!")
def test_round_exact():
    s = mk(A1="=ROUND(2.5)", A2="=ROUND(-2.5)", A3="=ROUND(1.005,2)", A4="=ROUND(1234.5,-2)", A5="=ROUND(2.675,2)", A6="=ROUND(0.5)", A7="=ROUND(3.14159,2.9)")
    eq(s.get("A1"), 3.0); eq(s.get("A2"), -3.0); eq(s.get("A3"), 1.01); eq(s.get("A4"), 1200.0); eq(s.get("A5"), 2.68); eq(s.get("A6"), 1.0); eq(s.get("A7"), 3.14)
def test_function_names_case():
    s = mk(A1="2", A2="=sum(a1, 3)", A3="=Round(2.5)")
    eq(s.get("A2"), 5.0); eq(s.get("A3"), 3.0)
def test_text_compare_case_insensitive():
    s = mk(A1="Apple", A2="=A1=\"apple\"", A3="=\"b\">\"A\"", A4="=Z1=\"\"", A5="=Z1=0")
    eq(s.get("A2"), True); eq(s.get("A3"), True); eq(s.get("A4"), True); eq(s.get("A5"), True)
def test_self_cycle():
    s = mk(A1="=A1+1"); eq(s.get("A1"), "#CYCLE!")
def test_range_cycle_and_propagation():
    s = mk(A1="1", A2="=SUM(A1:A3)", A3="2", B1="=A2*2")
    eq(s.get("A2"), "#CYCLE!"); eq(s.get("B1"), "#CYCLE!"); eq(s.get("A1"), 1.0)
def test_cycle_break_and_undo():
    s = mk(A1="=B1+1", B1="=C1+1", C1="=A1+1", D1="=C1")
    eq(s.get("A1"), "#CYCLE!"); eq(s.get("D1"), "#CYCLE!")
    s.set("C1", "5"); eq(s.get("A1"), 7.0); eq(s.get("B1"), 6.0); eq(s.get("D1"), 5.0)
    assert s.undo() is True; eq(s.get("B1"), "#CYCLE!"); eq(s.get("D1"), "#CYCLE!")
def test_no_stale_values():
    s = mk(A1="1", A2="=A1*10", A3="=A2+1")
    eq(s.get("A3"), 11.0); s.set("A1", "2"); eq(s.get("A3"), 21.0); s.set("A2", "=A1*100"); eq(s.get("A3"), 201.0)
def test_clear_and_undo():
    s = mk(A1="5", B1="=A1+1"); s.set("A1", "")
    eq(s.get_raw("A1"), None); eq(s.get("B1"), 1.0)
    assert s.undo(); eq(s.get_raw("A1"), "5"); eq(s.get("B1"), 6.0)
def test_undo_sequence():
    s = S(); s.set("A1", "1"); s.set("A1", "2"); s.set("A1", "3")
    assert s.undo() and s.get("A1") == 2.0
    assert s.undo() and s.get("A1") == 1.0
    assert s.undo() and s.get_raw("A1") is None
    assert s.undo() is False
def test_dependents():
    s = mk(A1="1", B1="=A1", C1="=B1*2", D1="=SUM(A1:A3)", E1="=D1", F1="=Z9")
    assert s.dependents("A1") == ["B1", "C1", "D1", "E1"], s.dependents("A1")
    assert s.dependents("A2") == ["D1", "E1"], s.dependents("A2")
    assert s.dependents("F1") == []
def test_dependents_sorted_row_col():
    s = mk(A1="1", B2="=A1", A3="=A1", C1="=A1", AA1="=A1")
    assert s.dependents("A1") == ["C1", "AA1", "B2", "A3"], s.dependents("A1")
def test_long_chain():
    s = S(); s.set("A1", "1")
    for i in range(2, 3001): s.set(f"A{i}", f"=A{i-1}+1")
    eq(s.get("A3000"), 3000.0)
    s.set("A1", "10"); eq(s.get("A3000"), 3009.0)
def test_long_chain_cycle():
    s = S()
    for i in range(1, 2001): s.set(f"B{i}", f"=B{i+1}" if i < 2000 else "=B1")
    eq(s.get("B1000"), "#CYCLE!")
def test_performance_block():
    s = S()
    for r in range(1, 201):
        s.set(f"A{r}", str(r))
        for c in "BCDEFGHIJ":
            prev = chr(ord(c) - 1)
            s.set(f"{c}{r}", f"={prev}{r}+{prev}{max(1, r-1)}")
    t0 = time.time(); v = s.get("J200"); dt = time.time() - t0
    assert isinstance(v, float) and dt < 1.0, (v, dt)
def test_column_order_aa():
    s = mk(Z1="1", AA1="2", AZ1="3", BA1="4", C2="=SUM(Z1:BA1)")
    eq(s.get("C2"), 10.0)
def test_csv_basic():
    s = mk(A1="1", B1="x", A2="=1/0", C2="=2.5")
    assert s.to_csv() == "1,x,\n#DIV/0!,,2.5", repr(s.to_csv())
def test_csv_quoting_and_empty():
    assert S().to_csv() == ""
    s = mk(A1='a,b', B1='say "hi"', A2="=\"line\"&\"\"")
    assert s.to_csv() == '"a,b","say ""hi"""\nline,', repr(s.to_csv())
def test_csv_reflects_edits():
    s = mk(A1="1", B1="=A1*2"); s.to_csv(); s.set("A1", "5")
    assert s.to_csv() == "5,10", repr(s.to_csv())

GROUPS = {
    "values": ["test_literals", "test_case_insensitive_refs", "test_invalid_refs_raise", "test_set_type_error", "test_empty_refs"],
    "grammar": ["test_precedence", "test_comparison_lowest", "test_whitespace_and_strings", "test_function_names_case"],
    "coercion": ["test_text_coercion_numbers", "test_bool_arithmetic", "test_text_compare_case_insensitive"],
    "errors": ["test_value_errors", "test_div0", "test_parse_errors", "test_name_and_ref_errors", "test_error_left_to_right"],
    "functions": ["test_if_lazy", "test_sum_range_skips", "test_range_any_corner_order", "test_min_max_average",
                  "test_count_skips_errors", "test_concat_range_order", "test_len_abs", "test_column_order_aa"],
    "round": ["test_round_exact"],
    "cycles": ["test_self_cycle", "test_range_cycle_and_propagation", "test_cycle_break_and_undo", "test_long_chain_cycle"],
    "recalc_undo": ["test_no_stale_values", "test_clear_and_undo", "test_undo_sequence"],
    "graph_scale": ["test_dependents", "test_dependents_sorted_row_col", "test_long_chain", "test_performance_block"],
    "csv": ["test_csv_basic", "test_csv_quoting_and_empty", "test_csv_reflects_edits"],
}
failed = set()
for n, f in list(globals().items()):
    if n.startswith("test_") and callable(f):
        before = len(details); t(n, f)
        if len(details) > before: failed.add(n)
gp = sum(1 for ts in GROUPS.values() if not any(x in failed for x in ts))
bad_groups = [g for g, ts in GROUPS.items() if any(x in failed for x in ts)]
# score unit = feature groups (a feature counts only if all its tests pass)
print(f"LG_RESULT {gp}/{len(GROUPS)}")
print(f"LG_DETAIL tests {passed}/{total}; broken: " + ",".join(bad_groups) + " | " + ";".join(details[:6]))
'''
