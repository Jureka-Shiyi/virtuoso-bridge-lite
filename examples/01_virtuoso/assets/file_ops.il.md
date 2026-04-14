# file_ops.il

## 功能概述

提供远程主机上的文件读写操作辅助函数。

## 函数列表

### `VbWriteFile(path content)`

将字符串内容写入远程主机文件。

```skill
VbWriteFile(path content)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | 字符串 | 目标文件路径 |
| `content` | 字符串 | 要写入的内容 |

**返回值**：
- 成功：`"ok"`
- 失败：`"ERROR: cannot write <path>"`

**实现**：
```skill
procedure(VbWriteFile(path content)
  prog((port)
    port = outfile(path "w")
    unless(port return(sprintf(nil "ERROR: cannot write %s" path)))
    fprintf(port "%s" content)
    close(port)
    return("ok")))
```

### `VbReadFile(path)`

读取远程主机文件内容。

```skill
VbReadFile(path)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | 字符串 | 要读取的文件路径 |

**返回值**：
- 成功：文件内容字符串
- 失败：`"ERROR: cannot read <path>"`

**实现**：
```skill
procedure(VbReadFile(path)
  prog((port line lines)
    port = infile(path)
    unless(port return(sprintf(nil "ERROR: cannot read %s" path)))
    lines = ""
    while(gets(line port)
      lines = strcat(lines line))
    close(port)
    return(lines)))
```

## 关键 SKILL 语法

| 语法 | 说明 |
|------|------|
| `outfile(path mode)` | 打开文件用于写入 |
| `infile(path)` | 打开文件用于读取 |
| `fprintf(port fmt args)` | 格式化输出到文件 |
| `gets(line port)` | 逐行读取，失败返回 nil |
| `close(port)` | 关闭文件 |
| `prog((vars) ...)` | 局部变量作用域 |

## 使用示例

```python
# 写入文件
client.execute_skill('VbWriteFile("/tmp/test.txt" "Hello World")')

# 读取文件
result = client.execute_skill('VbReadFile("/tmp/test.txt")')
print(result.output)
```

## 用途

- 在远程 Virtuoso 主机上读写文本文件
- 用于辅助 Python 端与 SKILL 端的数据交换
