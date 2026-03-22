---
name: openclaw-vps-deploy
description: Deploy and harden OpenClaw on a remote Linux/VPS host, especially Ubuntu servers reached over SSH. Use when setting up OpenClaw from scratch, configuring gateway/web UI exposure, enabling Telegram bot channels, wiring SOCKS5 proxies for Telegram and model traffic, handling OpenAI Codex OAuth on a different local machine and copying auth files to the server, or troubleshooting remote access/origin/auth/timeout issues during VPS deployment.
---

# OpenClaw VPS Deploy

Deploy OpenClaw on a remote Linux host methodically. Prefer SSH-first, reversible changes, explicit verification after each step, and rollback of temporary public exposure once recovery is complete.

## Operator rules

- Confirm the host identity before trusting passwords on a changed SSH fingerprint.
- Ask before enabling public Web UI exposure or leaving dangerous Control UI flags enabled.
- Treat `channels.telegram.proxy` and provider/model traffic as separate network paths.
- Trust `openclaw gateway status` and the systemd unit over assumptions when the effective port differs from the config file.
- Prefer copying a known-good `auth-profiles.json` from a working local machine over repeatedly retrying broken VPS-side Codex OAuth.

## Core workflow

1. Verify SSH access and host identity before changing anything.
2. Install Node.js 22+ and OpenClaw.
3. Set `gateway.mode` to `local` before expecting the service to listen.
4. Decide access model early:
   - safest: loopback + SSH tunnel / tailnet / HTTPS reverse proxy
   - temporary convenience: public bind + token auth
5. Configure channels and proxies.
6. Configure model auth.
7. Restart the gateway and verify logs/status.
8. Remove dangerous temporary settings when no longer needed.

## Baseline install

On Ubuntu/Debian hosts:

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | bash
apt-get install -y nodejs
npm install -g openclaw
openclaw --version
```

If the installer reports Node was installed but not active on `PATH`, verify with `node -v` and `npm -v` in a fresh shell before continuing.

## Minimum working config

Create `~/.openclaw/openclaw.json` with at least:

```json
{
  "gateway": {
    "mode": "local"
  }
}
```

Without `gateway.mode: "local"`, the service may appear started but the gateway will refuse to bind.

## Quick decision tree

- If the user only needs remote access temporarily, prefer loopback + SSH tunnel.
- If the user refuses local tunneling and explicitly accepts risk, use public IP + token auth and document that it is temporary.
- If the browser says `origin not allowed`, fix `gateway.controlUi.allowedOrigins` first and verify the real service port.
- If browser OAuth succeeds but server token exchange fails with region/territory errors, authenticate locally and copy `auth-profiles.json` to the server.
- If the UI works but model calls time out, configure service-level proxy env vars for the systemd unit.
- If model calls fail with `Incorrect API key provided`, remove stale `openai` API-key profiles and keep valid `openai-codex` OAuth.

## Telegram channel setup

For Telegram bot deployments, set:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "<BOT_TOKEN>",
      "dmPolicy": "pairing"
    }
  }
}
```

If the host needs a proxy for Telegram Bot API access, add:

```json
{
  "channels": {
    "telegram": {
      "proxy": "socks5://user:pass@host:port"
    }
  }
}
```

`channels.telegram.proxy` affects Telegram traffic, not general model/provider traffic.

## Remote Web UI patterns

### Preferred

Keep the gateway on loopback and use SSH forwarding or a trusted HTTPS/tailnet layer.

### Temporary public exposure

If the user explicitly wants direct browser access by IP:

- set `gateway.bind` to `lan`
- keep token auth enabled
- set explicit `gateway.controlUi.allowedOrigins`
- verify which port the actual systemd service uses

Example:

```json
{
  "gateway": {
    "mode": "local",
    "bind": "lan",
    "auth": {
      "mode": "token",
      "token": "<TOKEN>"
    },
    "controlUi": {
      "allowedOrigins": ["http://SERVER_IP:18789"]
    }
  }
}
```

