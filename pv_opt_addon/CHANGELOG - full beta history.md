## 1.0.7-Beta-7
Update Pv_opt to 5.1.9-Beta-3:
- Introduce support for Octopus Free Sunday Sessions (needs opt-in via email)
- Sunsynk - remove erroneous mapping of battery voltage to battery current sensor. 

## 1.0.7-Beta-6
Update Pv_opt to 5.1.9-Beta-2:
- Report stale "planned_dispatches" attribute from the Octopus Energy Integration in Pv_opt log
- Always write all six slots when writing to Sunsynk inverter.

Update Pv_opt to 5.1.9-Beta-1:
- Solar is impacting charge rate when its irrelevant, correct this.
- Correct bug in charge algorithm that add swaps to last 1 hour of overnight cheap rate when it should spread over all cheap slots
- Add awareness of charger_power_watts to Sunsynk integration

## 1.0.7-Beta-5
Update Pv_opt to 5.1.8-Beta-6:
- Further bugfix in Free Electricity Sessions (https://github.com/stevebuk1/pv_opt_app/issues/52)
- Correct error in event start/event end windowing for Saving Sessions and Free Electricity Sessions

## 1.0.7-Beta-4
Update Pv_opt to 5.1.8-Beta-5:
- Bugfixes for #424
- If on IOG, use the Octopus Energy Integration for pricing information in preference to the website (#459)
- Bugfix - axle_allow_pv_opt_writes is inverted.

       Note: commit includes a fix to make a onetime write to switch.pvopt_axle_allow_pvopt_writes to set it to True, 
       and will store it has done this by creating a new entity sensor.pvopt_axle_write_polarity_migrated. (#479)
  
- Handle code=null in Free Electricity Sessions (https://github.com/stevebuk1/pv_opt_app/issues/52)
- Add year to logging for Free Electricity Session Events (https://github.com/stevebuk1/pv_opt_app/issues/52)

## 1.0.7-Beta-3
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
## 1.0.6
Update Pv_opt to 5.1.7:
Bugfix for error message "AttributeError: 'NoneType' object has no attribute 'keys'" when loading free electricity sessions (no issue raised)

## 1.0.5
- ha_interface.py, Improve error logging
- requirements.txt, allow use of Pandas libraries 3.X.X. (resolves #46).

Update Pv_opt to 5.1.6
- Bigfix on last commit for redacting MQTT password (#47)
- Redact MQTT password (and anything else that looks like a login or key). (Bugfix for #47)
- Bugfix for "run_every callback error: unsupported operand type(s) for 'str' and 'int'" error (no issue raised)
- Fix bug in Cyclic removal (if there is a single discharge slot, it is incorrectly tagged as cyclic).
- Sunsynk bugfixes for Selltime3 (stevebuk1/pv_opt#424)
- Sunsynk bugfixes (stevebuk1/pv_opt#424) - ensure Selltime3 is positive.
- Sunsynk bugfixes (stevebuk1/pv_opt#424) - remove Sysworkmode write from disable charging routine.
- IOG tariff - update Pv_opt to handle 6 hour charge cap tariff codes. Note: this is a partial fix and requires the use of the previous IOG tariff code being added to config.yaml.


## 1.0.5-Beta-6
Update Pv_opt to 5.1.6-Beta-4:
- Bigfix on last committ for redacting MQTT password (stevebuk1/pv_opt_app#47)

## 1.0.5-Beta-5
Update Pv_opt to 5.1.6-Beta-3:
- Redact MQTT password (and anything else that looks like a login or key). (Bugfix for stevebuk1/pv_opt_app#47)

## 1.0.5-Beta-4
- ha_interface.py, Improve error logging v2
- requirements.txt, allow use of Pandas libraries 3.X.X. (resolves https://github.com/stevebuk1/pv_opt_app/issues/46).
Pv_opt remains at 5.1.6-Beta-2.

## 1.0.5-Beta-3
Improve error logging in ha_interface.py. 

Update Pv_opt to 5.1.6-Beta-2:
- Sunsynk bugfixes (https://github.com/stevebuk1/pv_opt/issues/424) - ensure Selltime3 is positive. 
- Sunsynk bugfixes (https://github.com/stevebuk1/pv_opt/issues/424) - remove Sysworkmode write from disable charging routine.
- Bugfix for "run_every callback error: unsupported operand type(s) for 'str' and 'int'" error (no issue raised)

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

## 1.0.4-Beta-16
- Ensure MQTT STATE topic is updated by pv_opt for all entity changes received by pv_opt. 
- Correctly update both STATE and SET topics during startup, depending on whether overwrite_ha_on_restart is true or false — previously SET was never refreshed on startup overwrite, leaving stale retained commands that could be replayed and override config.yaml on a later restart.
Pv_opt updated to 5.1.3-Beta-14

## 1.0.4-Beta-15
- Fix handling of "None" as a string in _value_from__state.
- Handle none if returned during loading of Octopus Savings events.
- Remove dead code.
Pv_opt updated to 5.1.3-Beta-13

## 1.0.4-Beta-14
- Don't republish to MQTT when values haven't changed.
Pv_opt updated to 5.1.3-Beta-12

## 1.0.4-Beta-13
- Try a token method in the debounced optimiser. 
Pv_opt updated to 5.1.3-Beta-11

## 1.0.4-Beta-12
- Remove previous change and debounce optimiser.
Pv_opt updated to 5.1.3-Beta-10

## 1.0.4-Beta-11

- Suppress phantom optimiser state change calls until initial optimisation is complete. 
Pv_opt updated to 5.1.3-Beta-9

## 1.0.4-Beta-10
- Ensure reads in _value_from_state are case insensitive
Pv_opt updated, but remains at 5.1.3-Beta-8

## 1.0.4-Beta-9
- Gate "_active" entity updates from triggering new optimise cycles. 
Pv_opt updated to 5.1.3-Beta-8  

## 1.0.4-Beta-8
- fix(ha_interface): make app_lock actually serialize optimise() entry points
Pv_opt remains at 5.1.3-Beta-7

## 1.0.4-Beta-7
- serialize MQTT callbacks against optimise_lock; add connect/disconnect logging
Pv_opt remains at 5.1.3-Beta-7

## 1.0.4-Beta-6
- Bugfix for #40, MQTT publish non-functional (fix identing in ha_interface.py)
Pv_opt remains at 5.1.3-Beta-7

## 1.0.4-Beta-5
- Write battery current using service set_battery_settings instead of set_solar_settings
Pv_opt updated to 5.1.3-Beta-7

## 1.0.4-Beta-4
- Sunsynk: Write battery current using service set_battery_settings instead of set_solar_settings
- Remove use of IOG charge_to_add (slots are now read from Octopus API every optimiser run)
- Sunsynk: Use intentionally incorrect entity defaults for id_consumption such that id_consumption_today is used in preference.
Pv_opt updated to 5.1.3-Beta-6

## 1.0.4-Beta-3
- Bugfixes for Pv_opt Issue #466.
Pv_opt updated to 5.1.3-Beta-5

## 1.0.4-Beta-2
- Further Bugfixes for issues 39 and 40 - MQTT updates not updating Pv_opt
- Include latest Sunsynk code changes (Issue #424 on Pv_opt)
- Bugfixes for Pv_opt Issue #466.
  
Pv_opt updated to 5.1.3-Beta-4

## 1.0.4-Beta-1
- Bugfixes for issues 39 and 40 - MQTT updates not updating Pv_opt. Pv_opt updated to 5.1.3-Beta-3

## 1.0.3
- Update repo to use prebuilt images

## 1.0.2-Beta-1
- Update to Pv_opt 5.1.3-Beta1 (More fixes for inverter double writes)

## 1.0.1
- Update to Pv_opt 5.1.2 (Bugfix for #459 in Pv_opt repo (Axle events to be checked each optimiser run))

## 1.0.0
- First Release of Pv_opt v5.1.0 running as an App (formerly known as an AddOn)
