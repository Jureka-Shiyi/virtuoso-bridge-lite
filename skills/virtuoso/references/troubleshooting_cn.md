# 故障排除——已知的陷阱和坑

当某些事情意外失败时，在调试之前先在这个文件中搜索关键字（错误消息、函数名、症状）。

---

## SKILL / CIW

### `csh()` 返回 `t`/`nil`，不是命令输出
永远不要使用 `csh()` 或 `sh()` 来验证文件或读取命令输出。它们只返回成功/失败。对所有远程文件操作使用 `download_file`（SSH/SCP）。

### `procedurep()` 对编译函数返回 `nil`
像 `maeCreateNetlistForCorner` 这样的函数被编译成 .cxt——`procedurep()` 即使它们能工作也返回 nil。用错误参数调用来测试代替。

### `inst~>prop` 对 PDK 器件返回 nil
MOS 晶体管参数（W、L、nf、fingers、m）存储在 CDF 中，而不是原理图实例属性中。使用 `cdfGetInstCDF(inst)` 来读取它们：
```scheme
let((cdf)
  cdf = cdfGetInstCDF(inst)
  printf("W=%s L=%s nf=%s\n" cdf~>w~>value cdf~>l~>value cdf~>nf~>value))
```
`inst~>prop` 只对非 CDF 属性（如用户添加的注解）有效。

---

## GUI 对话框阻塞

### `simInitEnvWithArgs` 触发 GUI 对话框
如果运行目录已经存在，"Run Directory exists but has not been used in SE. Initialize?" 对话框会阻塞 CIW 事件循环——所有后续的 `execute_skill` 调用会挂起直到用户点击 OK。

**变通方法：** 每次使用新鲜（唯一）的目录名称，或在自动化流程中避免使用 `simInitEnvWithArgs`。

### Maestro 对话框阻塞 SKILL 通道
GUI 对话框（"Specify history name"、"No analyses enabled" 等）阻塞整个 CIW 事件循环。所有 `execute_skill` 调用会超时直到对话框被关闭。

**检测：** 如果 `maeWaitUntilDone` 返回空/nil，很可能是对话框在阻塞。

**恢复：**
```python
client.execute_skill("hiFormDone(hiGetCurrentForm())", timeout=5)
```
如果仍然卡住，用户必须在 Virtuoso 中手动关闭对话框。截图诊断：
```python
client.execute_skill('hiWindowSaveImage(?target hiGetCurrentWindow() ?path "/tmp/debug.png" ?format "png" ?toplevel t)')
client.download_file("/tmp/debug.png", "output/debug.png")
```

---

## 网表 / si

### 网表文件在远程上
`maeCreateNetlistForCorner` 写到远程文件系统。总是使用 `client.download_file()` 检索它们——不要尝试通过 SKILL 读取它们。

### si 输出位置
`si -batch -command nl` 输出到 `<runDir>/netlist`（单个文件）。但如果出了问题（例如 GUI 对话框阻塞），`spectre.inp` 可能几乎为空。下载后检查文件大小。

---

## Maestro / 设计变量

### `mae*` 函数未定义（`*Error* undefined function`）
旧版 Virtuoso 可能没有 `mae*` API。改用 `asi*` 等效函数。有关完整映射表，见 `maestro-skill-api.md` 中的 "asi\* Fallback" 部分。检测：`fboundp('maeRunSimulation)`。

### `maeGetSetup(?typeName "globalVar")` 可能返回 nil
使用 `asiGetDesignVarList(asiGetCurrentSession())` 作为回退。

### 全局 vs 测试级变量
`maeSetVar("f" "1G")` 设置一个**全局**变量。要设置测试级变量：
```python
client.execute_skill('maeSetVar("f" "1G" ?typeName "test" ?typeValue \'("IB_PSS"))')
```
如果测试有同名局部变量，它会覆盖全局变量。要删除测试级变量，使用 `axl*` API（见主技能文档）。

### 必须在 `maeRunSimulation` 之前 `maeSaveSetup`
跳过保存会导致陈旧状态——仿真用旧参数运行。总是先保存后运行。

---

## 连接 / 隧道

### 套接字在 30s 时超时
CIW 过载或对话框在阻塞。重试前检查 Virtuoso GUI 状态。

### 视图访问时 `OPEN_FAILED`
cellview 不存在或被另一个进程锁定。打开前用 `ddGetObj(lib cell view)` 验证。

### `.il line 16` SKILL 探针失败
RAMIC daemon 设置脚本加载失败。在 CIW 中重新运行 `load("/tmp/virtuoso_bridge_zhangz/setup.il")`。
