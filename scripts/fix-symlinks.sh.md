这个 Bash 脚本用于**在 Windows 系统上修复 Git 仓库中的符号链接问题**。

## 核心功能

将 Git 在 Windows 上存储为普通文本文件的"伪符号链接"转换为 Windows 原生的 **NTFS 交接点 (Junction)**。

## 工作原理

1. **检测系统平台**：只在 Windows (MINGW/MSYS 环境) 下执行，其他系统直接退出

2. **扫描 Git 索引**：通过 `git ls-files -s` 查找所有类型为 `120000` 的文件（这是 Git 中符号链接的标记）

3. **识别损坏的符号链接**：读取文件内容，如果内容是 `../*` 或 `./*` 格式的相对路径，说明这是一个未被正确处理的符号链接

4. **解析目标路径**：将相对路径转换为绝对路径，并验证目标是否存在且为目录

5. **创建交接点**：
   - 删除原来的文本文件
   - 使用 Windows 的 `mklink /J` 命令创建 NTFS 交接点
   - 不需要管理员权限，也不需要开启开发者模式

## 使用场景

- 在 Windows 上通过 `git clone`（未启用 `core.symlinks`）后，符号链接被保存为普通文本文件
- 需要让这些符号链接在 Windows 文件系统中正常工作

## 使用方法

```bash
bash scripts/fix-symlinks.sh
```

## 输出示例

- 成功：`OK: path/to/link -> target/path`
- 跳过（目标不是目录）：`SKIP: ... (target not a directory)`
- 统计：`Fixed X symlink(s).`

这个脚本解决了跨平台开发中 Windows 和 Linux/macOS 之间符号链接不兼容的常见问题。


## NTFS 交接点 (Junction) 详解

**NTFS 交接点**是 Windows NTFS 文件系统的一种特殊功能，允许在文件系统中的一个位置**指向另一个目录**，类似于 Unix/Linux 中的**目录符号链接**。

## 核心特征

### 1. 工作原理
```
C:\Projects\Current → C:\Projects\v2024\build
```
- 访问 `C:\Projects\Current` 实际会重定向到 `C:\Projects\v2024\build`
- 对应用程序完全透明，看起来就像一个普通目录

### 2. 与符号链接的对比

| 特性 | NTFS 交接点 (Junction) | NTFS 符号链接 (Symlink) |
|------|------------------------|------------------------|
| **支持目标** | 仅目录 | 文件和目录 |
| **跨卷** | 仅同一卷（同一分区） | 可以跨卷 |
| **网络路径** | 不支持 | 支持 (需要启用) |
| **权限要求** | 无需特殊权限 | 需要开发者模式或管理员 |
| **创建命令** | `mklink /J` | `mklink /D` (目录)<br>`mklink` (文件) |
| **Windows 版本** | Windows 2000+ | Windows Vista+ |

## 为什么这个脚本选择交接点？

### 优势
1. **无需管理员权限**：普通用户即可创建
2. **无需开发者模式**：Windows 10/11 默认允许
3. **兼容性好**：从 Windows 2000 就开始支持
4. **适合 CI/CD**：在自动化构建环境中更容易使用

### 局限性
1. **只支持目录**：这就是为什么脚本会跳过指向文件的符号链接
2. **不能跨分区**：只能在同一个磁盘卷内
3. **不支持网络路径**：不能指向 `\\server\share`

## 实际示例

### 创建交接点
```cmd
# Windows 命令提示符
mklink /J C:\MyLink C:\Real\Target\Directory

# 输出: 为 C:\MyLink <<===>> C:\Real\Target\Directory 创建的联接
```

### 在 PowerShell 中
```powershell
# PowerShell 使用 cmd /c 调用
cmd /c mklink /J C:\MyLink C:\Real\Target\Directory
```

### 查看交接点
```cmd
# 使用 dir 命令，会显示 <JUNCTION> 标记
dir C:\
# 输出: 2024-01-01  10:00    <JUNCTION>     MyLink [C:\Real\Target\Directory]
```

## 底层实现

### 文件系统层面
- 交接点是一个**重解析点 (Reparse Point)**
- 在 NTFS MFT（主文件表）中有一个特殊标记
- 包含一个指向目标路径的缓冲区
- 文件系统驱动在访问时自动重定向

### 数据结构
```
NTFS 属性：
- 重解析点标记: IO_REPARSE_TAG_MOUNT_POINT (0xA0000003)
- 重解析数据缓冲区: 包含目标路径（UTF-16 编码）
- 其他属性: 标准信息、文件名等
```

