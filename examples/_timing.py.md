# 计时辅助函数

## 功能概述

提供 CLI 示例中常用的计时和结果打印辅助函数。

## 核心函数

### `timed_call()`

```python
def timed_call(fn: Callable[[], T]) -> tuple[float, T]:
    start = time.perf_counter()
    value = fn()
    return time.perf_counter() - start, value
```

执行函数并返回 **(耗时, 结果)** 元组。

**使用示例**：
```python
elapsed, result = timed_call(lambda: client.execute_skill("1+2"))
print(f"执行耗时: {elapsed:.3f}s")
```

### `format_elapsed()`

```python
def format_elapsed(seconds: float) -> str:
    return f"{seconds:.3f}s"
```

格式化时间显示，保留三位小数。

### `print_elapsed()`

```python
def print_elapsed(label: str, seconds: float) -> None:
    print(f"[elapsed] {label}: {format_elapsed(seconds)}")
```

打印带标签的耗时信息。

### `decode_skill()`

```python
def decode_skill(raw: str) -> str:
    from virtuoso_bridge import decode_skill_output
    return decode_skill_output(raw)
```

解码 SKILL 字符串返回值。

### `print_load_il()`

```python
def print_load_il(result: object) -> None:
    meta = result.metadata
    print(f"[load_il] {'uploaded' if meta.get('uploaded') else 'cache hit'}"
          f"  [{format_elapsed(result.execution_time or 0.0)}]")
```

打印 `load_il()` 结果，包含是否上传或缓存命中。

### `print_execute()`

```python
def print_execute(label: str, result: object) -> None:
    print(f"[{label}] [{format_elapsed(result.execution_time or 0.0)}]")
```

打印带标签的执行结果。

### `print_result()`

```python
def print_result(result: object) -> None:
    """Print output and errors from a VirtuosoResult."""
    output = result.output
    errors = result.errors or []
    if output:
        print(output)
    for e in errors:
        print(f"[error] {e}")
```

打印 VirtuosoResult 的输出和错误。

## 使用模式

典型使用模式：
```python
from _timing import format_elapsed, timed_call, decode_skill

# 计时执行
elapsed, result = timed_call(lambda: client.execute_skill("1+2"))
print(f"[execute_skill] [{format_elapsed(elapsed)}]")
print(decode_skill(result.output or ""))

# load_il
elapsed, load_result = timed_call(lambda: client.load_il(IL_FILE))
print(f"[load_il] {'uploaded' if load_result.metadata.get('uploaded') else 'cache hit'}  [{format_elapsed(elapsed)}]")
```

## 前置条件

本模块是辅助模块，被其他示例调用。
