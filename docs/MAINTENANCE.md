# trellis-mcu-templates 维护手册

> 本文档同时给两类读者看：
> - **你**（人类 supervisor）——看顶部「Supervisor 模式」一节就够了，知道怎么喊 AI 干活
> - **AI**（Codex / Claude，被你喊去改东西的）——看下面 §0~§10 的详细 SOP，按章节执行
>
> 本文档不会被 `trellis init` 装到下游项目，住在 `docs/` 目录里。

---

## Supervisor 模式：喊 AI 干活（推荐，先看这里）

> 如果你**不想自己跑命令、不想逐字写 spec**，只想告诉 AI 想要什么，看这一节就够了。下面 §0~§10 是给 AI 自己读的执行细节，你不用逐行学。

### S.1 你 vs AI 的分工

**关键认知**：本仓库**所有内容**——包括 `specs/` 下面的规则、坑点知识库、新增 spec 文件、文档措辞、CHANGELOG——**都是 AI 写**，不是你自己逐字写。你的角色永远是"**提需求 + review**"，哪怕最细节的 spec 内容也一样。开发实际项目时踩了什么坑、你想固化成什么规则，你**口头说一句**，AI 落字。

| 你做 | AI 做 |
|---|---|
| 用一句话告诉 AI 想要的结果（包括 spec/pitfall 内容） | 找对位置、改文件、改索引、按格式写 |
| review 改完的 diff（看动了啥、写得对不对） | 跑 `validate.py`、写 CHANGELOG、`git commit` |
| 决定要不要采纳 / 要不要反哺到模板 | 按你的决定去执行 |
| 网络出问题时切代理 / 检查 Clash | 报告失败、给修复建议、重试 |
| 确认 commit 信息合理 | 用 `bash scripts/push-all.sh` 推三个 remote |

### S.2 常用请求模板（口语化即可，下面只是示例）

**加一条坑点 / 把开发经验固化成规则**：
```
我开发 XXX 项目时踩了个坑：<现象一句话描述>。这种坑别的 MCU 项目也会遇到，帮我抽成一条 pitfall 加进模板。
```

```
帮我在 firmware/pitfalls.md 加一条新坑：<现象>，分类 <PIT-DMA / PIT-RTOS / PIT-MEM / ...>。
```

**改已有内容**：
```
帮我改 README.md，把 <X 那段> 改成 <Y>。
```

```
firmware/coding-standard.md 里关于注释那段太啰嗦，帮我精简。
```

**新增 spec 文件**：
```
帮我新增一个 trigger spec 文件 <name>.md，主题是 <CAN 总线 / SPI flash / I2S 音频 / ...>，先放草稿我 review。
```

**从下游项目反哺**：
```
从下游项目反哺一条坑点：项目里的原始描述是 "<原话或一段截图文字>"，去敏后写进模板。
```

**审核 / 询问**：
```
review 一下我刚改的，validator 过了没？还有哪里要补？
```

```
最近 N 个 commit 改了啥？给我个概览。
```

**推送 / 紧急**：
```
帮我推一下所有 remote。
```

```
紧急：上一个 commit 改坏了，帮我 revert 然后重推。
```

### S.3 AI 改完后你 review 什么

通常只看两件事：

1. **diff 范围**——AI 是不是只动了你要它动的？没乱改其他文件？
   ```bash
   git diff HEAD~1            # 看上一次 commit 改了啥
   git log --stat -1          # 看上一次动了哪些文件、各动了多少行
   ```
2. **CHANGELOG 那一条**——分类对不对（BREAKING/ADD/DEL/FIX）？BREAKING 是否附了下游迁移命令？

不满意就直接告诉 AI："这条不对，改成 XXX" 或 "revert 上一个 commit"。AI 会处理。

### S.4 AI 干不了的事（你必须自己做）

| 事 | 原因 |
|---|---|
| 启动 / 关闭 Clash Verge | AI 不能操作你电脑的 GUI 应用 |
| 配 GitHub SSH key | 涉及私钥，AI 不该碰 |
| 决定一条坑点是"项目本地"还是"反哺模板" | 这是判断题，需要你拍板 |
| 在 Trellis registry 服务器上发新版 | 服务器配置不在本仓库范围 |
| 答应别人的承诺、回复 issue | 沟通这部分必须你自己 |

### S.5 出问题怎么办

