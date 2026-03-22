#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: write_systemd_proxy_override.sh <proxy-url>" >&2
  exit 2
fi

PROXY_URL="$1"
TARGET="${HOME}/.config/systemd/user/openclaw-gateway.service.d/proxy.conf"
mkdir -p "$(dirname "$TARGET")"
cat > "$TARGET" <<EOF
[Service]
Environment="ALL_PROXY=${PROXY_URL}"
Environment="all_proxy=${PROXY_URL}"
Environment="HTTPS_PROXY=${PROXY_URL}"
Environment="HTTP_PROXY=${PROXY_URL}"
EOF

systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
systemctl --user cat openclaw-gateway.service
printf '\n---\n'
cat "$TARGET"
