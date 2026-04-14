# 并行仿真与任务管理

## 目录

- Fire-and-forget 使用 `submit()`
- 批量使用 `run_parallel()`
- 并发控制
- 多服务器仿真
- 任务管理 CLI（sim-jobs、sim-cancel）
- .env 配置

---

## Fire-and-forget 使用 `submit()`

`submit()` 立即返回 `Future`。仿真在后台线程中运行。

```python
sim = SpectreSimulator.from_env()

# 按需提交仿真——立即返回 Future
t1 = sim.submit(Path("tb_comparator.scs"), {"include_files": ["comp.va"]})
t2 = sim.submit(Path("tb_dac.scs"))

# 其他仿真运行时做其他工作...

# 非阻塞检查
if t1.done():
    result = t1.result()

# 阻塞等待特定仿真
result2 = t2.result()

# 在其他仿真仍在运行时提交更多
t3 = sim.submit(Path("tb_sar_logic.scs"))

# 等待一批
results = SpectreSimulator.wait_all([t1, t2, t3])
```

## 批量使用 `run_parallel()`

一次性提交全部，等待全部完成：

```python
results = sim.run_parallel([
    (Path("tb_comp.scs"), {"include_files": ["comp.va"]}),
    (Path("tb_dac.scs"), {}),
    (Path("tb_logic.scs"), {}),
], max_workers=5)
```

## 并发控制

```python
sim.set_max_workers(4)  # 默认是 8，根据许可证/CPU 限制调整
sim.shutdown()           # 拆除池，下次 submit 时创建新池
```

每个仿真使用独立的远程目录（基于 uuid）——无文件冲突。SSH ControlMaster 自动在线程间共享。

## 多服务器仿真

为每个配置创建独立的模拟器以跨机器分发工作：

```python
# .env 定义 VB_REMOTE_HOST_worker1, VB_REMOTE_HOST_worker2 等
sim1 = SpectreSimulator(remote=True, profile="worker1")
sim2 = SpectreSimulator(remote=True, profile="worker2")

t1 = sim1.submit(Path("tb_comp.scs"))
t2 = sim2.submit(Path("tb_dac.scs"))

results = SpectreSimulator.wait_all([t1, t2])
```

## 任务管理（CLI）

在终端监控和控制仿真：

```bash
# 显示所有任务：user@host、状态、时间、运行中任务的 CPU/MEM
virtuoso-bridge sim-jobs

# 取消正在运行的仿真（杀死远程 Spectre 进程）
virtuoso-bridge sim-cancel <job-id>
```

`sim-jobs` 输出：
```
Simulation Jobs: 2 running, 1 queued, 3 done, 0 failed

● a3f2c1d0  zhangz@zhangz-wei         tb_comp.scs              running  16:45:29 45s  CPU:98.2% MEM:3.1%
● b7e9a412  designer1@wei-worker1     tb_dac.scs               running  16:45:30 12s  CPU:45.7% MEM:1.8%
○ c4d5e6f7  zhangz@zhangz-wei         tb_logic.scs             queued   16:45:35 0s
✓ d8e9f012  zhangz@zhangz-wei         tb_bias.scs              done     16:44:10-16:44:25 15s
```

已完成的任务在 10 分钟后自动过期。

## .env 配置

`.env` 文件可以放在 virtuoso-bridge-lite 目录中或项目根目录中（当 virtuoso-bridge-lite 作为子目录克隆时推荐）。两个位置都会被自动搜索。

```dotenv
# 默认连接
VB_REMOTE_HOST=my-server
VB_REMOTE_USER=username
VB_REMOTE_PORT=65081
VB_LOCAL_PORT=65082
VB_CADENCE_CSHRC=/path/to/.cshrc.cadence

# 多服务器附加配置
VB_REMOTE_HOST_worker1=eda-node1
VB_REMOTE_USER_worker1=sim_user
VB_REMOTE_PORT_worker1=65432
VB_LOCAL_PORT_worker1=65433
```
