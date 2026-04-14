---
name: optimizer
description: "使用 TuRBO 或 scipy 对设计参数进行黑盒优化。当用户想要优化、调优、确定尺寸、扫描或探索设计空间以满足规格时触发。这包括电路尺寸确定（W/L、偏置、无源器件）、寻找最佳工作点、最小化功耗-延迟或噪声-功耗权衡，或任何需要搜索多个参数以达到目标的任务。当用户说「找到最佳尺寸」、「帮我调优这个」、「运行优化」、「什么值能给出最佳 FOM」或「扫描这些参数以满足规格」时也会触发。对于单变量参数扫描或解析计算，不要触发。"
---

# 优化器

## 这是什么

一个黑盒优化框架。你提供：
- 一组带边界的**参数**（例如晶体管宽度、偏置电流、电阻值）
- 一个**评估函数**，接收参数并返回性能指标
- 一个**目标函数**，将指标组合成要最小化的单个标量

优化器迭代选择参数值、评估它们，并向最优值收敛。它将评估视为黑盒——它不需要知道你是在运行 Spectre、Maestro、Python 模型还是其他任何东西。

## 何时使用

- **电路尺寸确定**——找到满足增益/带宽/噪声/功耗规格的 W/L、偏置电流、无源器件值
- **设计空间探索**——扫描手动调优或参数扫描无法处理的高维参数空间
- **多目标权衡**——最小化功耗-延迟积、噪声-功耗 FOM 等
- **任何昂贵的黑盒函数**——评估可能很慢（每个点秒到分钟级）；TuRBO 是样本高效的

## 何时不使用

- **单变量扫描**——直接使用 Maestro 中的参数扫描或 for 循环
- **存在解析解**——如果你能推导最优解，就不要搜索
- **< 5 次评估预算**——TuRBO 至少需要 `2 * n_params` 个初始样本

## 算法选择

| 情况 | 算法 | 原因 |
|------|------|------|
| ≤ 3 个参数，平滑 | `scipy.optimize.minimize` | 快速，无 GP 开销 |
| 3–20 个参数，噪声/昂贵 | TuRBO (`turbo.Turbo1`) | 带信任域的样本高效贝叶斯优化 |
| > 20 个参数 | 考虑随机搜索 + 细化 | GP 在约 20 维以上扩展性不好 |

## 前置条件

- TuRBO：`pip install torch gpytorch` 并本地安装 TuRBO (`pip install -e TuRBO/`)
  - TuRBO（信任域贝叶斯优化）来自 [uber-research/TuRBO](https://github.com/uber-research/TuRBO)
- scipy：包含在标准 Python 科学栈中

## 核心模式

```python
import numpy as np
from turbo import Turbo1

# 1. 定义参数和边界
PARAMS = ["W_tail", "W_inp", "R_load"]
LB = np.array([0.5, 0.5, 100.])
UB = np.array([10., 10., 5000.])

# 2. 目标函数：params → 标量（最小化）
def objective(x):
    try:
        result = evaluate(x, PARAMS)
    except Exception:
        return 1e6                     # 失败惩罚，永不用 nan/inf
    return compute_metric(result)

# 3. 运行
turbo = Turbo1(f=objective, lb=LB, ub=UB,
               n_init=2*len(LB), max_evals=100, batch_size=1)
turbo.optimize()
best = turbo.X[turbo.fX.argmin()]
```

## 评估后端

`evaluate()` 函数是唯一在不同用例之间变化的部分：

**Spectre 网表**——参数化 `.scs` 模板并远程运行：
```python
from virtuoso_bridge.spectre.runner import SpectreSimulator
sim = SpectreSimulator.from_env(work_dir="./opt", output_format="psfascii")

def evaluate(x, params):
    text = Path("tb_template.scs").read_text()
    for name, val in zip(params, x):
        text = text.replace(f"@@{name}@@", f"{val:.6g}")
    Path("opt/tb.scs").write_text(text)
    return sim.run_simulation(Path("opt/tb.scs"), {})
```

**Maestro**——设置设计变量并通过 SKILL 运行现有测试：
```python
from virtuoso_bridge import ramic_send

def evaluate(x, params):
    for name, val in zip(params, x):
        ramic_send(f'maeSetDesignVar("{name}" {val:.6g})')
    ramic_send('maeRunTest("myTest")')
    gain = float(ramic_send('maeGetTestResult("myTest" "gain_db")'))
    bw = float(ramic_send('maeGetTestResult("myTest" "bw_hz")'))
    return {"gain": gain, "bw": bw}
```

**任何 Python 可调用对象**：
```python
def evaluate(x, params):
    return my_model.predict(dict(zip(params, x)))
```

## 目标函数设计

返回 **标量 float**。失败时返回 `1e6`——永不用 `nan` 或 `inf`，因为这些会破坏 GP 代理模型并导致优化器发散。

| 目标 | 返回值 |
|------|--------|
| 最小化功耗-延迟 | `power * delay` |
| 最大化增益-带宽 | `-(gain_db + 20*log10(bw))` |
| 带约束 | `obj + 1e3 * max(0, noise - spec)**2` |

## 相关技能

- **spectre**——Spectre 仿真运行器、网表语法、结果解析
- **virtuoso**——Maestro 设置、原理图编辑、设计变量管理
