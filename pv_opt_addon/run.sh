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

# ── pv_opt config path ───────────────────────────────────────────────────────
# /config is the HA config directory (mounted read-only via config:ro in config.yaml)
# Add-On config location:   /config/pv_opt/config.yaml
# AppDaemon config location: /config/appdaemon/apps/pv_opt/config/config.yaml
ADDON_CONFIG="/config/pv_opt/config.yaml"
APPDAEMON_CONFIG="/config/appdaemon/apps/pv_opt/config/config.yaml"
export PV_OPT_CONFIG="$(bashio::config 'config_path' "${ADDON_CONFIG}")"
bashio::log.info "pv_opt config path: ${PV_OPT_CONFIG}"

if [ ! -f "${PV_OPT_CONFIG}" ]; then
    mkdir -p "$(dirname "${PV_OPT_CONFIG}")"
    if [ -f "${APPDAEMON_CONFIG}" ]; then
        # Migrating from AppDaemon — copy existing config across
        bashio::log.info "Found AppDaemon config at ${APPDAEMON_CONFIG}"
        bashio::log.info "Copying to Add-On location: ${PV_OPT_CONFIG}"
        cp "${APPDAEMON_CONFIG}" "${PV_OPT_CONFIG}"
        bashio::log.info "Migration complete — config.yaml copied to ${PV_OPT_CONFIG}"
    else
        # Fresh install — copy built-in default
        bashio::log.warning "No config.yaml found — installing default"
        cp /app/config.yaml.default "${PV_OPT_CONFIG}"
        bashio::log.info "Default config.yaml written to ${PV_OPT_CONFIG}"
        bashio::log.warning "Please edit ${PV_OPT_CONFIG} to match your system, then restart the Add-On"
    fi
fi

# ── Launch ────────────────────────────────────────────────────────────────────
# Options are passed via /data/options.json which ha_interface.py reads directly.
# stdout/stderr captured by the Supervisor log infrastructure.
bashio::log.info "Launching PV Opt..."

exec python3 /app/pv_opt.py
