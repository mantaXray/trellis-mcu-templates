# Branch Protection 配置

> 给希望"接手维护本仓库"的人保留一道审核闸门。Owner（你自己）也建议走 PR 流程，避免直接推 main 时绕过 CI。
>
> 优先级：**私有 Git 镜像 (origin) > Gitee > GitHub**。Gitea 是团队真实协作的主战场，必须配；Gitee/GitHub 是个人镜像，按需配。GitHub 在 free personal + private 账户下**服务端保护机制基本不可用**（详见 §GitHub 一节），可以直接跳过它的服务端保护。
>
> 注意服务端保护被绕过时，**本地 pre-push hook + 个人讨厌 force push 的习惯**仍然是有效的最后一道防线。

## 推荐的保护规则

| 规则 | 必要性 |
|---|---|
| 直接 push 到 `main` 被拦截（包括 owner） | 强烈推荐 |
| 必须经过 PR 才能合并 | 强烈推荐 |
| Validator CI 必须绿才能合并 | 强烈推荐 |
| 至少 1 个 reviewer approve 才能合并 | 推荐（仅你 owner 时可选） |
| 禁止 force push 到 `main` | 必须 |
| 禁止删除 `main` | 必须 |

---

## 私有 Git 镜像 (origin)  —— 优先级最高，必须配

团队真实协作发生在这里，没有 free/paid 限制，所有规则都能用。

1. 打开仓库 → **Settings** → **Branches**
2. **Protected Branches** 部分，点击 **Add Rule**
3. **Branch Name**: `main`
4. 勾选：
   - ✅ **Enable Push Whitelist** → 只允许 owner / specific users 直接推
   - ✅ **Enable Merge Whitelist** → 同上（控制谁能合并 PR）
   - ✅ **Require approval from N reviewers**（按团队规模填，单人或两人时填 1）
   - ✅ **Block on official review requests**
   - ✅ **Block on outdated branch**
5. 保存

> Gitea 1.19+ 也支持 Gitea Actions 做 status check；如果私有 Git 镜像 开了 Actions 并跑了 validator workflow，可在 **Status Check Patterns** 里加 `validate`。如果没开 Actions，靠人工 review 也够。

---

## Gitee  —— 可选，镜像保护

1. 打开仓库 → **管理** → **分支管理**
2. 找到 `main` 分支，点击 **保护**
3. 设置：
   - ✅ **仅 Owner / Admin 可推送**
   - ✅ **不允许强推（force push）**
   - ✅ **不允许删除**
4. 如果团队加了协作者，再去「PR 设置」要求 N 个 approve

> Gitee Actions 的状态检查可能需要单独配置。本仓库 CI 主战场在 GitHub Actions，这里跳过 status check，靠人工 review 即可。

---

## GitHub  —— free personal + private 实质无服务端保护

### 现实状况

GitHub 把两套保护机制都对 **free personal account + private 仓库**做了限制：

| 机制 | private + free personal | private + Pro / Team Org | public + free |
|---|---|---|---|
| **Branch protection rules**（老版） | ⚠️ 可创建但**不强制执行** | ✅ 强制 | ✅ 强制 |
| **Repository Rulesets**（新版） | ❌ 完全不可用 | ✅ 强制 | ✅ 强制 |

GitHub 自己的提示原话：

- Rulesets：*"To access rulesets in a private repository, you'll need to move it to a GitHub Team organization account."*
- Branch protection：*"Your protected branch rules for your branch won't be enforced on this private repository until you move to a GitHub Team or Enterprise organization account."*

**等价于：本仓库当前状态下 GitHub 没有服务端保护手段**。

### 你的三个选择

1. **接受现状（推荐）**：把 GitHub 当镜像，主战场是 Gitea，本地 pre-push hook + `bash scripts/push-all.sh` 已经能挡住所有意外。GitHub 即使有人直接推也只是把镜像污染，影响不大。
2. **付费**：GitHub Pro 个人版 $4/月 解锁 personal private 仓库的保护（Rulesets 也能用）；或者把仓库转移到 GitHub Team Organization（更适合团队协作但更贵）。
3. **改 public**：保护规则立刻生效。Git 历史里的内网 IP 已经清干净（commit `dda8492`/`9b75081` 之后的版本），技术上没风险。但要先想清楚是否真的要把模板开源。

### 如果走选项 2 或 3，配置步骤

**升级到 public、Pro、或 Team Org 后**，推荐用 Rulesets：

1. 打开 `https://github.com/mantaXray/trellis-templates/settings/rules`
2. 点击 **New ruleset** → **New branch ruleset**
3. **Ruleset name**: `main protection`
4. **Enforcement status**: `Active`
5. **Bypass list**: 留空
6. **Target branches** → **Add target** → **Include default branch**
7. **Branch rules** 勾选：
   - ✅ Restrict deletions
   - ✅ Block force pushes
   - ✅ Require a pull request before merging → Required approvals: 1
   - ✅ Require status checks to pass → Add checks: `validate`，勾选 Require branches to be up to date
   - 可选：Require linear history / Require signed commits
8. **Create**

如果不想升级 Pro/Team Org 但仓库已 public，老版 Branch protection rules 也能用（`settings/branches` → Add rule），步骤类似。

---

## 验证配完没

最简单的方式：

```bash
# 1. 在本地 main 上做个无意义的小改动
echo "" >> README.md
git add README.md && git commit -m "test: verify branch protection"

# 2. 试着直接推
git push origin main         # Gitea 应该被拒绝
git push gitee main          # Gitee 应该被拒绝
git push github main         # GitHub（free + private）会成功——这是 GitHub 限制，不是你配错

# 3. 撤销刚才的 test commit
git reset --hard HEAD~1
```

如果 Gitea 或 Gitee 也能直接推上去，说明那个 remote 的保护没生效，回去检查规则。GitHub 在 free + private 状态下推上去是正常的（前面解释过了）。

---

## 紧急绕过

如果出现真正的紧急情况（CI 跑不通且必须立刻 push），可以临时关掉 branch protection：
- Gitea: Settings → Branches → 该规则旁边 **Disable** / 删除，处理完立刻恢复
- Gitee: 类似操作
- GitHub: 它本来就不强制，不用处理

**不要养成 `--no-verify` 习惯**——本地 pre-push hook 可以跳过，但服务端 branch protection 是最后一道防线（在它真能强制的 remote 上）。
