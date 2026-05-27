# Firmware Coding Standard

> 公司 MCU 固件 C/C++ 编码规范（STM32 / GD32 通用，IAR + STM32CubeIDE+GCC 通用）。

## 1. Source Standard

新写或改动 C/C++ 代码时，遵循公司纸面规范 `ref_docs/C&C++语言编码规范v1.0.txt`（或同名 docx/pdf 作为 fallback 副本）。

因为 `ref_docs/` 是本地引用，下面把核心规则提炼出来作为 Trellis 可见的稳定基线。

## 2. Naming

- **函数名、变量名、参数名、结构体字段** 用 lower camelCase 加清晰的模块前缀，例如 `imss`、`aht20`、`hp303s`、`color`、`distance`
- **宏常量和枚举常量** 仍为全大写下划线分隔
- **布尔标识符** 没有现成命名时用 `is`-style 前缀
- **全局变量** 用 `g`-style 前缀；**静态变量** 用 `s`-style 前缀
- **时间和单位值** 在变量名里带单位（如 `delayMs`, `gDistanceMm`）
- **保留模块现有公开类型族**：若模块已用 `_t` 公开类型，不要混入 `_T` 命名，除非任务明确含 API 重命名

## 3. File Headers And Comments

### 3.1 文件头

新增或修改的源文件必须用公司文件头模板。版权年份用当前项目工作年（不一定是本年自然年，**遵循 `User` 给出的项目时间基准**）：

```c
/*
 * Copyright (c) 2026,北京合鲸科技发展有限公司
 * All rights reserved
 *
 * Filename：module.c
 * Version：v1.00.00
 * Description：模块说明
 *
 * Author：李东殊
 * Date：YYYY年MM月DD日
 *
 * Changelog：
 * YYYY年MM月DD日 v1.00.00 初始版本
 */
```

### 3.2 修改时更新文件头

修改已有源文件 / 头文件时，**同步更新文件头**：

- 添加或更新 `Changelog`
- 每文件每天最多 bump 一次 `Version`
- 同日多次修改：保留同一日期 / Version 行，把当天的多次改动**合并**到该 Changelog 条目下
- 文件头 `Changelog` 不应变成提交流水账 —— 当 commit 只是 bump 整体 `VERSION` 宏时，文件头保持简洁

### 3.3 函数 / 类型 / 变量注释

- **公开函数** 必须有 `@brief`、`@param`、`@return` 注释
- **枚举定义、枚举值、结构体定义、结构体成员、变量定义** 必须有注释说明其用途或单位
- **行内注释** 用于时序、DMA、cache、协议帧格式、字节序、内存所有权、硬件约束等非显然逻辑
- **不写**重述简单赋值的注释
- **代码注释** 可以用逗号，但**不应**以中英文句号结尾

## 4. Formatting And APIs

### 4.1 基础格式

- 头文件用 `#ifndef` / `#define` / `#endif` 守卫，只 include 实际需要的头
- 标准 / 库头用 `<...>`，项目头用 `"..."`
- 避免绝对 include 路径
- **一行一条** 语句或声明
- **大括号独占一行**
- **4 空格**缩进
- 每个 `if` `for` `while` `do` body 必须带大括号
- 一般源代码行宽**70~80 字符**为宜
- 指针 / 引用标记紧贴变量名：`char *name`，**不是** `char* name`
- **不要**在同一语句中混合声明指针和非指针变量

### 4.2 局部变量与初始化

- 使用前初始化局部变量
- 未知指针初始化为 `NULL`

### 4.3 公开嵌入式 API

- 使用固定宽度整型（`uint8_t` / `int32_t` 等），**不要**裸 `int` `long`
- 显式 buffer 长度参数（不要靠隐式 `\0` 终止）
- 输入型指针参数加 `const`
- 函数入口校验输入参数
- **不要**返回栈存储指针
- BSP / 协议代码**避免动态分配**，除非该模块已经依赖（如 LVGL）

## 5. Expressions And Control Flow

- 优先用 typed `const` 值，能不用宏就不用宏
- 必须用宏时：**宏定义** 和**宏参数** 都要加括号
- 表达式简单化，优先级不明显时加括号
- 多目的复合表达式拆成多条语句
- 布尔类值**直接比较**（不要 `flag == TRUE`）
- 指针与 `NULL` **显式比较**（不要 `if (ptr)`）
- **不要** `==` / `!=` 比较浮点
- 每个 `switch` 必须有 `default` 分支
- 每个 fall-through case 必须有**显式注释**

## 6. Firmware-Specific Rules

### 6.1 I2C 传感器驱动

- 硬件 I2C 驱动应接收 `I2C_HandleTypeDef *` 句柄 和 **7-bit** 传感器地址参数
- 在驱动内部做 `<<1` 移位适配 STM32 HAL 要求的 8-bit 形式
- 软件 I2C 驱动同样按 **7-bit** 接受输入

### 6.2 UART / Protocol 解析

- UART/DMA 解析器必须能处理：
  - 分片 DMA 输入（一帧分多次回调到达）
  - 一次回调多帧
  - 一帧跨越多次回调（buffer 跨帧）
- 协议解析器必须**先校验** delimiter、声明的 length、最大 payload 大小、CRC/checksum、字节序，**再**使用 payload 字段

### 6.3 DMA 缓冲

- DMA 面对的 buffer 必须记录：
  - 内存放置（DTCM / D2 / SRAM4 / AXI 等，STM32H7 类高端 MCU）
  - 对齐要求
  - cache clean / invalidate 规则（STM32H7 类含 cache）
  - producer / consumer 所有权

### 6.4 中断 / FreeRTOS 边界

- ISR 内**不**做长时间阻塞工作
- `*FromISR` API 只在符合 `configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY` 的中断优先级中调用
- 队列发送前检查队列 handle 非 `NULL`
- 新任务栈大小**按附近任务模式确定**，不要拍脑袋
- 长循环 / 长等待**喂狗或 `osDelay()` 让步**

### 6.5 Flash 操作

- Flash 写地址使用**halfword 对齐**（STM32F1 / GD32F1 类）或按 MCU 实际页边界
- Flash 写入只在文档化的持久化页范围内
- 关键参数（校准、版本号等）写入前必须有失败重试或回滚策略

## 7. Modbus / 主机协议（如适用）

- 寄存器映射变更必须**新增不破坏**：保留老寄存器编号和语义，新增功能用未使用区域
- 字节序与位序按协议文档统一（保持 register 内 high/low byte 顺序一致）
- 新增寄存器同步更新主机协议文档（与安卓 / 上位机团队对齐）

## 8. Trellis Spec 一致性

- 任务实施过程中如发现本规范与项目实际有冲突或需补充，**通过 `trellis-update-spec` 沉淀到项目 spec**，而不是单方面违反
- 项目 spec 优先级高于本通用 spec（项目 spec 是特化，本规范是通用基线）
