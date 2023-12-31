from pathlib import Path
from typing_extensions import Self, Union, List
from jinja2 import Template
from textwrap3 import dedent
from genisys.modules import base
from genisys.config_parser import YAMLParser

class Nat(base.Module):
    """Manages the IPtables settings to allow the host system to perform NAT"""
    IPV4_DIR = "/etc/iptables/rules.v4"  # IPv4 Assumed default

    # Maybe think about adding a configuration option to enable/disable IPv6?
    IPV6_DIR = "/etc/iptables/rules.v6"

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["network"] = config.get_section("Network")
    # end __init__

    def generate(self: Self) -> str:
        # Set vars from config, error on config missing
        if "nat-interface" in self.config["network"]:
            nat_interface = self.config["network"]["nat-interface"]
        else:
            raise ValueError("Nat Interface value not found in config file.")

        if "subnet" in self.config["network"]:
            subnet = self.config["network"]["subnet"]
        else:
            raise ValueError("Subnet value not found in config file.")

        if "interface" in self.config["network"]:
            interface = self.config["network"]["interface"]
        else:
            raise ValueError("Interface value not found in config file.")

        # Error on nat interface and non-nat interface having the same value
        if nat_interface == interface:
            raise ValueError("The Nat Interface and Interface configs have the same value.")

        # Begin adding iptables rules
        template_text = """
        *nat
        :PREROUTING ACCEPT [0:0]
        :INPUT ACCEPT [0:0]
        :OUTPUT ACCEPT [0:0]
        :POSTROUTING ACCEPT [0:0]
        -A POSTROUTING -o {{ nat_interface_tmp }} -s {{ subnet_tmp }} -j MASQUERADE
        COMMIT

        *filter
        :INPUT ACCEPT [0:0]
        :FORWARD ACCEPT [0:0]
        :OUTPUT ACCEPT [0:0]
        -P FORWARD ACCEPT
        -A FORWARD -i {{ interface_tmp }} -o {{ nat_interface_tmp }} -j ACCEPT
        -A FORWARD -i {{ nat_interface_tmp }} -o {{ interface_tmp }} -m state --state RELATED,ESTABLISHED -j ACCEPT
        COMMIT
        """
        template = Template(dedent(template_text)) #remove indentation
        iptables_rules = template.render(
                nat_interface_tmp=nat_interface,
                interface_tmp=interface,
                subnet_tmp=subnet)
        # NOTE: "sudo netfilter-persistent save" and "sudo netfilter-persistent reload" will need
        # to be run to make these rules stick.
        return iptables_rules
    # end generate

    # May need to do a check in the future for IPv6 options, if they are included
    def install_location(self: Self) -> Path:
        return Path(self.IPV4_DIR)
    # end install_location

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return [
                ["iptables-restore", self.IPV4_DIR],
                ["netfilter-persistent", "reload"],
                ["systemctl", "enable", "iptables"],
                ["systemctl", "start", "iptables"]
                ]
    # end setup_commands
# end nat class
