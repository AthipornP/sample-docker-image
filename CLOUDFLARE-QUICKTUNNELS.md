Cloudflare Quick Tunnel Setup
=============================

This document and the accompanying `start-cloudflare-quicktunnels.sh` script show how to expose local services using Cloudflare's ephemeral quick tunnels (the default `trycloudflare.com` hostnames), and how to run the tunnels in the background.

Prerequisites
-------------
- A Linux machine with curl and sudo privileges.
- (Optional) A Cloudflare account and domain if you prefer persistent DNS mapping.

Quick (ephemeral) mode - zero-config
------------------------------------
The script `start-cloudflare-quicktunnels.sh` performs these steps:
1. Installs `cloudflared` if it isn't present.
2. Starts two ephemeral quick-tunnels in the background that expose:
   - http://10.191.10.50:32090
   - http://10.191.10.50:30318
3. Captures and prints the generated trycloudflare.com URLs (the tunnels' public endpoints).

Usage:
```bash
# Make sure the script is executable
chmod +x start-cloudflare-quicktunnels.sh
# Run it (it will use sudo to install cloudflared if missing)
sudo ./start-cloudflare-quicktunnels.sh
```

The script writes logs to `logs/tunnel-32090.log` and `logs/tunnel-30318.log`, and prints a status summary along with the trycloudflare URLs when available.

Notes:
- The trycloudflare URLs are ephemeral and will change each time you run a quick tunnel.
- If the URLs are not immediately printed, check the logs and wait a few seconds.

Persistent (recommended for production) named tunnels
----------------------------------------------------
If you have a Cloudflare account and a DNS domain, use a named tunnel with DNS mapping instead for a stable hostname.

1. Install cloudflared (if not installed):
```bash
sudo curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
```
2. Authenticate and create a tunnel:
```bash
# This will open a browser for you to sign in and select your Cloudflare zone
cloudflared login

# Create a named tunnel
cloudflared tunnel create my-tunnel
```
3. Create a config `~/.cloudflared/config.yml` with ingress rules:
```yaml
# Example config.yml
# See also: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/configuration

# Replace with tunnel UUID and credentials-file path from the create command
tunnel: <TUNNEL-UUID>
credentials-file: /home/<user>/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: grafana.example.com
    service: http://10.191.10.50:32090
  - hostname: prometheus.example.com
    service: http://10.191.10.50:30318
  - service: http_status:404
```
4. Create DNS records pointing the hostnames to the tunnel:
```bash
cloudflared tunnel route dns my-tunnel grafana.example.com
cloudflared tunnel route dns my-tunnel prometheus.example.com
```
5. Run the tunnel as a background service with systemd (recommended):
```bash
# create a systemd unit
sudo tee /etc/systemd/system/cloudflared-tunnel.service <<'EOF'
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=<your-user>
ExecStart=/usr/local/bin/cloudflared tunnel run my-tunnel
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now cloudflared-tunnel.service
```

Troubleshooting
---------------
- If you can't access the internal IP address from the machine running cloudflared, check networking & firewall rules.
- Confirm `cloudflared` logs for the assigned URLs (ephemeral) or connection issues.
- To view the logs:
```bash
tail -F logs/tunnel-32090.log logs/tunnel-30318.log
```

Security note
-------------
For production, protect services with Cloudflare Access policies or restrict allowed ingress to the specific hostnames.