| 现象 | 你说一句话给 AI |
|---|---|
| validator 红了 | "validator 报错了，看一下" |
| GitHub 推不上去 | "GitHub 推不上去，我已经开了 Clash 7897，看一下"（AI 会查 git 代理配置） |
| AI 改错了 | "上个 commit 不对，revert 一下" |
| 想撤回还没 push 的改动 | "撤掉刚才的本地改动" |
| 不确定要不要做某件事 | "我想做 X，会不会破坏下游？给我看下影响面再决定" |

### S.6 第一次配置（一次性，以后免）

| 事 | 做法 |
|---|---|
| 装 git pre-push hook（每次 push 前自动跑 validator） | 让 AI 装："帮我装 pre-push hook" |
| 配 Clash 代理给 git（GitHub 推得上去） | 让 AI 配："帮我配 git 代理走 Clash 7897"，本机已配 |
| 加 `github` / `gitee` remote | 已经配好（见 `git remote -v`） |
| 在三个 remote 配 branch protection（强制 PR + CI 绿才能合并） | 按 [`branch-protection-setup.md`](branch-protection-setup.md) 在网页上操作，AI 干不了这件事 |

---

> 下面是 AI 执行任务时的详细 SOP（§0~§10）。**你（人类 supervisor）可以略过**——AI 在执行你的请求时会自己查阅。

---

## 0. 这是什么仓库

**trellis-mcu-templates** 是一个 Trellis 模板 registry，专门给 MCU 固件项目用。下游项目通过：

```bash
trellis init -t mcu-stm32-base -t mcu-bootstrap -r <registry-url>
```

把 `.trellis/spec/`（spec 知识库）和 `.claude/skills/` 或 `.codex/skills/`（bootstrap skill）拉到自己项目根。

**核心使用场景**：
- 团队**主要用 Codex CLI**，少量用 Claude + Codex 双轨
- 平台是 **Windows + IAR Embedded Workbench / STM32CubeIDE+GCC**
- 双轨版本控制：**Git + SVN** 共存
- 项目数：长期会持续新增，老项目也会回头升级模板

**这个仓库要解决什么**：
1. 让 AI agent 在每个新 MCU 项目里不需要从头学一遍坑点
2. 让任务相位（planning）和代码相位（in_progress）严格分开，AI 不乱动代码
3. 让单个项目踩过的坑能反哺到模板，避免别的项目再踩
4. 维护成本不超过"每月 10 分钟检查 + 每个项目结束反哺一次"

---

## 1. 仓库目录结构

```
trellis-mcu-templates/
├── index.json                    # 模板清单，trellis 用这个发现可装的模板
├── README.md                     # 给下游用户看的入门
├── specs/                        # ← trellis init 会装到下游 .trellis/spec/
│   └── mcu-stm32-base/
│       ├── firmware/             #   AI 任务时读的规则
│       └── guides/               #   AI 流程导航/协同规则
├── skills/                       # ← trellis init 会装到下游 .claude/skills/ 或 .codex/skills/
│   └── mcu-bootstrap/
│       └── SKILL.md              #   一键收尾新项目的 skill
├── templates/                    # ← 仅本仓库内部用，不发下游
│   ├── README.md                 #   说明本目录契约
│   ├── agents-bootstrap-block.md
│   ├── gitignore-block.txt
│   ├── svn-ignore.list
│   └── doc-readme.md
├── docs/                         # ← 仅维护者文档，不发下游
│   ├── MAINTENANCE.md            #   本文件
│   ├── bootstrap-checklist.md    #   AI 全不可用时的手工 fallback
│   ├── pitfall-feedback-loop.md  #   坑点反哺 SOP
│   ├── external-knowledge-base.md#   搭建外部知识库的指南
│   └── CHANGELOG.md              #   (推荐) 跨项目影响的变更记录
├── scripts/
│   └── validate.py               # 一致性检查器
└── .github/workflows/validate.yml# CI 配置（如果用 GitHub）
```

**记住这一条**：每次新增文件，问自己**「AI 在跑下游项目任务时会读吗」**。
- 会读 → `specs/`
- 不会读、但 AI bootstrap 时需要 → `skills/` 或 `templates/`
- 只是给我自己/团队维护看 → `docs/`

---

## 2. 日常编辑流程

### 2.1 改一条已有规则

