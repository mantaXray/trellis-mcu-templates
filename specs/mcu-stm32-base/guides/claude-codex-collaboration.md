# Claude / Codex 协同工作规则

> 本项目采用 **Claude（task-side）+ Codex（code-side）双 agent 协同**。本文档定义两个 agent 的职责边界、交接物、以及禁止越界的硬规则。**任何 AI 助手开始工作前必读**。

---

## 1. 角色分工（硬约束）

| 角色 | Claude（task / 文档侧） | Codex（code 侧） |
|---|---|---|
| **主要职责** | 需求收敛、PRD 编写、方案设计、文档维护、Trellis 任务管理 | C/H 代码实现、编译验证、单元测试编写 |
| **能写什么** | `.trellis/tasks/**`、`doc/**`、`.trellis/spec/**`、`.trellis/workspace/**`、AGENTS.md / README.md / CHANGELOG.md 等纯文档 | `Core/**`、`User/**`、`Drivers/**`、`Middlewares/**` 等所有 C/H 代码；CubeMX 生成区域的 `USER CODE` 块 |
| **不能写什么** | **绝对不能改 C/H 代码**（即使一行）；不能 `git commit` 代码改动 | 不能改 PRD / 方案文档（除非 PRD 漏写实现细节，可通过提案让 Claude 补） |
| **典型工具调用** | `Read/Edit/Write/Glob/Grep/Bash`（仅读、文档写、Trellis 脚本） | `Read/Edit/Write/Bash`（含编译命令） |
| **Trellis 阶段** | Phase 1（Plan）+ Phase 3（Finish 阶段文档与 spec 更新） | Phase 2（Execute），包括 implement + check |

---

## 2. 工作流交接

### 2.1 Claude → Codex 交接（Phase 1 → Phase 2）

Claude 完成 brainstorm 收敛后，**必须**在交付给 Codex 前完成以下产物：

1. `prd.md` —— 完整 PRD（含 Goal / Requirements / AC / Out of Scope / Technical Approach / Implementation Plan）
2. `implement.jsonl` —— spec/research 文件清单，**只填路径不写代码**
3. `check.jsonl` —— check 阶段同样的 spec 清单
4. 一份**优化方案文档**放在 `doc/` 下（命名建议：`优化方案_YYYY-MM-DD_<scope>.md`）
5. 一份**当前设计基线文档**（如果不存在）放在 `doc/` 下（命名建议：`软件设计说明_<scope>.md`）
6. 任务状态切到 `in_progress`（通过 `python ./.trellis/scripts/task.py start <task-dir>`）

> 交接信号：在主会话里明确告诉用户"PRD 完成，等 Codex 接手实现"，并停止任何代码改动尝试。

### 2.2 Codex 接手时的 entry 点

Codex 启动时必须读取（按重要性排序）：

1. PRD：`.trellis/tasks/<active-task>/prd.md`
2. 优化方案：`doc/优化方案_*.md`（本次任务的）
3. 当前设计基线：`doc/软件设计说明_*.md`
4. `implement.jsonl` 列出的所有 spec / 参考文档
5. 实际 C/H 代码（按 PRD Implementation Plan 中列出的文件清单）

### 2.3 Codex → Claude 反馈（Phase 2 → Phase 3）

Codex 改完代码、编译通过、check 通过后，**主动通知 Claude**：

- 列出实际改了哪些文件、相对 PRD Implementation Plan 是否有偏差
- 编译输出（make / IAR / CubeIDE 完整 log 的关键行）
- 任何在实现过程中发现的、PRD 没覆盖的边缘情况（让 Claude 决定补 PRD 还是单独跟进）

Claude 收到反馈后：
- 更新设计基线文档 `doc/软件设计说明_*.md` 到与新代码一致
- 必要时通过 `trellis-update-spec` 把新约定沉淀到 `.trellis/spec/`
- 不主动 commit 代码（commit 也归 Codex 做）

---

