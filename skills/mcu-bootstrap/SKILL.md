---
name: mcu-bootstrap
description: "After `trellis init -t mcu-stm32-base`, run this once to finish the project-root configuration that trellis init cannot write itself: AGENTS.md append, .gitignore, doc/, version macros, svn:ignore, git remote. Idempotent — re-running is safe. Use when the user just initialized a new MCU firmware project from the mcu-stm32-base template, or says '跑一下 bootstrap' / 'mcu bootstrap' / 'finish init'."
---

# MCU Project Bootstrap

This skill finalizes a new MCU firmware project after `trellis init -t mcu-stm32-base -r <registry>`. trellis init only copies the spec into `.trellis/spec/`; this skill writes the project-root files that trellis init cannot touch.

## Trigger Conditions

Invoke when:

- User just ran `trellis init -t mcu-stm32-base -r ...` in a new MCU project
- User explicitly says `/mcu-bootstrap`, `跑 bootstrap`, `mcu 引导`, `finish init`
- User asks "把项目初始化收尾" / "配一下新项目"

Do **not** invoke when:

- `AGENTS.md` already contains the marker `<!-- MCU-BOOTSTRAP:DONE -->` (already bootstrapped)
- Project is not actually a freshly initialized MCU project (e.g., no `.trellis/spec/firmware/version-control.md` from this template)

## Workflow

### Step 1 — Idempotency Check

Read project root `AGENTS.md`. If it contains `<!-- MCU-BOOTSTRAP:DONE -->`:

- Tell user: "项目已 bootstrap 过，本次跳过。如需重做，请删除 AGENTS.md 中的 `<!-- MCU-BOOTSTRAP:DONE -->` 标记。"
- Stop.

### Step 2 — Detect Toolchain

Check project root for indicators:

- `EWARM/` directory present → **IAR project (default, ~90% of company projects)**
- `.cproject` + `Debug/` directory present → **STM32CubeIDE+GCC project (legacy exception)**
- Neither present → ask user explicitly

Record toolchain for later steps (different `.gitignore` template, different version macro path).

### Step 3 — Detect SVN Working Copy

Check `..` and `.` for `.svn` directory:

- If found at parent → record SVN root path; bootstrap will set `svn:ignore` on this project's directory
- If not found → skip SVN step entirely

### Step 4 — Collect Project Variables (Interactive)

Ask the user via `AskUserQuestion` tool (one bundle, up to 4 questions per call):

1. **项目代号** (Project Code) —— e.g., `BW-STS130_S9706`, `BW2024-XAYF-023_MCU-MAIN`. Used in version stamp, SVN log template, file naming.
2. **初始固件版本号** —— default `v1.00.00` for IAR projects, `v1.0.0` for legacy CubeIDE projects.
3. **Git remote URL** (optional) —— Gitea / GitHub URL if user wants to bind right away. Skip if not yet ready.
4. **是否有独立算法核心需要 ALGO_VERSION** —— y/n, default n. If y, ask for initial `ALGO_VERSION` value (e.g., `v1.0`).

### Step 5 — Append AGENTS.md

Read `AGENTS.md`. Append the following content **after** `<!-- TRELLIS:END -->`:

```markdown
---

## 本项目专用：Claude / Codex 协同硬规则

本项目采用 **Claude（task / 文档侧）+ Codex（code 侧）双 agent 协同**，职责边界严格：

- **Claude** 只负责：任务管理（PRD、brainstorm、Trellis 任务状态切换）、文档维护（`doc/`、`.trellis/spec/`、`.trellis/tasks/`）
- **Codex** 只负责：C/H 代码实现、编译验证（`iarbuild`）、`git commit` 代码改动

**Claude 严禁修改任何 `.c` / `.h` 文件**（即使一行）。即使 PRD 已经写完，Claude 也不应自行越界改代码 —— 代码部分等 Codex 接手。

唯一例外：用户在**当前消息**里明确说出 "你直接改" / "别派 sub-agent" / "main session 写就行" / "do it inline" / "no sub-agent" 等短语时，Claude 可以临时改一次。

完整规则与流程见：[`.trellis/spec/guides/claude-codex-collaboration.md`](.trellis/spec/guides/claude-codex-collaboration.md)

<!-- MCU-BOOTSTRAP:DONE 2026-05-27 项目代号: {{PROJECT_CODE}} -->
```

