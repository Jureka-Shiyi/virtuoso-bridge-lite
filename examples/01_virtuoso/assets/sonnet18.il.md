# sonnet18.il

## 功能概述

在 Virtuoso CIW 中打印莎士比亚十四行诗第 18 首（Sonnet 18）。

## 打印内容

```
========================================================
  Sonnet 18  by William Shakespeare
========================================================

  Shall I compare thee to a summer's day?
  Thou art more lovely and more temperate:
  Rough winds do shake the darling buds of May,
  And summer's lease hath all too short a date:
  Sometime too hot the eye of heaven shines,
  And often is his gold complexion dimm'd;
  And every fair from fair sometime declines,
  By chance, or nature's changing course untrimm'd;
  But thy eternal summer shall not fade,
  Nor lose possession of that fair thou ow'st;
  Nor shall Death brag thou wander'st in his shade,
  When in eternal lines to Time thou grow'st:
    So long as men can breathe, or eyes can see,
    So long lives this, and this gives life to thee.

========================================================
```

## 代码结构

脚本使用多次 `printf()` 调用，每行一首诗一行输出。注意开头和结尾各有多个空行用于美化格式。

## 与 02_ciw_print.py 的对比

| 方式 | 实现 | 效率 |
|------|------|------|
| `sonnet18.il` | 加载后一次性打印全部 | 一次网络往返 |
| `02_ciw_print.py` | 逐行多次 `execute_skill()` | 多次网络往返 |

## 使用方法

```python
SONNET_IL = Path(__file__).parent.parent / "assets" / "sonnet18.il"
result = client.load_il(SONNET_IL)
```

## 用途

- 演示多行文本输出的简单方法
- 作为测试辅助脚本
