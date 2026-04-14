# 多行 SKILL 执行测试

## 功能概述

本脚本验证 `execute_skill()` 正确处理多行 SKILL 表达式的各种场景。

## 测试覆盖场景

### 1. 多行算术运算

```python
skill_cmd = """
let((result)
    result = (1
        +2
        +3)
    printf("\\n[Test 1] multiline arithmetic: %d\\n" result)
    result
)
"""
```

### 2. sprintf 多行字符串

```python
sprintf(nil "line1: %d\\nline2: %d\\nline3: %d" 10 20 30)
```

### 3. let 块 + 整行注释

```python
let((a b c)
    ; this is a comment
    a = 10
    b = 20
    ; another comment
    c = a + b
    ...
)
```

### 4. for 循环 + 注释

```python
for(i 1 10
    result = result + i
)
```

### 5. 列表操作

```python
mylist = '(1 2 3 4 5 6 7 8 9 10)
filtered = setof(x mylist (evenp x))
```

### 6. 字符串中的分号（不是注释）

```python
s = "hello; world; test"
n = strlen(s)  ; 返回 18，包含分号
```

### 7. 行内注释

```python
a = 100       ; first value
b = a * 2     ; double it
```

### 8. 过程定义和调用

```python
procedure(_vb_test_add(x y)
    let((result)
        result = x + y
        ...
    )
)
_vb_test_add(17 25)
```

## 测试结果格式

```
============================================================
Multi-line SKILL Tests
============================================================

  [PASS] multiline arithmetic
  [PASS] sprintf multiline string
  [PASS] let + full-line comments
  [PASS] for loop + comments
  [PASS] list filter
  [PASS] string with semicolons
  [PASS] inline comments
  [PASS] procedure def + call

8/8 passed
```

## 关键 SKILL 语法

| 语法 | 说明 |
|------|------|
| `let((var) ...)` | 局部变量绑定 |
| `for(var start end)` | 循环 |
| `procedure(name args) ...` | 函数定义 |
| `setof(x list condition)` | 列表过滤 |
| `sprintf(nil format args)` | 格式化字符串 |
| `;` | 注释（行注释） |

## 注意事项

- 分号在字符串内部**不是**注释
- 多行表达式可以正常换行
- 注释不影响表达式求值
