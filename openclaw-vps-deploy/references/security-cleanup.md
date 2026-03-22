# Security cleanup after emergency access

Use this checklist after temporary public debugging or break-glass access.

## 1. Remove dangerous Control UI flags

Delete or set to safe defaults:

```json
{
  "gateway": {
    "controlUi": {
      "dangerouslyDisableDeviceAuth": false,
      "dangerouslyAllowHostHeaderOriginFallback": false
    }
  }
}
```

## 2. Revert public bind when possible

Preferred end state:

```json
{
  "gateway": {
    "bind": "loopback"
  }
}
```

Then access via SSH tunnel, Tailscale Serve, or a proper HTTPS reverse proxy.

## 3. Rotate exposed gateway token

If a token was shared in chat or browser history, replace it.

## 4. Re-check service proxy settings

Keep them only if the provider path truly needs them. Inspect:

```bash
systemctl --user cat openclaw-gateway.service
cat ~/.config/systemd/user/openclaw-gateway.service.d/proxy.conf
```

## 5. Re-run verification

```bash
openclaw gateway status
openclaw models status
openclaw channels list
```

## 6. Optional audit

```bash
openclaw security audit
openclaw security audit --deep
```
