# PyCliConf
An Junos on-box Python helper library to do very minimal bootstrapping of your Junos device. Primarily for Zero Touch Provisioning (ZTP) use cases. 

The "examples" directory includes a ZTP script that has been tested on 13.2X51 and 14.1X53.

"test.py" includes testing utilities to be run when testing directly on QFX switch.

NOTE: When committing configuration with this script, please ensure that "chassis auto-image-upgrade" is in the configuration, otherwise "Auto Image Upgrade" process will exit and mark the script as a failure.