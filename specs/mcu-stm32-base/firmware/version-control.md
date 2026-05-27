# Version Control And Submission Rules

> 公司 MCU 固件项目使用 **Git（个人 / 团队副本）+ SVN（公司主线）** 双轨管理。本文档规定两条轨道各自的范围、提交格式、版本号管理、以及触发词约定。**新项目落地时按需将占位符替换为本项目具体信息**。

---

## 1. Git / SVN 双轨原则

### 1.1 各自范围（通用规则）

| 路径 | Git | SVN | 说明 |
|---|---|---|---|
| `Core/` `User/` `Drivers/` `Middlewares/` 等源码 | ✅ | ✅ | 双轨同步跟踪 |
| `.cproject` `.project` `.settings/` `.mxproject` `.ioc` `*.ld` `*.code-workspace` `*.ewp` `*.eww` | ✅ | ✅ | IDE / 链接器 / 工程配置 |
| `Bin/*.bin` `Bin/*.hex` 已发布版本 | ✅ | ✅ | 双轨保留发布产物 |
| `.agents/` `.claude/` `.codex/` `.trellis/` | ✅ | ❌ | AI / Trellis 配置，**仅 Git**，SVN 不上传 |
| `AGENTS.md` `.gitignore` `.git/` | ✅ | ❌ | Git 工具链配置 |
| `doc/` 项目文档（设计说明、优化方案等） | ✅ | ❌ | 通用约定：只上 Git，不上 SVN |
| `ref_doc/` 参考资料（PDF、docx、第三方文档） | ❌ | ❌ | 本地引用，两侧都不上 |
| `Debug/` `Release/` `*.o` `*.d` `*.su` `*.elf` `*.map` `*.list` 构建产物 | ❌ | ❌ | 由 IDE 重新生成 |
| `.qoder/` `.lingma/` `.uv-cache/` `tmp/` `~$*` 本地噪音 | ❌ | ❌ | 工具临时状态 / Office 锁 |
| `.trellis/workspace/*/journal-*.md` 个人 journal | ❌ | ❌ | 单开发者本地状态 |

### 1.2 配置文件

- 项目根的 `.gitignore` 必须声明上述 Git 端 ignore 规则
- 项目对应的 SVN 目录必须设 `svn:ignore` 属性，内容同步规则
- `.trellis/.gitignore` 已由 trellis init 默认声明 Trellis 内部 ignore

### 1.3 跨轨同步纪律

- **不要**在 `.gitignore` 里 ignore AI/Trellis 路径（这些路径就是 Git 该跟踪的内容）
- **不要**在 SVN 端 add 任何 AI/Trellis 路径
- Git 和 SVN 提交节奏可以**有意不同步** —— Git 频繁、SVN 节制（按公司里程碑）

---

## 2. 版本号管理

### 2.1 版本宏定义

新项目应当在 `User/App/Inc/define.h`（或公司项目惯例的等价位置）定义以下版本宏：

| 宏 | 类型 | 含义 | 何时 bump |
|---|---|---|---|
| `VERSION` | 字符串 `"vX.Y.Z"` | 整体固件版本号 | **每次改固件行为的 commit** |
| `VERSION_DATE` | 字符串 `"YYYYMMDD"` | 当前 VERSION 的发布日期 | 跟 VERSION 同步 bump |
| `ALGO_VERSION` *（可选）* | 字符串 `"vX.Y"` | 算法核心版本 | **仅算法核心变更**（拟合公式、阈值算法、核心处理算法） |

> 项目落地时按实际情况调整命名（参考项目用 `SOFTWARE_VERSION` / `SOFTWARE_VERSION_DATE`，部分项目使用 `VERSION` / `VERSION_DATE`，**全项目内保持一致即可**）。

### 2.2 版本号语义层次

- **整体固件版本**：覆盖任何改变运行时行为的修改 —— 包括流程修改、bug 修复、refactor 引起的行为变化、寄存器映射变更
- **算法核心版本**（若项目有此区分）：只在算法核心（拟合公式、阈值算法、信号处理核心）发生变化时 bump；纯流程修改 / 状态机调整 / 寄存器映射变更**不动**
- **日期戳**：单纯记录当前版本对应的日历日期

