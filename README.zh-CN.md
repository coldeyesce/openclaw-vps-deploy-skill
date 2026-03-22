# OpenClaw VPS 部署 Skill

[English](README.md) | 简体中文

这是一个可复用的 AgentSkill，用于通过 SSH 在远程 Linux / VPS 服务器上部署 OpenClaw。

这个仓库整理了已经在真实部署中验证过的一整套流程，重点覆盖这些高频坑位：

- 在 Ubuntu 服务器上安装 Node.js 22 和 OpenClaw
- 正确设置 `gateway.mode=local`
- 以安全方式或临时 IP + Token 方式暴露 Web UI
- 修复 Control UI 的 `origin not allowed` 问题
- 配置 Telegram Bot 接入与 Telegram SOCKS5 代理
- 为 **systemd 服务本身** 配置模型/Provider 请求代理环境变量
- 在“服务器远程、浏览器本地”的场景下处理 OpenAI Codex OAuth
- 将本地已可用的 `auth-profiles.json` 同步到服务器
- 当 `openai-codex` OAuth 有效但旧的 OpenAI API key 无效时，清理错误认证项
- 排查超时、端口不一致、鉴权失败、区域限制导致的 OAuth token exchange 失败等问题

## 安全立场

这个仓库现在明确把“**直接把 OpenClaw 本体暴露到公网**”定义为：

- 仅限临时应急
- 默认不推荐
- 恢复后应尽快回滚

推荐优先级是：

1. loopback + SSH 隧道
2. loopback + tailnet / 私网访问
3. loopback + HTTPS 反代 + 认证
4. 直接公网暴露仅作为临时 break-glass 方案

## 仓库结构

```text
openclaw-vps-deploy/
├── SKILL.md
├── references/
│   ├── config-example.json
│   ├── nginx-basic-auth-https.md
│   ├── runbook.md
│   ├── security-cleanup.md
│   └── troubleshooting.md
└── scripts/
    ├── sanitize_auth_profiles.py
    └── write_systemd_proxy_override.sh
```

## 适用场景

当你需要完成以下任务时使用这个 skill：

1. 在 VPS 或远程 Ubuntu/Linux 服务器部署 OpenClaw
2. 在服务器上接入 Telegram Bot 并启用 pairing
3. 远程暴露或排查 Control UI
4. 让 Telegram 流量和模型流量分别/统一走 SOCKS5 代理
5. 处理“浏览器授权成功，但服务器换 token 失败”的 OpenAI Codex OAuth 问题
6. 处理认证混乱状态，例如：Codex OAuth 正常，但旧 OpenAI API key 已失效
7. 给 OpenClaw 前面加一个更安全的 HTTPS + 认证访问层

## 这个 skill 的几个重点

### 1）明确区分两类代理

这个 skill 特别强调：

- `channels.telegram.proxy` → 只影响 Telegram Bot API
- systemd 服务代理环境变量 → 才影响模型/Provider 请求

这点在实战里非常容易混淆，也是很多“明明配了代理但模型还是超时”的根源。

### 2）更安全的公网访问方式

它现在不再优先推荐“把 OpenClaw 裸露到公网”，而是优先推荐：

- OpenClaw 只监听本地回环
- Nginx / Caddy 负责 HTTPS
- 用 Basic Auth 先拦一层
- 再把流量反代到 `127.0.0.1:18789`

对应参考文档：`references/nginx-basic-auth-https.md`

### 3）远程 Codex OAuth 的稳定兜底方案

当服务器端 `code -> token` 这一步因为地区/风控失败时，这个 skill 推荐一个更稳的办法：

- 在本地可用机器完成认证
- 把 `auth-profiles.json` 拷到服务器
- 重启并验证

### 4）加入可复用脚本，减少手工改 JSON

仓库里额外提供了两个脚本：

- `scripts/sanitize_auth_profiles.py`
  - 删除失效的 `openai:*` API key 认证项，同时保留有效的 `openai-codex` OAuth
- `scripts/write_systemd_proxy_override.sh`
  - 为网关服务写入 systemd proxy override，专门解决模型流量不走代理的问题

## 安装方式

把 `openclaw-vps-deploy/` 目录复制到你的 OpenClaw skills 目录，或者按你平时的打包流程打包后安装。

## 使用说明

- 所有危险配置都被明确标注为“临时措施”，问题恢复后应尽快回滚。
- 如果你曾把 gateway token 暴露在聊天、浏览器历史或截图里，调试结束后最好主动轮换。
- 如果你用的是裸 IP + 自签名 HTTPS，浏览器第一次会报证书警告，这是正常现象。

## skill 内参考文件

- `references/runbook.md` —— 端到端部署流程
- `references/troubleshooting.md` —— 报错到修复方法的映射
- `references/security-cleanup.md` —— 应急公网暴露后的安全回收清单
- `references/nginx-basic-auth-https.md` —— 更安全的公网访问方案
- `references/config-example.json` —— 可直接改的基础配置样例

## 许可证

MIT
