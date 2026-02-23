#!/usr/bin/env bash
# scripts/free_port.sh
# Find and optionally kill processes listening on a TCP port (interactive).
# Usage:
#   ./scripts/free_port.sh            # defaults to port 5000
#   ./scripts/free_port.sh 5000       # check port 5000
#   FORCE=1 ./scripts/free_port.sh 5000  # force kill without prompt
#   FORCE=1 ALLOW_SYSTEM=1 ./scripts/free_port.sh 5000  # allow killing system processes

set -euo pipefail

PORT="${1:-5000}"
FORCE="${FORCE:-0}"
ALLOW_SYSTEM="${ALLOW_SYSTEM:-0}"

echo "Checking for processes listening on TCP port ${PORT}..."

# Get PIDs (works on macOS and Linux)
PIDS=$(lsof -t -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true)

if [ -z "${PIDS}" ]; then
  echo "No process is listening on port ${PORT}."
  exit 0
fi

# Detect if any PID looks like a system process (macOS ControlCenter / AirPlay, etc.)
SYSTEM_PIDS=""
for pid in ${PIDS}; do
  # comm may be truncated; args gives more context
  comm=$(ps -p ${pid} -o comm= 2>/dev/null || true)
  args=$(ps -p ${pid} -o args= 2>/dev/null || true)
  # simple heuristics to detect macOS system services that may own ports
  if [[ "${comm}" == *"ControlCenter"* ]] || [[ "${args}" == *"AirPlay"* ]] || [[ "${comm}" == *"AirPlay"* ]] || [[ "${args}" == *"ControlCenter"* ]] || [[ "${comm}" == */System/Library/* ]] ; then
    SYSTEM_PIDS="${SYSTEM_PIDS} ${pid}"
  fi
done

if [ -n "${SYSTEM_PIDS}" ] && [ "${FORCE}" != "1" ]; then
  echo ""
  echo "WARNING: Detected system process(es) listening on port ${PORT}: ${SYSTEM_PIDS}"
  echo "These look like macOS system processes (ControlCenter / AirPlay)."
  echo "Killing system processes may destabilize your system or be restarted by launchd."
  echo "Recommended actions:"
  echo " - Disable AirPlay Receiver in System Settings: System Settings -> General -> AirPlay & Handoff -> AirPlay Receiver (turn off)."
  echo " - Or run this app on a different port: PORT=5001 python main.py"
  echo "If you still want to force-kill system processes, re-run with:"
  echo "  FORCE=1 ALLOW_SYSTEM=1 ./scripts/free_port.sh ${PORT}"
  exit 1
fi

echo "Found the following PIDs listening on port ${PORT}: ${PIDS}"
for pid in ${PIDS}; do
  echo
  echo "--- PID: ${pid} ---"
  ps -p ${pid} -o pid,user,comm,args || true
done

action_kill() {
  for pid in ${PIDS}; do
    echo "Attempting graceful kill of PID ${pid}..."
    kill ${pid} 2>/dev/null || true
  done

  sleep 1
  # check remaining
  REMAINING=$(lsof -t -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "${REMAINING}" ]; then
    echo "Some processes are still listening: ${REMAINING}. Trying force kill..."
    for pid in ${REMAINING}; do
      echo "Force killing PID ${pid}..."
      sudo kill -9 ${pid} 2>/dev/null || true
    done
  fi

  echo "Final check:"
  lsof -nP -iTCP:${PORT} -sTCP:LISTEN || echo "No listener on port ${PORT}."
}

if [ "${FORCE}" = "1" ] && [ -n "${SYSTEM_PIDS}" ] && [ "${ALLOW_SYSTEM}" != "1" ]; then
  echo "Refusing to kill detected system processes without ALLOW_SYSTEM=1. To proceed: FORCE=1 ALLOW_SYSTEM=1 ./scripts/free_port.sh ${PORT}"
  exit 1
fi

if [ "${FORCE}" = "1" ]; then
  echo "FORCE=1 set — killing without confirmation."
  action_kill
  exit 0
fi

# Interactive prompt
read -r -p "Kill these processes? [y/N]: " ans
case "${ans}" in
  y|Y|yes|YES)
    action_kill
    ;;
  *)
    echo "Aborted by user. To force kill non-interactively, run: FORCE=1 ./scripts/free_port.sh ${PORT}"
    exit 0
    ;;
esac
