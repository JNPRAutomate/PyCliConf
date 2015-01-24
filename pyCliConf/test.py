from pyCliConf import CliConf

print "Testing Config: Set from Local File\n\n"
dev = CliConf()
dev.load_config(url = "/var/tmp/set.cfg", action = "set")
dev.commit()
dev.close()

print "\n\nTesting Config: Template String + Dict\n\n"
config_template = "system { host-name {{ hostname }}-{{ suffix }}; }"
config_vars = {"hostname": "foo", "suffix": "bah"}
dev = CliConf()
dev.load_config_template(config_template, config_vars)
dev.commit()
dev.close()
