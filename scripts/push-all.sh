#!/usr/bin/env bash
# scripts/push-all.sh
#
# 把当前分支 push 到所有已配置的 trellis-mcu-templates remote
# (origin / gitee / github)。
#
# 设计：
#   - 单个 remote 推送失败不中断后续 remote，所有 remote 跑完再总结
#   - 任一失败都按 remote 类型给出具体修复建议（切网络、走 SSH、配代理等）
#   - 推送前先跑一次 validate.py 防止把坏内容推出去
#
# 用法：bash scripts/push-all.sh

set -u

# cd 到仓库根
cd "$(dirname "$0")/.."

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
REMOTES=(origin gitee github)
FAILED=()

echo "==> Branch: $BRANCH"
echo "==> Remotes: ${REMOTES[*]}"
echo ""

# 1. 前置验证（fail fast）
echo "==> Running scripts/validate.py..."
if ! python scripts/validate.py; then
  echo "" >&2
  echo "[push-all] validate.py 失败。先修好上面的问题再 push。" >&2
  exit 2
fi
echo ""

# 2. 依次 push 每个 remote
for remote in "${REMOTES[@]}"; do
  echo "==> git push $remote $BRANCH"
  if git push "$remote" "$BRANCH"; then
    echo "    [$remote] OK"
  else
    echo "    [$remote] FAILED"
    FAILED+=("$remote")
  fi
  echo ""
done

# 3. 总结
if [ ${#FAILED[@]} -eq 0 ]; then
  echo "==> All ${#REMOTES[@]} remotes pushed successfully."
  exit 0
fi

echo "==================================================="
echo "  推送失败：${#FAILED[@]} / ${#REMOTES[@]} 个 remote 没推上去"
echo "  失败列表：${FAILED[*]}"
echo "==================================================="
echo ""
echo "针对失败 remote 的修复建议："
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
    github)
      echo "  [github / 国际个人]"
      echo "    GitHub HTTPS 在国内常被重置/超时。按以下任一方式处理："
      echo ""
      echo "    A. 切换到能访问 GitHub 的网络（手机热点 / VPN / 其他可访问外网的线路）"
      echo "       然后重试：git push github $BRANCH"
      echo ""
      echo "    B. 改用 SSH（前提是 GitHub 账户已配 SSH key）："
      echo "       git remote set-url github git@github.com:mantaXray/trellis-templates.git"
      echo "       git push github $BRANCH"
      echo ""
      echo "    C. 临时走本地代理（假设本地代理在 127.0.0.1:7890）："
      echo "       git config --global http.https://github.com.proxy http://127.0.0.1:7890"
      echo "       git push github $BRANCH"
      echo "       git config --global --unset http.https://github.com.proxy   # 推完撤掉"
      ;;
    *)
      echo "  [$remote]"
      echo "    - 修好网络/权限后重试：git push $remote $BRANCH"
      ;;
  esac
  echo ""
done

echo "==================================================="
echo "  ⚠️  请处理网络/认证问题后，单独重推失败的 remote："
echo "==================================================="
for remote in "${FAILED[@]}"; do
  echo "    git push $remote $BRANCH"
done
echo ""
echo "  或重跑本脚本：bash scripts/push-all.sh"
echo ""

exit 1