最常见的场景。例如修改 `pitfalls.md` 里 `PIT-DMA-001` 的描述。

```bash
# 1. 改文件
# (在编辑器里改 specs/mcu-stm32-base/firmware/pitfalls.md)

# 2. 本地验证
python scripts/validate.py

# 3. 通过后提交
git add specs/mcu-stm32-base/firmware/pitfalls.md
git commit -m "fix(pitfalls): clarify PIT-DMA-001 boundary"

# 4. 推送到所有 remote（私有 Git 镜像 + Gitee + GitHub）
bash scripts/push-all.sh
```

**绝对不要在 validator 红的时候 push**。validator 红意味着仓库不自洽，下游 `trellis init` 拉到的内容会有问题。

**关于 `scripts/push-all.sh`**：依次推送 origin / gitee / github 三个 remote，单个 remote 失败不中断后续。任一失败会按 remote 类型给出针对性修复建议（私有 Git 镜像检查 VPN、Gitee 检查外网、GitHub 切网络/SSH/代理）。如果只想推单个 remote，仍可用 `git push <remote> main`。

### 2.2 改"内嵌副本"的内容

涉及 4 种内容时**必须三处同步改**：
- `.gitignore` managed block
- `svn:ignore` 列表
- `AGENTS.md` managed block
- `doc/README.md` 模板

**流程**（以 `.gitignore` 加一条 `*.pyc` 为例）：

```bash
# 1. 改"标准答案"
#    templates/gitignore-block.txt 里加一行 *.pyc

# 2. 同步改 skills/mcu-bootstrap/SKILL.md 里嵌入的那段 .gitignore 代码块

# 3. 同步改 docs/bootstrap-checklist.md 里嵌入的那段 .gitignore 代码块

# 4. validate.py 会逐字节比对三处。漏改任何一处会红
python scripts/validate.py

# 5. 三处对齐后 commit
git add templates/gitignore-block.txt skills/mcu-bootstrap/SKILL.md docs/bootstrap-checklist.md
git commit -m "feat(bootstrap): ignore *.pyc in project .gitignore"
git push
```

**记忆要点**：先改 `templates/`，validator 就会"指引"你后面该改哪两个文件。

### 2.3 加一条新 MCU 坑点

```bash
# 1. specs/mcu-stm32-base/firmware/pitfalls.md
#    在合适的分类下加一条新条目，分配稳定 ID：PIT-<AREA>-<NNN>
#    例如新增 PIT-DMA-003

# 2. specs/mcu-stm32-base/firmware/pitfalls-index.md
#    在快速索引和（如果适用）症状入口里加一行链接到新 ID

# 3. 检查 pitfalls.md 该分类是否已超过 10 条
#    如果超了，按 docs/pitfall-feedback-loop.md §5 拆到 pitfalls-<category>.md

# 4. 验证 + 提交
python scripts/validate.py
git commit -am "feat(pitfalls): add PIT-DMA-003 (xxx)"
```

**新坑点必备字段**（写在 pitfalls.md 里）：
- 稳定 ID
- 一句话规则（默认行为或禁止项）
- 触发条件（什么任务/什么 MCU/什么外设时要读这条）
- 验证方式（怎么知道有没有踩坑）

### 2.4 加一个新 trigger spec 文件

例如新增 `can-bus.md` 给 CAN 总线相关任务用。

```bash
# 1. 写文件
#    specs/mcu-stm32-base/firmware/can-bus.md

# 2. 把它挂到触发表
#    编辑 specs/mcu-stm32-base/firmware/index.md
#    在 "Tier 2 — 按变更类型触发" 表格里加一行

# 3. validate.py 如果想为新文件加存在性断言
#    编辑 scripts/validate.py，在第 6 节加：
#    can_bus = read_text("specs/mcu-stm32-base/firmware/can-bus.md")
#    assert_contains(can_bus, "<某个稳定关键词>", "can-bus.md 应包含 xxx")
#    并把 can_bus 加进 generic_template_text 列表

# 4. 验证 + 提交
python scripts/validate.py
git commit -am "feat(spec): add can-bus.md trigger spec"
```

### 2.5 加一个新 skill

例如做一个 `mcu-release` skill 帮助打 release。

