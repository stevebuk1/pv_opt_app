## 1.0.7-Beta-3
Update Pv_opt to 5.1.8-Beta-5:
- Bugfixes for #424
- If on IOG, use the Octopus Energy Integration for pricing information in preference to the website (#459)
- Bugfix - axle_allow_pv_opt_writes is inverted.
       Note: commit includes a fix to make a onetime write to switch.pvopt_axle_allow_pvopt_writes to set it to True, 
       and will store it has done this by creating a new entity sensor.pvopt_axle_write_polarity_migrated. (#479)
- Handle code=null in Free Electricity Sessions (https://github.com/stevebuk1/pv_opt_app/issues/52)
- Add year to logging for Free Electricity Session Events (https://github.com/stevebuk1/pv_opt_app/issues/52)

Update Pv_opt to 5.1.8-Beta-3:
- Fix error introduced in last commit. 

## 1.0.7-Beta-2
Update Pv_opt to 5.1.8-Beta-2:
- Bugfix for "TypeError: unsupported operand type(s) for /: 'str' and 'int'" by
  Utilising historic SOC if current SOC read fails.

## 1.0.7-Beta-1
Update Pv_opt to 5.1.8-Beta-1:
- Bugfix to address stevebuk1/pv_opt_app#44

## 1.0.6
Update Pv_opt to 5.1.7:
- Bugfix for error message "AttributeError: 'NoneType' object has no attribute 'keys'" when loading free electricity sessions (no issue raised)

## 1.0.5

- ha_interface.py, Improve error logging
- requirements.txt, allow use of Pandas libraries 3.X.X. (resolves https://github.com/stevebuk1/pv_opt_app/issues/46).

Update Pv_opt to 5.1.6
- Bigfix on last commit for redacting MQTT password (stevebuk1/pv_opt_app#47)
- Redact MQTT password (and anything else that looks like a login or key). (Bugfix for stevebuk1/pv_opt_app#47)
- Bugfix for "run_every callback error: unsupported operand type(s) for 'str' and 'int'" error (no issue raised)
- Fix bug in Cyclic removal (if there is a single discharge slot, it is incorrectly tagged as cyclic).
- Sunsynk bugfixes for Selltime3 (https://github.com/stevebuk1/pv_opt/issues/424)
- Sunsynk bugfixes (https://github.com/stevebuk1/pv_opt/issues/424) - ensure Selltime3 is positive. 
- Sunsynk bugfixes (https://github.com/stevebuk1/pv_opt/issues/424) - remove Sysworkmode write from disable charging routine.
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
