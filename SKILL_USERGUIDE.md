[TOC]










evalstring (字符串)= 把字符串里的内容，当成 SKILL 代码直接执行= 相当于动态执行代码最基础例子.
```
evalstring("1+2")      ; 返回 3
evalstring("printf(\"hello\")")  ; 打印 hello
```

---


# `procedure` 在 Cadence Skill 中的用法
在 SKILL 语言中，`procedure` 是定义**函数（过程）**的最核心关键词，相当于 C 语言中的 `void/int func()` 或 Python 中的 `def`。

以下是关于 `procedure` 用法、语法结构及进阶特性的详细介绍：

### 1. 基本语法结构

```skill
procedure( 函数名( 参数1 参数2 ... )
    ; 函数体：具体的逻辑代码
    let( (变量)
        ...代码...
    )
    ; 返回值：最后一个表达式的结果即为函数返回值
)
```

**示例：**
```skill
procedure( AddTwoNumbers(a b)
    a + b
)

; 调用函数
AddTwoNumbers(5 10) ; 返回 15
```

---

### 2. 局部变量管理（配合 `let`）

在 `procedure` 内部，强烈建议使用 `let` 来定义**局部变量**。如果不使用 `let`，在函数内赋值的变量会变成**全局变量**，这可能会污染环境并导致难以排查的 Bug。

```skill
procedure( CalculateArea(radius)
    let( (pi area)    ; 定义局部变量 pi 和 area
        pi = 3.14159
        area = pi * radius * radius
        area          ; 最后一个值作为返回值
    )
)
```

---

### 3. 参数的高级用法

SKILL 的 `procedure` 支持非常灵活的参数定义，这在编写复杂的工具时非常有用：

#### **A. 默认参数 (Optional Arguments)**
使用 `@optional` 关键字。如果调用时不传该参数，它默认为 `nil`（或者你可以手动赋默认值）。
```skill
procedure( GreetUser(name @optional (title "Mr/Ms"))
    printf("Hello, %s %s\n" title name)
)
GreetUser("Smith")          ; 输出: Hello, Mr/Ms Smith
GreetUser("Alice" "Dr.")    ; 输出: Hello, Dr. Alice
```

#### **B. 剩余参数 (Rest Arguments)**
使用 `@rest` 关键字，将多余的参数收集到一个列表中。
```skill
procedure( SumAll(first @rest others)
    let( (total)
        total = first
        foreach(num others total = total + num)
        total
    )
)
SumAll(1 2 3 4) ; 返回 10
```

#### **C. 关键字参数 (Keyword Arguments)**
使用 `@key` 关键字，模仿类似 Python 的 `key=value` 调用方式。
```skill
procedure( CreateRect(@key (width 1.0) (height 1.0))
    printf("Width: %f, Height: %f\n" width height)
)
CreateRect(?height 2.5 ?width 5.0) ; 使用 ? 开头指明参数名
```

---

### 4. 关键特性与注意事项

* **返回值**：SKILL 函数不需要 `return` 语句。函数体内**最后一个执行的表达式的结果**会自动返回。如果你需要中途退出，可以使用 `return()`（但通常配合 `prog` 使用）。
* **大小写敏感**：`AddTwo` 和 `addtwo` 是两个不同的函数。
* **符号绑定**：`procedure` 实际上是将一段代码逻辑绑定到一个符号（Symbol）上。你可以通过 `getd('函数名)` 来查看该函数是否已定义。
* **覆盖定义**：如果你在 CIW 中重新输入同名的 `procedure`，旧的定义会被直接覆盖，无需重启 Virtuoso。

---

### 5. 实际案例解析
回到你之前的脚本中：
```skill
procedure( RBIpcDataHandler(ipcId data)
  let((result)
    if(errset(result = evalstring(data)) then
      ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 2 result 30))
    else
      ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 21 errset.errset 30))
    )
  )
)
```
* **函数名**：`RBIpcDataHandler`
* **参数**：`ipcId` (进程句柄) 和 `data` (接收到的字符串)。
* **逻辑**：它定义了一个局部变量 `result`，尝试解析并执行 `data`，然后根据执行成功与否给外部进程回传不同的响应。


# Cadence Skill 脚本：`sprintf(nil "%c%L%c" 2 result 30)` 完整解析
---

## 1. 核心函数：`sprintf`
SKILL 里的 `sprintf` = **格式化字符串生成函数**
语法：
```skill
sprintf( 目标变量 "格式化模板" 参数1 参数2 参数3 ... )
```
- 第一个参数 `nil`：**不把结果存入变量**，直接返回拼接后的字符串
- 中间是**格式化占位符**
- 后面是要填充的参数