### Break-glass browser compatibility

For direct public HTTP access that still fails due to device/origin controls, these emergency flags may be temporarily required:

```json
{
  "gateway": {
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "dangerouslyAllowHostHeaderOriginFallback": true
    }
  }
}
```

Treat both as temporary. Remove them after the user regains access through a safer path.

## Port mismatch warning

`openclaw gateway status` may show a different effective port from the config if the systemd service was installed with `--port` or `OPENCLAW_GATEWAY_PORT`. Always trust the service command/status output over assumptions.

Check:

```bash
openclaw gateway status
systemctl --user cat openclaw-gateway.service
ss -ltnp | grep openclaw
```

## OpenAI Codex OAuth on VPS

Remote/VPS Codex OAuth often works like this:

1. Run `openclaw models auth login --provider openai-codex` on the server.
2. Open the provided auth URL in the user's local browser.
3. Copy the final `http://localhost:1455/auth/callback?...` URL from the browser location bar.
4. Paste that full URL back into the server prompt.

The `localhost:1455` page does not need to load successfully; the URL itself is what matters.

## Country/region failures during Codex OAuth

If token exchange returns `unsupported_country_region_territory` even when browser auth succeeded:

- the failure is on the server-side code→token exchange
- a Telegram proxy alone is not enough
- the model/provider request path may need its own proxy or a different machine

Preferred workaround: authenticate on a local machine that already works, then copy `auth-profiles.json` to the server.

## Reusing local auth on the server

Local auth file:

- Windows: `C:\Users\<user>\.openclaw\agents\main\agent\auth-profiles.json`
- Linux/macOS: `~/.openclaw/agents/main/agent/auth-profiles.json`

Server destination:

```bash
/root/.openclaw/agents/main/agent/auth-profiles.json
```

If the destination directory is missing:

```bash
mkdir -p /root/.openclaw/agents/main/agent
```

After copying, verify with:

```bash
openclaw models status
openclaw gateway restart
```

## Bad OpenAI API key mixed with valid Codex OAuth

A copied auth file may contain both:

- a valid `openai-codex` OAuth profile
- an invalid `openai` API key profile

Symptoms include `401 Incorrect API key provided: sk-proj-...` even though Codex OAuth is valid.

Use the bundled script for deterministic cleanup:

```bash
python3 scripts/sanitize_auth_profiles.py /root/.openclaw/agents/main/agent/auth-profiles.json
openclaw gateway restart
```

The script backs up the file, removes stale `openai:*` entries, and keeps `openai-codex` intact.

## Model traffic proxy for the gateway service

`channels.telegram.proxy` does not proxy OpenAI/Codex/model requests. For provider/model traffic, configure the systemd service environment.

Use the bundled helper:

```bash
bash scripts/write_systemd_proxy_override.sh 'socks5://user:pass@host:port'
```

This writes `~/.config/systemd/user/openclaw-gateway.service.d/proxy.conf`, reloads systemd, restarts the gateway, and prints the effective unit + override.

If you need to do it manually, the drop-in is:

```ini
[Service]
Environment="ALL_PROXY=socks5://user:pass@host:port"
Environment="all_proxy=socks5://user:pass@host:port"
Environment="HTTPS_PROXY=socks5://user:pass@host:port"
Environment="HTTP_PROXY=socks5://user:pass@host:port"
```

## Verification checklist

Run these after each major change:

```bash
openclaw gateway status
openclaw models status
openclaw channels list
```

For service-side debugging:

```bash
tail -n 100 /tmp/openclaw/openclaw-$(date +%F).log
```

## Read next

- For an end-to-end runbook, read `references/runbook.md`.
- For a ready-to-edit config example, read `references/config-example.json`.
- For error mapping and fixes, read `references/troubleshooting.md`.
- For cleanup after emergency public access, read `references/security-cleanup.md`.
