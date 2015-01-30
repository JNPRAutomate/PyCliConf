# PyCliConf
An Junos on-box Python helper library to do very minimal bootstrapping of your Junos device. Primarily for Zero Touch Provisioning (ZTP) use cases. 

__NOTE:__ The load_config_template() function is only supported on 14.1X53 onwards.
Not supported on 13.2X51-D25 image from factory, so this method should
be deleted from switches booting this code, as well as the "from jinja2 import Template"