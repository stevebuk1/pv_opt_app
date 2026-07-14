## 1.0.04
- Updates to sunsynk.py to continue Inverter development (Instructions for SunSynk inverters #424)
- Remove inverter power cap when performing forced discharging at full rate (Discharge rates during Axle events #464)
- Do not automatically join Octopus Saving Sessions if Axle integration is installed (Axle and Octopus Saving Sessions - only one Demand Flexiblity service allowed #463)
- Resolve various MQTT issues (Pv_opt reads wrong value from HA after an HA disconnect #466, Inconsistent use of MQTT pv_opt_app#40, Not honouring config pv_opt_app#39)
Update Pv_opt to 5.1.4.

## 1.0.3
- Update repo to use prebuilt images

## 1.0.2-Beta-1
- Update to Pv_opt 5.1.3-Beta1 (More fixes for inverter double writes)

## 1.0.1
- Update to Pv_opt 5.1.2 (Bugfix for #459 in Pv_opt repo (Axle events to be checked each optimiser run))

## 1.0.0
- First Release of Pv_opt v5.1.0 running as an App (formerly known as an AddOn)