```bash
# 1. 建目录与 SKILL.md
mkdir -p skills/mcu-release
# 写 skills/mcu-release/SKILL.md，frontmatter 必须有 name: mcu-release 和 description: ...

# 2. 注册到 index.json
#    在 templates 数组里追加一项：
#    { "id": "mcu-release", "type": "skill", "name": "...", "description": "...", "path": "skills/mcu-release", "tags": [...] }

# 3. README.md 的清单表格加一行

# 4. 验证 + 提交
python scripts/validate.py
git commit -am "feat(skills): add mcu-release skill"
```

---

## 3. 下游项目反哺流程

**核心理念**：项目本地踩坑 → 项目内 spec 化 → 抽象去敏 → 反哺模板。

```
下游 MCU 项目              本仓库
─────────────              ────────
doc/pitfalls.md            (项目现场细节，不上模板)
    ↓
.trellis/spec/firmware/pitfalls.md   (项目本地规则)
    ↓ 判断"是 MCU 通病"
    ↓ 去敏：去掉项目代号/寄存器编号/客户信息/具体路径
    ↓
specs/mcu-stm32-base/firmware/pitfalls.md  (加 PIT-XXX-NNN 条目)
specs/mcu-stm32-base/firmware/pitfalls-index.md  (加索引行)
    ↓
git push
    ↓
其他下游项目下次 trellis init --append 拉到
```

**判断"能不能反哺"的 4 条**（来自 `docs/pitfall-feedback-loop.md`）：
1. 跨项目常见
2. 与 MCU 工具链/RTOS/外设/协议有关
3. 能写成"检查项/禁止项/默认策略"
4. 已去掉项目代号、客户信息、具体寄存器编号、现场日期、一次性路径

满足 4 条才反哺；不满足留在项目本地。

**完整 SOP** 在 `docs/pitfall-feedback-loop.md`，反哺前必读一遍。

---

## 4. 下游项目同步流程

下游项目想升级到模板新版本时：

### 4.1 只补新文件（安全，默认）

```powershell
cd <下游项目>
trellis init --append -t mcu-stm32-base -r <registry-url>
```

`--append` 只补 `.trellis/spec/` 里下游缺失的新文件，**不会覆盖已存在的文件**。适合：
- 模板加了新的 trigger spec（如 `can-bus.md`）
- 模板加了新 skill
- 模板加了新坑点（pitfalls.md 已存在的话不会被覆盖，新坑点不会自动补，需要手动 merge）

### 4.2 同步已有文件的新版本

```powershell
# 不要直接 --overwrite。先 diff
git -C <模板仓库本地路径> show HEAD:specs/mcu-stm32-base/firmware/coding-standard.md > /tmp/template-version.md
diff /tmp/template-version.md .trellis/spec/firmware/coding-standard.md

# 手动 merge：把模板新内容合到下游版本，保留下游的项目特化
# 然后下游 git commit
```

**永远不要**：

```powershell
trellis init --overwrite -t mcu-stm32-base ...  # 会丢掉下游所有项目特化
```

除非**百分百确认**下游没有本地化改动。

### 4.3 大重构的下游迁移

像本仓库历史上把 `guides/bootstrap-checklist.md` 移到 `docs/` 这种结构性改动：
- `--append` 不会删下游已有的旧文件
- 下游会有"旧位置 + 新位置"两份冗余
- 维护者需要在 `docs/CHANGELOG.md` 明确写出迁移指引：「下游需要手工执行 `rm .trellis/spec/guides/bootstrap-checklist.md`」

---

## 5. 重命名 / 移动文件 / 大重构

**前置思考**：会不会破坏下游已存项目？破坏程度多大？是否需要写迁移指引？

### 检查清单

```
□ 1. 用 git grep 或 Grep 工具找全所有引用旧路径的地方
       git grep -l "旧路径"
       重点查：
         - specs/ 里的 markdown 链接（[xxx](xxx)）
         - skills/ 里 SKILL.md 引用的 spec 路径
         - templates/ 里的内嵌副本（如果改的是被嵌入的内容）
         - README.md 的目录树
         - scripts/validate.py 的 read_text() 路径常量和断言
         - 其它 docs/ 文档
□ 2. 实际移动文件
       git mv 旧路径 新路径    （文件已被 git 追踪时）
       mv 旧路径 新路径        （文件还没追踪时）
□ 3. 改所有引用
□ 4. 改 validate.py 的路径常量
□ 5. python scripts/validate.py 全绿
□ 6. 在 docs/CHANGELOG.md 加一条变更记录，标 BREAKING（如果会影响下游）
□ 7. commit message 也加 BREAKING: 前缀
□ 8. push
```

