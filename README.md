# trellis-mcu-templates

> 合鲸科技 MCU 固件项目的 Trellis 通用模板 registry。给 `trellis init --template ... --registry ...` 使用。

## 使用方法

### 在新 MCU 项目初始化

```bash
# 进入新项目目录
cd /path/to/new-mcu-project

# 跑 trellis init，附带本 registry 的模板
trellis init -y --claude --codex \
  -t mcu-stm32-base \
  -r http://<origin URL>/Xray/trellis-mcu-templates
```

完成后 `.trellis/spec/` 下会出现：

```
.trellis/spec/
├── guides/
│   ├── claude-codex-collaboration.md      # AI 协同硬规则
│   └── bootstrap-checklist.md             # 模板装完后要手动做的事
└── firmware/
    ├── version-control.md                  # Git/SVN 双轨提交规范
    └── coding-standard.md                  # 公司 C 编码规范
```

### 在已有项目追加模板（不覆盖已有 spec）

```bash
trellis init --append \
  -t mcu-stm32-base \
  -r http://<origin URL>/Xray/trellis-mcu-templates
```

### 强制覆盖已有 spec

```bash
trellis init --overwrite \
  -t mcu-stm32-base \
  -r http://<origin URL>/Xray/trellis-mcu-templates
```

## 装完模板后的手动步骤

`trellis init -t` 只能写入 `.trellis/spec/`。**项目根级的配置文件（`.gitignore`、`AGENTS.md` 附录、`doc/` 目录命名约定）需要参考新项目内 `.trellis/spec/guides/bootstrap-checklist.md` 手动完成**。

## 当前模板清单

见 `index.json`。

| ID | 类型 | 适用场景 |
|---|---|---|
| `mcu-stm32-base` | spec | 通用 MCU 固件项目（覆盖 AI 协同 + 提交规范 + 编码规范） |

## 维护规则

- 模板内容**不许包含**项目专属命名（如具体项目名、Modbus 寄存器编号、Gitea repo URL 等）—— 用占位符或抽象描述
- 模板演进时遵循同 trellis 主仓库的版本约定，在 commit message 里明确变更点
- 新增模板时同步更新 `index.json` 和本 README
- 模板内容学到新 lesson 时，从下游项目反哺回来（手动 diff + 合并），不要让模板长期落后
