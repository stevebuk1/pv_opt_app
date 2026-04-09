# PV Opt App: Home Assistant Solar/Battery Optimiser 
App (AddOn) v1.0.0, utilising Pv_opt v5.0.1. 

<h2>Introduction</h2>

Solar / Battery Charging Optimisation App for Home Assistant. 

This App (previously known as an AddOn) can be used with Home Assistant to run Pv_opt without using AppDaemon.

Pv_opt itself is unchanged from the AppDaemon version and so will behave identically. 

<h2>Upgrading from PV_opt running under AppDaemon</h2>

If you are currently running PV_opt under AppDaemon, follow this section, otherwise go to Installation Instuctions below . 

* Make a copy of your config.yaml in /HomeAssistant/AppDaemon/apps/config.config.yaml
* Stop Appdaemon (or remove Pv_opt from AppDaemon if you have other AppDeamon apps still running)
* Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
* Go to settings, apps, install app
* Click the 3 vertical dots at top right and select "Repositories". 
* Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository
* Take your preivously copied config.yaml and put it at /addon_configs/xxxxxxxxxxxx. 
* Click restart on the app if need be (it might start automatically anyway)


Please note the xxxxxxx.log will be in this addon_configs directory also.

Remember: Do not run the Pv_opt App at the same time as Pv_opt within AppDaemon. 

<h2>Installation Instructions</h2>

Follow these instructions if you are installing Pv_opt for the very first time. 

Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
Go to settings, apps, install app, custom repositories
Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository image

Click out of the repository list and refresh the page
Scroll down and find Pv_opt, click on it and click 'Install'

Navigate to /addon_configs/xxxxxxxxxxxx directory in Home Assistant file editor or via a Samba/SSH mount

Edit/replace config.yaml with a correct completed one.

Click restart on the app if need be (it might start automatically anyway)

Please note the xxxxxxx.log will be in this addon_configs directory also.