### 典型大重构案例

| 类型 | 是否破坏下游 | 必须写迁移指引 |
|---|---|---|
| 加新文件 | 否（--append 安全） | 否 |
| 删文件 | 是（下游残留） | 是 |
| 移动/重命名文件 | 是（下游残留旧文件） | 是 |
| 改文件内容 | 否（下游不会自动同步） | 否，但 CHANGELOG 记一笔 |
| 改 marker 格式（如 `MCU-BOOTSTRAP:MODE`） | 是（下游 AGENTS.md 旧 marker 不被识别） | 是 |
| 改 `index.json` 字段名 | 是（旧 trellis CLI 可能不兼容） | 是 |

---

## 6. 验证与 CI

### 6.1 `scripts/validate.py` 在检查什么

简要清单：

1. **`index.json` 结构合法**：每个 template 有 id/type/path，skill 类型必须有 SKILL.md
2. **泛化清洁**：模板里不能出现项目代号、客户信息、内网 IP、`FatFs`/`LVGL` 等特化默认
3. **默认工具链中立**：不能让 IAR 看起来是默认、CubeIDE 看起来是"legacy"
4. **README 必须包含**：模板 ID、registry-url 占位、关键文件名引用、`validate.py` 引用
5. **SKILL.md 与 docs/bootstrap-checklist.md 必须包含特定关键词**：`MCU-BOOTSTRAP:STARTED/DONE/MODE`、`PowerShell`、`Bash`、`session_auto_commit` 等
6. **`.gitignore` 顺序**：`*.hex` 必须在 `!Bin/*.hex` 之前
7. **各 spec 必须包含特定章节标题**：例如 `verification.md` 要有 "Required Checks By Change Type"
8. **pitfalls 系列**：必须有 `PIT-DMA-001` / `PIT-REPO-001` 等稳定 ID
9. **`templates/` 与内嵌副本字节一致**：SKILL.md 和 docs/bootstrap-checklist.md 必须包含 `templates/` 里 4 份规范源的逐字节副本
10. **`svn-ignore.list` 每条都出现在 SKILL.md 和 checklist.md 里**

### 6.2 本地必须每次跑

**任何 commit 前必跑**：

```bash
python scripts/validate.py
```

绿了再 commit。红了不要硬 push。

### 6.3 给自己一个 git pre-push hook

强烈推荐。一次配置，自动拦截。

```bash
# 在仓库根目录跑：
cat > .git/hooks/pre-push <<'EOF'
#!/bin/sh
python scripts/validate.py || {
  echo "validate.py failed; push blocked. Fix or use --no-verify to bypass." >&2
  exit 1
}
EOF
chmod +x .git/hooks/pre-push
```

之后每次 `git push` 会自动跑 validator。挂了就推不上去。

### 6.4 CI（持续集成）

仓库根目录有 `.github/workflows/validate.yml`，**如果**仓库托管在 GitHub，每次 push 和 PR 会自动跑 validator。

如果仓库在**内网 Gitea**：
- Gitea 1.19+ 支持 Gitea Actions，语法兼容 GitHub Actions。把 `.github/workflows/` 复制到 `.gitea/workflows/` 试试
- Gitea 不开 Actions 时：只能靠维护者本地 pre-push hook 兜底

如果仓库在**纯 SVN / 没有 CI**：
- pre-commit / pre-push hook 是唯一防线
- 加一条节奏：**每月手动跑一次 `validate.py` + grep 检查硬编码**（见 §10）

---

## 7. 版本与变更记录

### 7.1 现状

目前**没有正式版本号**。下游项目唯一区分"自己用的是哪版模板"的方式是看 `.trellis/spec/` 文件的内容或本地 git 历史。

### 7.2 暂时够用的 CHANGELOG 约定

在 `docs/CHANGELOG.md` 维护跨项目影响的变更（不是每次 commit 都记，只记**下游会感知到**的）：

