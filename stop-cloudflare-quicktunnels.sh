#!/usr/bin/env bash
set -eu

# stop-cloudflare-quicktunnels.sh
# Stops cloudflared quick tunnels started by `start-cloudflare-quicktunnels.sh`.
# Behavior:
# - Looks for PID files in logs/ (tunnel-32090.pid, tunnel-30318.pid) and kills the PIDs if they appear to be cloudflared processes.
# - Falls back to searching for `cloudflared tunnel --url` processes and kills them if the PID files are missing or stale.
# - Accepts -y to skip confirmation and --remove-logs to delete logs & pid files after stopping.
# - You may need sudo if the processes are owned by other users.

LOG_DIR="logs"
PID_FILES=("$LOG_DIR/tunnel-32090.pid" "$LOG_DIR/tunnel-30318.pid")
REMOVE_LOGS=false
ASSUME_YES=false

usage() {
  cat <<EOF
Usage: $0 [-y] [--remove-logs]
  -y                Skip confirmation
  --remove-logs     Also remove logs/tunnel-*.log and PID files after stopping
  --help            Show this help
EOF
}

# Parse args
while [ "$#" -gt 0 ]; do
  case "$1" in
    -y) ASSUME_YES=true; shift;;
    --remove-logs) REMOVE_LOGS=true; shift;;
    --help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

confirm() {
  if [ "$ASSUME_YES" = true ]; then
    return 0
  fi
  read -r -p "$1 [y/N]: " ans
  case "$ans" in
    [Yy]*) return 0;;
    *) return 1;;
  esac
}

killed_any=false

kill_pid() {
  local pid=$1
  local reason=$2
  if [ -z "$pid" ]; then
    return 1
  fi
  if ! ps -p "$pid" > /dev/null 2>&1; then
    echo "PID $pid not running (skipping)"
    return 1
  fi
  # Optionally verify process is cloudflared or tunnel
  local cmdline
  cmdline=$(ps -p "$pid" -o cmd= | sed 's/^\s*//') || cmdline=""
  if echo "$cmdline" | grep -qiE "cloudflared.*tunnel"; then
    echo "Killing PID $pid (cloudflared): $cmdline"
    if kill "$pid"; then
      killed_any=true
      # Wait briefly, then escalate
      sleep 2
      if ps -p "$pid" > /dev/null 2>&1; then
        echo "PID $pid still running; sending SIGKILL"
        kill -9 "$pid" || true
      fi
      echo "PID $pid terminated (reason: $reason)"
      return 0
    else
      echo "Failed to kill PID $pid; try running this script under sudo" >&2
      return 1
    fi
  else
    echo "Warning: PID $pid doesn't look like a cloudflared process (cmd: $cmdline). Skipping. Use process matching if you want to find cloudflared processes instead."
    return 1
  fi
}

# 1) Try using PID files
for pf in "${PID_FILES[@]}"; do
  if [ -f "$pf" ]; then
    pid=$(cat "$pf" 2>/dev/null || true)
    if [[ "$pid" =~ ^[0-9]+$ ]]; then
      echo "Found PID file: $pf -> PID $pid"
      if confirm "Kill PID $pid (from $pf)?"; then
        kill_pid "$pid" "from $pf" || true
      else
        echo "Skipping PID $pid (user declined)"
      fi
    else
      echo "PID file $pf contains non-numeric content; removing or ignoring"
      # remove invalid file optionally
      if [ "$REMOVE_LOGS" = true ]; then
        rm -f "$pf" || true
      fi
    fi
  fi
done

# 2) If nothing killed by PIDs, try searching for cloudflared tunnel processes and kill them
if [ "$killed_any" = false ]; then
  echo "Trying to find running cloudflared tunnel processes..."
  mapfile -t procs < <(ps -eo pid,cmd --no-headers | grep -i "cloudflared.*tunnel" | grep -v grep || true)
  if [ "${#procs[@]}" -eq 0 ]; then
    echo "No cloudflared tunnel processes found."
  else
    for proc in "${procs[@]}"; do
      pid=$(echo "$proc" | awk '{print $1}')
      cmd=$(echo "$proc" | cut -d' ' -f2-)
      echo "Found: PID $pid -> $cmd"
      if confirm "Kill PID $pid ($cmd)?"; then
        kill_pid "$pid" "matched process" || true
      else
        echo "Skipping PID $pid (user declined)"
      fi
    done
  fi
fi

# Optional: remove logs & PIDs
if [ "$REMOVE_LOGS" = true ]; then
  echo "Removing logs and PID files in $LOG_DIR"
  rm -f "$LOG_DIR"/tunnel-*.log "$LOG_DIR"/tunnel-*.pid || true
fi

if [ "$killed_any" = true ]; then
  echo "Done — some cloudflared tunnel processes were stopped."
  exit 0
else
  echo "No cloudflared tunnel processes stopped by this script."
  exit 1
fi
