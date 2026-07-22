"""
ha_interface.py  –  AppDaemon shim for the pv_opt Add-On.

Replaces:
    import appdaemon.adbase as ad
    import appdaemon.plugins.hass.hassapi as hass
    import appdaemon.plugins.mqtt.mqttapi as mqtt

All three are now:
    import ha_interface.ha_interface as ad   (or hass)

The line  class PVOpt(hass.Hass)  is unchanged; Hass is defined here.
app_lock is a no-op decorator (asyncio is single-threaded in the event loop).

WebSocket listener
------------------
Hass._start_ws_listener() opens a persistent WebSocket to the HA
Supervisor and subscribes to 'state_changed' events.  When a matching
entity fires, the registered callbacks are invoked with the same
positional signature AppDaemon uses:

    callback(entity_id, attribute, old_state, new_state, kwargs)

Event listeners registered via listen_event() receive:

    callback(event_name, data, kwargs)

Both run in the asyncio event loop (fire-and-forget tasks), so they
must not block; long-running work in pv_opt is synchronous and will
block the loop briefly — acceptable for a local HA add-on.
"""

from __future__ import annotations

import asyncio
import functools
import json
import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

import paho.mqtt.client as _paho_mqtt
import requests
import websockets

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment – injected automatically by HA Supervisor at Add-On runtime
# ---------------------------------------------------------------------------

HA_URL = os.environ.get("HA_URL", "http://supervisor/core")
HA_WS_URL = os.environ.get("HA_WS_URL", "ws://supervisor/core/api/websocket")
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
MQTT_HOST = os.environ.get("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASS = os.environ.get("MQTT_PASS", "")


def _ha_headers() -> dict:
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }


def app_lock(fn):
    """
    Drop-in for @ad.app_lock. Acquires the owning instance's
    _optimise_lock (an RLock) so that every entry point into optimise()
    — the initial synchronous call from initialize(), scheduler-triggered
    runs, event-triggered runs, and state-change-triggered runs (from
    both the WebSocket and MQTT dispatch paths) — is fully serialized
    against every other one, regardless of which thread calls it.
    """
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        with self._optimise_lock:
            return fn(self, *args, **kwargs)
    return wrapper


def _mqtt_topic_matches(pattern: str, topic: str) -> bool:
    """Match paho-style MQTT topic patterns with # and + wildcards."""
    import re
    regex = re.escape(pattern).replace(r"\#", ".*").replace(r"\+", "[^/]+")
    return bool(re.fullmatch(regex, topic))


# ---------------------------------------------------------------------------
# MQTTShim – thin paho wrapper; mirrors AppDaemon's MQTT plugin API
# ---------------------------------------------------------------------------