### 2.3 同一日期多次 bump

如果一天里有多次"改固件行为"的 commit：

- 日期戳保持当天日期不变
- 整体版本递增小版本：`v1.0.17` → `v1.0.18` → `v1.0.19`

### 2.4 仅文档 / Trellis / 重构（不改行为）的 commit

- 所有版本宏**不动**
- Commit 消息里明确写 `版本号：未变更` / `Version: unchanged` 并说明原因
- 例：`docs: 更新设计说明` / `chore: 调整 .gitignore` / `refactor: 重命名变量（无行为变化）`

### 2.5 文件头 Changelog 与版本号的关系

版本宏所在文件（如 `define.h`）的**文件头 `Changelog` 不是 commit-by-commit 流水账**。当 commit 只是 bump 版本号时，文件头 Changelog 只写一句简要概述。详细 commit 历史在 Git / SVN log 里。

文件头一般规则：
- 每个源文件最多一天一个 `Changelog` 条目
- 同一天多次改：合并到当天那条 Changelog 下
- 文件头 `Version`：每天至多 bump 一次（与全项目 `VERSION` 是不同概念）

---

## 3. Git Commit 规范

### 3.1 标题格式（Conventional Commits）

```text
<type>(<scope>): <短描述> [vX.Y.Z]

例：
feat: add work-state machine v1.0.18
fix(color): clear stale state on idle transition v1.0.19
chore: gitignore Office lock files
docs: update design baseline doc
refactor: extract distance helper （行为不变）
```

`type` 取值参考：`feat` `fix` `refactor` `chore` `docs` `test` `perf` `build` `style`

`scope` 可选，常用按模块：`color` `distance` `report` `bsp` `bootloader` `flash` `trellis` `doc`

### 3.2 正文模板（双语结构化 —— 公司标准）

```text
版本号：v1.0.18

摘要
- <中文摘要 1>
- <中文摘要 2>

关键变更
- <中文关键变更 1>
- <中文关键变更 2>

验证
- <编译命令>：PASS / 编译输出无新增 warning
- <其他验证项>：<PASS / 阻塞说明>

English

Version: v1.0.18

Summary
- <English summary 1>
- <English summary 2>

Verification
- <build command>: PASS
- <other check>: <PASS / blocked note>
```

#### 注意事项

- 每个段落都不能省略 —— 若该段无内容，写"无运行时变更"或"N/A"，**不能直接缺段**
- `版本号：` 必须与代码中的版本宏完全一致；纯文档/Trellis/重构则写 `未变更` / `unchanged` 并说明原因
- 不要把模板替换为单行 `Verification:` `Version:` 这种简化版
- commit 前自检：暂存的 commit 消息要满足上述完整模板

### 3.3 AI / Trellis 路径上 Git 的允许情况

`.agents/` `.claude/` `.codex/` `.trellis/` `AGENTS.md` `doc/` 都属于 Git 跟踪范围，正常 commit 即可。

---

## 4. SVN Commit 规范

### 4.1 触发条件

**只在用户明确说出 "提交 SVN" / "上传 SVN" / "SVN 提交"** 才动 SVN。SVN 提交是**公司级永久记录**，submitted 后无法编辑，因此不可隐式触发。

### 4.2 提交前必做事项

1. **比较 SVN 基线 vs 本地基线**（Git 和 SVN 可能有意不同步，SVN 落后多个版本是常态）：

   ```bash
   # SVN 端基线
   svn cat -r HEAD <定义版本宏的路径> | grep -E "VERSION|VERSION_DATE"

   # 本地基线
   grep -E "VERSION|VERSION_DATE" <定义版本宏的路径>

   # Git 端基线（如果有 git tag 对应每个 SVN release）
   git log --oneline --reverse <svn-baseline>..HEAD
   git diff --name-status <svn-baseline>..HEAD
   ```

2. **SVN log 要写完整版本跨度**（不是只写最近一次 commit）：
   - 若 SVN 落后到 v1.0.13，本地已到 v1.0.18，SVN log 必须涵盖 `v1.0.13 → v1.0.18` 全部行为变更
   - 中间各小版本的关键变更要逐条列出

