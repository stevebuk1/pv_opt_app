#!/usr/bin/with-contenv bashio
# ==============================================================================
# PV Opt Add-On - Entry point
# Reads /data/options.json (written by HA Supervisor from config.yaml schema)
# and launches the pv_opt application.
# ==============================================================================

set -e

bashio::log.info "Starting PV Opt ${BUILD_VERSION:-dev}"

# ── Supervisor-provided environment ──────────────────────────────────────────
# The HA Supervisor injects these for add-ons with homeassistant_api: true
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export HA_URL="http://supervisor/core"
export HA_WS_URL="ws://supervisor/core/api/websocket"

# ── MQTT credentials ──────────────────────────────────────────────────────────
# Set in the Add-On UI (Settings > People > Users to create a dedicated user)
export MQTT_HOST="core-mosquitto"
export MQTT_PORT="1883"
export MQTT_USER="$(bashio::config 'mqtt_user')"
export MQTT_PASS="$(bashio::config 'mqtt_pass')"

# ── Log level ─────────────────────────────────────────────────────────────────
LOG_LEVEL=$(bashio::config 'log_level' 'info')
bashio::log.level "${LOG_LEVEL}"

# ── Validate mandatory options ────────────────────────────────────────────────
if ! bashio::config.exists 'battery_capacity_wh'; then
    bashio::log.fatal "battery_capacity_wh is required but not set"
    exit 1
fi

if ! bashio::config.exists 'inverter_type'; then
    bashio::log.fatal "inverter_type is required but not set"
    exit 1
fi

bashio::log.info "Inverter type: $(bashio::config 'inverter_type')"
bashio::log.info "Battery capacity: $(bashio::config 'battery_capacity_wh') Wh"
bashio::log.info "Read-only mode: $(bashio::config 'read_only' 'false')"

# ── Launch ────────────────────────────────────────────────────────────────────
# Options are passed via /data/options.json which ha_interface.py reads directly.
# stdout/stderr captured by the Supervisor log infrastructure.
bashio::log.info "Launching PV Opt..."

exec python3 /app/pv_opt.py