```markdown
# CHANGELOG

## 2026-05-29
- BREAKING: 把 `guides/bootstrap-checklist.md`、`guides/external-knowledge-base.md`、`guides/pitfall-feedback-loop.md` 移到 `docs/`，不再发到下游。
  - 下游迁移：`rm -f .trellis/spec/guides/{bootstrap-checklist,external-knowledge-base,pitfall-feedback-loop}.md`
- ADD: AGENTS.md managed block 新增 `MCU-BOOTSTRAP:MODE` 标记。下游升级后 bootstrap 重跑会询问模式。
- ADD: `firmware/index.md` 改为 Tier 1 / Tier 2 分层，默认读量从 ~700 行降到 ~70 行。

## 2026-05-28
- ADD: `templates/` 目录 + `scripts/validate.py` Python 版 + `.github/workflows/validate.yml` CI。
- DEL: `scripts/validate.ps1`（被 validate.py 替代）。
- DEL: 空的 `specs/mcu-stm32-base/firmware/pitfalls/` 目录；分类拆分改为 `pitfalls-<category>.md` 同级文件。
```

**约定**：
- 一条 = 一个跨项目影响
- 前缀 `BREAKING:` / `ADD:` / `DEL:` / `FIX:`
- BREAKING 必须附下游迁移命令
- 按日期倒序

### 7.3 未来上 semver

团队规模上来后再做：
- 给 `index.json` 每个 template 加 `version: "x.y.z"` 字段
- 给会被 spec 反哺的核心文件（pitfalls.md、version-control.md）头部加 `<!-- SPEC-VERSION: x.y.z -->` 注释
- BREAKING 变更升 major，ADD 升 minor，FIX 升 patch
- CHANGELOG 按 version 分段

---

## 8. 新人 / 自己几个月后回来时的读法

读完这 6 个文件就能动手：

```
1. README.md                                  仓库总入口，30 秒
2. docs/MAINTENANCE.md (本文件)               维护 SOP，10 分钟
3. specs/mcu-stm32-base/firmware/index.md     下游 AI 任务入口长啥样
4. specs/mcu-stm32-base/firmware/pitfalls.md  模板的实际价值密度在这
5. skills/mcu-bootstrap/SKILL.md              bootstrap 流程
6. scripts/validate.py                        一致性边界在哪
```

读完这 6 个 ≈ 20 分钟。剩下的文件需要的时候按需读。

---

## 9. 常见陷阱

| # | 陷阱 | 怎么避免 |
|---|---|---|
| 1 | 改了 `.gitignore` 块只改一处 | validator 会拦你，看错误信息按指引同步另外两处 |
| 2 | 加了新 trigger spec 但没挂到 `firmware/index.md` 触发表 | 自己 review 时刻意检查；validator 不查这个 |
| 3 | 把项目代号 / 寄存器编号 / 客户信息 / 内网 URL 写进模板 | validator 有 `org_specific_patterns` 黑名单兜底，但不全。push 前自己 `git grep` 一遍 |
| 4 | 改 SKILL.md 改了步骤编号（Step 5 → Step 4），但 docs/checklist 还说 "Step 5" | grep `Step \d` 全仓库查 |
| 5 | 下游 spec 反哺时把现场细节一起带回来 | 反哺前按 `docs/pitfall-feedback-loop.md` §"去敏规则" 自查 |
| 6 | 用 `git push --force` 推 main | 不允许。模板仓库的下游已经在依赖你的 commit hash；force-push 会让他们的 `--append` 状态错乱 |
| 7 | 一时兴起删了 `templates/` 或 `docs/` 里的文件，validator 拦不住所有 | 删之前先在 CHANGELOG 写 BREAKING + 迁移指引 |
| 8 | 模板里出现绝对路径 `D:\00_Work\...` | 用相对路径或占位符 `<repo-root>`；validator 不查这个 |
| 9 | 提交后才发现内嵌副本漂移了 | 上 pre-push hook（§6.3） |
| 10 | 老下游项目几个月没升级、突然来问"为什么 marker 格式变了" | CHANGELOG 提前留好迁移命令，告诉他们对照执行 |

---

## 10. 维护节奏建议

