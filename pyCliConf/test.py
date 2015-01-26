from pyCliConf import CliConf

print "Testing Config: Set from Local File\n\n"
dev = CliConf()
dev.load_config(url = "/var/tmp/set.cfg", action = "set")
dev.commit()
dev.close()

print "Testing Config: Set from HTTP File\n\n"
dev = CliConf()
dev.load_config(url = "http://172.32.32.254/ztp-set.cfg", action = "set")
dev.commit()
dev.close()

print "Testing Config: Set from String\n\n"
dev = CliConf()
dev.load_config(cfg_string="set system host-name set-string", action = "set")
dev.commit()
dev.close()

print "\n\nTesting Config: Template String + Dict\n\n"
config_template = "system { host-name {{ hostname }}-{{ suffix }}; }"
config_vars = {"hostname": "foo", "suffix": "bah"}
dev = CliConf()
dev.load_config_template(config_template, config_vars)
dev.commit()
dev.close()

# This next case causes the switch to reboot, so only uncomment when ready to test this case.
# Initial tests by Kurt worked, but further testing and use cases needed
"""
print "\n\nTesting Package Install: Junos from HTTP\n\n"
dev = CliConf()
dev.install_package("http://172.32.32.254/jinstall-qfx-5-flex-14.1X53-D15.2-domestic-signed.tgz", reboot=True)
dev.close()
"""