---

## 2. 格式化占位符含义
`"%c%L%c"` 里有 3 个占位符，对应后面 3 个参数：

| 占位符 | 含义 |
|--------|------|
| `%c`   | 按 **ASCII 字符** 输出（把数字转成对应字符） |
| `%L`   | 按 SKILL 原生格式输出（自动识别类型：字符串/数字/列表） |

---

## 3. 逐段拆解整行代码
```skill
sprintf(nil "%c%L%c" 2 result 30)
```

### ① `2` → `%c`
- `2` 是 ASCII 码
- 对应字符：**STX（文本开始符）**
作用：标记一段数据的**开头**

### ② `result` → `%L`
- 把变量 `result` 的值**原样格式化输出**
- `result` 可以是：数字、字符串、列表、坐标等
- `%L` 会自动适配它的类型

### ③ `30` → `%c`
- `30` 是 ASCII 码
- 对应字符：**RS（记录分隔符）**
作用：标记一段数据的**结尾/分隔**

---

## 4. 最终效果（举例）
假设 `result = 12345`
整行执行后会生成字符串：
```
[STX]12345[RS]
```

如果 `result = "abc"`
生成：
```
[STX]abc[RS]
```

> 这两个特殊字符 `STX(2)` 和 `RS(30)` 是**不可见控制字符**，不会显示在界面上，但程序可以识别它们作为数据的起止标记。

---

## 5. 这段代码的实际用途
在 Cadence SKILL 中，这种写法**非常典型**，通常用于：
1. **给数据加包头包尾**，方便程序解析一段完整数据
2. **日志/调试输出**，区分不同数据段
3. **与外部工具通信**时的协议格式

---
在 Cadence Skill 语言中，表示不同进制的数字非常直观，主要通过添加特定的**前缀**来实现。

下表是 Skill 支持的四种常见进制表示法，其中八进制与之前提到的 `\036` 规则一致，同样使用数字 `0` 作为前缀：

| 进制 | 前缀 | 有效字符 | 示例 | 对应的十进制值 |
| :--- | :--- | :--- | :--- | :--- |
| **十进制** | 无 | 0-9 | `123` | `123` |
| **二进制** | `0b` 或 `0B` | 0, 1 | `0b0011` | `3` |
| **八进制** | `0` (数字零) | 0-7 | `011` | `9` |
| **十六进制** | `0x` 或 `0X` | 0-9, A-F, a-f | `0x11` | `17` |
> **注意**：八进制的前缀是**数字0**，而不是字母O。

除了不同进制，Skill 语言为了便于 IC 设计，还支持直接在数字后使用**数量级单位**（如 `u`, `n`, `p`, `k`, `M`, `G` 等）。例如：


你观察得很仔细！在代码中出现了 `errset.errset`，这看起来有点奇怪。让我解释一下：

# `errset` 在 Cadence Skill 中的用法

### 1. **标准用法：`errset(expression)`**

`errset` 是一个错误捕获函数，它的返回值是**一个列表**：

```skill
; 正常执行
result = errset(2 + 2)      ; 返回 (4)

; 发生错误
result = errset(abc + 2)    ; 返回 nil，错误信息存储在系统变量 errset 中
```

### 2. **关键点：`errset` 既是函数又是变量**

- **函数**：`errset(expr)` - 执行表达式并捕获错误
- **全局变量**：`errset` - 存储最后一次 `errset` 捕获的错误信息

```skill
; 当 errset 捕获到错误时
errset(nonExistentFunc(10))  ; 返回 nil
println(errset)              ; 输出类似: ("*Error* eval: undefined function - nonExistentFunc")
```

### 3. **你代码中的 `errset.errset`**

```skill
if(errset(result = evalstring(data)) then
  ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 2 result 30))
else
  ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 21 errset.errset 30))
)
```

这里的逻辑是：

- **成功分支**：`errset(result = evalstring(data))` 返回非 `nil`（即执行成功），发送 ASCII 2 + 结果 + ASCII 30
- **失败分支**：如果 `errset` 返回 `nil`（执行失败），则发送 ASCII 21 + **错误信息** + ASCII 30

**`errset.errset` 的含义：**

- 外层的 `errset` 是指上面那个 `errset` 函数调用吗？**不是！**
- 实际上，当 `errset` 捕获错误时，错误信息被存储在**同名的全局变量 `errset`** 中
- `errset.errset` 这个写法**看起来可疑**，可能是笔误或特定 Skill 版本的扩展语法

