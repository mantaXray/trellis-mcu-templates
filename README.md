# trellis-mcu-templates

> MCU 固件项目的 Trellis 通用模板 registry。给 `trellis init --template ... --registry ...` 使用。
>
> 支持按项目实际选择 IAR Embedded Workbench for Arm、STM32CubeIDE+GCC 或其他 MCU 工具链；spec 内仅保留通用差异提示。

> **外部读者**：本仓库是 [mantaXray](https://github.com/mantaXray) 团队 MCU 固件实践沉淀出来的 Trellis 模板，开源（MIT）给同类需求的团队参考。示例工具链组合（IAR/CubeIDE 任选、Git+SVN 双轨、私有 Git 镜像 + GitHub/Gitee）按你实际情况调整；pitfall 知识库和 AI 协同规则可以直接复用。

> **谁应该读这个文档？**
> - 你要在**新 MCU 项目里用这个模板** → 看下面「使用方法」一节，跑两步命令就能用
> - 你要**接手维护本仓库** → 跳到 [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)，顶部"Supervisor 模式"是新人入门

## Registry 地址

示例里统一使用 `<registry-url>` 占位。当前 registry 地址以团队通知或脚本配置为准，不在模板正文里写死，避免服务迁移后批量失效。

## 使用方法（新 MCU 项目两步完成）

### 第 1 步：跑 trellis init，同时拉 spec + bootstrap skill

按你使用的 AI 工具组合选一行命令。本仓库默认按 Codex 为主、Claude 为辅设计；下表第一行是团队默认。

| 模式 | 适用 |
|---|---|
| `--codex` | **团队默认**。Codex CLI 单 agent 跑任务+代码两个相位 |
| `--claude --codex` | 双轨。Claude 跑任务相位，Codex 跑代码相位 |
| `--claude` | Claude-only。同一个 Claude agent 跑两个相位 |

#### PowerShell

```powershell
cd <new-mcu-project>

# 团队默认（Codex-only）
trellis init -y --codex -t mcu-stm32-base -t mcu-bootstrap -r <registry-url>

# 双轨（Claude planning + Codex codegen）
trellis init -y --claude --codex -t mcu-stm32-base -t mcu-bootstrap -r <registry-url>

# Claude-only
trellis init -y --claude -t mcu-stm32-base -t mcu-bootstrap -r <registry-url>
```

#### Bash

```bash
cd <new-mcu-project>

# 团队默认（Codex-only）
trellis init -y --codex \
  -t mcu-stm32-base \
  -t mcu-bootstrap \
  -r <registry-url>

# 双轨
trellis init -y --claude --codex \
  -t mcu-stm32-base \
  -t mcu-bootstrap \
  -r <registry-url>

# Claude-only
trellis init -y --claude \
  -t mcu-stm32-base \
  -t mcu-bootstrap \
  -r <registry-url>
```

完成后会出现：

```text
.trellis/spec/                              <- 来自 mcu-stm32-base (type:spec)，平台无关
├── guides/
│   ├── index.md                            # guide 总入口
│   ├── claude-codex-collaboration.md       # 双轨/单轨协同规则
│   ├── firmware-data-flow-guide.md         # ISR/queue/task/parser/display/storage 边界图
│   ├── firmware-reuse-guide.md             # 搜索优先与复用规则
│   ├── task-process.md                     # PRD/research/implement/check/finish 规则
│   └── debug-symptom-index.md              # 项目 debug 症状索引写法
└── firmware/
    ├── index.md                            # firmware spec 总入口
    ├── project-context.md                  # 项目上下文填空模板
    ├── directory-structure.md              # 目录/生成代码/IAR 工程同步
    ├── verification.md                     # 按变更类型选择验证
    ├── memory-placement.md                 # 内存放置、DMA/cache、map 检查
    ├── uart-dma-protocol.md                # UART DMA 与协议边界
    ├── freertos-task-ownership.md          # task/queue/watchdog/ISR 所有权
    ├── ui-display.md                       # 可选 UI/显示快照规则
    ├── storage-persistence.md              # 可选存储/持久化/append-only 记录
    ├── command-contracts.md                # 设备 command API 合同模板
    ├── pitfalls-index.md                   # 坑点快速索引
    ├── pitfalls.md                         # MCU 通用坑点知识库（章节 >10 条时拆到 pitfalls-<category>.md 同级文件）
    ├── version-control.md
    └── coding-standard.md

.claude/skills/mcu-bootstrap/SKILL.md       <- 装了 --claude 时
.codex/skills/mcu-bootstrap/SKILL.md        <- 装了 --codex 时
```

### 第 2 步：在 AI 工具里触发 mcu-bootstrap skill

- **Claude Code**：输入 `/mcu-bootstrap`
- **Codex CLI**：说“用 mcu-bootstrap skill”或“跑一下 mcu-bootstrap”
- **任何 AI 工具**：说“执行 MCU 项目引导”，AI 检测到本地 skill 后应调用

`mcu-bootstrap` 会：

1. 检测项目工具链（IAR / STM32CubeIDE+GCC / other）
2. 检测是否在 SVN 工作副本下
3. 询问项目代号、初始版本号、Git remote URL、是否需要 `ALGO_VERSION`
4. 自动完成：
   - 追加/修复 `AGENTS.md` managed block
   - 合并项目根 `.gitignore`
   - 创建 `doc/` + `doc/README.md`
   - 在 `User/App/System/define.h`（IAR）或 `User/App/Inc/define.h`（CubeIDE）写缺失版本宏
   - 合并 SVN `svn:ignore` 属性（不提交 SVN）
   - 绑定或修正 Git remote（不 push）
5. 用 `MCU-BOOTSTRAP:STARTED` / `MCU-BOOTSTRAP:DONE` 标记支持失败后重跑修复

## 已有项目更新

只补新增文件，不覆盖已有项目特化 spec：

```powershell
trellis init --append -t mcu-stm32-base -r <registry-url>
```

这适合把新增的 `firmware/pitfalls-index.md`、`firmware/pitfalls.md`、`firmware/index.md` 等文件补进已有 `.trellis`。

如果要同步模板里已有文件的新版本，例如 `version-control.md` 或 `coding-standard.md`，不要直接全量覆盖。先 diff 模板和项目本地文件，再手动 merge，避免覆盖项目特化规则。

强制覆盖只适合确认项目本地 spec 没有特化改动的情况：

```powershell
trellis init --overwrite -t mcu-stm32-base -r <registry-url>
```

## Pitfall 知识库共享方式

每个工程可以保留自己的 pitfall 文件；模板仓库维护通用知识库。

- 项目本地 pitfall：记录现场事实、项目特化约定、具体排查过程
- 模板 pitfall：只记录跨 MCU 项目可复用的规则和检查项，默认入口保持短小
- 大量长篇内容：单章节 >10 条时拆到 `firmware/pitfalls-<category>.md` 同级文件；再大就放外部知识库或独立仓库，由索引链接
- 反哺入口：模板仓库 `docs/pitfall-feedback-loop.md`（维护者文档，不随 trellis init 发到下游项目）
- 外部知识库搭建方式：模板仓库 `docs/external-knowledge-base.md`（维护者文档）
- mcu-bootstrap 手工 fallback：模板仓库 `docs/bootstrap-checklist.md`（AI 完全不可用时人工对照执行）

反哺原则：先在项目本地记录，确认能抽象掉项目代号、寄存器编号、客户信息和一次性路径后，再合并到本仓库 `specs/mcu-stm32-base/firmware/pitfalls.md`。

## Trellis 任务与会话约定

- 跨 ISR / queue / task / parser / display / storage / command 的任务，先按 `.trellis/spec/guides/firmware-data-flow-guide.md` 写清数据路径
- 新增 helper、常量、驱动、parser、command API 前，先按 `.trellis/spec/guides/firmware-reuse-guide.md` 搜索现有实现
- PRD、`research/`、`implement.jsonl`、`check.jsonl`、finish 阶段规则见 `.trellis/spec/guides/task-process.md`
- 项目可在 `.trellis/config.yaml` 明确 `session_auto_commit`、`max_journal_lines`、生命周期 hooks、package scope 和 Codex `dispatch_mode`

## 当前模板清单

见 `index.json`。

| ID | 类型 | 适用场景 |
|---|---|---|
| `mcu-stm32-base` | spec | 通用 MCU 固件 spec 套件（AI 协同 + 提交规范 + 编码规范 + pitfall 知识库） |
| `mcu-bootstrap` | skill | trellis init 之后一键收尾（AGENTS / .gitignore / doc / svn:ignore / 版本宏 / git remote） |

## 兼容性约束

- `mcu-bootstrap` 依赖 `mcu-stm32-base` 已安装
- 目标平台：Windows PowerShell 优先，同时给 Bash fallback
- 工具链：按项目实际选择 IAR Embedded Workbench for Arm、STM32CubeIDE+GCC 或其他构建方式
- Bootstrap 不执行 `git push` 或 `svn commit`

## 维护规则

> 完整维护 SOP（日常编辑、反哺、CI、变更记录、节奏建议、紧急情况）见 **[`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)**。下面只列最关键的硬规则。

- 模板内容不许包含项目专属命名（如具体项目名、Modbus 寄存器编号、Gitea repo URL 等），用占位符或抽象描述
- 当前 registry 地址、内网 IP、账号等环境信息只放团队通知或本地脚本，不写死到模板正文
- 模板演进时遵循同 Trellis 主仓库的版本约定，在 commit message 里明确变更点
- 新增模板或新增 spec 文件时同步更新 `index.json`、README 和 `scripts/validate.py`
- `templates/` 目录存放跨文件复用的规范内容（gitignore block、svn:ignore 列表、AGENTS.md managed block、doc/README 模板）；改动后跑一次 `python scripts/validate.py` 确保 `SKILL.md` 与 `docs/bootstrap-checklist.md` 的内嵌副本仍然一致
- `docs/` 目录存放仅供模板维护者参考的文档（bootstrap 手工 fallback、坑点反哺规则、外部知识库搭建指南），不通过 `trellis init` 发到下游项目，保持下游 `.trellis/spec/` 精简
- 运行 validator：`python scripts/validate.py`（跨平台，Python 3.10+）。CI 会自动跑一次
- 模板内容学到新 lesson 时，从下游项目反哺回来（手动 diff + 合并），不要让模板长期落后
