# Python 3.12 f-string with Chinese Characters

**Discovery date**: 2026-07-10 | **Debug time**: 30+ minutes

## Symptom

```python
f"""生成一张 matplotlib PNG(200dpi),记录实际执行路径:"""
```

Python 3.12 raises:
```
SyntaxError: invalid character '（' (U+FF08)
```
or
```
SyntaxError: invalid decimal literal
```

Even though the Chinese characters are **inside** the f-string literal text
(not in `{...}` expressions), Python 3.12's parser rejects them.

## Root Cause

Python 3.12 tightened rules around non-ASCII characters. When the f-string
body contains characters like `（` `）` `：` (full-width punctuation common
in Chinese text), the parser may misinterpret them as part of expression
syntax.

## Fix

Replace f-strings containing Chinese text with `.format()`:

```python
# BROKEN in Python 3.12:
instruction = f"""生成 {workspace}/flowcharts/chart.png"""

# FIXED:
instruction = """生成 {0}/flowcharts/chart.png""".format(workspace)
```

Also replace full-width punctuation with ASCII equivalents:
- `（` → `(`
- `）` → `)`
- `：` → `:`

## Detection

```bash
# Find files with Chinese in f-strings
cd path/to/project
grep -n "f\"\"\".*[一-龥].*\"\"\"" *.py
```

## Verification

After fixing, validate the file compiles:
```bash
"C:\...\python.exe" -c "exec(open('file.py', encoding='utf-8').read())"
```
