import subprocess
from jinja2 import Template

class CliConf():
    def __init__(self):
        self.session = " "

    def rpc(self, rpc):
        try:
            self.session = subprocess.Popen(['/usr/sbin/cli', 'xml-mode', 'netconf'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except Exception as err:
            print "RPC Session Error: %r" % err

        try:
            self.session.communicate(rpc)
        except Exception as err:
            print "RPC Communication Error: %r" % err

    def close(self):
        rpc_close = """
        <rpc>
            <close-session/>
        </rpc>
        ]]>]]>
        """
        try:
            self.rpc(rpc_close)
        except Exception as err:
            print "RPC Close Error: %r" % err

    def commit(self):
        rpc_commit = """
        <rpc>
            <commit/>
        </rpc>
        ]]>]]>
        """
        try:
            self.rpc(rpc_commit)
        except Exception as err:
            print "RPC Commit Error: %r" % err


    def load_config(self, config_file, action=" ", cfg_format="text"):
        if action == "set":
            action = ' action = "set" '
            cfg_format = "text"

        rpc_load_url = """
        <rpc> 
            <load-configuration url="%s"%sformat="%s" />
        </rpc>
        ]]>]]>
        """ % (config_file, action, cfg_format)

        try:
            self.rpc(rpc_load_url)
        except Exception as err:
            print "RPC Load Error: %r" % err



dev = CliConf()
dev.load_config(config_file = "/var/tmp/set.cfg", action = "set")
dev.commit()
dev.close()
