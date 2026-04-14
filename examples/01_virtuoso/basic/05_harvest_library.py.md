# 采集库元数据

## 功能概述

本脚本从 Virtuoso 库中采集完整的元数据，包括：
- 库根目录
- 所有单元（cells）
- 所有视图（views）
- Maestro session 视图
- 原理图视图
- 每个 session 的测试设置和结果路径

## 使用方法

```bash
# 采集单个库的元数据
python 05_harvest_library.py NEX_ADC_export

# 保存 JSON 输出到指定目录
python 05_harvest_library.py NEX_ADC_export -o out
```

## 核心函数

### `harvest_library()`

```python
def harvest_library(client: VirtuosoClient, lib_name: str) -> dict:
    # 1. 获取库根目录
    lib_root = decode_skill(r.output)

    # 2. 获取所有单元
    cells = _skill_list(r.output)

    # 3. 遍历每个单元，获取视图信息
    for cell_name in cells:
        # 获取所有视图
        all_views = _skill_list(r.output)

        # 分类视图：session views / schematic views
        session_views = _skill_list(r.output)
        schematic_views = _skill_list(r.output)

        # 探测每个 session view 的设置
        setups_info = ...
```

### SKILL 列表解析

```python
def _skill_list(raw: str) -> list[str]:
    """将 SKILL 列表如 '("maestro" "adexl")' 解析为 Python 列表"""
    text = (raw or "").strip().strip('"')
    if not text or text == "nil":
        return []
    text = text.strip("()")
    return [m.group(1) for m in re.finditer(r'"([^"]*)"', text)]
```

## 输出结构

```json
{
  "library": "NEX_ADC_export",
  "root": "/path/to/library",
  "cells": {
    "ADC_CORE": {
      "all_views": ["schematic", "maestro", "layout"],
      "session_views": ["maestro"],
      "schematic_views": ["schematic"],
      "sessions": {
        "maestro": {
          "setups": ["test1: ac", "test2: tran"],
          "has_results": true
        }
      }
    }
  }
}
```

## 特殊处理

### 1. 非标准 Session 视图

处理使用非标准 session 视图（如 `adexl`, `maestro2`）的库。

### 2. nil 响应规范化

```python
if not text or text == "nil":
    return []
```

### 3. 库路径解析

通过 fallback 链解析库根目录，处理不同配置下的路径问题。

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
- `assets/harvest_library.il` 存在（包含 HarvestGetLibRoot 等辅助函数）
