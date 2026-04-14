# 清除所有布线形状

## 功能概述

本示例演示如何清除当前布局中所有 routing 形状（走线），同时**保留实例**（晶体管、电容等）。

## 使用方法

```bash
# 先在 Virtuoso 中打开一个布局
python 08_clear_routing.py
```

## 代码逻辑解析

### 调用清除路由

```python
result = client.layout.clear_routing(timeout=30)
print(f"[layout.clear_routing] [{format_elapsed(elapsed)}]")
print(decode_skill(result.output or ""))
```

## 与其他清除操作的对比

| 函数 | 作用 | 保留实例 |
|------|------|---------|
| `clear_routing()` | 清除所有走线 shapes | 是 |
| `clear_current()` | 清除所有可见图元 | 否 |
| `delete_shapes_on_layer()` | 清除指定层 | 是 |

## Routing Shapes 包含

- 金属路径 (paths)
- 多层过孔 (vias)
- 总线 (bus)
- 标签 (labels on routing layers)

## 适用场景

- 重新开始布线
- 清理测试结构
- 批量修改前准备

## 前置条件

- Virtuoso中有打开的布局视图
- `virtuoso-bridge start` 已运行
