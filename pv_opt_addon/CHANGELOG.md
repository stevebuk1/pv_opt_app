## 1.0.7
Update Pv_opt to 5.1.9:
- Bugfix for #479
- Add warning to startup if Axle entities not found (#474)
- Introduce support for Octopus Free Sunday Sessions (needs opt-in via email)
- Report stale "planned_dispatches" attribute from the Octopus Energy Integration in Pv_opt log
- Solar is impacting charge rate when its irrelevant, correct this.
- Correct bug in charge algorithm that add swaps to last 1 hour of overnight cheap rate when it should spread over all cheap slots
- Further bugfix in Free Electricity Sessions (#52)
- Correct error in event start/event end windowing for Saving Sessions and Free Electricity Sessions
- If on IOG, use the Octopus Energy Integration for pricing information in preference to the website ([#459](https://github.com/stevebuk1/pv_opt/issues/459))
- Bugfix - axle_allow_pv_opt_writes is inverted.

       Note: commit includes a fix to make a onetime write to switch.pvopt_axle_allow_pvopt_writes to set it to True, 
       and will store it has done this by creating a new entity sensor.pvopt_axle_write_polarity_migrated. (#479)
  
- Handle code=null in Free Electricity Sessions (#52)
- Add year to logging for Free Electricity Session Events (#52)
- Bugfix for "TypeError: unsupported operand type(s) for /: 'str' and 'int'" by utilising historic SOC if current SOC read fails.
- Bugfix for #44
- Sunsynk further development:
   - Add awareness of charger_power_watts to Sunsynk integration
   - Always write all six slots when writing to Sunsynk inverter.
   - Sunsynk - remove erroneous mapping of battery voltage to battery current sensor (https://github.com/stevebuk1/pv_opt/issues/424). 
   - Bugfixes for Sunsynk (https://github.com/stevebuk1/pv_opt/issues/424)

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