Replace `{{PROJECT_CODE}}` with the value from Step 4 #1. Replace `2026-05-27` with the actual current date.

### Step 6 — Write `.gitignore`

If project root has no `.gitignore`, write one based on Step 2 toolchain detection.

**For IAR project** (default), use this template:

```gitignore
# IAR Embedded Workbench temporary/intermediate files
EWARM/*/Obj/
EWARM/*/BrowseInfo/
EWARM/*/Exe/
EWARM/*/List/
EWARM/*/.ninja_deps
EWARM/*/.ninja_log
EWARM/*/*.dep
EWARM/*/*.rsp
EWARM/*/*.pbi
EWARM/*/*.pbw
EWARM/*/*.pbd
EWARM/*/*.browse
EWARM/*/*build_cache*
EWARM/*/build.ninja
EWARM/Backup*
.ninja_deps
.ninja_log
build.ninja

EWARM/settings/

*.elf
*.map
*.list
*.hex
*.bin
*.out
!Bin/*.hex
!Bin/*.bin
!Bin/*.out

.vscode/BROWSE.VC.DB*
.vscode/ipch/

.qoder/
.lingma/
.uv-cache/
tmp/

ref_doc/
ref_docs/

.trellis/workspace/*/journal-*.md

*.swp
*~
*.bak
*.orig
~$*

Thumbs.db
Desktop.ini
.DS_Store
```

**For STM32CubeIDE+GCC project** (legacy), use:

```gitignore
Debug/
Release/

*.o
*.d
*.su
*.cyclo

*.elf
*.map
*.list

*.hex
*.bin
!Bin/*.hex
!Bin/*.bin

.metadata/
.vscode/BROWSE.VC.DB*
.vscode/ipch/

.qoder/
.lingma/
.uv-cache/
tmp/

ref_doc/
ref_docs/

.trellis/workspace/*/journal-*.md

*.swp
*~
*.bak
*.orig
~$*

Thumbs.db
Desktop.ini
.DS_Store
```

If `.gitignore` already exists, **do not overwrite**. Tell user: "`.gitignore` 已存在，跳过覆盖；如需重置请删除后重跑。"

### Step 7 — Create `doc/` and `doc/README.md`

`mkdir -p doc/`，写 `doc/README.md`：

```markdown
# doc/ 目录约定

本目录存放项目相关的设计文档、优化方案、阶段性总结。**只上 Git，不上 SVN**。

## 命名约定

| 类型 | 命名 | 示例 |
|---|---|---|
| 当前设计基线 | `软件设计说明_<scope>.md` | `软件设计说明_采集流程与算法.md` |
| 优化方案 | `优化方案_<YYYY-MM-DD>_<scope>.md` | `优化方案_2026-05-27_采集流程修复.md` |
| 阶段性总结 | `阶段总结_<YYYY-MM-DD>_<phase>.md` | `阶段总结_2026-06-15_alpha-release.md` |

## 同步规则

代码改动完成后，**Claude 负责**把"软件设计说明" 文档同步到与新代码一致的状态。
"优化方案" 文档作为单次任务的产物，归档后不再修改。
```

### Step 8 — Inject Version Macros

Locate the version header file based on toolchain:

- **IAR project**：`User/App/System/define.h`
- **STM32CubeIDE+GCC project**：`User/App/Inc/define.h`

If file does not exist, **stop and tell user**: "项目中未找到 `User/App/System/define.h`（IAR）/ `User/App/Inc/define.h`（CubeIDE）。请在该文件创建后手动添加：

```c
#define SOFTWARE_VERSION        \"v1.00.00\"
#define SOFTWARE_VERSION_DATE   \"20260527\"
```

或参考 `.trellis/spec/firmware/version-control.md` §2"

If file exists and **does not** already have `SOFTWARE_VERSION` / `VERSION` macro, append after existing `#define` block:

For IAR:
```c
#define SOFTWARE_VERSION        "{{INITIAL_VERSION}}"   /* 整体固件版本 */
#define SOFTWARE_VERSION_DATE   "{{TODAY_YYYYMMDD}}"    /* 当前版本发布日期 */
```

