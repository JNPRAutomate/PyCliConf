import subprocess

from datetime import datetime

# Jijna2 is not supported until Junos 14.1X53, so catch exception on versions without this library.
try:
    from jinja2 import Template
    JINJA_SUPPORT = True
except:
    JINJA_SUPPORT = False

class CliConf():
    """
    CliConf

    This class is designed to be used for configuring a Junos device
    using only the libraries supported by the Junos Enhanced Automation
    images.

    Args:
        :Debug: Ensure log() method prints output to stdout and logfile. Defaults to False, and all log() output only goes to logfile.
        :logfile: Destination logfile for log() method. Defaults to "/var/root/ztp-log.txt" as this is a persistant writable location during ZTP.

    Examples:

    Basic device connection:

    .. code-block:: python

        from pyCliConf import CliConf

        dev = CliConf()
        dev.load_config(config_file = "/var/tmp/set.cfg", action = "set")
        dev.commit()
        dev.close()

    NOTE: When committing configuration with this script, please ensure that "chassis auto-image-upgrade" is in the configuration, otherwise "Auto Image Upgrade" process will exit and mark the script as a failure.
    """
    def __init__(self, logfile="/var/root/ztp-log.txt", Debug=False):
        self.session = " "
        self.logfile = open(logfile, "a", 0)
        self.debug = Debug

        try:
            self.session = subprocess.Popen(['/usr/sbin/cli', 'xml-mode', 'netconf'], stdin=subprocess.PIPE, stdout=self.logfile, stderr=self.logfile)
        except Exception as err:
            print "RPC Session Error: %r \n\t Are you on Junos?\n" % err

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
            errmsg = "RPC Close Error: %r" % err
            self.log(errmsg)
        try:
            self.logfile.close()
        except Exception as err:
            errmsg = "Error closing logfile: %r" % err
            self.log(errmsg)

    def commit(self):
        """
        Commit current candidate configuration

        NOTE: When committing configuration with this script, please ensure that "chassis auto-image-upgrade" is in the configuration, otherwise "Auto Image Upgrade" process will exit and mark the script as a failure.
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
            errmsg = "RPC Commit Error: %r" % err
            self.log(errmsg)

    def install_package(self, url, no_copy=True, no_validate=True, unlink = True, reboot=False):
        """
        Install Junos package onto the system.

        The primary use case is for performing Junos upgrades during the
        ZTP process, though any package should work.

        NOTE: "reboot" is set by default to "False", to ensure you do not
        surprise yourself.

        Args:
            :url: string containing Junos standard URL scheme:
                - File path (eg /var/tmp/config.cfg)
                - FTP (eg ftp://username:password@hostname/path/filename)
                - HTTP (eg http://username:password@hostname/path/filename)
            :no_copy: Defaults to True
            :no_validate: Defaults to True
            :unlink: Defaults to True
            :reboot: Defaults to False

        Example:

        .. code-block:: python
        from pyCliConf import CliConf

        dev = CliConf()
        dev.install_package("http://172.32.32.254/jinstall-X.Y.tgz", reboot=True)
        dev.close()
        """
        if no_copy:
            rpc_package_nocopy = "<no-copy/>"
        else:
            rpc_package_nocopy = ""
        if no_validate:
            rpc_package_novalidate = "<no-validate/>"
        else:
            rpc_package_novalidate = ""
        if unlink:
            rpc_package_unlink = "<unlink/>"
        else:
            rpc_package_unlink = ""
        if reboot:
            rpc_package_reboot = "<reboot/>"
        else:
            rpc_package_reboot = ""

        rpc_package = """
            <rpc>
               <request-package-add>
                <package-name>
                    %s
                </package-name>
                 %s
                 %s
                 %s
                 %s
               </request-package-add>
            </rpc>
            ]]>]]>
        """ % (url, rpc_package_nocopy, rpc_package_novalidate, rpc_package_unlink, rpc_package_reboot)

        rpc_send = rpc_package

        try:
            self.rpc(rpc_send)
        except Exception as err:
            errmsg = "Install Package Error: %r" % err
            self.log(errmsg)

    def load_config(self, cfg_string=False, url=False, cfg_format="text", action="merge"):
        """
        Loads Junos configuration from a URL or file location

        Args:
            :cfg_string: string containing valid Junos configuration syntax
            :url: string containing Junos standard URL scheme:
                - File path (eg /var/tmp/config.cfg)
                - FTP (eg ftp://username:password@hostname/path/filename)
                - HTTP (eg http://username:password@hostname/path/filename)
            :cfg_format: string containing format of config url or cfg_string
                - "text" (eg Junos { } format)
                - "xml" (eg XML structured format)
                - "set" (eg "set system host-name foo")
            :action: string telling Junos how to implement new configuration 
            in relation to existing configuration on the device.
                - 'set'
                - 'merge'
                - 'overide'
                - 'replace'
                - 'update'

        Examples:

           Load configuration from local file using "set" format:

            .. code-block:: python

                from pyCliConf import CliConf

                dev = CliConf()
                dev.load_config(config_file = "/var/tmp/set.cfg", action = "set")

        NOTE: When committing configuration with this script, please ensure that "chassis auto-image-upgrade" is in the configuration, otherwise "Auto Image Upgrade" process will exit and mark the script as a failure.
        """
        try:
            cfg_string
            url
        except Exception as err:
            errmsg = "Error: load_config needs either 'cfg_string' or 'url' defined: %r" % err
            self.log(errmsg)

        if action == "set" or cfg_format == "set":
            action_string = ' action = "set" '
            cfg_format = "text"
        elif action in  ['merge', 'overide', 'replace', 'update']:
            action_string = ' action = "%s" ' % action
        else:
            raise Exception("RPC Load Error - Unknown action type")

        rpc_load_url = """
        <rpc> 
            <load-configuration url="%s"%sformat="%s" />
        </rpc>
        ]]>]]>
        """ % (url, action_string, cfg_format)

        rpc_load_text_string = """
           <rpc> 
            <load-configuration%sformat="text">
                <configuration-text>
                    %s
                </configuration-text>
            </load-configuration>
        </rpc>
        ]]>]]>
        """ % (action_string, cfg_string)

        rpc_load_set_string = """
           <rpc> 
            <load-configuration%sformat="text">
                <configuration-set>
                    %s
                </configuration-set>
            </load-configuration>
        </rpc>
        ]]>]]>
        """ % (action_string, cfg_string)

        rpc_load_string = """
           <rpc> 
            <load-configuration%sformat="xml">
                <configuration>
                    %s
                </configuration>
            </load-configuration>
        </rpc>
        ]]>]]>
        """ % (action_string, cfg_string)

        if url:
            rpc_send = rpc_load_url
        elif action == "set" or cfg_format == "set":
            rpc_send = rpc_load_set_string
        elif cfg_format == "text":
            rpc_send = rpc_load_text_string
        elif cfg_format == "xml":
            rpc_send = rpc_load_string

        try:
            self.rpc(rpc_send)
        except Exception as err:
            errmsg = "RPC Load Error: %r" % err
            self.log(errmsg)

    def load_config_template(self, template, template_vars, cfg_format="text", action="merge"):
        """
        :template: A templated string using Jinja2 templates
        :template_vars: A dict containing the vars used in the :template: string
        :cfg_format: The type of configuration to load. The default is "text" or a standard Junos config block. Other options are: "set" for set style commands, "xml" for xml configs
        :action: Configurtion action. The default is "merge".

        Uses standard `Jinja2`_ Templating.

        .. _`Jinja2`: http://jinja.pocoo.org/

        Example:

        .. code-block:: python
            from pyCliConf import CliConf

            config_template = "system { host-name {{ hostname }}-{{ suffix }}; }"
            config_vars = {"hostname": "foo", "suffix": "bah"}

            dev = CliConf()
            dev.load_config_template(config_template, config_vars)
            dev.commit()
            dev.close()

        NOTE: When committing configuration with this script, please ensure that "chassis auto-image-upgrade" is in the configuration, otherwise "Auto Image Upgrade" process will exit and mark the script as a failure.
        """
        if JINJA_SUPPORT == True:
            try:
                new_template = Template(template)
            except Exception as err:
                errmsg = "Load_Template New Error: %r" % err
                self.log(errmsg)

            try:
                final_template = new_template.render(template_vars)
            except Exception as err:
                errmsg = "Load_Template Render Error: %r" % err
                self.log(errmsg)

            try:
                self.load_config(cfg_string=final_template, cfg_format=cfg_format,  action=action)
            except Exception as err:
                errmsg = "RPC Load_Template Send Error: %r" % err
                self.log(errmsg)
        else:
            self.log("Jinja2 Template supported on this software version. First support Junos 14.1X53")

    def log(self, msg):
        """
        Basic logging function for use by script.
        """
        logfile = self.logfile
        log_time = self.time()

        if self.debug == True:
            print(str(log_time) + ": " + str(msg) + "\n")

        try:
            logfile.write(str(log_time) + ": " + str(msg) + "\n")
        except Exception as err:
            print "Error logging to file: %r" % err

    def reboot(self):
        """
        Reboot the device.
        """
        rpc_reboot = """
        <rpc>
            <request-reboot>
            </request-reboot>
        </rpc>
        ]]>]]>
        """
        try:
            self.rpc(rpc_reboot)
        except Exception as err:
            errmsg = "RPC Reboot Error: %r" % err
            self.log(errmsg)

    def rpc(self, rpc):
        """
        Opens a NETCONF session via CLI session and sends RPC.

        Primarily used by other methods.

        Args:
            :rpc: string containing properly structured NETCONF RPC

        """

        try:
            log_string = "RPC Data Sent to host:\n %r" % rpc
            self.log(log_string)
            self.session.stdin.write(rpc)
        except Exception as err:
            errmsg = "RPC Communication Error: %r" % err
            self.log(errmsg)

    def time(self):
        """
        Basic Time Function for log function use.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
