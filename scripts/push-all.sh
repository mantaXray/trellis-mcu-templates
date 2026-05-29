#!/usr/bin/env bash
# scripts/push-all.sh
#
# 把当前分支推送到所有 trellis-mcu-templates remote。
#
# 行为差异：
#   - origin (私有 Git 镜像) / gitee  → 直接 push（这些 remote 允许 Xray force push）
#   - github                         → 走 PR 工作流（Rulesets 强制 PR + CI 绿 + 禁止直推 main）
#
# GitHub PR 流程（在 main 分支上）：
#   - 有 gh CLI 已认证 → 自动建 feature branch + gh pr create + 等 CI + admin self-merge + sync 本地
#   - 没 gh CLI / 未认证 → 推 feature branch，打印 PR URL，让你网页点 merge 后再 sync
#
# 非 main 分支：所有 remote 直接 push（Rulesets 只拦 main）
#
# 用法：bash scripts/push-all.sh

set -u

cd "$(dirname "$0")/.."

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SHA="$(git rev-parse --short HEAD)"
DIRECT_REMOTES=(origin gitee)
GITHUB_REMOTE=github
FAILED=()

# ----- 定位 gh CLI（PATH 可能没刷新认不到全局命令） -----
GH_BIN=""
if command -v gh >/dev/null 2>&1; then
  GH_BIN="gh"
elif [ -x "/c/Program Files/GitHub CLI/gh.exe" ]; then
  GH_BIN="/c/Program Files/GitHub CLI/gh.exe"
fi

echo "==> Branch: $BRANCH @ $SHA"
if [ -n "$GH_BIN" ]; then
  echo "==> gh CLI: $GH_BIN"
else
  echo "==> gh CLI: 未找到（github 将回退到手动 PR URL 模式）"
fi
echo ""

# ----- 1. 前置 validate（fail fast） -----
echo "==> Running scripts/validate.py..."
if ! python scripts/validate.py; then
  echo "" >&2
  echo "[push-all] validate.py 失败。先修好上面的问题再 push。" >&2
  exit 2
fi
echo ""

# ----- 2. origin / gitee 直接 push -----
for remote in "${DIRECT_REMOTES[@]}"; do
  echo "==> git push $remote $BRANCH"
  if git push "$remote" "$BRANCH"; then
    echo "    [$remote] OK"
  else
    echo "    [$remote] FAILED"
    FAILED+=("$remote")
  fi
  echo ""
done

# ----- 3. github：非 main 直推，main 走 PR -----
if [ "$BRANCH" != "main" ]; then
  echo "==> git push $GITHUB_REMOTE $BRANCH  (非 main 分支，Rulesets 不拦)"
  if git push "$GITHUB_REMOTE" "$BRANCH"; then
    echo "    [$GITHUB_REMOTE] OK"
  else
    echo "    [$GITHUB_REMOTE] FAILED"
    FAILED+=("$GITHUB_REMOTE")
  fi
  echo ""
