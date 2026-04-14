# harvest_library.il

## 功能概述

采集 Virtuoso 库的完整元数据，包括单元、视图、Maestro 设置和仿真结果路径。修复了以下问题：
1. 硬编码的 `"maestro"` 视图名 - 现在探测所有 session 类视图
2. SKILL nil 被当作真实数据 - 现在规范化处理
3. `ddGetObj(lib)->libPath` 不可靠 - 使用 fallback 链

## 函数列表

### 辅助函数

#### `HarvestIsSessionView(viewName)`

判断视图是否为 session 类型。

```skill
HarvestIsSessionView(viewName)
```

**匹配的视图前缀**：`"maestro"`, `"adexl"`, `"normVim"`, `"topsim"`, `"spectre"`

**返回值**：`t` 或 `nil`

---

#### `HarvestIsSchematicView(viewName)`

判断视图是否为 schematic 类型。

```skill
HarvestIsSchematicView(viewName)
```

**返回值**：匹配 `"^schematic"` 则返回 `t`

---

#### `HarvestIsConfigView(viewName)`

判断视图是否为 config 类型。

```skill
HarvestIsConfigView(viewName)
```

**返回值**：匹配 `"^config"` 则返回 `t`

---

#### `HarvestNormNil(val)`

规范化 SKILL 的 nil 值。

```skill
HarvestNormNil(val)
```

| 输入 | 输出 |
|------|------|
| `nil` | `""` |
| 字符串 `"nil"` | `""` |
| 其他值 | 原值 |

---

#### `HarvestNormNilList(val)`

规范化 SKILL 的 nil 列表值。

```skill
HarvestNormNilList(val)
```

| 输入 | 输出 |
|------|------|
| `nil` | `'()` |
| 其他值 | 原值 |

---

### 核心函数

#### `HarvestGetLibRoot(libName)`

解析库根目录路径。

```skill
HarvestGetLibRoot(libName)
```

**路径解析顺序**：
1. `libPath`
2. `writePath`
3. `readPath`

**返回值**：库根目录路径

---

#### `HarvestGetSessionViews(viewNames)`

从视图名列表中筛选 session 类视图。

```skill
HarvestGetSessionViews(viewNames)
```

**返回值**：匹配的视图名列表

---

#### `HarvestGetSchematicViews(viewNames)`

从视图名列表中筛选 schematic 类视图。

```skill
HarvestGetSchematicViews(viewNames)
```

**返回值**：匹配的视图名列表

---

#### `HarvestProbeSetups(libName cellName viewName)`

探测指定 cell/view 的 Maestro 设置。

```skill
HarvestProbeSetups(libName cellName viewName)
```

**返回值**：setup 信息字符串列表

---

#### `HarvestProbeResults(libRoot cellName viewName)`

检查仿真结果目录是否存在。

```skill
HarvestProbeResults(libRoot cellName viewName)
```

**返回值**：如果存在结果目录则返回 `t`

---

#### `HarvestCellInfo(libName cellName)`

采集单个 cell 的完整元数据。

```skill
HarvestCellInfo(libName cellName)
```

**返回值**：格式化的 cell 信息字符串

**输出格式**：
```
cell=ADC_CORE
  all_views=("schematic" "maestro" "layout")
  session_views=("maestro")
  schematic_views=("schematic")
  config_views=()
  [maestro]
    setup=AC analyses=("ac")
    setup=tran analyses=("tran")
    has_results=t
```

---

#### `HarvestLibrary(libName)`

采集整个库的完整元数据。

```skill
HarvestLibrary(libName)
```

**返回值**：格式化的库信息字符串

## 输出示例

```
========================================
[harvest] myLibrary
[harvest] root=/path/to/library
========================================
cell=INV
  all_views=("schematic" "symbol")
  session_views=()
  schematic_views=("schematic")
  config_views=()
cell=DFF
  all_views=("schematic" "maestro" "layout")
  session_views=("maestro")
  schematic_views=("schematic")
  [maestro]
    setup=AC analyses=("ac")
    has_results=t
========================================
```

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 库不存在 | 打印错误，返回空字符串 |
| 路径解析失败 | 打印警告，返回空字符串 |
| nil 值 | 规范化为空字符串或空列表 |

## 使用示例

```python
# 采集整个库
result = client.execute_skill(f'HarvestLibrary("{LIB}")')
print(result.output)

# 获取库根路径
lib_root = client.execute_skill(f'HarvestGetLibRoot("{LIB}")')
```

## 用途

- 批量导出库元数据
- 检查哪些 cell 有仿真结果
- 自动化测试流程中的库扫描