## 与其他 Windows 链接类型的区别

```bash
# 1. 硬链接 (Hard Link)
# 同一文件的不同名称，共享相同的数据
fsutil hardlink create new.txt existing.txt

# 2. 符号链接 (Symbolic Link)
# 指向文件或目录的指针
mklink link.exe target.exe  # 文件
mklink /D link_dir target_dir  # 目录

# 3. 交接点 (Junction)
# 仅指向目录，不能跨卷
mklink /J link_dir target_dir

# 4. 快捷方式 (Shortcut .lnk)
# Shell 层面的链接，不是文件系统原生的
# 需要 Shell 解析，应用程序需要特殊处理
```



## 1. 脚本头部和配置

```bash
#!/bin/bash
# fix-symlinks.sh — Fix git symlinks on Windows (creates NTFS junctions)
#
# On Windows, git clone with core.symlinks=false stores symlinks as plain
# text files containing the target path. This script replaces them with
# NTFS junctions, which need no admin rights and no Developer Mode.
#
# Usage:  bash scripts/fix-symlinks.sh

set -e
```

- `#!/bin/bash`：Shebang，指定用 bash 执行
- `set -e`：**错误即退出** - 任何命令返回非零状态码时脚本立即退出，防止级联错误

## 2. 确定仓库根目录

```bash
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
```

这是一个巧妙的路径解析：
- `$0`：脚本自身的路径（如 `scripts/fix-symlinks.sh`）
- `dirname "$0"`：获取脚本所在目录（`scripts/`）
- `/..`：回到上一级目录（仓库根目录）
- `cd ... && pwd`：切换到该目录并打印绝对路径

**示例**：如果脚本在 `/home/user/project/scripts/fix-symlinks.sh`，则 `REPO_ROOT=/home/user/project`

## 3. 平台检测函数

```bash
is_windows() {
    [[ "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]
}
```

- `uname -s`：打印系统内核名称
- `MINGW*`：MinGW（Minimalist GNU for Windows）环境
- `MSYS*`：MSYS（Minimal SYStem）环境
- 这两个是 Windows 上常见的类 Unix 环境（Git Bash、Cygwin 的变体）

## 4. 非 Windows 系统快速退出

```bash
if ! is_windows; then
    echo "Not on Windows — symlinks should work natively, nothing to do."
    exit 0
fi
```

- 在 Linux/macOS 上，Git 原生支持符号链接，无需处理
- `exit 0`：正常退出，不报错

## 5. 初始化计数器

```bash
fixed=0
```

记录成功修复的符号链接数量

## 6. 主循环：扫描并处理符号链接

```bash
while IFS= read -r entry; do
    # ... 处理逻辑
done < <(git -C "$REPO_ROOT" ls-files -s | awk '$1 == "120000" {print $NF}' |
         while read -r f; do echo "$REPO_ROOT/$f"; done)
```

这是一个**进程替换**（Process Substitution）结构：
- `<(...)`：将内部命令的输出作为文件传递给 `while` 循环
- 这样做的好处是循环变量在子 shell 中修改后能保留（相比管道 `|`）

**内部命令详解**：

```bash
git -C "$REPO_ROOT" ls-files -s
```
- `-C`：切换到仓库目录执行
- `ls-files -s`：显示索引（staging area）中所有文件，带模式位信息

输出格式示例：
```
100644 7b9f0c3... 0       README.md
120000 a1b2c3d... 0       docs/symlink
100755 4d5e6f7... 0       script.sh
```

其中第一列是文件模式：
- `100644`：普通文件
- `100755`：可执行文件
- `120000`：**符号链接**（关键标识）

```bash
awk '$1 == "120000" {print $NF}'
```
- `$1`：第一列（模式）
- `$NF`：最后一列（文件名，相对于仓库根目录）
- 只输出符号链接的文件名

```bash
while read -r f; do echo "$REPO_ROOT/$f"; done
```
- 读取每个相对路径的文件名
- 拼接绝对路径并输出

最终，`while IFS= read -r entry` 会逐行接收这些绝对路径。

## 7. 文件类型检查

```bash
[[ -f "$entry" ]] || continue          # only plain files (broken symlinks)
```

- `-f`：判断是否为普通文件（不是目录、不是设备文件等）
- `|| continue`：如果不是文件就跳过
- 正常符号链接在 Windows 上被 Git 存储为**包含目标路径的文本文件**

