# Spectre 网表语法参考

## 基本结构

每个 Spectre 网表遵循此骨架：

```spectre
simulator lang=spectre
global 0
include "/path/to/pdk/models/spectre/toplevel.scs" section=TOP_TT

// 电路定义（子电路、实例、源）
// ...

// 分析语句
// ...

// 保存语句
save VIN VOUT
saveOptions options save=selected
```

`save` + `saveOptions save=selected` 将输出限制为列出的信号——避免生成过大的 PSF 文件。

## 分析类型

### 瞬态（Transient）

```spectre
tran tran stop=3n errpreset=conservative
```

结果信号：`time`，加上你 `save` 的信号。结果在 `<raw_dir>/tran.tran`。

### 交流（AC）

```spectre
ac ac start=1 stop=10G dec=20
```

结果信号：`freq`，加上保存的信号（复数）。结果在 `<raw_dir>/ac.ac`。

### PSS（周期稳态）

```spectre
pss pss fund=1G harms=10 errpreset=conservative autotstab=yes saveinit=yes
```

结果信号：`time`，加上保存的信号（一个稳态周期）。结果在 `<raw_dir>/pss.td.pss`。

### Pnoise（周期噪声）

必须跟在 PSS 分析之后：

```spectre
pss pss fund=1G harms=10 errpreset=conservative autotstab=yes saveinit=yes

pnoise pnoise start=0 stop=500M pnoisemethod=fullspectrum \
    noisetype=sampled measurement=[pm0]
pm0 jitterevent trigger=[I4.LP I4.LM] triggerthresh=50m triggernum=1 \
    triggerdir=rise target=[I4.LP I4.LM]
```

结果信号：`freq`、`out`（噪声功率谱密度 V/sqrt(Hz)）。结果在 `<raw_dir>/pnoiseMpm0.0.sample.pnoise`。

## 实例语法

```spectre
// 无源器件
R0 (VIN VOUT) resistor r=1k
C0 (VOUT 0) capacitor c=10p

// 电压源
V0 (VIN 0) vsource type=dc dc=1.8

// 子电路实例
XI0 (IN OUT VDD VSS) my_subckt param1=value1
```

## 常用参数

| 参数 | 含义 |
|------|------|
| `errpreset=conservative` | 更严格的收敛容差 |
| `autotstab=yes` | 自动时间步长稳定（PSS） |
| `saveinit=yes` | 保存初始条件 |
| `maxiters=200` | 增加最大迭代次数以促进收敛 |

## 网表参数化

在模板网表中使用 `@@PARAM@@` 占位符，然后用 Python `str.replace()` 替换：

```spectre
// 在模板中
XI0 (IN OUT VDD VSS) nch w=@@W_INP@@ l=60n
```

```python
template = template.replace("@@W_INP@@", f"{value:.6g}")
```
