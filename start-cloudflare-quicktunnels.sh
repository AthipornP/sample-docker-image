#!/usr/bin/env bash
set -eu

# start-cloudflare-quicktunnels.sh
# Creates two ephemeral Cloudflare "quick tunnels" (trycloudflare.com) to local services
# and runs them in the background. The script prints the generated URLs.
#
# Usage: sudo ./start-cloudflare-quicktunnels.sh
# Requires: cloudflared binary on the PATH (installed by script if missing)

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

CLOUDFLARED_BIN=$(command -v cloudflared || true)
if [ -z "$CLOUDFLARED_BIN" ]; then
  echo "cloudflared not found; downloading latest release..."
  TMP_BIN="/tmp/cloudflared"
  curl -sL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" -o "$TMP_BIN"
  chmod +x "$TMP_BIN"
  sudo mv "$TMP_BIN" /usr/local/bin/cloudflared
  CLOUDFLARED_BIN=$(command -v cloudflared)
fi

# Targets to expose
TARGET1="http://10.191.10.50:32090"
TARGET2="http://10.191.10.50:30318"

# Background logs and PID files
LOG1="$LOG_DIR/tunnel-32090.log"
LOG2="$LOG_DIR/tunnel-30318.log"
PID1="$LOG_DIR/tunnel-32090.pid"
PID2="$LOG_DIR/tunnel-30318.pid"

# Start tunnel 1
nohup "$CLOUDFLARED_BIN" tunnel --url "$TARGET1" --no-autoupdate > "$LOG1" 2>&1 &
PID_A=$!
echo $PID_A > "$PID1"

# Start tunnel 2
nohup "$CLOUDFLARED_BIN" tunnel --url "$TARGET2" --no-autoupdate > "$LOG2" 2>&1 &
PID_B=$!
echo $PID_B > "$PID2"

# Helper to find the quick tunnel URL from a log file
find_trycloudflare_url() {
  # Wait up to 15 seconds for the URL to appear
  local log_file="$1"
  local url=""
  for i in {1..15}; do
    # Look for trycloudflare.com in the log
    url=$(grep -oE 'https?://[A-Za-z0-9.-]+trycloudflare.com[^" ]*' "$log_file" || true)
    if [ -n "$url" ]; then
      # return first match
      echo "$url"
      return 0
    fi
    sleep 1
  done
  return 1
}

# Wait and capture the generated URLs
URL1=""
URL2=""
if URL1=$(find_trycloudflare_url "$LOG1"); then
  echo "Tunnel 1 started and available at: $URL1"
else
  echo "Warning: Could not detect Tunnel 1 URL in $LOG1 yet; check logs or run 'tail -F $LOG1'." >&2
fi

if URL2=$(find_trycloudflare_url "$LOG2"); then
  echo "Tunnel 2 started and available at: $URL2"
else
  echo "Warning: Could not detect Tunnel 2 URL in $LOG2 yet; check logs or run 'tail -F $LOG2'." >&2
fi

# Print status summary
printf "\nStatus summary:\n"
printf "Service 1: %s -> %s\n" "$TARGET1" "${URL1:-(URL not found)}"
printf "Service 2: %s -> %s\n" "$TARGET2" "${URL2:-(URL not found)}"

printf "Log files: %s\n" "$LOG_DIR"
printf "PIDs: %s, %s\n" "$PID1" "$PID2"

# Exit 0 even if URLs can't be found; user can inspect logs
exit 0
