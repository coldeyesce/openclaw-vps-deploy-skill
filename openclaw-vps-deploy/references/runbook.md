# OpenClaw VPS deployment runbook

## 1. Connect and verify host

- Confirm SSH target/IP and host key before trusting credentials.
- For changed host keys, pause and confirm with the user before deleting old `known_hosts` entries.

## 2. Install runtime

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | bash
apt-get install -y nodejs
npm install -g openclaw
node -v
npm -v
openclaw --version
```

## 3. Create initial config

Start with:

```json
{
  "gateway": { "mode": "local" }
}
```

Then extend with channel/model/network settings.

## 4. Bring up the gateway

```bash
openclaw gateway start
openclaw gateway status
```

If the status says the service is running but the port is not listening, inspect logs and verify `gateway.mode` and the service command line.

## 5. Add Telegram bot + pairing

Minimal Telegram block:

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

If the user wants group behavior, explicitly define allowlists/policies. Do not assume default group access is acceptable.

## 6. Decide browser access mode

### Safe

- `bind: loopback`
- access via SSH tunnel or trusted HTTPS/tailnet

### Temporary public

- `bind: lan`
- token auth enabled
- explicit `allowedOrigins`
- only with explicit user consent

## 7. Handle Codex OAuth

If server-side token exchange fails due to region/risk checks, stop fighting the VPS and instead:

1. authenticate locally on a working machine
2. copy `auth-profiles.json` to the server
3. verify `openclaw models status`

## 8. If web UI loads but chat fails

### `origin not allowed`
- Add the exact browser origin to `gateway.controlUi.allowedOrigins`
- Restart the gateway
- Confirm the service is using the expected port

### `LLM request timed out`
- Remember: Telegram proxy != model proxy
- Add proxy env vars to the systemd service drop-in
- Restart and retest

### `Incorrect API key provided`
- Remove stale `openai` API-key profiles from auth storage
- Keep valid `openai-codex` OAuth
- Restart and retest
