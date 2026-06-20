# syntax=docker/dockerfile:1
# ============================================================
# PV Opt Add-On Dockerfile
#
# The HA builder action sets BUILD_ARCH at build time.
# We use a multi-stage approach so each architecture gets the
# correct HA base image without relying on the deprecated
# build.yaml / BUILD_FROM ARG pattern (removed in Supervisor
# 2026.04.0).
#
# Base images: official HA Python 3.12 on Alpine 3.19
# ============================================================

# No default on purpose: if BUILD_ARCH isn't passed explicitly,
# the build should fail rather than silently produce an amd64 image.
ARG BUILD_ARCH

# ── Per-arch base image aliases ───────────────────────────
FROM ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.19   AS base-amd64
FROM ghcr.io/home-assistant/aarch64-base-python:3.12-alpine3.19 AS base-aarch64
FROM ghcr.io/home-assistant/armhf-base-python:3.12-alpine3.19   AS base-armhf
FROM ghcr.io/home-assistant/armv7-base-python:3.12-alpine3.19   AS base-armv7

# ── Select the right base via the build arg ───────────────
# shellcheck disable=SC2140
FROM base-${BUILD_ARCH} AS final

# ── System dependencies ───────────────────────────────────
# gcc/g++/musl-dev/openblas-dev needed to build numpy/pandas
# wheels on Alpine when no pre-built wheel is available
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    lapack-dev \
    openblas-dev \
    libffi-dev \
    openssl-dev \
    git

# ── Python dependencies ───────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── Application code ──────────────────────────────────────
WORKDIR /app
COPY pv_opt/pv_opt.py      .
COPY pv_opt/pvpy.py        .
COPY pv_opt/solis.py       .
COPY pv_opt/solax.py       .
COPY pv_opt/sunsynk.py     .

# Default config for first-time installs — copied to /config/pv_opt/ by run.sh
# if no config.yaml already exists there
COPY pv_opt/config/config.yaml /app/config.yaml.default

# Shim replaces AppDaemon's hass.Hass base class
COPY ha_interface/ ./ha_interface/

# ── Entry point ───────────────────────────────────────────
COPY run.sh /usr/bin/run.sh
RUN chmod +x /usr/bin/run.sh

CMD ["/usr/bin/run.sh"]

# ── Build-time labels (injected by HA builder action) ─────
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.source="https://github.com/stevebuk1/pv_opt_app" \
    org.opencontainers.image.licenses="MIT" \
    maintainer="stevebuk1"