## 3. 硬禁止清单

### 3.1 Claude 严禁

| ❌ 禁止行为 | 为什么 |
|---|---|
| 修改任何 `.c` / `.h` 文件 | 越界；Codex 是 code-side owner |
| 修改 `Drivers/` `Middlewares/` 等 vendor / 生成代码 | 同上 |
| 执行 `make` / `iarbuild` 等编译命令 | 编译验证归 Codex；Claude 的编译输出会污染上下文 |
| 在 brainstorm 阶段就跳到"我来写代码" | 违反协同流程 |
| 在 PRD / 方案文档里嵌入大段可直接 copy-paste 的 C 代码片段 | 这是 Codex 的工作；Claude 应描述设计意图，不应预写实现 |
| `git commit` C/H 代码改动 | commit 归 Codex |

### 3.2 Codex 严禁

| ❌ 禁止行为 | 为什么 |
|---|---|
| 在没有 PRD 的情况下凭"自己理解"开始改代码 | 流程绕过 brainstorm，会偏离用户意图 |
| 改 PRD 文件 | PRD 是 Claude / 用户产物；Codex 发现 PRD 有问题应反馈给 Claude，不应自己修 |
| 实现 PRD 明确标记为 "Out of Scope" 的功能 | 范围蔓延 |
| 跳过 check 阶段直接 commit | 流程不完整 |

---

## 4. 例外条款

### 4.1 用户显式 inline 改动

如果用户在**当前消息**里明确说出以下任一短语，**Claude 可以临时跨界改代码一次**（仅当前轮）：

- `"do it inline"` / `"no sub-agent"`
- `"你直接改"` / `"别派 sub-agent"` / `"main session 写就行"` / `"不用 sub-agent"`

未见用户说出上述短语时，**严禁自行越界**。

### 4.2 紧急小修

修一个 typo / 注释错别字 / 文档里嵌的过时代码示例 —— 这类**纯文档性**的小修，Claude 可以做。但**只要涉及编译产物**，立刻收手。

---

## 5. 文档命名约定

| 类型 | 命名 | 路径 |
|---|---|---|
| 当前设计基线 | `软件设计说明_<scope>.md` | `doc/` |
| 优化方案 | `优化方案_<YYYY-MM-DD>_<scope>.md` | `doc/` |
| 任务 PRD | `prd.md` | `.trellis/tasks/<MM-DD-slug>/` |
| 任务 spec 上下文 | `implement.jsonl` / `check.jsonl` | `.trellis/tasks/<MM-DD-slug>/` |
| 协同规则（本文件） | `claude-codex-collaboration.md` | `.trellis/spec/guides/` |

---

## 6. Trellis 阶段对照

```
Phase 1 (Plan)          Claude 主导
  ├─ task.py create
  ├─ trellis-brainstorm
  ├─ prd.md
  ├─ implement.jsonl / check.jsonl
  └─ task.py start                  ← Claude 在这里收手

Phase 2 (Execute)       Codex 主导
  ├─ 读 PRD + 设计文档 + spec
  ├─ 改代码
  ├─ 编译验证（make / iarbuild）
  ├─ trellis-check
  └─ 反馈给 Claude

Phase 3 (Finish)        Claude + Codex 接力
  ├─ Codex: git commit 代码改动
  ├─ Claude: 更新 doc/软件设计说明_*.md 到与新代码一致
  ├─ Claude: 可能通过 trellis-update-spec 沉淀新约定
  └─ /trellis:finish-work
```

---

## 7. 如何让用户判断当前是哪个阶段

- **任务状态 `planning`** → Phase 1，Claude 当家
- **任务状态 `in_progress`** → Phase 2，Codex 当家（Claude 此时**只读不写代码**）
- **任务状态 `complete` 前的收尾** → Phase 3，Claude 更新文档 + spec、Codex 收尾 commit

用 `python ./.trellis/scripts/task.py current` 或 `task.py list` 随时查看。
