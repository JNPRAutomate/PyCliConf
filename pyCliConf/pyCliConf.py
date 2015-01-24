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
            print "RPC Session Error: %r \n\t Are you on Junos?\n" % err

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


    def load_config(self, cfg_string=False, url=False, cfg_format="text", action="merge"):
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
        try:
            cfg_string
            url
        except Exception as err:
            print "Error: load_config needs either 'cfg_string' or 'url' defined: %r" % err

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
            <load-configuration "%sformat="text">
                <configuration-text>
                    %s
                </configuration-text>
            </load-configuration>
        </rpc>
        ]]>]]>
        """ % (action_string, cfg_string)

        rpc_load_set_string = """
           <rpc> 
            <load-configuration "%sformat="text">
                <configuration-set>
                    %s
                </configuration-set>
            </load-configuration>
        </rpc>
        ]]>]]>
        """ % (action_string, cfg_string)

        rpc_load_string = """
           <rpc> 
            <load-configuration "%sformat="xml">
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
        elif cfg_form == "xml":
            rpc_send = rpc_load_string

        try:
            print rpc_send
            self.rpc(rpc_send)
        except Exception as err:
            print "RPC Load Error: %r" % err

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
        """
        try:
            new_template = Template(template)
        except Exception as err:
            print "Load_Template New Error: %r" % err

        try:
            final_template = new_template.render(template_vars)
            print final_template
        except Exception as err:
            print "Load_Template Render Error: %r" % err

        try:
            self.load_config(cfg_string=final_template, cfg_format=cfg_format,  action=action)
        except Exception as err:
            print "RPC Load_Template Send Error: %r" % err
