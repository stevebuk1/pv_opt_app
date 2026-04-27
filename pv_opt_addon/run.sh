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

# ── pv_opt config ─────────────────────────────────────────────────────────────
# /config is mounted read-write — users can find and edit files here via the
# HA File Editor, consistent with how AppDaemon stores its files.
#
# On first start, if /config/pv_opt/config.yaml doesn't exist:
#   1. Copy from AppDaemon location if found (migration path)
#   2. Otherwise copy the built-in default (fresh install)
# Subsequent starts use /config/pv_opt/config.yaml directly.

PV_OPT_DIR="/config/pv_opt"
DATA_CONFIG="${PV_OPT_DIR}/config.yaml"
APPDAEMON_CONFIG="/config/appdaemon/apps/pv_opt/config/config.yaml"
export PV_OPT_CONFIG="${DATA_CONFIG}"

mkdir -p "${PV_OPT_DIR}"

if [ ! -f "${DATA_CONFIG}" ]; then
    if [ -f "${APPDAEMON_CONFIG}" ]; then
        bashio::log.info "Migrating from AppDaemon — copying config to ${DATA_CONFIG}"
        cp "${APPDAEMON_CONFIG}" "${DATA_CONFIG}"
        bashio::log.info "Config copied from ${APPDAEMON_CONFIG}"
        bashio::log.info "AppDaemon config is unchanged. Edit ${DATA_CONFIG} to configure the Add-On."
    else
        bashio::log.warning "No config.yaml found — installing default to ${DATA_CONFIG}"
        cp /app/config.yaml.default "${DATA_CONFIG}"
        bashio::log.warning "Please edit ${DATA_CONFIG} to match your system, then restart the Add-On"
        bashio::log.warning "You can access this file via the HA File Editor add-on"
    fi
else
    bashio::log.info "Using existing config at ${DATA_CONFIG}"
fi

export ADDON_VERSION="${BUILD_VERSION:-unknown}"

# ── Launch ────────────────────────────────────────────────────────────────────
bashio::log.info "Launching PV Opt..."
exec python3 /app/pv_opt.py