### 4. **可能的问题**

正常的写法应该是：

```skill
else
  ipcWriteProcess(ipcId sprintf(nil "%c%s%c" 21 errset 30))
  ; 或
  ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 21 errset 30))
```

因为 `errset` 变量本身存储的就是错误字符串列表。

### 5. **验证测试**

```skill
; 模拟错误
result = errset(nonExistentFunc(5))  ; 返回 nil
printf("Error info: %L\n" errset)    ; 输出: Error info: ("*Error* eval: undefined function - nonExistentFunc")

; errset.errset 会报错吗？
printf("%L\n" errset.errset)  ; 这很可能出错，因为 errset 不是结构体
```

## 结论

`errset.errset` 在标准 Cadence Skill 语法中**很可能是笔误**，应该改为 `errset`（全局变量）或通过其他方式提取具体的错误字符串。正确的错误处理应该是：

```skill
else
  ;; errset 变量包含错误信息的列表
  ipcWriteProcess(ipcId sprintf(nil "%c%L%c" 21 errset 30))
```

如果这段代码实际能运行，可能是特定环境对 `errset` 做了扩展，使其既能作为函数又能作为结构体访问。建议在 CIW 中测试验证。

---

### 1. 特殊控制字符（ASCII 码）
这是最轻量级的方式，与你现有的设计一致，利用 ASCII 表中不可见的控制字符来标记帧边界。

| 标记 (缩写) | ASCII 码 (十进制/十六进制) | Python 表示 | 含义与用途 |
| :--- | :--- | :--- | :--- |
| **SOH** | 1 / 0x01 | `b'\x01'` | Header 开始，常用于元数据段前 |
| **STX** | 2 / 0x02 | `b'\x02'` | 正文开始 |
| **ETX** | 3 / 0x03 | `b'\x03'` | 正文结束 |
| **EOT** | 4 / 0x04 | `b'\x04'` | 传输结束 |
| **ENQ** | 5 / 0x05 | `b'\x05'` | 询问请求 |
| **ACK** | 6 / 0x06 | `b'\x06'` | 肯定应答 |
| **NAK** | 21 / 0x15 | `b'\x15'` | 否定应答 |
| **RS** | 30 / 0x1E | `b'\x1E'` | 记录分隔符 |
| **US** | 31 / 0x1F | `b'\x1F'` | 单元分隔符 |
| **DLE** | 16 / 0x10 | `b'\x10'` | 转义/数据链路转义 |

> **经典协议参考**：BISYNC (BSC) 协议大量使用了这些字符。

### 2. 显式长度前缀
不依赖特殊字符，而是先发送一个固定大小的头部来声明后续数据的长度。

**Python 常见实现**：
-   **4字节无符号整数** (`struct.pack('>I', len(data))`) —— 常用于 TCP 流式传输。
-   **7-bit 编码的变长整数** —— 类似 UTF-8 的编码规则，节省空间，常见于 WebSocket、MQTT。
-   **JSON 头部** —— `{"size": 12345}`，可读性好，但解析略有开销。

**优点**：无需转义，解析速度极快，不会因数据内容恰好等于标记符而出错。

### 3. 可打印分隔符
使用标准可读字符作为边界，方便调试。

| 类别 | 常用分隔符 | 典型应用 |
| :--- | :--- | :--- |
| **单字符** | `\n` (换行 LF), `\r\n`, `\0` (空字符) | 文本协议、HTTP 头部、Redis RESP |
| **多字符** | `\r\n\r\n` | HTTP 头部结束标记 |
| **字符串边界** | `---boundary---` | 邮件 (MIME)、HTTP `multipart/form-data` |

### 4. 自描述协议/编码
数据本身包含其结构信息，几乎不使用外部帧标记。

-   **TLV (Type-Length-Value)**：每个字段独立编码，常见于金融行业 (如 ISO 8583)。
-   **ASN.1 / BER / PER**：电信与加密领域的基础编码规则。
-   **ProtoBuf / MessagePack**：在工业界广泛使用，其自带帧标识。

### 5. 基于时间的帧定界 (Timing-Based)
主要用于物理层或极低功耗的无线传感器网络 (如 LoRa)，根据数据包间的**空闲时间**来区分帧。

**总结建议**：

-   **简单命令/状态**：使用 STX/ETX (如你的场景) 或 \n 即可。
-   **二进制/混合数据**：推荐 **长度前缀 + 数据** 的模式。
-   **需要调试/日志**：可打印分隔符 (如 `\r\n`) 更方便。
