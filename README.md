# PV Opt App: Home Assistant Solar/Battery Optimiser 
App (AddOn) v1.0.4-Beta-3, utilising Pv_opt v5.1.3-Beta-5. 

<h2>Introduction</h2>

Solar / Battery Charging Optimisation App for Home Assistant. 

This App (previously known as an AddOn) can be used with Home Assistant to run Pv_opt without using AppDaemon.

Pv_opt itself is unchanged from the AppDaemon version and so will behave identically. 

<h2>Upgrading from PV_opt running under AppDaemon</h2>

If you are currently running PV_opt under AppDaemon, follow this section, otherwise go to Installation Instuctions below . 

* Make a copy of your Pv_opt config.yaml file (its at /homeasistant/appdaemon/apps/pv_opt/config/config.yaml). 

* Stop Appdaemon, and make sure the toggles "Start on Boot" and "Watchdog" are set to off (or remove Pv_opt from AppDaemon if you have other AppDeamon apps still running).
* Open your Home Assistant instance and show the Add app repository dialog with a specific repository URL pre-filled.
* Go to settings, apps, install app
* Click the 3 vertical dots at top right and select "Repositories". 
* Press the "Add" button, and add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository
* Go back one page, scroll to the bottom to the Pv_opt Addon, and press Install
* Installation will take a few minutes as the App is built (you can follow progress in the HA Supervisor Log)
* When installed, go to the Configuration tab and add the MQTT username and password you used when originally intalling Mosquito. 
* Click Start on the App. 


Notes:
* The installer will copy across your config.yaml from the AppDaemon area (if installed at /homeasistant/appdaemon/apps/pv_opt/config/config.yaml)
  this will now live at /homeassistant/pv_opt/config.yaml. No changes are required. 
* pv_opt.log is now written to /homeassistant/pv_opt/pv_opt.log
* error.log is now written to /homeassistant/pv_opt/error.log
* There is also a live log in the Log Tab of the App which includes the contents of both logs as well as any logging that went to main.log/AppDaemon.log.

And remember: Do not run the Pv_opt App at the same time as Pv_opt within AppDaemon. 

<h2>Installation Instructions</h2>

Follow these instructions if you are installing Pv_opt for the very first time. 

<h3>1. Get a Solcast Hobby Account</h3>

