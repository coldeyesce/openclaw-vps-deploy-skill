# OpenClaw VPS Deploy Skill

English | [简体中文](README.zh-CN.md)

A reusable AgentSkill for deploying OpenClaw on remote Linux/VPS hosts over SSH.

It captures a real-world deployment workflow including:

- Installing Node.js 22 and OpenClaw on Ubuntu servers
- Setting `gateway.mode=local` correctly
- Exposing the Web UI safely or temporarily by IP+token
- Fixing `origin not allowed` Control UI errors
- Configuring Telegram bot access and Telegram SOCKS5 proxy
- Configuring systemd-level proxy env vars for model/provider traffic
- Handling OpenAI Codex OAuth from a local browser when the server is remote
- Copying `auth-profiles.json` from a working local machine to the server
- Removing stale/bad OpenAI API keys when valid Codex OAuth already exists
- Troubleshooting timeouts, port mismatches, auth failures, and region-restricted OAuth exchange errors

## Repository layout

```text
openclaw-vps-deploy/
├── SKILL.md
└── references/
    ├── config-example.json
    ├── runbook.md
    └── troubleshooting.md
```

## What this skill is for

Use this skill when you need to:

1. Deploy OpenClaw on a VPS or remote Ubuntu/Linux server
2. Configure Telegram bot + pairing on that server
3. Expose or troubleshoot the Control UI remotely
4. Route Telegram traffic and model traffic through SOCKS5 proxies
5. Fix OpenAI Codex OAuth issues that succeed in the browser but fail on server-side token exchange
6. Recover from mixed auth state, such as valid Codex OAuth plus invalid OpenAI API keys

## Installation

Copy the `openclaw-vps-deploy/` folder into your OpenClaw skills directory, or package it using your normal skill packaging flow.

## Notes

- The skill intentionally documents both the **safe path** (loopback + SSH/tailnet) and the **temporary break-glass path** (public HTTP + token + dangerous flags).
- Dangerous settings are described as temporary and should be rolled back after recovery.

## License

MIT
