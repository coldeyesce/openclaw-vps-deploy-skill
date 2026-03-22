# Troubleshooting map

## Gateway appears running but nothing listens

Typical causes:

- `gateway.mode` is unset instead of `local`
- systemd service was installed with a fixed `--port` and the config assumes another port

Checks:

```bash
openclaw gateway status
systemctl --user cat openclaw-gateway.service
ss -ltnp | grep 18789
```

## Browser says `origin not allowed`

Cause:

- browser origin does not match `gateway.controlUi.allowedOrigins`
- or the operator is hitting the wrong port

Fix:

- allow the exact origin, e.g. `http://IP:18789`
- restart the gateway
- if necessary and explicitly approved, temporarily enable host-header fallback/device-auth bypass

## Browser UI works but model calls fail with auth errors

### `No API key found for provider "openai-codex"`
- copy a valid `auth-profiles.json` to the server
- verify `openclaw models status`

### `unsupported_country_region_territory`
- browser auth succeeded but server code→token exchange was rejected
- switch to local auth then copy the auth file to the server

### `Incorrect API key provided: sk-proj-...`
- stale `openai` API-key profile exists
- remove it from `auth-profiles.json`

## Telegram works but model requests timeout

Cause:

- only `channels.telegram.proxy` is set
- gateway service itself still reaches providers directly

Fix:

- add proxy env vars in the systemd drop-in for `openclaw-gateway.service`
- restart the service

## Public Web UI security cleanup after emergency access

Undo these if they were enabled temporarily:

- `gateway.bind: "lan"` → revert to `loopback`
- `gateway.controlUi.dangerouslyDisableDeviceAuth`
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`

Then prefer SSH tunneling, Tailscale Serve, or a proper HTTPS reverse proxy.
