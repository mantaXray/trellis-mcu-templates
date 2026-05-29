# CHANGELOG

> 只记录**下游会感知到**的跨项目影响。一行一条，按日期倒序，前缀 `BREAKING:` / `ADD:` / `DEL:` / `FIX:`。BREAKING 必须附下游迁移命令。详细约定见 [`MAINTENANCE.md`](MAINTENANCE.md) §7.2。

## 2026-05-29

- ADD: 仓库开源准备（Phase 1）：
  - 新增 `LICENSE` (MIT)，2026 © mantaXray
  - README.md 加「外部读者」简介块，说明本仓库定位 + 默认设定可调整
  - 各处「公司 Gitea」等措辞统一改为「私有 Git 镜像」，避免假设外部读者也是公司团队
  - `scripts/validate.py` 新增 LICENSE 存在性断言
  - Phase 2（commit 历史 email 脱敏）将在下一个 commit 后用 `git filter-repo --email-callback` 处理，再 force push 三个 remote
- FIX: `docs/branch-protection-setup.md` 大幅重排：实测 GitHub 在 free personal + private 仓库下**两套机制都封了**——Rulesets 完全不可用，Branch protection rules 可创建但不强制执行（"won't be enforced... until you move to a GitHub Team or Enterprise organization account"）。文档优先级改为 **私有 Git 镜像 (主战场) > Gitee > GitHub (实质无服务端保护)**。给出 3 个对应选项：接受现状（推荐，靠 pre-push hook + 私有 Git 镜像保护）、付费、改 public。
- FIX: `docs/branch-protection-setup.md` GitHub 章节再次调整：实测 GitHub 限制 Rulesets 在 free personal + private 仓库里不可用（必须 Pro 付费或 Team Organization）。当前推荐路径改回 Branch protection rules（老版，free 可用）；Rulesets 降为"仓库 public 或账户升级后的迁移路径"。
- FIX: `docs/branch-protection-setup.md` GitHub 章节改以 **Repository Rulesets**（2023 新版）为推荐路径，旧版 Branch protection rules 降为"兼容路径"。Rulesets 颗粒度更细、跨分支可复用、bypass 控制更精细，是 GitHub 当前演进方向。
- ADD: README.md 顶部加「谁应该读这个文档？」3 行分流块，把下游用户和接手维护者分开引导。下游用户继续看「使用方法」，新维护者直接跳到 `docs/MAINTENANCE.md`。
- ADD: `docs/branch-protection-setup.md` 详细说明 GitHub / Gitee / 私有 Git 镜像三个 remote 各自怎么配 branch protection（强制 PR + CI 绿才能合并）。MAINTENANCE.md S.6 新增一行指向。
- FIX: `scripts/push-all.sh` origin 失败提示里去掉硬编码内网 IP，改为运行时从 `git remote get-url origin` 读取。仓库现在是 private 没影响；如果未来开源能避免内网信息泄漏（注意 git 历史里旧 IP 仍在，开源前需用 `git filter-repo` 清理）。
- ADD: `docs/MAINTENANCE.md` 顶部加 Supervisor 模式专节（S.1~S.6），明确"人 supervisor + AI 执行"的分工。原 §0~§10 详细 SOP 降级为 AI 自己执行时查阅的参考，人类不必逐行学。新增"spec/pitfall 内容也是 AI 写，人只口述需求 + review"的关键认知。
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
