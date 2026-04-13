# core/ 目录 —— 仅3个文件实现完整桥接机制

这是核心底层实现逻辑，无打包、无需pip安装、无命令行工具（CLI）。

这3个文件对应完整包中的两个解耦层：

| 文件 | 行数 | 层级 | 完整包中等价模块 |
|---|---|---|---|
| `ramic_bridge.il` | 33 | Virtuoso 端 | `resources/ramic_bridge.il` |
| `ramic_daemon.py` | 90 | TCP 中继层 | `resources/ramic_bridge_daemon_*.py` |
| `bridge_client.py` | 40 | 客户端层 | `VirtuosoClient`（纯TCP实现） |

SSH隧道功能（对应完整包中的`SSHClient`）未包含在此处——需手动配置。

## 使用方法

```bash
# 1. 将守护进程文件复制到远程服务器
scp core/ramic_daemon.py 远程服务器地址:/tmp/

# 2. 在 Virtuoso CIW（命令交互窗口）中加载 IL 文件：
#    load("/tmp/ramic_bridge.il")
#    （该操作会自动在 65432 端口启动守护进程）

# 3. 建立 SSH 隧道（这是 SSHClient 会自动完成的操作）
ssh -N -L 65432:localhost:65432 远程服务器地址 &

# 4. 在本地机器执行 SKILL 命令
python core/bridge_client.py '1+2'
python core/bridge_client.py 'hiGetCurrentWindow()'
python core/bridge_client.py 'geGetEditCellView()~>cellName'
```

## 工作原理

```
本地机器                          远程 Virtuoso 服务器
────────────                      ──────────────────────

bridge_client.py                  Virtuoso 进程
(等价于 VirtuosoClient)               (等价于 ramic_bridge.il)
    │                                 │
    │ TCP 传输: {"skill":"1+2"}       │
    ├──── SSH 隧道 ────────────► ramic_daemon.py
    │     (等价于 SSHClient)         │
    │                                 │ 标准输出(stdout): "1+2"
    │                                 ├──► 执行 evalstring("1+2")
    │                                 │        │
    │                                 │        ▼
    │                                 │ 标准输入(stdin): "\x02 3 \x1e"
    │                                 ◄──┘
    │ TCP 回传: "\x02 3"              │
    ◄──── SSH 隧道 ─────────────┘
    │
    ▼
   输出结果 "3"
```

`core/` 目录仅用于理解底层实现机制。生产环境使用时，建议安装完整包（执行`pip install -e .`），该完整包新增了 SSHClient（自动SSH隧道、自动重连、文件传输）和 VirtuosoClient（版图/原理图API、Spectre仿真集成）等功能。


# `pip install -e .` 的功能和含义（超通俗讲解）
## 一、核心一句话总结
`pip install -e .` 是 **「可编辑模式安装」**（editable install），也叫**开发模式安装**。

它的作用：**把当前文件夹的代码，直接链接安装到 Python 环境里，修改代码会立刻生效，不用反复重装！**

---

## 二、拆解命令含义
```bash
pip install -e .
```
1. **`pip install`**：Python 包安装命令
2. **`-e`**：= `--editable`，**可编辑模式**（最关键）
3. **`.`**：代表**当前目录**（命令在哪个文件夹运行，就安装哪个文件夹里的 Python 包）

---

## 三、它到底做了什么？（和普通安装的区别）
### 1. 普通安装 `pip install .`
- 把代码**复制**一份到 Python 的 `site-packages` 目录
- 你**修改原代码不会生效**，必须重新安装才能更新
- 适合**最终用户使用**，不适合开发

### 2. 可编辑安装 `pip install -e .`
- 只创建一个**软链接/快捷方式**指向你的源码文件夹
- 你**直接修改源码，项目立刻就能用最新代码**
- 不用反复卸载、安装，**开发必备**

---

## 四、适用场景（你刚才的文档里为什么用它？）
你之前看到的：
> 生产环境使用时，建议安装完整包（执行`pip install -e .`）

原因：
1. 这个工具是**你需要本地修改、调试**的开发型包
2. 用 `-e` 安装后，你改代码、加功能**不用重新安装**
3. 能直接在环境里导入包、调用函数，非常方便

---

## 五、简单例子
假设你的项目结构：
```
my_project/
   setup.py       # 包配置文件（必须有这个才能用 pip install）
   my_module/
      __init__.py
      code.py
```

你在 `my_project/` 文件夹执行：
```bash
pip install -e .
```

✅ 结果：
- 全局/虚拟环境中可以直接 `import my_module`
- 修改 `my_module/code.py` 后，**立刻生效**
- 卸载也很简单：`pip uninstall my_module`

---

## 六、必须满足的条件
要使用 `pip install -e .`，当前文件夹**必须有**：
- `setup.py` 或 `pyproject.toml`
（这是 Python 包的配置文件，告诉 pip 这是一个可安装包）

---

### 总结
1. **`-e` = 可编辑、开发模式**
2. **`.` = 安装当前文件夹的包**
3. **核心好处：改代码立刻生效，不用反复重装**
4. **用途：开发自己的 Python 包、工具库时使用**