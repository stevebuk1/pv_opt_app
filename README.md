# PV Opt App: Home Assistant Solar/Battery Optimiser 
App (AddOn) v1.0.0, utilising Pv_opt v5.1.2-Beta-4. 

<h2>Introduction</h2>

Solar / Battery Charging Optimisation App for Home Assistant. 

This App (previously known as an AddOn) can be used with Home Assistant to run Pv_opt without using AppDaemon.

Pv_opt itself is unchanged from the AppDaemon version and so will behave identically. 

<h2>Upgrading from PV_opt running under AppDaemon</h2>

If you are currently running PV_opt under AppDaemon, follow this section, otherwise go to Installation Instuctions below . 

* Stop Appdaemon (or remove Pv_opt from AppDaemon if you have other AppDeamon apps still running)
* Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
* Go to settings, apps, install app
* Click the 3 vertical dots at top right and select "Repositories". 
* Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository
* When prompted, add the MQTT username and password that was originally created when installing Mosquito
* Click restart on the app if need be (it might start automatically anyway)


Please note 
* The installer will copy across your config.yaml from the AppDaemon area, this will now live at /config/pv_opt/config.yaml
* pv_opt.log will be in addon_configs/pv_opt/pv_opt.log

Remember: Do not run the Pv_opt App at the same time as Pv_opt within AppDaemon. 

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

Both of these add-ons make it easier to edit text files on your HA Install but aren't strictly necessary. `Samba Share` also makes it easier to access the AppDaemon log files.

<h3>9. Install the PV_opt App (formerly known as an AddOn)</h3>

* Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
* Go to settings, apps, install app
* Click the 3 vertical dots at top right and select "Repositories". 
* Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository
* When prompted, add the MQTT username and password from Step4 above. 
* Click restart on the app if need be (it might start automatically anyway)

Please note 
* config.yaml will be om /config/pv_opt/config.yaml
* pv_opt.log will be in /addon_configs/pv_opt/pv_opt.log
