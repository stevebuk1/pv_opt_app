## 1.0.5-Beta-2
Update Pv_opt to 5.1.6-Beta-1:
- Sunsynk bugfixes for Selltime3 (https://github.com/stevebuk1/pv_opt/issues/424)
- Fix bug in Cyclic removal (if there is a single discharge slot, it is incorrectly tagged as cyclic).

## 1.0.5-Beta-1
Update Pv_opt to 5.1.5:
- IOG tariff - update Pv_opt to handle 6 hour charge cap tariff codes. 
  Note: this is a partial fix and requires the use of the previous IOG tariff code being added to config.yaml.

## 1.0.4
- Introduce Websocket retry backoff mechanisms into ha_interface.py (WebSocket reconnect causes spurious optimiser re-runs and log flooding at scheduled HA maintenance windows #41)

Update Pv_opt to 5.1.4:
- Updates to sunsynk.py to continue Inverter development (https://github.com/stevebuk1/pv_opt/issues/424)
- Remove inverter power cap when performing forced discharging at full rate (https://github.com/stevebuk1/pv_opt/issues/464)
- Do not automatically join Octopus Saving Sessions if Axle integration is installed (https://github.com/stevebuk1/pv_opt/issues/463)
- Resolve various MQTT issues (https://github.com/stevebuk1/pv_opt/issues/466, https://github.com/stevebuk1/pv_opt_app/issues/40,  https://github.com/stevebuk1/pv_opt_app/issues/39)

## 1.0.3
- Update repo to use prebuilt images

## 1.0.2-Beta-1
- Update to Pv_opt 5.1.3-Beta1 (More fixes for inverter double writes)

## 1.0.1
- Update to Pv_opt 5.1.2 (Bugfix for #459 in Pv_opt repo (Axle events to be checked each optimiser run))

## 1.0.0
- First Release of Pv_opt v5.1.0 running as an App (formerly known as an AddOn)
