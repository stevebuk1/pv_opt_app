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