class MQTTShim:
    """
    Used via  self.mqtt = self.get_plugin_api("MQTT")
    Implements mqtt_publish, mqtt_subscribe, listen_state.
    """

    # MQTT CONNACK result codes (paho-mqtt v1 callback API).
    _CONNACK_MESSAGES = {
        0: "connection accepted",
        1: "connection refused — incorrect protocol version",
        2: "connection refused — invalid client identifier",
        3: "connection refused — server unavailable",
        4: "connection refused — bad username or password",
        5: "connection refused — not authorised",
    }

    def __init__(self, lock: Optional[threading.Lock] = None):
        # Shared with the owning Hass instance's _optimise_lock so that
        # MQTT-triggered callbacks (running on paho's own background thread
        # via loop_start()) can't run concurrently with WebSocket-triggered
        # callbacks (dispatched through _locked_call). Without this, the two
        # threads can both enter optimise() at once and corrupt shared
        # dataframe state mid-calculation.
        self._lock = lock
        self._client = _paho_mqtt.Client()
        if MQTT_USER:
            self._client.username_pw_set(MQTT_USER, MQTT_PASS)
        self._topic_callbacks: dict[str, list[Callable]] = {}

        def _on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode("utf-8", errors="replace")
            for t, cbs in list(self._topic_callbacks.items()):
                # Support '#' wildcard and '+' single-level wildcard
                if topic == t or t == "#" or (
                    "+" in t and _mqtt_topic_matches(t, topic)
                ):
                    for cb in cbs:
                        try:
                            cb(topic, payload)   # pass topic so caller knows which entity
                        except Exception as e:
                            logger.exception("MQTT callback error on {topic}:")

        def _on_connect(client, userdata, flags, rc):
            # rc == 0 is the only success case. Anything else means the
            # broker rejected the connection (bad credentials, ACL, etc) —
            # previously this failed completely silently.
            reason = self._CONNACK_MESSAGES.get(rc, f"unknown result code {rc}")
            if rc == 0:
                logger.info(f"MQTT connected to {MQTT_HOST}:{MQTT_PORT} ({reason})")
            else:
                logger.error(
                    f"MQTT connection to {MQTT_HOST}:{MQTT_PORT} REJECTED by broker: "
                    f"{reason} — MQTT discovery and state sync will not work until this is fixed"
                )

        def _on_disconnect(client, userdata, rc):
            if rc == 0:
                logger.info("MQTT disconnected cleanly")
            else:
                logger.warning(
                    f"MQTT disconnected unexpectedly (rc={rc}) — paho will attempt to reconnect automatically"
                )

        self._client.on_message = _on_message
        self._client.on_connect = _on_connect
        self._client.on_disconnect = _on_disconnect
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            self._client.loop_start()
            logger.info(f"MQTT connect initiated to {MQTT_HOST}:{MQTT_PORT} — awaiting broker response...")
        except Exception as e:
            logger.error(f"MQTT connect failed: {e} — MQTT discovery will be unavailable")

    def mqtt_publish(self, topic: str, payload: Any, retain: bool = False, **kwargs):
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        self._client.publish(topic, payload, retain=retain)

    def mqtt_subscribe(self, topic: str, callback: Optional[Callable] = None):
        self._client.subscribe(topic)
        if callback:
            self._topic_callbacks.setdefault(topic, []).append(callback)

    def listen_state(self, callback: Callable, topic: str = "#", **kwargs):
        """
        AppDaemon-style listen_state on the MQTT plugin.
        pv_opt calls this with no topic to catch all MQTT state changes,
        which feeds into optimise_state_change.
        We subscribe to '#' and invoke callback with a synthetic
        AppDaemon-style signature: (entity_id, attribute, old, new, kwargs)
        """
        actual_topic = kwargs.get("entity_id", topic)

        def _wrap(topic, payload):
            try:
                if self._lock is not None:
                    with self._lock:
                        callback(topic, None, None, payload, {})
                else:
                    callback(topic, None, None, payload, {})
            except Exception as e:
                logger.error(f"MQTT listen_state callback error: {e}")

        self.mqtt_subscribe(actual_topic, _wrap)


# ---------------------------------------------------------------------------
# Hass – base class replacing hass.Hass / ad.ADBase
# ---------------------------------------------------------------------------

