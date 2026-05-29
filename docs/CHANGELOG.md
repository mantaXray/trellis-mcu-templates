# CHANGELOG

> 只记录**下游会感知到**的跨项目影响。一行一条，按日期倒序，前缀 `BREAKING:` / `ADD:` / `DEL:` / `FIX:`。BREAKING 必须附下游迁移命令。详细约定见 [`MAINTENANCE.md`](MAINTENANCE.md) §7.2。

## 2026-05-29

- ADD: `scripts/push-all.sh` 一键推送三个 remote（origin / gitee / github）。单个 remote 失败不中断，按 remote 类型给针对性修复建议（VPN / SSH / HTTP 代理）。
- ADD: `docs/MAINTENANCE.md` 维护手册（10 章 + 2 附录），覆盖日常编辑、反哺、CI、变更记录、节奏、紧急情况。
- ADD: pre-push hook 模板（见 `MAINTENANCE.md` §6.3），每次 `git push` 自动跑 `validate.py`。维护者本地安装一次。
- ADD: `docs/CHANGELOG.md` 起步（本文件）。
- BREAKING: 把 `specs/mcu-stm32-base/guides/bootstrap-checklist.md`、`external-knowledge-base.md`、`pitfall-feedback-loop.md` 移到 `docs/`，不再随 `trellis init` 发到下游项目。下游 `.trellis/spec/` 文件数从 23 降到 20。
  - 下游迁移：
    ```bash
    cd <下游项目>
    rm -f .trellis/spec/guides/bootstrap-checklist.md \
          .trellis/spec/guides/external-knowledge-base.md \
          .trellis/spec/guides/pitfall-feedback-loop.md
    git commit -am "chore(spec): drop maintainer-only docs from local spec"
    ```
  - 这些文档现在只存在于模板仓库 `docs/`，由维护者参考；AI agent 不读它们。
- ADD: AGENTS.md managed block 新增 `<!-- MCU-BOOTSTRAP:MODE <codex-only|dual-track|claude-only> -->` 标记。`mcu-bootstrap` skill Step 4 现在会询问协同模式并写入。
  - 下游已 bootstrap 的项目升级方式：手工编辑 `AGENTS.md` 的 managed block，在 `STARTED`/`DONE` 行后加一行 `<!-- MCU-BOOTSTRAP:MODE codex-only -->`（按团队实际填）；或重跑 mcu-bootstrap skill 让它补。
- ADD: `specs/mcu-stm32-base/firmware/index.md` 改为 Tier 1（必读）+ Tier 2（按变更触发）分层。默认任务时读量从 7 个文件 (~700 行) 降到 2 个文件 + index 本身 (~70 行)。
  - 下游无破坏：所有 Tier 2 文件原位不动，只是触发条件更明确。

## 2026-05-28

- ADD: `templates/` 目录存放 4 份"规范源"内容（`agents-bootstrap-block.md` / `gitignore-block.txt` / `svn-ignore.list` / `doc-readme.md`），是 SKILL.md 和 bootstrap-checklist.md 内嵌副本的标准答案。
- ADD: `scripts/validate.py` Python 版验证器（替代 `validate.ps1`），跨平台。新增字节级 drift 检测：内嵌副本必须与 `templates/` 一致。
- ADD: `.github/workflows/validate.yml` GitHub Actions CI，push/PR 自动跑 validator。
- DEL: `scripts/validate.ps1`（被 `validate.py` 替代）。下游不受影响（脚本只在模板仓库内部用）。
- DEL: `specs/mcu-stm32-base/firmware/pitfalls/` 空目录及其 `README.md`。
  - 拆分约定改为：单分类 >10 条时拆到 `firmware/pitfalls-<category>.md` 同级文件（不再用子目录）。
  - 下游迁移（如果之前从模板拿到了这个目录）：
    ```bash
    cd <下游项目>
    rm -rf .trellis/spec/firmware/pitfalls/
    git commit -am "chore(spec): drop unused pitfalls/ subdirectory"
    ```
- ADD: README 命令示例重排，Codex-only 提到第一位并标注"团队默认"，反映团队实际工具栈。
