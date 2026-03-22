# Nginx + HTTPS + Basic Auth front-end for OpenClaw

This is the recommended public-access pattern when a user insists on browser access over the public internet but does not have a proper private network path.

## Target architecture

- OpenClaw binds to loopback only: `127.0.0.1:18789`
- Nginx listens publicly on `443`
- Nginx terminates HTTPS
- Nginx enforces Basic Auth
- Nginx reverse-proxies to OpenClaw

## Why this is safer

Compared with exposing OpenClaw directly on a public port, this pattern adds:

- a username/password prompt before the app is reachable
- TLS encryption for credentials and session traffic
- the ability to keep OpenClaw itself off the public network

It is still not as strong as a tailnet, SSO, or proper external identity layer, but it is much better than raw public HTTP exposure.

## Required OpenClaw settings

Example:

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "<NEW_TOKEN>"
    },
    "controlUi": {
      "allowedOrigins": [
        "https://<SERVER_IP_OR_HOSTNAME>"
      ]
    }
  }
}
```

Remove any temporary break-glass flags such as:

- `dangerouslyDisableDeviceAuth`
- `dangerouslyAllowHostHeaderOriginFallback`

## Example Nginx config

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}
server {
    listen 443 ssl;
    server_name <SERVER_IP_OR_HOSTNAME>;

    ssl_certificate /etc/nginx/ssl/openclaw.crt;
    ssl_certificate_key /etc/nginx/ssl/openclaw.key;

    auth_basic "OpenClaw";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

## Self-signed certificate example

```bash
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -newkey rsa:2048 -sha256 -days 365 \
  -keyout /etc/nginx/ssl/openclaw.key \
  -out /etc/nginx/ssl/openclaw.crt \
  -subj '/CN=<SERVER_IP_OR_HOSTNAME>'
```

## Basic Auth file example

```bash
apt-get install -y apache2-utils
htpasswd -bc /etc/nginx/.htpasswd <USERNAME> <PASSWORD>
```

## Browser UX note

If you use a self-signed certificate on a raw IP, browsers will show a certificate warning the first time. That is expected. The user must manually trust/bypass it before the Basic Auth prompt and app will load.

## Recommended cleanup later

Longer term, prefer one of these:

1. Tailscale / private network only
2. Proper domain + trusted TLS certificate
3. Reverse proxy + stronger auth layer (SSO / Authelia / Cloudflare Access)