3. **检查 svn:add 是否齐全**：

   ```bash
   svn status  # 关注 ? 标记的新源文件
   ```

   新增的源文件、IDE 工程配置文件需要 `svn add` 后再 commit。**不要**`svn add` AI/Trellis 路径。

### 4.3 SVN log 模板（**中文 + 版本前缀**，不含英文）

```text
版本：<项目代号>:v1.0.18_20260527
简述：xxx 功能完成 / xxx 问题修复
1. 增加 xxx 模块
2. 修复 xxx bug
3. 优化 xxx 性能
```

- **不要**包含 `Verification`、`English`、`Summary`、`Key Changes` 等 Git 专用字段
- `版本：` 行必须含产品名前缀（`<项目代号>` 替换成本项目 SVN 标识，如 `BW-STS130_S9706` / `BW2024-XAYF-023_MCU-MAIN`），格式严格为 `<项目代号>:vX.Y.Z_YYYYMMDD`
- `简述：` 一句话整体描述
- 编号变更项使用阿拉伯数字 + 中文

### 4.4 提交执行流程（**强制**）

1. **写完 SVN log 后，先把完整内容打印给用户，等待显式确认**
2. 用 UTF-8 no-BOM 临时文件保存 log：
   ```bash
   # 例：写到 /tmp/svn_log.txt（UTF-8 no-BOM）
   svn commit <paths> --file /tmp/svn_log.txt --encoding UTF-8
   ```
3. **不要**用 `svn commit -m "..."` 命令行直接传中文（容易乱码）
4. commit 后立即验证 log 不乱码：
   ```bash
   svn log -r <REV> --xml | grep -A 20 "<msg>"
   ```
5. 显式列出要提交的路径（**避免目录级 commit**），防止误传 docs、tmp、生成产物、AI/Trellis 路径

### 4.5 SVN 不应包含的路径（再次强调）

`.agents/` `.claude/` `.codex/` `.trellis/` `AGENTS.md` `.gitignore` `.git/` `doc/` `ref_doc/` `Debug/` `Release/` `tmp/` `*.swp` `Thumbs.db` —— 这些都应在 `svn:ignore` 属性里。

例外：用户明确要求提交某 AI 配置时（如更新 Trellis spec 后需要同步给同事 SVN 副本），可以临时 `svn add` 该路径 + 显式提交 + commit 消息里说明。

---

## 5. 触发词约定（重要 —— 影响 AI 助手行为）

| 用户说的话 | AI 助手该做的事 |
|---|---|
| "提交 git" / "提交 Git" / "git 提交" | Git 端 commit + push 到 origin/main |
| "提交远程" | 同上（默认指 Git，因为 SVN 是公司主线，提交需要更显式） |
| "提交 SVN" / "上传 SVN" / "SVN 提交" | 走 §4 SVN 流程（先打印 log → 等用户确认 → commit） |
| "本地 commit" / "commit 一下" | Git 端 commit，**不 push** |
| 没说提交两个字 | 不要主动 commit，等用户开口 |

---

## 6. AI 助手协同（与 `claude-codex-collaboration.md` 配合）

- **Claude** 不修改 C/H 代码，因此 Claude 一般只做 `doc/` `.trellis/` 内文档 commit + push
- **Codex** 负责实际的固件行为变更 commit，必须先 bump 版本宏
- **Phase 3.4 commit（Trellis 工作流硬约束）**：实现验证完成后，由 main agent 驱动 `git commit`，**消息严格按 §3.2 模板**

---

## 7. 紧急回滚 / 历史改写

- Git 改写历史（`filter-branch` / `filter-repo`）和 force push 是**高风险操作**，必须在用户明确要求且确认远端无协作者时才做
- 推荐用 `git-filter-repo` 替代已 deprecated 的 `filter-branch`：
  ```bash
  pip install git-filter-repo
  git filter-repo --path <要清的路径> --invert-paths
  git push --force-with-lease origin main
  ```
- SVN 端无法改写已 commit 的历史，错误 commit 只能通过新 commit 撤销 + 在 commit log 中说明