class Hass:
    """
    Minimal AppDaemon hass.Hass replacement backed by the HA Supervisor
    REST API and a persistent WebSocket for state-change events.

    PVOpt(hass.Hass) inherits from this class unchanged.
    """

    def __init__(self, options: dict | None = None):
        self.args: dict = options or {}

        # handle → (entity_id, callback, filter_kwargs)
        self._state_listeners: dict[str, tuple[str, Callable, dict]] = {}
        # event_name → list of (callback, kwargs)
        self._event_listeners: dict[str, list[tuple[Callable, dict]]] = {}

        self._scheduler_tasks: list[asyncio.Task] = []
        self._mqtt_shim: Optional[MQTTShim] = None
        self._handle_counter = 0
        self._init_done = asyncio.Event()   # set by _run() after initialize() returns

        # Serialises all callbacks that may call optimise() so that a
        # state-change or event trigger cannot start a second optimise()
        # while one is already running (replaces AppDaemon's @app_lock).

        # RLock (not Lock): optimise() and optimise_state_change() etc. are
        # all wrapped by app_lock, and optimise_state_change() calls
        # self.optimise() internally — same thread needs to re-acquire the
        # lock it already holds. A plain Lock would deadlock on that.
        self._optimise_lock = threading.RLock()
        self._main_loop: asyncio.AbstractEventLoop | None = None  # set in _run()
        self._session = requests.Session()  # persistent HTTP session for HA REST API

        # Reconnect state: used by _start_ws_listener() for backoff and by
        # _dispatch_state_change() to suppress the post-reconnect entity flood.
        self._ws_reconnect_count: int = 0          # increments on each reconnect
        self._ws_suppress_until: float = 0.0       # epoch time; callbacks suppressed while time() < this

    def _next_handle(self, prefix: str) -> str:
        self._handle_counter += 1
        return f"{prefix}_{self._handle_counter}"

    # ------------------------------------------------------------------
    # AppDaemon API shims
    # ------------------------------------------------------------------

    def get_ad_api(self):
        return self

    def get_plugin_api(self, plugin_name: str):
        if plugin_name.upper() == "MQTT":
            if self._mqtt_shim is None:
                self._mqtt_shim = MQTTShim(lock=self._optimise_lock)
            return self._mqtt_shim
        raise NotImplementedError(f"Plugin '{plugin_name}' is not supported by ha_interface")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(self, msg: str, level: str = "INFO", **kwargs):
        lvl = getattr(logging, level.upper(), logging.INFO)
        logger.log(lvl, msg)

    # ------------------------------------------------------------------
    # State – REST API
    # ------------------------------------------------------------------

    def get_state(self, entity_id: str, attribute: Optional[str] = None, **kwargs) -> Any:
        """
        Get state of an entity or all entities in a domain.

        AppDaemon supports two call patterns:
          1. get_state("sensor.my_sensor")         → returns state string
          2. get_state("sensor")                   → returns dict of all
                                                     entities in that domain
        The second pattern is detected by the absence of '.' in entity_id.
        """
        # Domain-level call — return all entities in domain as a dict
        # matching AppDaemon's return format: {entity_id: state_dict, ...}
        if "." not in str(entity_id):
            url = f"{HA_URL}/api/states"
            try:
                r = self._session.get(url, headers=_ha_headers(), timeout=10)
                r.raise_for_status()
                all_states = r.json()
                return {
                    s["entity_id"]: s
                    for s in all_states
                    if s["entity_id"].startswith(f"{entity_id}.")
                }
            except Exception as e:
                logger.error(f"get_state({entity_id}): {e}")
                return None

        # Single entity call
        url = f"{HA_URL}/api/states/{entity_id}"
        try:
            r = self._session.get(url, headers=_ha_headers(), timeout=10)
            r.raise_for_status()
            data = r.json()
            if attribute == "all":
                return data
            if attribute:
                return data.get("attributes", {}).get(attribute)
            return data.get("state")
        except Exception as e:
            logger.error(f"get_state({entity_id}): {e}")
            return None

    @staticmethod
    def _json_serialiser(obj: Any) -> str:
        """
        Fallback JSON serialiser for types that are not natively serialisable.
        Handles pandas Timestamp, numpy types, datetime, and timedelta.
        """
        import pandas as pd
        import numpy as np
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        if isinstance(obj, pd.Timedelta):
            return str(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialisable")

    def set_state(
        self,
        entity_id: str,
        state: Any = None,
        attributes: Optional[dict] = None,
        replace: bool = False,
        **kwargs,
    ):
        url = f"{HA_URL}/api/states/{entity_id}"
        payload: dict = {}
        if state is not None:
            payload["state"] = str(state)
        if attributes is not None:
            if replace:
                payload["attributes"] = attributes
            else:
                existing_attrs: dict = {}
                try:
                    r = self._session.get(url, headers=_ha_headers(), timeout=10)
                    if r.ok:
                        existing_attrs = r.json().get("attributes", {})
                except Exception:
                    pass
                payload["attributes"] = {**existing_attrs, **attributes}
        try:
            # Use custom serialiser to handle Timestamps and numpy types
            payload_str = json.dumps(payload, default=self._json_serialiser)
            r = self._session.post(
                url,
                headers=_ha_headers(),
                data=payload_str,
                timeout=10,
            )
            r.raise_for_status()
        except Exception as e:
            logger.error(f"set_state({entity_id}): {e}")

    def entity_exists(self, entity_id: str, **kwargs) -> bool:
        if not entity_id or "." not in str(entity_id):
            return False
        url = f"{HA_URL}/api/states/{entity_id}"
        try:
            r = self._session.get(url, headers=_ha_headers(), timeout=10)
            return r.status_code == 200
        except Exception:
            return False

    def get_entity(self, entity_id: str, **kwargs):
        outer = self

        class _EntityProxy:
            def __init__(self_, eid: str):
                self_._eid = eid

            def get_state(self_, attribute: Optional[str] = None, **kw):
                return outer.get_state(self_._eid, attribute=attribute)

        return _EntityProxy(entity_id)

    # ------------------------------------------------------------------
    # History – REST API
    # ------------------------------------------------------------------

    def get_history(self, entity_id: str, days: int = 1, **kwargs) -> Optional[list]:
        """
        Replaces AppDaemon's get_history().
        Returns a list containing one list of state dicts, matching
        AppDaemon's format: [[{last_updated, state, ...}, ...]]
        """
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(days=days)
        start_str = start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        url = (
            f"{HA_URL}/api/history/period/{start_str}"
            f"?filter_entity_id={entity_id}"
            f"&end_time={end_str}"
            f"&significant_changes_only=false"
            f"&no_attributes=true"
        )
        try:
            r = self._session.get(url, headers=_ha_headers(), timeout=30)
            r.raise_for_status()
            data = r.json()
            logger.debug(f"get_history({entity_id}): got {len(data)} series, first series has {len(data[0]) if data else 0} entries")
            if data and len(data) > 0 and len(data[0]) > 0:
                return data
            logger.warning(f"get_history({entity_id}): API returned empty data")
            return [[]]
        except Exception as e:
            logger.error(f"get_history({entity_id}): {e}")
            return None

    # ------------------------------------------------------------------
    # Services – REST API
    # ------------------------------------------------------------------

    def call_service(self, service: str, **kwargs):
        service = service.replace(".", "/", 1)
        url = f"{HA_URL}/api/services/{service}"
        try:
            r = self._session.post(url, headers=_ha_headers(), json=kwargs, timeout=15)
            r.raise_for_status()
        except Exception as e:
            logger.error(f"call_service({service}): {e}")

    # ------------------------------------------------------------------
    # State listeners
    # ------------------------------------------------------------------

    def listen_state(
        self,
        callback: Callable,
        entity_id: str,
        attribute: Optional[str] = None,
        new: Optional[str] = None,
        old: Optional[str] = None,
        **kwargs,
    ) -> str:
        handle = self._next_handle("ls")
        self._state_listeners[handle] = (
            entity_id,
            callback,
            {"attribute": attribute, "new": new, "old": old, **kwargs},
        )
        logger.debug(f"listen_state: {entity_id} → {handle}")
        return handle

    def cancel_listen_state(self, handle: str, **kwargs):
        self._state_listeners.pop(handle, None)

    def info_listen_state(self, handle: str, **kwargs) -> Optional[str]:
        """Returns the entity_id registered for a given handle."""
        entry = self._state_listeners.get(handle)
        if entry:
            return entry[0]
        return None

    # ------------------------------------------------------------------
    # Event listeners
    # ------------------------------------------------------------------

    def listen_event(self, callback: Callable, event: str, **kwargs) -> str:
        handle = self._next_handle("le")
        self._event_listeners.setdefault(event, []).append((callback, kwargs))
        logger.debug(f"listen_event: {event} → {handle}")
        return handle

    def cancel_listen_event(self, handle: str, **kwargs):
        pass  # simplified

    # ------------------------------------------------------------------
    # WebSocket listener loop
    # ------------------------------------------------------------------

    async def _start_ws_listener(self):
        # Exponential backoff: 5s, 10s, 20s, 40s, capped at 60s.
        # Resets to 5s after a successful connection that stays up for >60s.
        RECONNECT_DELAY_BASE = 5
        RECONNECT_DELAY_MAX = 60
        # How long (seconds) to suppress state-change callbacks after a reconnect.
        # HA floods the WS with unavailable→current_value transitions for every
        # entity; the unavailable guard in pv_opt handles most of these, but a
        # suppression window at the shim level prevents any edge cases from
        # triggering spurious optimiser runs.
        POST_RECONNECT_SUPPRESS_S = 15

        import time
        reconnect_delay = RECONNECT_DELAY_BASE

        while True:
            try:
                logger.info(f"WebSocket: connecting to {HA_WS_URL}")
                async with websockets.connect(HA_WS_URL, ping_interval=30) as ws:

                    # Auth handshake
                    msg = json.loads(await ws.recv())
                    if msg.get("type") != "auth_required":
                        raise RuntimeError(f"Expected auth_required, got: {msg}")
                    await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
                    msg = json.loads(await ws.recv())
                    if msg.get("type") != "auth_ok":
                        raise RuntimeError(f"WebSocket auth failed: {msg}")
                    logger.info("WebSocket: authenticated")

                    # Subscribe to state_changed
                    await ws.send(json.dumps({
                        "id": 1,
                        "type": "subscribe_events",
                        "event_type": "state_changed",
                    }))
                    msg = json.loads(await ws.recv())
                    if not msg.get("success"):
                        raise RuntimeError(f"state_changed subscribe failed: {msg}")
                    logger.info("WebSocket: subscribed to state_changed")

                    # Wait for initialize() to complete so all listen_event()
                    # calls are registered before we subscribe to them.
                    logger.info("WebSocket: waiting for initialize() to complete...")
                    await self._init_done.wait()
                    logger.info("WebSocket: initialize() done — subscribing to custom events")

                    # Brief yield to ensure _event_listeners is fully populated
                    # by the worker thread before we iterate over it
                    await asyncio.sleep(0.5)

                    # Log what events are registered for debugging
                    logger.info(f"WebSocket: registered event listeners: {list(self._event_listeners.keys())}")

                    # Subscribe to custom event types (e.g. PV_OPT trigger).
                    # Use a session-unique sub_id base to avoid duplicate IDs on reconnect.
                    sub_id = 100 + (self._ws_reconnect_count * 100)
                    subscribed: set[str] = set()
                    for event_name in list(self._event_listeners.keys()):
                        if event_name not in subscribed:
                            await ws.send(json.dumps({
                                "id": sub_id,
                                "type": "subscribe_events",
                                "event_type": event_name,
                            }))
                            await ws.recv()
                            subscribed.add(event_name)
                            logger.info(f"WebSocket: subscribed to event '{event_name}'")
                            sub_id += 1

                    # Set suppression window: ignore state-change callbacks for
                    # POST_RECONNECT_SUPPRESS_S seconds while HA replays entity states.
                    if self._ws_reconnect_count > 0:
                        self._ws_suppress_until = time.time() + POST_RECONNECT_SUPPRESS_S
                        logger.info(
                            f"WebSocket: reconnected (attempt {self._ws_reconnect_count}) — "
                            f"suppressing state callbacks for {POST_RECONNECT_SUPPRESS_S}s"
                        )
                    self._ws_reconnect_count += 1

                    # Reset backoff on successful connection
                    reconnect_delay = RECONNECT_DELAY_BASE

                    # Dispatch loop
                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        if msg.get("type") != "event":
                            continue

                        event = msg.get("event", {})
                        event_type = event.get("event_type")
                        data = event.get("data", {})

                        if event_type == "state_changed":
                            await self._dispatch_state_change(data)
                        elif event_type in self._event_listeners:
                            await self._dispatch_event(event_type, data)

            except Exception as e:
                logger.error(
                    f"WebSocket error: {e} — reconnecting in {reconnect_delay}s "
                    f"(attempt {self._ws_reconnect_count + 1})"
                )
                await asyncio.sleep(reconnect_delay)
                # Exponential backoff, capped at max
                reconnect_delay = min(reconnect_delay * 2, RECONNECT_DELAY_MAX)

    async def _dispatch_state_change(self, data: dict):
        import time
        entity_id = data.get("entity_id", "")
        new_obj = data.get("new_state") or {}
        old_obj = data.get("old_state") or {}
        new_state = new_obj.get("state")
        old_state = old_obj.get("state")
        new_attrs = new_obj.get("attributes", {})

        # Suppress callbacks during the post-reconnect entity flood window.
        # pv_opt's own unavailable guard also catches most of these, but this
        # prevents any edge cases from triggering spurious optimiser re-runs.
        if time.time() < self._ws_suppress_until:
            logger.debug(f"Post-reconnect suppression: ignoring state_changed for {entity_id} ({old_state} -> {new_state})")
            return

        for handle, (eid, callback, filters) in list(self._state_listeners.items()):
            if eid != entity_id:
                continue

            filter_new = filters.get("new")
            filter_old = filters.get("old")
            filter_attr = filters.get("attribute")

            if filter_new is not None and new_state != filter_new:
                continue
            if filter_old is not None and old_state != filter_old:
                continue

            value = new_attrs.get(filter_attr) if filter_attr else new_state

            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, self._locked_call,
                    functools.partial(callback, entity_id, filter_attr, old_state, value, {})
                )
            except Exception as e:
                logger.exception("listen_state callback error for {entity_id}:")

    async def _dispatch_event(self, event_name: str, data: dict):
        for callback, kwargs in list(self._event_listeners.get(event_name, [])):
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, self._locked_call,
                    functools.partial(callback, event_name, data, kwargs)
                )
            except Exception as e:
                logger.exception("listen_event callback error for {event_name}:")

    def _locked_call(self, fn: Callable):
        """
        Acquire _optimise_lock then call fn().
        All executor callbacks go through here so that only one
        pv_opt callback runs at a time — replicating @app_lock.
        """
        with self._optimise_lock:
            fn()

    # ------------------------------------------------------------------
    # Scheduler
    # ------------------------------------------------------------------

    def run_in(self, callback: Callable, delay: float, **kwargs) -> str:
        async def _delayed():
            await asyncio.sleep(delay)
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, self._locked_call, functools.partial(callback, kwargs)
                )
            except Exception as e:
                logger.exception("run_in callback error:")

        asyncio.run_coroutine_threadsafe(_delayed(), self._main_loop)
        return self._next_handle("ri")

    def run_every(self, callback: Callable, start, interval: float, **kwargs) -> str:
        async def _repeating():
            # Calculate the first fire time
            if isinstance(start, datetime):
                next_run = start.astimezone(timezone.utc)
            else:
                next_run = datetime.now(tz=timezone.utc)

            while True:
                # Sleep until the next absolute wall-clock fire time
                now = datetime.now(tz=timezone.utc)
                delay = max(0.0, (next_run - now).total_seconds())
                await asyncio.sleep(delay)

                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, self._locked_call, functools.partial(callback, kwargs)
                    )
                except Exception as e:
                    logger.exception("run_every callback error:")

                # Advance to the next absolute boundary — never drifts regardless
                # of how long the callback took
                next_run = next_run + timedelta(seconds=interval)
                # If we've fallen more than one interval behind (e.g. after a
                # long blocking call), skip missed fires and re-anchor to now
                now = datetime.now(tz=timezone.utc)
                while next_run < now:
                    logger.warning(f"run_every: skipping missed fire, re-anchoring schedule")
                    next_run = next_run + timedelta(seconds=interval)

        task = asyncio.run_coroutine_threadsafe(_repeating(), self._main_loop)
        self._scheduler_tasks.append(task)
        return self._next_handle("re")

    def cancel_timer(self, handle: str, **kwargs):
        logger.debug(f"cancel_timer: {handle} (best-effort)")

    # ------------------------------------------------------------------
    # Datetime helpers
    # ------------------------------------------------------------------

    def get_now(self) -> datetime:
        return datetime.now(tz=timezone.utc)

    def get_now_ts(self) -> float:
        return datetime.now(tz=timezone.utc).timestamp()

    def parse_datetime(self, dt_str: str, **kwargs) -> datetime:
        from dateutil import parser as dtparser
        return dtparser.parse(dt_str)

    def convert_utc(self, utc_dt: datetime) -> datetime:
        return utc_dt.astimezone()

    def get_tz_offset(self) -> int:
        offset = datetime.now().astimezone().utcoffset()
        return int(offset.total_seconds() / 60) if offset else 0

    def _load_tz(self):
        pass

    # ------------------------------------------------------------------
    # Misc stubs
    # ------------------------------------------------------------------

    def get_app(self, app_name: str):
        return None

    def notify(self, message: str, **kwargs):
        self.call_service("notify/persistent_notification", message=message)

    # ------------------------------------------------------------------
    # initialize() – overridden by PVOpt; _run() is called from __main__
    # ------------------------------------------------------------------

    async def initialize(self):  # pragma: no cover
        raise NotImplementedError("Subclass must implement initialize()")

    async def _run(self):
        """
        Called from __main__ instead of initialize() directly.
        Starts the WebSocket listener concurrently with initialize() so
        both run in the same event loop.  Sets _init_done after initialize()
        returns so the WS listener knows it's safe to subscribe to custom events.

        initialize() (and all callbacks it triggers) is run in a thread executor
        so that blocking time.sleep() calls inside pv_opt don't stall the asyncio
        event loop — keeping the WebSocket alive and MQTT responsive throughout.
        """
        ws_task = asyncio.ensure_future(self._start_ws_listener())
        try:
            loop = asyncio.get_event_loop()
            self._main_loop = loop   # store for use by run_every/run_in in worker thread
            await loop.run_in_executor(None, self._initialize_sync)
            self._init_done.set()
            logger.info("initialize() complete — WS custom event subscriptions unblocked")
            await ws_task
        except Exception as e:
            logger.exception("Fatal error in _run():")
            ws_task.cancel()
            raise

    def _initialize_sync(self):
        """
        Synchronous wrapper around initialize() for run_in_executor.
        initialize() is decorated with @ad.app_lock which in the Add-On is a
        no-op wrapper that makes it a regular synchronous function, so we call
        it directly rather than via run_until_complete().
        """
        self.initialize()
