ARG BUILD_FROM
FROM ${BUILD_FROM}

# ── System dependencies ───────────────────────────────────────────────────────
# gcc/g++/musl-dev/lapack-dev needed to build numpy/pandas wheels on Alpine
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    lapack-dev \
    openblas-dev \
    libffi-dev \
    openssl-dev \
    git

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
WORKDIR /app
COPY pv_opt/pv_opt.py      .
COPY pv_opt/pvpy.py        .
COPY pv_opt/solis.py       .
COPY pv_opt/solax.py       .
COPY pv_opt/sunsynk.py     .

# Default config for first-time installs — copied to /config/pv_opt/ by run.sh
# if no config.yaml already exists there
COPY pv_opt/config/config.yaml    /app/config.yaml.default

# Shim replaces AppDaemon's hass.Hass base class
COPY ha_interface/ ./ha_interface/

# ── Entry point ───────────────────────────────────────────────────────────────
COPY run.sh /usr/bin/run.sh
RUN chmod +x /usr/bin/run.sh

CMD ["/usr/bin/run.sh"]

# Labels injected by build.yaml
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
    io.hass.version=${BUILD_VERSION} \
    maintainer="stevebuk1"
