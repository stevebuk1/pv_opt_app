# PV Opt App: Home Assistant Solar/Battery Optimiser 
App (AddOn) v1.0.0, utilising Pv_opt v5.0.1. 

<h2>Introduction</h2>

Solar / Battery Charging Optimisation App for Home Assistant. 

This App (previously known as an AddOn) can be used with Home Assistant to run Pv_opt without using AppDaemon.

Pv_opt itself is unchanged from the AppDaemon version and so will behave identically. 

<h2>Upgrade Instructions</h2>

If you are currently running PV_opt under AppDaemon, follow this section, otherwise go to Installation Instuctions. 

<h2>Installation Instructions</h2>

Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.
Go to settings, apps, install app, custom repositories
Add '[https://github.com/stevebuk1/pv_opt_app)](https://github.com/stevebuk1/pv_opt_app)' as a new repository image

Click out of the repository list and refresh the page
Scroll down and find Pv_opt, click on it and click 'Install'

Navigate to /addon_configs/xxxxxxxxxxxx directory in Home Assistant file editor or via a Samba/SSH mount

Edit/replace config.yaml with a correct completed one.

Click restart on the app if need be (it might start automatically anyway)

Please note the xxxxxxx.log will be in this addon_configs directory also.

Remember: Do not run this at the same time as Pv_opt within AppDaemon (stop that first and remember to only have one on auto-start)