| 频率 | 动作 | 时长 |
|---|---|---|
| **每完成一个下游项目** | 翻一遍这个项目的 `doc/pitfalls.md`，看有没有可反哺的；走 §3 反哺流程 | 5-15 分钟 |
| **每周（如果当周有改动）** | `git log --oneline` 看本周改了啥，CHANGELOG 漏记的补上 | 2 分钟 |
| **每月一次** | `git grep` 找硬编码（`192\.168\.` / 项目代号 / `FatFs` 等）；跑一次 `validate.py`；review `docs/CHANGELOG.md` 写没写漏 | 10 分钟 |
| **每季度一次** | 重读 `pitfalls.md` 和 `pitfalls-index.md`，删过时条目、合并相似条目；看 `firmware/index.md` 的 Tier 1/Tier 2 分层是否还合理 | 30 分钟 |
| **每半年一次** | 整体重读本手册，更新跟仓库实际不一致的地方 | 1 小时 |
| **每次大改之前** | 在 `docs/CHANGELOG.md` 写一行；评估下游迁移成本；BREAKING 标好 | 5 分钟 |

---

## 附录 A：全文件清单与读者

| 文件 | 读者 | 修改频率 | 改之前必读章节 |
|---|---|---|---|
| `index.json` | trellis CLI | 仅加 skill / spec 时 | §2.5 |
| `README.md` | 下游用户 | 命令/目录变化时 | - |
| `specs/.../firmware/index.md` | AI（每个任务） | 加 Tier 2 文件时 | §2.4 |
| `specs/.../firmware/pitfalls.md` | AI（按 trigger） | 加坑点时 | §2.3 |
| `specs/.../firmware/pitfalls-index.md` | AI（每个任务，Tier 1） | 加坑点时 | §2.3 |
| `specs/.../firmware/project-context.md` | AI（每个任务，Tier 1） | 几乎不改（项目填空模板） | - |
| `specs/.../firmware/<其他 trigger>.md` | AI（按 trigger） | 该领域规则变化时 | §2.4 |
| `specs/.../guides/index.md` | AI（按需） | 加 guide 时 | §2.4 |
| `specs/.../guides/claude-codex-collaboration.md` | AI（按需） | 协同规则变化时 | - |
| `specs/.../guides/task-process.md` | AI（按需） | Trellis 流程变化时 | - |
| `specs/.../guides/debug-symptom-index.md` | AI / 项目本地参考 | 几乎不改 | - |
| `skills/mcu-bootstrap/SKILL.md` | AI（bootstrap 时） | bootstrap 流程变化时 | §2.2 |
| `templates/*` | validate.py | 改"内嵌内容"时 | §2.2 |
| `docs/MAINTENANCE.md` | 维护者（你） | 流程变化时 | - |
| `docs/bootstrap-checklist.md` | 维护者 / 极端 fallback | 同 SKILL.md 变化时 | §2.2 |
| `docs/pitfall-feedback-loop.md` | 维护者 | 反哺规则变化时 | - |
| `docs/external-knowledge-base.md` | 维护者 | 几乎不改 | - |
| `docs/CHANGELOG.md` | 维护者 / 下游升级时查 | 每个跨项目影响的改动 | §7.2 |
| `scripts/validate.py` | CI / 维护者 | 加新检查时 | §6.1 |
| `.github/workflows/validate.yml` | GitHub Actions | 几乎不改 | §6.4 |

---

## 附录 B：紧急情况

**validator 突然全红，但我啥也没改**：
- 拉最新 main 再跑一遍：`git pull && python scripts/validate.py`
- 还红：看 `git log -p scripts/validate.py` 最近改了啥断言

**下游项目报"trellis init --append 失败"**：
- 检查 registry 是否在线
- 检查 `index.json` 是否合法 JSON（`python -c "import json; json.load(open('index.json'))"`）
- 检查模板 `path` 指向的目录是否存在

**我不小心 push 了带客户信息的 commit**：
- 立刻 `git revert <hash>` 或 `git reset --hard HEAD^ && git push --force-with-lease`（**仅在确认没有其他人 pull 到时才用 force**）
- 通知所有团队成员 `git pull --rebase`
- 如果信息很敏感，按 BFG / `git filter-repo` 重写历史，并通知 registry 用户重新拉

**模板出了一个回退不掉的错误版本，所有下游都拉到了**：
- 立刻在主分支推一个 fix commit
- 在 `docs/CHANGELOG.md` 写明问题和修复
- 通知团队 `trellis init --append` 拉新版（如果是新增文件可修复）或手工 patch（如果是已存文件变化）

---

**最后一句话**：这个仓库的核心价值不是文件数量，是**模板里每一条规则都能让 AI 在新项目里少踩一次坑**。维护时多问自己「这条规则是不是真能让下一个项目少踩一次坑？如果不能，要不要删？」