<b>PV_Opt</b> relies on solar forecasts data from Solcast. You can sign up for a Private User account [here](https://solcast.com/free-rooftop-solar-forecasting?gclid=CjwKCAiAr4GgBhBFEiwAgwORrQp6co5Qw8zNjEgUhBee7Hfa39_baEWG-rB-GB3FFpiaIA5eAPHhahoC3vAQAvD_BwE). This licence gives you 10 (it used to be 50 🙁) API calls a day.

<h3>2. Install the Solcast PV Solar Integration (v4.1.x)</h3>

1. Install the integation via HACS: https://github.com/BJReplay/ha-solcast-solar
2. Add the Integration via Settings: http://homeassistant.local:8123/config/integrations/dashboard
3. Once installed configure using your Solcast API Key from (1) .
4. Set up an automation to update according to your desired schedule. Once every 3 hours will work. Or utilise Solcast automatic updates. 

<h3>3. Install the Octopus Energy Integration (If Required)</h3>

This excellent integration will pull Octopus Price data in to Home Assistant. Pv Opt pulls data from Octopus independently of this integration but will extract current tariff codes from it if they are avaiable. If not it will either use account details supplied in `secrets.yaml` or explicitly defined Octopus tariff codes set in `config.yaml`. If on Intelligent Octopus Go, this integration is required, as Pv_opt will use this to identify any slots allocated outside of 23:30 to 05:30 for use in its charge plan and managing the house battery during car charging slots.

<h3>4. Install the Integration to Control Your Inverter</h3>

At present this app works directly with Solis hybrid inverters using one of the following:
1) the Solax Modbus integration (https://github.com/wills106/homeassistant-solax-modbus)
2) the HA Core Modbus as described here: (https://github.com/fboundy/ha_solis_modbus)
3) SolisCloud - via the Solis-Sensor integration (with Control enabled) as described here (https://github.com/hultenvp/solis-sensor)
4) SolisCloud - Combining the Solis-Sensor (https://github.com/hultenvp/solis-sensor) and Solis-Control (https://github.com/mkuthan/solis-cloud-control) integrations. 
5) A Solarman integration (https://github.com/davidrapan/ha-solarman)

<h4>Solax Modbus:</h4>

1. Install the integration via HACS: https://github.com/wills106/homeassistant-solax-modbus
2. Add the Integration via Settings: http://homeassistant.local:8123/config/integrations/dashboard
3. Configure the connection:
   |||
   |:--|:--|
   | Prefix| solis|
   |Interface| TCP/Ethernet|
   |Inverter Type| solis|
   |IP Address| IP of your datalogger|
   |TCP Port| 502|
   |Protocol| Modbus TCP|
4. Check that you have comms with the inverter and the various entities in the integration are populated with data

<h4>HA Core Modbus</h4>

Follow the Github instructions here: https://github.com/stevebuk1/ha_solis_modbus

<h4>Using Solis Cloud</h4>
<h5>Solis-Sensor</h5>

Follow the Github instruction here: https://github.com/hultenvp/solis-sensor
Either enable Control via this integration (mnote this is Experimental/Beta), or leave disabled and install Solis-Control below. 


<h5>Solis-Control</h5>

Follow the Github instruction here: https://github.com/mkuthan/solis-cloud-control

Note: install with device name of "solis" rather than the default of "inverter_control_XXXXXXXXXXX" (where X is the inverter S/N)


<h4>Solarman</h4>

Follow the Github instructions here: (https://github.com/davidrapan/ha-solarman)

For Solis Inverters, replace existing Solis_Hybrid.yaml with this one:

https://github.com/stevebuk1/pv_opt/blob/main/files/solis_hybrid.yaml

<h3>5. Install the MQTT Integraion in Home Assistant</h3>

1. Click on the button below to add the MQTT integration:

    [![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=mqtt)

<h3>6. Install Mosquitto MQTT Broker</h3>

1. Navigate to Settings -> Addons and click "Mosquito Broker"

2. Click on Install

3. Configure the Add-On as per the documentation: http://homeassistant.local:8123/hassio/addon/core_mosquitto/documentation

4. Make a note of the MQTT username and password for later.

<h3>7. Install File Editor</h3>

Follow instructions here: https://github.com/home-assistant/addons/blob/master/configurator/README.md

Navigate to Settings -> Addons -> File editor -> Configuration and set "Enforce Basepath" to "off".

<h3>8. Install Samba Share and/or Studio Code Server Add-ons If Required</h3>

Both of these add-ons make it easier to edit text files on your HA Install but aren't strictly necessary. `Samba Share` also makes it easier to access the log files.

<h3>9. Install the PV_opt App (formerly known as an AddOn)</h3>

* Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
* Go to settings, apps, install app
* Click the 3 vertical dots at top right and select "Repositories". 
* Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository
* Go back one page, scroll to the bottom to the Pv_opt Addon, and press Install. This will take a couple of minutes. 
* When installed, go to the Configuration tab and add the MQTT username and password from Step 4 above. 
* Click Start on the App.
* Select the Log tab. The following should be produced:

```
[22:20:33] INFO: Starting PV Opt dev
[22:20:33] INFO: Using existing config at /config/pv_opt/config.yaml
[22:20:33] INFO: Launching PV Opt...
2026-04-28 22:20:35  INFO     *************** PV Opt Add-On Version: 1.0.0-Beta-2 ***************
2026-04-28 22:20:35  INFO     Logging to /config/pv_opt/pv_opt.log and /config/pv_opt/error.log
2026-04-28 22:20:35  INFO     Loaded pv_opt config from /config/pv_opt/config.yaml
2026-04-28 22:20:35  INFO     
2026-04-28 22:20:35  INFO     WebSocket: connecting to ws://supervisor/core/api/websocket
2026-04-28 22:20:35  INFO     *************** PV Opt Version: v5.1.2-Beta-6 ***************
2026-04-28 22:20:35  INFO     
2026-04-28 22:20:35  INFO     Pre-release version. Enabling debug logging
2026-04-28 22:20:35  INFO     Debug Categories selected = O
2026-04-28 22:20:35  INFO     Debug Categories selected = O
2026-04-28 22:20:35  INFO     MQTT connected to core-mosquitto:1883
2026-04-28 22:20:35  INFO     Local timezone set to GB
2026-04-28 22:20:35  INFO     Time Zone Offset: 60 minutes
2026-04-28 22:20:35  INFO     Inverter type: SOLIS_SOLAX_MODBUS: inverter module: solis.py

```

<h2>Configuration</h2>

If you have the Solcast, Octopus and Solax integrations set up as specified above, there should be minimal configuration required.

If you are running a different integration or inverter brand you will need to edit the `config.yaml` file in the appropriate section to select the correct `inverter_type`.
You may also need to change the `device_name`. This is the name given to your inverter by your integration. The default is `solis` but this can also be changed in `config.yaml`.

E.g:

For the Core Modbus Integration:

    inverter_type: SOLIS_CORE_MODBUS
    device_name: solis

For the Solarman integration:

    inverter_type: SOLIS_SOLARMAN_V2
    device_name: solis

The `config.yaml` file also includes all the other configuration used by PV Opt. If you are using the default setup you shouldn't need to change this but you can edit anything by un-commenting the relevant line in the file. The configuration is grouped by inverter/integration and should be self-explanatory. Once PV Opt is installed the config is stored within entities in Home Assistant. It you want these over-ritten please ensure that `overwrite_ha_on_restart` is set to `true`:

    overwrite_ha_on_restart: true

<b><i>PV_Opt</b></i> needs to know the size of your battery and the power of your inverter: both when inverting battery to AC power and when chargingh tha battery. It will attempt to work these out from the data it has loaded (WIP) but you should check the following enitities in Home Assistant:

<h3>System Parameters</h3>

| Parameter           | Units | Entity                              | Default Value |
| :------------------ | :---: | :---------------------------------- | :-----------: |
| Battery Capacity    |  Wh   | `number.pvopt_batter_capacity_wh`   |     10000     |
| Inverter Power      |   W   | `number.pvopt_inverter_power_watts` |     3600      |
| Charger Power       |   W   | `number.pvopt_charger_power_watts`  |     3500      |
| Inverter Efficiency |   %   | `number.pvopt_inverter_efficiency`  |      97%      |
| Charger Efficiency  |   %   | `number.pvopt_charger_efficiency`   |      91%      |

There are then only a few things to control the optimisation process. These have been grouped as follows:

<h3>Control Parameters</h3>
These are the main parameters that will control how PV Opt runs:

| Parameter                |   Units    | Entity                                    | Default | Description                                                                                                                                                                                                                  |
| :----------------------- | :--------: | :---------------------------------------- | :-----: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read Only Mode           | `on`/`off` | `switch.pvopt_read_only`                  |   On    | Controls whether the app will actually control the inverter. Start with this on until you are happy the charge/discharge plan makes sense.                                                                             |
| Charge to 100%           | `on`/`off` | `switch.pvopt_charge_to_100`                  |   Off    | Override Optimised Charging by instead charging to 100% in the cheap rate, keeping as low a charge rate as possible such that 100% is reached smoothly by the end of the cheap rate period. During Winter, on a tariff that has a defined cheap rate (Go, IOG, Cosy etc) theres little benefit to be gained by optimizing battery use to achieve a battery SOC of "flat" just before the next cheap rate begins, as errors in consumption and solcast mean that "flat" can happen early with a large consequential cost. Any benefit of leaving room for solar to fill the battery (which Pv_opt will normally do) is largely neglible in winter. Note: this mode is ultimately an overide of the prime aim of Pv_opt, which is to optimise based on cost, but is provided where error margins can lead to a frequent flat battery. It has no effect for Octopus Agile users nor if Optimise Discharging is selected (see below). The cost of this plan is displayed in "Optimsed Charging" so it can be compared with Base (no charging or discharging). |
| Optimise Discharging     | `on`/`off` | `switch.pvopt_forced_discharge`           |   On   | Controls whether the app will allow for forced discharge as well as charge                                                                                                                                                   |
| Allow Cyclic             | `on`/`off` | `switch.pvopt_allow_cyclic`               |   On    | Controls whether the app will allow cycles of alternating charge/discharge                                                                                                                                                   |
| Use Solar                | `on`/`off` | `switch.pvopt_use_solar`                  |   On    | Controls whether the app will use the Solcast solar forecast. If set to Off no solar will be used but battery charging can still be optimised for a time-of use tariff.                                                      |
| Solcast Confidence Level |  `number`  | `number.pvopt_solcast_confidence_level`   | Solcast | Selects which the Confidence Level for the Solcast forecast. Levels between 10% and 50% are weighted from the Solcast 10% and 50% forecasts. Levels between 50% and 90% are weighted from the Solcast 50% and 10% forecasts. |
| Optimser Frequency       |  minutes   | `number.pvopt_optimise_frequency_minutes` |   10    | Frequency of Optimiser calculation                                                                                                                                                                                           |

<h3>Consumption Parameters</h3>
These parameters will define how PV Opt estimates daily consumption:

| Parameter               |   Units    | Entity                                 | Default | Description                                                                                       |
| :---------------------- | :--------: | :------------------------------------- | :-----: | :------------------------------------------------------------------------------------------------ |
| Use Consumption History | `on`/`off` | `switch.pvopt_use_consumption_history` |   On    | Toggles whether to use actual <b>consumption history</b> or an estimated <b>daily consumption</b> |
| Load History Days | days | `number.pvopt_consumption_history_days` | 7 | Number of days of consumption history to use when predicting future load. HomeAssisant stores 10 days of history by default, longer periods requires additional tools e.g. MariaDB  |
| Load Margin | % | `number.pvopt_consumption_margin` | 10% | Margin to add to historic load for forecast (safety factor) |
| Weekday Weighting| fraction | `number.pvopt_day_of_week_weighting` | 0.5 | Defines how much weighting to give to the day of the week when averaging the load. 0.0 will use the simple average of the last `n` days based on `load_history_days` and 1.0 will just used the same day of the week within that window. Values in between will weight the estimate accordingly. If every day is the same use a low number. If your usage varies daily use a high number.
| Daily Consumption | kWh | `number.pvopt_daily_consumption_kwh` | 17 | Estimated daily consumption to use when predicting future load |
| Shape Consumption Profile | `on`/`off` | `switch.pvopt_shape_consumption_profile` | On | Defines whether to shape the consumption to a typical daily profile (`on`) or to assume constant usage (`off`). The shape of the daily profile can be modified within config.yaml. |

<h3>EV parameters</h3>

| Parameter               |  Units     | Entity                                 |  Default | Description                                                                                       |
| :---------------------- | :--------: | :------------------------------------- | :------: | :------------------------------------------------------------------------------------------------ |
| EV Charger                | None / Zappi / Other | `select.pvopt_ev_charger` |  None    | Set EV Charger Type. At the current release, only 'Zappi' is supported, 'Other' is unused and is for a future release. Note: Zappi support requires the MyEnergi HA integration to be installed. |
| EV Part of House Load     |       On / Off       | `switch.pvopt_ev_part_of_house_load` |   On    | Prevents house battery discharge when EV is charging. If your EV Charger is wired so it is seen as part of the house load, then it will discharge to the EV when the EV is charging. Setting this to On prevents this, as well as ensuring that any EV consumption is removed from Consumption History. If your Zappi is wired on its own Henley block and thus outside of what the inverter CT clamp will measure, then set this to Off. Note: PV Opt does not support allowing the house battery to be used to charge the car. |
| Car Charge Plan           |         kWh          | `switch.control_car_charging` |   Off    | Toggle Car Plan generation On/Off. For users on Agile, setitng to On will generate a candidate car charging plan on each optimiser run based on the settings below. The candidate plan is made active upon car plugin, or via Dashbaord command (see "Transfer Car Charge Plan" below). The active car charging plan is output live on binary_sensor.pvopt_car_charging_slot for use in HA automations to switch the EV charger on and off. An example HA automation to control a Zappi charger is included [here](https://github.com/stevebuk1/pv_opt/blob/main/files/zappi_automation.yaml). Intelligent Octopus Go users should set this to Off. If Off, the rest of the EV parameters below have no effect. |
| Transfer Car Charge Plan  |        On/Off        | `switch.transfer_car_charge_plan` |    30     | Make Candidate Car Charging Plan the active plan. Useful if adjusting any of the below paramaters after the car has been plugged in. This will automatically be set back to Off after the plan is transferred. This ensures any external HA automations used to auto-calculate "Car Charge to Add" based on car SOC don't corrupt the car charging plan once the car starts charging. |
| EV Charger Power          |          W           | `number.pvopt_ev_charger_power_watts` |     7000      | Set EV charger power. |
| EV Batttery Capacity      |         kWh          | `number.pvopt_ev_battery_capacity_kwh` |      60       | Set EV Battery Capacity. |
| Car Ready By              |         Time         | `select.car_charging_ready_by` |     06:30     | Set Time for when the Car is to be ready by. |
| Car Charge to Add         |          %           | `number.pvopt_ev_charge_target_percent` |      30       | % of 'charge to add' to the car. I.e if your car is at 40% and want it to be charged to 90% then set this to 50%. |
| Car Charge Slot max price |          p           | `number.pvopt_max_ev_price_p` |      30       | Maximum 1/2 hour slot price per kWh in pence added to the candidate car charging plan. Disable by setting to 0. Note: setting a low value may mean the car will not charge to the required SOC if overnight Agile rates are high.|
| Car Charge Efficiency     |          %           | `number.pvopt_ev_charger_efficiency_percent` |      92       | Charging Efficiency for EV Charger/Car. 92% is average for most cars/chargers but adjust if the car is consistently undercharging or overcharging against its target. |
| Prevent Discharge         |        On/off        | `switch.pvopt_prevent_discharge`  |      Off      | Set to prevent house battery discharge. Clear to allow normal inverter use. Useful for house battery dicharge prevention when high loads are being used (EVs not otherwise coupled in to Pv_opt, showers etc). When set, does not affect the house battery charge plan. |
| id zappi plug status      |       `string`       |                                              | Auto detected | In config.yaml, remap the autodeteted Zappi car plugin status entity to a named entity. If you have a single Zappi then this line should remain commented out. If you have multiple zappis then if required, change the entity name to the Zappi linked to IOG / load the Agile car charging plan. |

<h3>Pricing Parameters</h3>
These parameters set the price that PV Opt uses:

<h4>Octopus Tariffs (usinng the Octopus API)</h4>

| Parameter                  |   Units    | Entity                       | Default | Description                                                                                              |
| :------------------------- | :--------: | :--------------------------- | :-----: | :------------------------------------------------------------------------------------------------------- |
| Octopus Auto               | `on`/`off` | `octopus_auto`               |   On    | Read tariffs from the Octopus Energy integration. If successful this over-rides the following parameters |
| Octopus Account            |  `string`  | `octopus_account`            |         | Octopus Account ID (Axxxxxxxx) - not required if Octopus Auto is set                                     |
| Octopus API Key            |  `string`  | `octopus_api_key`            |         | Octopus API Key - not required if Octopus Auto is set                                                    |
| Octopus Import Tariff Code |  fraction  | `octopus_import_tariff_code` |         | Import Tariff Code (eg `E-1R-AGILE-23-12-06-G`)                                                          |
| Octopus Export Tariff Code |  fraction  | `octopus_export_tariff_code` |         | Export Tariff Code (eg `E-1R-AGILE-OUTGOING-19-05-13-G`)                                                 |

<h4>Manual Tariffs</h4>

Import and/or export tarifs can be set manually as follows. These can be combined with Octopus Account Codes (ie you could set Octopus Agile for input using `octopus_import_tariff_code` and a manual export). Manual tariffs <b>will not work</b> with either `Octopus Auto` or `Octopus Account`.

    manual_import_tariff: True
    manual_import_tariff_name: Test Import
    manual_import_tariff_tz: GB
    manual_import_tariff_standing: 43
    manual_import_tariff_unit:
      - period_start: "00:00"
        price: 4.2
      - period_start: "05:00"
        price: 9.7
      - period_start: "16:00"
        price: 77.0
      - period_start: "19:00"
        price: -2.0

    manual_export_tariff: True
    manual_export_tariff_name: Test Export
    manual_export_tariff_tz: GB
    manual_export_tariff_unit:
      - period_start: "01:00"
        price: 14.2
      - period_start: "03:00"
        price: 19.7
      - period_start: "16:00"
        price: 50.0
      - period_start: "14:00"
        price: 0.0

<h4>Axle Energy Information</h4>

| Parameter                  |   Units    | Entity                       | Default | Description                                                                                              |
| :------------------------- | :--------: | :--------------------------- | :-----: | :------------------------------------------------------------------------------------------------------- |
| Pv_opt control during Axle events   |  `True/False`  | `switch.pv_opt_axle_allow_pvopt_writes`      | True | Allow Pv_opt to write to inverter during Axle Energy events. Axle should control your inverter during an event but has been known to start late or not at all. Until Axle fix this it is recommended that Pv_opt should also control your inverter, which given the current export price will almost certainly schedule an export event and as such there will be no conflicts.                                                      |
| Axle Energy export price   |  pence  | `number.pvopt_axle_export_rate_p`   |  100p   | Price for Axle Energy Export events. Defaults to 100p which is the current price Axle offer for all events. Change it here if it changes.                                                           |


<h3>Tuning Parameters</h3>
These parameters will tweak how PV Opt runs:

| Parameter           | Units | Entity                                      | Default | Description                                                                                                                                                                                                                                            |
| :------------------ | :---: | :------------------------------------------ | :-----: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pass threshold      |   %   | `number.pvopt_pass_throshold_p`             |   4p    | The incremental cost saving that each iteration of the optimiser needs to show to be included. Reducing the threshold may marginally reduce the predicted cost but have more marginal charge windows.                                                  |
| Discharge threshold |   %   | `number.pvopt_discharge_throshold_p`        |   5p    | The incremental cost saving that each iteration of the discharge optimiser needs to show to be included. Reducing the threshold may marginally reduce the predicted cost but have more marginal discharge windows.                                     |
| Slot threshold      |   %   | `number.pvopt_slop_throshold_p`             |   1p    | The incremental cost saving that each 30 minute slot of the optimiser needs to show to be included. Reducing the threshold may marginally reduce the predicted cost but have more marginal charge/discharge windows.                                   |
| Power Resolution    |   W   | `number.pvopt_forced_power_group_tolerance` |   100   | The resolution at which forced charging / discharging is reported. Changing this will change the reporting of the charge plan but will not change the detail of it. It is however used in windowing logic and will be applied to inverter programming. |

<h3>Alternative Tariffs</h3>
PV Opt can also check what each day would have cost using any combination of Octopus tariffs. Run over time this can give you an idea of whether it would be worth switching. To  enable this simply add a block like this to `config.yaml`:

    id_daily_solar: sensor.{device_name}_power_generation_today
    alt_tariffs:
      - name: Agile_Fix
        octopus_import_tariff_code: E-1R-AGILE-23-12-06-G
        octopus_export_tariff_code: E-1R-OUTGOING-FIX-12M-19-05-13-G

      - name: Eco7_Fix
        octopus_import_tariff_code: E-2R-VAR-22-11-01-G
        octopus_export_tariff_code: E-1R-OUTGOING-FIX-12M-19-05-13-G

      - name: Flux
        octopus_import_tariff_code: E-1R-FLUX-IMPORT-23-02-14-G
        octopus_export_tariff_code: E-1R-FLUX-EXPORT-23-02-14-G

In this example three alternatives are tested. For each tariff pair the Base and Optimised net cost for yesterday are calculated and saved to an entity called `sensor.pvopt_opt_cost_name`. The state of this entity is the optimised cost and the base cost is saved as the `net_base` attribute.

<h2>Output</h2>

The app always produces: 
1) a Base forecast of future battery SOC and the associated grid flow based on the forecast solar performance, the expected consumption and prices with no forced charging or discharging from the grid.. The total cost for today and tomorrow is written to `sensor.pvopt_base_cost` and the associated SOC vs time is written to the attributes of this entity allowing it to be graphed using `apex-charts`.
2) An "Optimsised Charging" plan, written to `sensor.pvopt_opt_cost`. In addition to the parameters written to base_cost this will also include a list of charge windows.

The easiest way to control and visualise this is through the `dashboards/pvopt_dashboard.yaml` Lovelace yaml file included in this repo. 

![Alt text](image-1.png)

This dashboard uses a couple of template sensors and time which will need adding to `/homeassistant/configuration.yaml`:

```
template:
  - sensor:
    - name: "Solis Grid Export Power"
      unique_id: solis_grid_export_power
      unit_of_measurement: W
      device_class: power
      state_class: measurement
      state: >-
        {{max(states('sensor.solis_meter_active_power') | float(0),0)}}

    - name: "Solis Grid Import Power"
      unique_id: solis_grid_import_power
      unit_of_measurement: W
      device_class: power
      state_class: measurement
      state: >-
        {{max(-(states('sensor.solis_meter_active_power') | float(0)),0)}}

sensor:
  - platform: time_date
    display_options:
      - 'time'
      - 'date'
      - 'date_time'
      - 'date_time_utc'
      - 'date_time_iso'
```

If you're using any of the Solis Cloud integrations, you can start with the '.dashboards\pvopt_dashboard_soliscloud_v2.yaml'. Note that you will need to manually paste this into a dashboard and edit the charts to use the correct Octopus Energy sensors. 

For this dashboard you'll also need a couple of extra template sensors which will need adding to `/homeassistant/configuration.yaml`:

```
    - name: "Solis Battery Charge Power"
      unique_id: solis_battery_charge_power
      unit_of_measurement: W
      device_class: power
      state_class: measurement
      state: >-
        {{max(states('sensor.solis_battery_power_2') | float(0),0)}}    

    - name: "Solis Battery Discharge Power"
      unique_id: solis_battery_discharge_power
      unit_of_measurement: W
      device_class: power
      state_class: measurement
      state: >-
        {{max(-(states('sensor.solis_battery_power_2') | float(0)),0)}}
```


The dashboards also depend on the following Frontend components from HACS:

-   template-entity-row
-   bar-card
-   card-mod
-   Stack In Card
-   layout-card
-   apexcharts-card

<h2>EV Charging on the Agile Tariff</h2>

For Agile tariff users, Pv_opt also contains functionality to generate a charge plan for your EV. This is fully integrated with the Pv_opt core functionality of optimising house battery use, such that EV charge plans will not discharge your house battery.

An example Dashbaord for control and output for this is provided at https://github.com/stevebuk1/pv_opt/blob/main/dashboards/ev_agile_control.yaml.

![image](https://github.com/user-attachments/assets/cee304ec-b9e3-4c50-9c75-7ebe8b8d1c43)

If you are an existing user, it is also recommended you download config.yaml from https://github.com/stevebuk1/pv_opt/blob/main/apps/pv_opt/config/config.yaml and repopulate with your system configuration.

To enable the functionality, do the following, either in the dashboard directly or in config.yaml:

1. Enable Agile Car Charging to On (switch.pvopt_control_car_charging, or control_car_charging in config.yaml)
2. Set Charger to Zappi (select.pvopt_ev_charger, or ev_charger in config.yaml)
3. Set the car battery capacity (number.pvopt_ev_battery_capacity_kwh, or ev_battery_capacity_kwh in config.yaml))
4. Adjust the EV chargerpower (if required) (number.pvopt_ev_charger_power_watts, or ev_charger_power_watts in config.yaml))
5. Set the Maximum Slot Price to zero.

Pv_opt will then generate a candidate car charging plan on each optimiser run.

The candidate car charge plan calculated is based on the following settings:

-   Charge to add , i.e if your EV is at 40% and you want to get charge it to 90% then set to 50% (number.pvopt_ev_charge_target_percent)
-   Car Ready by time (select.pvopt_car_charging_ready_by)
-   Maximum slot price . If the slot price is above this limit then the car will not charge during this slot (number.pvopt_max_ev_price_p). Setting to zero disables this.

The candidate plan is automatically made the active plan on car plugin, but is not changed again. This is to ensure that if the charge to add value is calculated by an external automation based on the cars SOC, the charging plan stays the same once charging begins and the cars SOC increments.

If required, the candidate plan can also be transferred to the active plan via mamual Dashboard command. This is useful if the car is plugged in before 4pm once Agile rates become available or parameters above are adjusted after car plugin, which then means the active plan needs an update.

In the example dashboard, the candidate charging plan and active charging plan are both displayed as a list of 1/2 hour charging slots. The active plan is also displayed as a series of charging windows. Display of the candiate plan as charging windows is future work.

The main PV_opt dashboard will display the house battery charge plan with any necessary car charging information interlaced. If your car is scheduled to charge but the house battery isnt then a hold slot with power 1W and "<=Car" is scheduled to prevent house battery discharge when the car is charging:

![image](https://github.com/user-attachments/assets/caec438f-aeb5-452d-b8a4-5e20369280da)

The active car charging plan result is then output at the right time on binary_sensor.pvopt_car_charging_slot for use in HA automations to switch the EV charger on and off.

An example automation for a Zappi charger is available here: https://github.com/stevebuk1/pv_opt/blob/main/files/zappi_automation.yaml

Notes: at the current release, the Agile EV charger only schedules charging for a complete half hour slot. The ability to schedule partial slots to allow a more accurate car SOC to be obtained is future work.

<h2> Known Issues</h2>

<h3>Docker MariaDB Cache Size</h3>

If you are using MariaDB for your database in a standalone container (ie Docker or Proxmox) rather than the Home Assistnt Add-On you may find that AppDaemon struggles to pull in enough history with the default cache settings.

MariaDB defaults to an in memory cache of 10MB. increasing `innodb_buffer_pool_size` to will allow more history to be transferred. This setting does not appear to be available in the Add-On configuration.

Full details are here: https://github.com/stevebuk1/pv_opt/issues/270

<h2>Development - Adding Additional Inverters: the PV Opt API</h2>

PV Opt is designed to be <i>pluggable</i>. A simple API is used to control inverters. This is defined as follows:

<h3>Inverter Type</h3>

Each inverter type is defined by a string in the config.yaml file. This should be of the format: `BRAND_INTEGRATION` for example `SOLIS_SOLAX_MODBUS`.

<h3>Inverter Module</h3>

PV Opt expects one module per inverter brand named `brand.py` which includes drives for all integrations/models associated with that brand. For example `solis.py` includes the drivers for `SOLIS_SOLAX_MODBUS`, `SOLIS_CORE_MODBUS` and `SOLIS_SOLARMAN`

Each module exposes the following:

<h4>Classes</h4>

The module exposes a single class `InverterController(inverter_type, host)`. The two required initialisation parameters are:

| Parameter       |  Type   | Description                                                                                                                                                                                               |
| :-------------- | :-----: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inverter_type` |  `str`  | The `inverter_type` string from the `config.yaml` file                                                                                                                                                    |
| `host`          | `PVOpt` | The instance of `PV Opt` that has instantiated the inverter class. This allows the class to, for instance, write to the main log file simply be setting `self.log=host.log` and then calling `self.log()` |

<h4>Class Attributes</h4>

The `InverterController` class must expose the following:

| Attribute       |               Key               |     Type      | Description                                                                                                                                                                                                                                                                                                                                                                                        | Example from `SOLIS_SOLAX_MODBUS`                 |
| :-------------- | :-----------------------------: | :-----------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| `.config`       |                                 |    `dict`     | This dict contains all the names of all the entities that PV Opt requires to run plus a few other parameters that are common to all inverters. Some entries must be an `entity_id`: keys for these itesms start with `id_`. Others may be `enitity_id`s or numbers. `entity_id`s should ideally include `{device_name}` to allow for the subsititution of a defined device name where appropriate. |
|                 |      `maximum_dod_percent`      | `str` / `int` | Maximum depth of discharge - nay be an entity_id or a number                                                                                                                                                                                                                                                                                                                                       | `number.{device_name}_battery_minimum_soc`        |
|                 |     `update_cycle_seconds`      |     `int`     | Time in seconds between HA updates                                                                                                                                                                                                                                                                                                                                                                 | 15                                                |
|                 |       `supports_hold_soc`       |    `bool`     | Flags whether the integration supports holding a fixed SOC                                                                                                                                                                                                                                                                                                                                         | `true`                                            |
|                 |        `id_battery_soc`         |     `str`     | `entity_id` of Battery State of Charge                                                                                                                                                                                                                                                                                                                                                             | `number.{device_name}_battery_soc`                |
|                 |     `id_consumption_today`      |     `str`     | `entity_id` of Daily Consumption Total                                                                                                                                                                                                                                                                                                                                                             | `sensor.{device_name}_house_load_today`           |
|                 |     `id_grid_import_today`      |     `str`     | `entity_id` of Daily Grid Import Total                                                                                                                                                                                                                                                                                                                                                             | `sensor.{device_name}_grid_import_today`          |
|                 |     `id_grid_export_today`      |     `str`     | `entity_id` of Daily Grid Export Total                                                                                                                                                                                                                                                                                                                                                             | `sensor.{device_name}_grid_export_today`          |
| `.brand_config` |                                 |    `dict`     | This dict contains all the names of all the entities that this brand/integration requires. These are only exposed for logging purposes and to allow the plug-in to use methods from the main app that use query `entity_id`s such as `.get_config(entity_id)` . A limited number of examples are given as this will vary for each plug-in.                                                         |
|                 |        `battery_voltage`        | `str` / `int` | Battery voltage for converting power to current - nay be an entity_id or a number                                                                                                                                                                                                                                                                                                                  | `sensor.{device_name}_battery_voltage`            |
|                 |  `id_timed_charge_start_hours`  |     `str`     | `entity_id` of Timed Charge Start Hours                                                                                                                                                                                                                                                                                                                                                            | `number.{device_name}_timed_charge_start_hours`   |
|                 | `id_timed_charge_start_minutes` |     `str`     | `entity_id` of Timed Charge Start Minutes                                                                                                                                                                                                                                                                                                                                                          | `number.{device_name}_timed_charge_start_minutes` |
|                 |   `id_timed_charge_end_hours`   |     `str`     | `entity_id` of Timed Charge End Hours                                                                                                                                                                                                                                                                                                                                                              | `number.{device_name}_timed_charge_end_hours`     |
|                 |  `id_timed_charge_end_minutes`  |     `str`     | `entity_id` of Timed Charge End Minutes                                                                                                                                                                                                                                                                                                                                                            | `number.{device_name}_timed_charge_end_minutes`   |
|                 |    `id_timed_charge_current`    |     `str`     | `entity_id` of Timed Charge Current                                                                                                                                                                                                                                                                                                                                                                | `number.{device_name}_timed_charge_current`       |
| `.status`       |                                 |    `dict`     | This dict reports the current status of the inverter                                                                                                                                                                                                                                                                                                                                               |                                                   |
|                 |            `charge`             |    `dict`     | Dict of the Timed Charge Status with the following keys: `active: bool, start: datetime, end: datetime, power: float`                                                                                                                                                                                                                                                                              |
|                 |           `discharge`           |    `dict`     | Dict of the Timed Discharge Status with the following keys: `active: bool, start: datetime, end: datetime, power: float`                                                                                                                                                                                                                                                                           |
|                 |           `hold_soc`            |    `dict`     | Dict of the Hold_SOC Status with the following keys: `active: bool, soc: int`                                                                                                                                                                                                                                                                                                                      |

<h4>Methods</h4>

The `InverterController` class must expose the following:

| Method                 | Parameters                  | Returns | Description                                                          |
| :--------------------- | :-------------------------- | :-----: | :------------------------------------------------------------------- |
| `.enable_timed_mode()` | -                           | `None`  | Switches the inverter mode to support timed changing and discharging |
| `.control_charge()`    | `enable: bool`              | `None`  | Enable or disable timed charging                                     |
|                        | `start: datetime, optional` |         | Start time of timed slot (default = don't set start)                 |
|                        | `end: datetime, optional`   |         | End time of timed slot (default = don't set end)                     |
|                        | `power: float, optional`    |         | Maximum power of timed slot (default = don't set power)              |
| `.control_discharge()` | `enable: bool`              | `None`  | Enable or disable timed discharging                                  |
|                        | `start: datetime, optional` |         | Start time of timed slot (default = don't set start)                 |
|                        | `end: datetime, optional`   |         | End time of timed slot (default = don't set end)                     |
|                        | `power: float, optional`    |         | Maximum power of timed slot (default = don't set power)              |
| `.hold_soc()`          | `soc`                       | `None`  | Switch inverter mode to hold specified SOC (if supported)            |

<h4>PV Opt Methods Available to the Inverter</h4>

The following methods may be useful for the inverter to call. If `self.host` is initialised to `host` they can be called using `self.host.method()`. As PV Opt is a sub-class of `hass.HASS` it includes all the AppDAemon methods listed here: https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html

| Method                      | Parameters                   | Returns / Decsription                                                                                                                                 |
| :-------------------------- | :--------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `self.host.log`             | `string`                     | Write `string` to the log file.                                                                                                                       |
|                             | `level: str, optional`       | Optionally set the error level (default = `INFO`)                                                                                                     |
| `self.host.get_state()`     | `entity_id`                  | Home Assitant state of the entity                                                                                                                     |
|                             | `attributes: str, optional`  | If attributes is set the attribute rather than the state is returned. If attribute is set to all a `dict` of all attributes is returned.              |
| `self.host.set_state()`     | `state`                      | Set the Home Assitant state of the entity and optionally the attributes. Returns a `dict` of the new state                                            |
|                             | `entity_id: str`             |
|                             | `attributes: dict, optional` |
| `self.host.entity_exists()` | `entity_id: str`             | `bool` that confirms whether an entity exists in Home Assistant                                                                                       |
| `self.host.call_service()`  | `service: str`               | Call `service` in Home Assistant                                                                                                                      |
|                             | `data: dict, optional`       | Data to be supplied to the service e.g. for writing to the Solis Modbus registers: `data={"hub": "solis", "slave": 1, "address": 43011, "value": 15}` |

<h2>Credits</h2>

- Pv_opt was created and maintained by FBoundy as fboundy/pv_opt for many years before being transferred to its current owner in April 2026.