else
  # main 分支 → PR 工作流
  PR_BRANCH="auto/$SHA"
  echo "==> github PR 流程（Rulesets 禁止直推 main）"
  echo "    feature branch: $PR_BRANCH"

  # 检查 github 是否已经 up-to-date（避免无意义 PR）
  git fetch "$GITHUB_REMOTE" "$BRANCH" >/dev/null 2>&1 || true
  github_head="$(git rev-parse "$GITHUB_REMOTE/$BRANCH" 2>/dev/null || echo '')"
  local_head="$(git rev-parse HEAD)"
  if [ "$github_head" = "$local_head" ]; then
    echo "    [github] 已经是最新（$SHA），跳过 PR"
    echo ""
  else
    # 推 feature branch
    echo "    [github] 推 feature branch..."
    if ! git push "$GITHUB_REMOTE" "$BRANCH:refs/heads/$PR_BRANCH" 2>&1 | tail -3; then
      echo "    [github] feature branch push 失败"
      FAILED+=("$GITHUB_REMOTE")
    else
      if [ -z "$GH_BIN" ] || ! "$GH_BIN" auth status >/dev/null 2>&1; then
        # 没 gh 或没认证：打印 URL 让用户手动 merge
        echo ""
        echo "    [github] gh CLI 不可用或未认证 → 切手动 PR 模式"
        echo ""
        echo "    👉 创建 PR 并 merge："
        echo "       https://github.com/mantaXray/trellis-templates/pull/new/$PR_BRANCH"
        echo ""
        echo "    merge 后跑下面命令同步本地和其他 remote："
        echo "       git fetch $GITHUB_REMOTE && git reset --hard $GITHUB_REMOTE/main"
        echo "       git push origin main && git push gitee main"
        echo "       git push $GITHUB_REMOTE --delete $PR_BRANCH"
        echo ""
        FAILED+=("$GITHUB_REMOTE(手动 PR 待 merge)")
      else
        # gh 全自动流程
        echo "    [github] 创建 PR..."
        pr_url=$("$GH_BIN" pr create \
          --base "$BRANCH" \
          --head "$PR_BRANCH" \
          --fill 2>&1 | grep -oE 'https://github.com/[^[:space:]]*' | tail -1)
        if [ -z "$pr_url" ]; then
          echo "    [github] gh pr create 失败"
          FAILED+=("$GITHUB_REMOTE")
        else
          echo "    [github] PR: $pr_url"
          echo "    [github] 等 CI..."
          if ! "$GH_BIN" pr checks "$pr_url" --watch --required >/dev/null 2>&1; then
            echo "    [github] CI 未通过。手动处理：$pr_url"
            FAILED+=("$GITHUB_REMOTE")
          else
            echo "    [github] CI 通过 ✓"
            echo "    [github] 合并 PR (admin self-merge)..."
            if ! "$GH_BIN" pr merge "$pr_url" --merge --admin --delete-branch >/dev/null 2>&1; then
              echo "    [github] merge 失败。手动处理：$pr_url"
              FAILED+=("$GITHUB_REMOTE")
            else
              echo "    [github] merged + branch deleted ✓"
              echo "    [github] sync 本地 + origin + gitee..."
              git fetch "$GITHUB_REMOTE" >/dev/null 2>&1
              git reset --hard "$GITHUB_REMOTE/$BRANCH" >/dev/null 2>&1
              for r in "${DIRECT_REMOTES[@]}"; do
                git push "$r" "$BRANCH" >/dev/null 2>&1 || \
                  echo "    [warn] sync push $r 失败，需手动 git push $r $BRANCH"
              done
              echo "    [github] 全部到 $(git rev-parse --short HEAD)"
            fi
          fi
        fi
      fi
    fi
    echo ""
  fi
fi

# ----- 4. 总结 -----
if [ ${#FAILED[@]} -eq 0 ]; then
  echo "==> 全部 remote 同步成功 ($(git rev-parse --short HEAD))"
  exit 0
fi

echo "==================================================="
echo "  ${#FAILED[@]} 个 remote 没成功：${FAILED[*]}"
echo "==================================================="
echo ""

for remote in "${FAILED[@]}"; do
  case "$remote" in
    origin)
      origin_url="$(git remote get-url origin 2>/dev/null || echo '<origin URL>')"
      echo "  [origin / 私有 Git 镜像]"
      echo "    - 检查 VPN / 私有网络连接"
      echo "    - 确认 origin 可达：curl -I \"$origin_url\""
      echo "    - 修好网络后重试：git push origin $BRANCH"
      ;;
    gitee)
      echo "  [gitee / 国内个人]"
      echo "    - 检查外网：ping gitee.com"
      echo "    - 重试：git push gitee $BRANCH"
      echo "    - 持续失败可改 SSH："
      echo "        git remote set-url gitee git@gitee.com:manta-xray/trellis-templates.git"
      ;;
    github*)
      echo "  [github / 国际个人]"
      echo "    可能原因："
      echo "    1. Clash Verge 没开 / 代理端口不对（默认 7897）"
      echo "    2. gh CLI 未认证（跑 'gh auth login'）"
      echo "    3. PR 等待 merge（按上面打印的 URL 处理）"
      echo "    4. CI 红了（看 PR 页面 Actions tab）"
      echo ""
      echo "    重试整个流程：bash scripts/push-all.sh"
      ;;
    *)
      echo "  [$remote]"
      echo "    - 处理后重试：git push $remote $BRANCH"
      ;;
  esac
  echo ""
done

exit 1
