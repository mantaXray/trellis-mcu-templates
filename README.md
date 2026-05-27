# trellis-mcu-templates

> 合鲸科技 MCU 固件项目的 Trellis 通用模板 registry。给 `trellis init --template ... --registry ...` 使用。
>
> **主流工具链**：IAR Embedded Workbench for Arm（公司约 90% MCU 项目）。少数 STM32CubeIDE+GCC legacy 项目共用本模板，spec 内对工具链差异有明确标注。

## 使用方法（新 MCU 项目两步完成）

### 第 1 步：跑 trellis init，同时拉 spec + bootstrap skill

```bash
# 进入新项目目录
cd /path/to/new-mcu-project

# 一行命令拉两个模板
trellis init -y --claude --codex \
  -t mcu-stm32-base \
  -t mcu-bootstrap \
  -r http://<origin URL>/Xray/trellis-mcu-templates
```

完成后：

```
.trellis/spec/                    ← 来自 mcu-stm32-base (type:spec)
├── guides/
│   ├── claude-codex-collaboration.md
│   └── bootstrap-checklist.md
└── firmware/
    ├── version-control.md
    └── coding-standard.md

.claude/skills/mcu-bootstrap/     ← 来自 mcu-bootstrap (type:skill)
└── SKILL.md                       ← 自动化引导脚本
```

### 第 2 步：在 Claude Code（或 Codex）里跑一次 bootstrap

```
/mcu-bootstrap
```

skill 会：

1. 检测项目工具链（IAR 主流 / STM32CubeIDE+GCC legacy）
2. 检测是否在 SVN 工作副本下
3. 询问项目代号、初始版本号、git remote URL、是否需要 ALGO_VERSION
4. 自动完成：
   - 追加 `AGENTS.md`（在 TRELLIS:END 之后）
   - 写项目根 `.gitignore`（按工具链选模板）
   - 创建 `doc/` + `doc/README.md`
   - 在 `User/App/System/define.h`（IAR）或 `User/App/Inc/define.h`（CubeIDE）写版本宏
   - 设 SVN `svn:ignore` 属性（不提交 SVN）
   - 绑定 git remote（不 push）
5. 在 `AGENTS.md` 加 `<!-- MCU-BOOTSTRAP:DONE -->` 标记，**幂等**——重复跑会跳过

### 已有项目追加 / 覆盖模式

```bash
# 只补充缺失文件，不覆盖现有
trellis init --append -t mcu-stm32-base -r http://<origin URL>/Xray/trellis-mcu-templates

# 强制覆盖现有 spec
trellis init --overwrite -t mcu-stm32-base -r http://<origin URL>/Xray/trellis-mcu-templates
```

## 当前模板清单

见 `index.json`。

| ID | 类型 | 适用场景 |
|---|---|---|
| `mcu-stm32-base` | spec | 通用 MCU 固件 spec 套件（AI 协同 + 提交规范 + 编码规范） |
| `mcu-bootstrap` | skill | trellis init 之后一键收尾（写 .gitignore / AGENTS / svn:ignore / 版本宏 / git remote） |

## 维护规则

- 模板内容**不许包含**项目专属命名（如具体项目名、Modbus 寄存器编号、Gitea repo URL 等）—— 用占位符或抽象描述
- 模板演进时遵循同 trellis 主仓库的版本约定，在 commit message 里明确变更点
- 新增模板时同步更新 `index.json` 和本 README
- 模板内容学到新 lesson 时，从下游项目反哺回来（手动 diff + 合并），不要让模板长期落后
