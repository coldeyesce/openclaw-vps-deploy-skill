# OpenClaw VPS 部署 Skill

[English](README.md) | 简体中文

这是一个可复用的 AgentSkill，用于通过 SSH 在远程 Linux / VPS 服务器上部署 OpenClaw。

它固化了这次真实部署过程中踩过的坑和验证过的流程，包括：

- 在 Ubuntu 服务器上安装 Node.js 22 和 OpenClaw
- 正确设置 `gateway.mode=local`
- 以安全方式或临时 IP+Token 方式暴露 Web UI
- 修复 Control UI 的 `origin not allowed` 问题
- 配置 Telegram Bot 接入与 Telegram SOCKS5 代理
- 为 systemd 服务配置模型/Provider 请求代理环境变量
- 在“服务器远程、浏览器本地”的场景下处理 OpenAI Codex OAuth
- 将本地已可用的 `auth-profiles.json` 同步到服务器
- 当 `openai-codex` OAuth 有效但旧的 OpenAI API key 无效时，清理错误认证项
- 排查超时、端口不一致、鉴权失败、区域限制导致的 OAuth token exchange 失败等问题

## 仓库结构

```text
openclaw-vps-deploy/
├── SKILL.md
└── references/
    ├── config-example.json
    ├── runbook.md
    └── troubleshooting.md
```

## 适用场景

当你需要完成以下任务时使用这个 skill：

1. 在 VPS 或远程 Ubuntu/Linux 服务器部署 OpenClaw
2. 在服务器上接入 Telegram Bot 并启用 pairing
3. 远程暴露或排查 Control UI
4. 让 Telegram 流量和模型流量分别/统一走 SOCKS5 代理
5. 处理“浏览器授权成功，但服务器换 token 失败”的 OpenAI Codex OAuth 问题
6. 处理认证混乱状态，例如：Codex OAuth 正常，但旧 OpenAI API key 已失效

## 安装方式

把 `openclaw-vps-deploy/` 目录复制到你的 OpenClaw skills 目录，或者按你平时的打包流程打包后安装。

## 说明

- 这个 skill 同时保留了**安全路径**（loopback + SSH / tailnet）和**临时应急路径**（公网 HTTP + token + 危险开关）。
- 所有危险配置都被明确标注为“临时措施”，问题恢复后应回滚。

## 许可证

MIT
