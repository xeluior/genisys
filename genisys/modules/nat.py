from typing import Self
from pathlib import Path

from genisys.modules import base
from typing import Self
from pathlib import Path

""" Notes for myself: 
Their Genisys repo did it by setting the iptables rules then using netfilter-persistent to save the configuration. 
Basically we want to skip the "running iptables commands" step and just generate the iptables rules files into the right directory.
I believe there is also a kernel parameter that needs set to forward instead of dropping requests. 
That may technically need to be a seperate module the way our architecture is, but it should be simple enough to fit under this task
My VM put the iptables rules into the /etc/iptables/rule.v4 file if that helps

This configuration will be for the pxe server (Ubuntu) 

https://github.com/mieweb/GeniSys
"""


class Nat(base.Module):
    IPV4_DIR = "/etc/iptables/rules.v4"  # IPv4 Assumed default
    IPV6_DIR = "/etc/iptables/rules.v6"  # Maybe think about adding a configuration option to enable/disable IPv6?

    def __init__(self: Self, config):
        self.config = {}
        self.config["network"] = config.getSection("Network")

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

        # Begin adding iptables rules TODO: Double check with Robert that these variables are being put in the correct rules.
        iptables_rules = f"""*nat
        :PREROUTING ACCEPT [0:0]
        :INPUT ACCEPT [0:0]
        :OUTPUT ACCEPT [0:0]
        :POSTROUTING ACCEPT [0:0]
        -A POSTROUTING -o {nat_interface} -s {subnet} -j MASQUERADE
        COMMIT
        
        *filter
        :INPUT ACCEPT [0:0]
        :FORWARD ACCEPT [0:0]
        :OUTPUT ACCEPT [0:0]
        -P FORWARD ACCEPT
        -A FORWARD -i {interface} -o {nat_interface} -j ACCEPT
        -A FORWARD -i {nat_interface} -o {interface} -m state --state RELATED,ESTABLISHED -j ACCEPT
        COMMIT
        """
        # NOTE: "sudo netfilter-persistent save" and "sudo netfilter-persistent reload" will need to be run to make these rules stick. 
        return iptables_rules

    # end generate

    # May need to do a check in the future for IPv6 options, if they are included
    def install_location(self: Self) -> Path:
        return Path(self.IPV4_DIR)

    # end install_location

# end nat class