For CubeIDE:
```c
#define VERSION                 "{{INITIAL_VERSION}}"   /* 整体固件版本 */
#define VERSION_DATE            "{{TODAY_YYYYMMDD}}"    /* 当前版本发布日期 */
```

If user said "有 ALGO_VERSION" (Step 4 #4), also add:
```c
#define ALGO_VERSION            "{{ALGO_VERSION_VALUE}}" /* 算法核心版本 */
```

If macros already exist, **do not modify**, just report current values to user.

⚠️ This step modifies a `.h` file. Per `claude-codex-collaboration.md`, Claude shouldn't normally do this. **mcu-bootstrap is an explicit exception**: bootstrap is a one-time setup operation, not ongoing development; the macros are pure constants, not behavior code; the user has explicitly invoked bootstrap. Note this exception in the message back to user.

### Step 9 — Set svn:ignore (if SVN detected)

If Step 3 found an SVN working copy, write to a temp file then `svn propset`:

```bash
cat > /tmp/svn_ignore.txt << 'EOF'
.agents
.claude
.codex
.trellis
.git
.gitignore
AGENTS.md

doc
ref_doc
ref_docs

EWARM/Backup*
*.pbi
*.pbw
*.pbd
*.browse
.ninja_deps
.ninja_log
build.ninja

Debug
Release

.qoder
.lingma
.uv-cache
tmp

Thumbs.db
Desktop.ini
.DS_Store
*.swp
*~
*.bak
~$*
EOF

svn propset svn:ignore -F /tmp/svn_ignore.txt <project_dir>
svn propget svn:ignore <project_dir>   # 验证
```

**Do not `svn commit`** —— per `version-control.md` §4.1，只在用户明确说"提交 SVN"才动 SVN。告诉用户这个属性会等下次 SVN 提交时一起带。

### Step 10 — Git Remote (if URL provided)

If Step 4 #3 gave a URL:

```bash
# 检查项目是否已是 git 仓库
if [ ! -d .git ]; then
    git init -b main
fi
git remote add origin <URL>
git remote -v
```

Tell user: 远端已绑定，等积累一些 commit 后再 `git push -u origin main`。**不要**主动 push。

### Step 11 — Final Summary

打印给用户：

```
✓ mcu-bootstrap 完成

项目代号: <project_code>
工具链: <IAR / STM32CubeIDE>
SVN: <已设 svn:ignore / N/A>
Git remote: <已绑定 / 待用户后续 add>

已完成步骤:
✓ AGENTS.md 追加协同规则 + bootstrap 标记
✓ .gitignore 写入（IAR/CubeIDE 模板）
✓ doc/ + README.md 创建
✓ 版本宏写入 <path>
[✓ SVN svn:ignore 设置（待下次 SVN 提交带上）]
[✓ Git remote origin 绑定]

下一步:
1. 检查 `User/App/System/define.h`（或等价位置）是否需要补 ALGO_VERSION
2. 准备好后，用 "提交 git" 触发首次 git push
3. 公司 SVN 提交时记得 svn:ignore 属性也要带（一次性的）
4. 开始第一个 Trellis 任务：python ./.trellis/scripts/task.py create "<title>"
```

## Error Handling

- 任何步骤失败 → 不要清理已完成的部分，告诉用户具体哪一步出错，保留 partial state 供 debug
- 用户中途说停 → 立即停止，已做的不撤销，告诉用户已完成哪些
- AGENTS.md 已包含 `<!-- MCU-BOOTSTRAP:DONE -->` → Step 1 已经处理，不会到这里

## Not In Scope

- ❌ 不创建 `.cproject` `.ioc` `.ewp` 等 IDE 工程文件 —— 这是 IDE 责任
- ❌ 不下载或安装工具链
- ❌ 不创建源代码（`Core/Src/main.c` 等）—— 这是 CubeMX / 用户责任
- ❌ 不修改 `.trellis/` 内已经由 trellis init / 模板写好的内容
- ❌ 不做 `git push`、不做 `svn commit` —— 严格按 version-control.md 触发词规则