## 8. 读取符号链接目标

```bash
target="$(cat "$entry")"
```

读取文件内容，这应该是目标路径（如 `../../other/file`）

## 9. 验证路径格式

```bash
# Skip if content doesn't look like a relative path
[[ "$target" == ../* || "$target" == ./* ]] || continue
```

- 只处理相对路径的符号链接
- 支持 `../*`（上级目录）和 `./*`（当前目录）
- 绝对路径或其他格式跳过

## 10. 解析绝对路径（核心逻辑）

```bash
link_dir="$(dirname "$entry")"
```

获取符号链接文件所在的目录

```bash
abs_target="$(cd "$link_dir" && cd "$(dirname "$target")" 2>/dev/null && pwd)/$(basename "$target")" || continue
```

这是一个**分步路径解析**：

**分解**：
1. `cd "$link_dir"`：切换到符号链接所在目录
2. `cd "$(dirname "$target")"`：切换到目标路径的父目录
   - 例如：`target="../../lib/foo"` → `dirname` 是 `../../lib`
3. `&& pwd`：获取这个目录的绝对路径
4. `/$(basename "$target")"`：拼接目标文件名

**示例**：
```
entry = /home/project/docs/link.txt
target = ../data/file.txt

link_dir = /home/project/docs
dirname(target) = ..
cd .. → /home/project
pwd → /home/project
basename(target) = file.txt
abs_target = /home/project/file.txt
```

- `2>/dev/null`：隐藏错误输出（如 cd 失败）
- `|| continue`：解析失败则跳过

## 11. 验证目标类型

```bash
if [[ ! -d "$abs_target" ]]; then
    echo "SKIP: $entry -> $target (target not a directory)"
    continue
fi
```

- **重要限制**：NTFS 交接点（Junction）**只能指向目录**，不能指向文件
- 如果目标不是目录就跳过（不能修复指向文件的符号链接）

## 12. 转换为 Windows 路径格式

```bash
win_link="$(cygpath -w "$entry")"
win_target="$(cygpath -w "$abs_target")"
```

- `cygpath -w`：将 Unix 风格路径转换为 Windows 风格
- 示例：`/home/project/docs` → `C:\home\project\docs`
- `mklink` 命令需要 Windows 路径格式

## 13. 创建交接点

```bash
rm "$entry"
cmd //c "mklink /J $win_link $win_target" > /dev/null
```

- `rm "$entry"`：删除原来的文本文件
- `cmd //c`：调用 Windows 命令解释器执行（`//c` 是因为在 Git Bash 中需要转义）
- `mklink /J`：创建目录交接点（Junction）
  - `/J`：Junction（目录链接）
  - 不需要管理员权限（相比符号链接需要开发者模式）
- `> /dev/null`：隐藏 mklink 的输出信息

## 14. 计数和输出

```bash
echo "  OK: $entry -> $target"
((fixed++)) || true
```

- `((fixed++))`：Bash 算术运算，变量加 1
- `|| true`：防止当 `fixed` 从 0 增加到 1 时，算术表达式返回 1（失败状态）导致 `set -e` 触发退出
  - 在 Bash 中，`((0++))` 返回 1（因为结果是 0）
  - 添加 `|| true` 确保总返回成功状态

## 15. 最终报告

```bash
if [[ $fixed -eq 0 ]]; then
    echo "Nothing to fix — all symlinks are already resolved."
else
    echo "Fixed $fixed symlink(s)."
fi
```

根据修复数量输出不同的提示信息。

## 关键技术点总结

| 技术 | 用途 |
|------|------|
| `set -e` | 错误时立即退出 |
| 进程替换 `<(...)` | 保持循环内变量修改有效 |
| `git ls-files -s` | 获取 Git 索引中的文件模式 |
| `awk '$1 == "120000"'` | 筛选符号链接 |
| `cd ... && pwd` | 解析相对路径为绝对路径 |
| `cygpath -w` | Unix → Windows 路径转换 |
| `cmd //c mklink /J` | 创建 NTFS 交接点 |
| `((fixed++)) \|\| true` | 安全的算术增量 |

## 局限性

1. **只能处理目录**：NTFS 交接点不支持文件链接
2. **需要 Git Bash 环境**：依赖 `cygpath` 和 `uname` 命令
3. **只处理相对路径**：绝对路径的符号链接会被忽略