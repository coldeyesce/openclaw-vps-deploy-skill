# OpenClaw VPS Deploy Skill

English | [简体中文](README.zh-CN.md)

A reusable AgentSkill for deploying OpenClaw on remote Linux/VPS hosts over SSH.

This repository packages a real-world deployment workflow that has already been tested against common remote-host problems:

- installing Node.js 22 and OpenClaw on Ubuntu servers
- setting `gateway.mode=local` correctly
- exposing the Web UI safely or temporarily by IP + token
- fixing `origin not allowed` Control UI errors
- configuring Telegram bot access and Telegram SOCKS5 proxy
- configuring **systemd-level** proxy env vars for model/provider traffic
- handling OpenAI Codex OAuth from a local browser when the server is remote
- copying `auth-profiles.json` from a working local machine to the server
- removing stale/bad OpenAI API keys when valid Codex OAuth already exists
- troubleshooting timeouts, port mismatches, auth failures, and region-restricted OAuth exchange errors

## Repository layout

```text
openclaw-vps-deploy/
├── SKILL.md
├── references/
│   ├── config-example.json
│   ├── runbook.md
│   ├── security-cleanup.md
│   └── troubleshooting.md
└── scripts/
    ├── sanitize_auth_profiles.py
    └── write_systemd_proxy_override.sh
```

## What this skill is for

Use this skill when you need to:

1. Deploy OpenClaw on a VPS or remote Ubuntu/Linux server
2. Configure Telegram bot + pairing on that server
3. Expose or troubleshoot the Control UI remotely
4. Route Telegram traffic and model traffic through SOCKS5 proxies
5. Fix OpenAI Codex OAuth issues that succeed in the browser but fail on server-side token exchange
6. Recover from mixed auth state, such as valid Codex OAuth plus invalid OpenAI API keys

## Highlights

### 1. Clear separation of network paths

The skill explicitly distinguishes between:

- `channels.telegram.proxy` → Telegram Bot API traffic
- systemd service proxy env vars → model/provider traffic

That distinction is easy to miss during live debugging and causes many false fixes.

### 2. Remote Codex OAuth workaround

When server-side Codex OAuth token exchange fails with region or territory restrictions, the skill recommends a reliable fallback:

- authenticate on a working local machine
- copy `auth-profiles.json` to the server
- restart and verify

### 3. Deterministic helper scripts

Included helper scripts:

- `scripts/sanitize_auth_profiles.py`
  - remove stale `openai:*` API-key entries while keeping valid `openai-codex` OAuth
- `scripts/write_systemd_proxy_override.sh`
  - write a systemd drop-in override for provider/model traffic proxying

## Installation

Copy the `openclaw-vps-deploy/` folder into your OpenClaw skills directory, or package it using your normal skill packaging flow.

## Operational notes

- The skill intentionally documents both the **safe path** (loopback + SSH/tailnet) and the **temporary break-glass path** (public HTTP + token + dangerous flags).
- Dangerous settings are described as temporary and should be rolled back after recovery.
- If you expose the gateway publicly, rotate the token after debugging.

## Related references inside the skill

- `references/runbook.md` — end-to-end deployment runbook
- `references/troubleshooting.md` — error-to-fix mapping
- `references/security-cleanup.md` — post-recovery hardening checklist
- `references/config-example.json` — ready-to-edit baseline config

## License

MIT
