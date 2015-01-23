"""An Junos on-box Python helper library to do very minimal bootstrapping of your Junos device. Primarily for Zero Touch Provisioning (ZTP) use cases.

.. moduleauthor:: Rob Cameron <rcameron@juniper.net>
"""
 from . import version

 __version__ = version.VERSION
 __date__ = version.DATE
 __all__ = ["pyCliConf"]
