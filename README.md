# PV Opt: Home Assistant Solar/Battery Optimiser 
App (AddOn) v1.0.0
using Pv_opt v5.0.0

<h2>Introduction</h2>

Solar / Battery Charging Optimisation App for Home Assistant. 

This App attempts to optimise charging and discharging of a home solar/battery system to minimise cost electricity cost on a daily basis using freely available solar forecast data from SolCast. This is particularly beneficial for Octopus Agile but is also benefeficial for other time-of-use tariffs such as Octopus Flux or simple Economy 7.

The application will integrate fully with Solis inverters which are controlled using any of:

-   [Home Assistant Solax Modbus Integration](https://github.com/wills106/homeassistant-solax-modbus)
-   [Home Assistant Core Modbus Integration](https://github.com/fboundy/ha_solis_modbus)
-   [SolisCloud via Home Assistant Solis Sensor Integration](https://github.com/hultenvp/solis-sensor) (1)
-   [Home Assistant Solarman Integration](https://github.com/davidrapan/ha-solarman)

(1) Control of inverter via this integration is Experimental/Beta. An alternative is to also install [Solis Control Integration](https://github.com/mkuthan/solis-cloud-control) for control aspects. 


Once installed it should require miminal configuration. Other inverters/integrations can be added if required or can be controlled indirectly using automations.

It has been tested primarily with Octopus tariffs but other tariffs can be manually implemented.

PV Opt supports EV charging:

-   If on Octopus Intelligent Go, PV Opt will incorporate any extra cheap slots in the house battery charge/discharge plan.
-   If on the Agile tariff, PV Opt can calculate a car charging plan which can be used to control your EV charger/car via external HA automation scripts.
-   If necessary Pv_opt automatically prevents house battery discharge during EV Charging.


