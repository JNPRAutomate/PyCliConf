import subprocess
from jinja2 import Template

class CliConf():
    """
    CliConf

    This class is designed to be used for configuring a Junos device
    using only the libraries supported by the Junos Enhanced Automation
    images.

    Args:
        None (yet)

    Examples:

    Basic device connection:

    .. code-block:: python

        from pyCliConf import CliConf

        dev = CliConf()
        dev.load_config(config_file = "/var/tmp/set.cfg", action = "set")
        dev.commit()
        dev.close()
    """
    def __init__(self):
        self.session = " "

    def rpc(self, rpc):
        """
        Opens a NETCONF session via CLI session and sends RPC.

        Primarily used by other methods.

        Args:
            :rpc: string containing properly structured NETCONF RPC

        """
        try:
            self.session = subprocess.Popen(['/usr/sbin/cli', 'xml-mode', 'netconf'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except Exception as err:
            print "RPC Session Error: %r" % err

        try:
            self.session.communicate(rpc)
        except Exception as err:
            print "RPC Communication Error: %r" % err

    def close(self):
        """
        Close a NETCONF session.
        """
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
        """
        Commit current candidate configuration
        """
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
        """
        Loads Junos configuration from a URL or file location

        Args:
            :config_file: string containing Junos standard URL scheme:
                - File path (eg /var/tmp/config.cfg)
                - FTP (eg ftp://username:password@hostname/path/filename)
                - HTTP (eg http://username:password@hostname/path/filename)

        Examples:

           Load configuration from local file using "set" format:

            .. code-block:: python

                from pyCliConf import CliConf

                dev = CliConf()
                dev.load_config(config_file = "/var/tmp/set.cfg", action = "set")

        """
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
