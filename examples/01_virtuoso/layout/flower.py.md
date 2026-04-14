# 在 Virtuoso 布局中绘制花朵

## 功能概述

这是一个趣味性示例，演示如何使用 LayoutEditor API 在 Virtuoso 布局中绘制一朵几何花朵，包括：
- 8 个花瓣（使用椭圆近似多边形）
- 中心圆形
- 茎干（路径）
- 两片叶子
- 标签

## 使用方法

```bash
python flower.py <LIB>
```

## 代码逻辑解析

### 花朵参数

```python
N_PETALS = 8              # 8 个花瓣
PETAL_A = 3.5            # 椭圆长半轴
PETAL_B = 1.2            # 椭圆短半轴
PETAL_D = 3.2            # 花瓣中心距原点的距离
CENTER_R = 1.8           # 中心圆半径
```

### 椭圆多边形近似

```python
def ellipse_pts(cx, cy, a, b, angle, n=28):
    """多边形近似椭圆"""
    pts = []
    for i in range(n):
        phi = 2 * math.pi * i / n
        x = cx + a * math.cos(phi) * math.cos(angle) - b * math.sin(phi) * math.sin(angle)
        y = cy + a * math.cos(phi) * math.sin(angle) + b * math.sin(phi) * math.cos(angle)
        pts.append((round(x, 3), round(y, 3)))
    return pts
```

### 花朵结构

```
         CODE<0> ──────────────────────
           CODE<1> ────────────────────
  Leaf       CODE<2> ─────────────────
      \       CODE<3> ───────────────
       \                    Center
        \       CODE<4> ───────────
         \       CODE<5> ─────────
           CODE<6> ───────────
             CODE<7> ─────────
                    |
                    | Stem
                    |
```

### 创建花瓣

```python
for i in range(N_PETALS):
    angle = math.pi * 2 * i / N_PETALS
    cx = PETAL_D * math.cos(angle)
    cy = PETAL_D * math.sin(angle)
    pts = ellipse_pts(cx, cy, PETAL_A, PETAL_B, angle)
    layer, purpose = PETAL_LAYERS[i % 2]  # 交替使用 M3 和 M4
    layout.add(polygon(layer, purpose, pts))
```

### 创建茎和叶子

```python
# 茎
layout.add(path(*STEM_LAYER, [(0.0, -4.8), (0.0, -14.5)], width=0.6))

# 左叶
leaf_l = ellipse_pts(-2.2, -8.5, 2.6, 0.85, math.radians(135), n=24)
layout.add(polygon(*LEAF_LAYER, leaf_l))

# 右叶
leaf_r = ellipse_pts(2.2, -11.5, 2.6, 0.85, math.radians(45), n=24)
layout.add(polygon(*LEAF_LAYER, leaf_r))
```

### 适用层

| 元素 | 层 |
|------|-----|
| 花瓣 | M3, M4（交替） |
| 中心圆 | M5 |
| 茎 | M1 |
| 叶子 | M2 |
| 标签 | M1 |

## 布局操作 API 综合使用

本示例展示了多个 LayoutEditor API 的综合运用：
- `layout_create_polygon` - 花瓣、叶子、中心圆
- `layout_create_path` - 茎干
- `layout_create_label` - 文字标签
- `layout_fit_view` - 自动适应视图

## 前置条件

- `virtuoso-bridge start` 已运行
- RAMIC daemon 已加载到 Virtuoso CIW
