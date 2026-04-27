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


# ---------------------------------------------------------------------------
# app_lock – no-op (asyncio is single-threaded; pv_opt uses it as a mutex)
# ---------------------------------------------------------------------------

def app_lock(fn):
    """Drop-in for @ad.app_lock — no-op in asyncio context."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# MQTTShim – thin paho wrapper; mirrors AppDaemon's MQTT plugin API
# ---------------------------------------------------------------------------

class MQTTShim:
    """
    Used via  self.mqtt = self.get_plugin_api("MQTT")
    Implements mqtt_publish, mqtt_subscribe, listen_state.
    """

    def __init__(self):
        self._client = _paho_mqtt.Client()
        if MQTT_USER:
            self._client.username_pw_set(MQTT_USER, MQTT_PASS)
        self._topic_callbacks: dict[str, list[Callable]] = {}

        def _on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode("utf-8", errors="replace")
            for t, cbs in list(self._topic_callbacks.items()):
                if topic == t:
                    for cb in cbs:
                        try:
                            cb(payload)
                        except Exception as e:
                            logger.error(f"MQTT callback error on {topic}: {e}")

        self._client.on_message = _on_message
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            self._client.loop_start()
            logger.info(f"MQTT connected to {MQTT_HOST}:{MQTT_PORT}")
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

        def _wrap(payload):
            try:
                callback(actual_topic, None, None, payload, {})
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
        self._optimise_lock = threading.Lock()
        self._main_loop: asyncio.AbstractEventLoop | None = None  # set in _run()

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
                self._mqtt_shim = MQTTShim()
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
                r = requests.get(url, headers=_ha_headers(), timeout=10)
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
            r = requests.get(url, headers=_ha_headers(), timeout=10)
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
                    r = requests.get(url, headers=_ha_headers(), timeout=10)
                    if r.ok:
                        existing_attrs = r.json().get("attributes", {})
                except Exception:
                    pass
                payload["attributes"] = {**existing_attrs, **attributes}
        try:
            # Use custom serialiser to handle Timestamps and numpy types
            payload_str = json.dumps(payload, default=self._json_serialiser)
            r = requests.post(
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
            r = requests.get(url, headers=_ha_headers(), timeout=10)
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
        url = (
            f"{HA_URL}/api/history/period/{start_str}"
            f"?filter_entity_id={entity_id}&minimal_response=true&no_attributes=false"
        )
        try:
            r = requests.get(url, headers=_ha_headers(), timeout=30)
            r.raise_for_status()
            data = r.json()
            if data and len(data) > 0:
                return data   # already [[{last_updated, state}, ...]]
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
            r = requests.post(url, headers=_ha_headers(), json=kwargs, timeout=15)
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
        RECONNECT_DELAY = 5

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

                    # Subscribe to custom event types (e.g. PV_OPT trigger)
                    sub_id = 2
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
                logger.error(f"WebSocket error: {e} — reconnecting in {RECONNECT_DELAY}s")
                await asyncio.sleep(RECONNECT_DELAY)

    async def _dispatch_state_change(self, data: dict):
        entity_id = data.get("entity_id", "")
        new_obj = data.get("new_state") or {}
        old_obj = data.get("old_state") or {}
        new_state = new_obj.get("state")
        old_state = old_obj.get("state")
        new_attrs = new_obj.get("attributes", {})

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
                logger.error(f"listen_state callback error for {entity_id}: {e}")

    async def _dispatch_event(self, event_name: str, data: dict):
        for callback, kwargs in list(self._event_listeners.get(event_name, [])):
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, self._locked_call,
                    functools.partial(callback, event_name, data, kwargs)
                )
            except Exception as e:
                logger.error(f"listen_event callback error for {event_name}: {e}")

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
                logger.error(f"run_in callback error: {e}")

        asyncio.run_coroutine_threadsafe(_delayed(), self._main_loop)
        return self._next_handle("ri")

    def run_every(self, callback: Callable, start, interval: float, **kwargs) -> str:
        async def _repeating():
            if isinstance(start, datetime):
                now = datetime.now(tz=start.tzinfo)
                delay = max(0.0, (start - now).total_seconds())
                if delay > 0:
                    await asyncio.sleep(delay)
            while True:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None, self._locked_call, functools.partial(callback, kwargs)
                    )
                except Exception as e:
                    logger.error(f"run_every callback error: {e}")
                await asyncio.sleep(interval)

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
            logger.error(f"Fatal error in _run(): {e}")
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
