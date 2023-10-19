from typing import Self
from pathlib import Path

from . import base
from typing import Self
from pathlib import Path

"""
Their Genisys repo did it by setting the iptables rules then using netfilter-persistent to save the configuration. 
Basically we want to skip the "running iptables commands" step and just generate the iptables rules files into the right directory.
I believe there is also a kernel parameter that needs set to forward instead of dropping requests. 
That may technically need to be a seperate module the way our architecture is, but it should be simple enough to fit under this task
My VM put the iptables rules into the /etc/iptables/rule.v4 file if that helps

This configuration will be for the pxe server (Ubuntu) 

https://github.com/mieweb/GeniSys
"""


class nat(base.Module):
    IPV4_DIR = "/etc/iptables/rules.v4"  # IPv4 Assumed default
    IPV6_DIR = "/etc/iptables/rules.v6"  # Maybe think about adding a configuration option to enable/disable IPv6?
    SYSCTL_FILE = "/etc/sysctl.conf"

    def __init__(self: Self, config: dict):
        self.config = config

    # end __init__

    def generate(self: Self) -> str:
        # verify that config options exist
        if "nat-interface" in self.config:
            nat_interface = self.config["nat-interface"]

        # check for kernel parameter net.ipv4.ip_forward=1 in /etc/sysctl.conf
        target_line = "#net.ipv4.ip_forward=1"
        kernel_parameter_present = False

        try:
            with open("/etc/sysctl.conf", "r") as file:
                for line in file:
                    if line.strip() == target_line:
                        kernel_parameter_present = True
        except FileNotFoundError:
            print("/etc/sysctl.conf not found.")

        if not kernel_parameter_present:
            print("Kernel parameter \"net.ipv4.ip_forward=1\" is not present")
        return super().generate()

    # end generate

    # May need to do a check in the future for IPv6 options, if they are included
    def install_location(self: Self) -> Path: 
        return Path("/etc/iptables/rules.v4")  

    # end install_location

    def install(self: Self, chroot: Path = ...):
        # Set vars from config
        if "nat-interface" in self.config:
            nat_interface = self.config["nat-interface"]
        if "subnet" in self.config:
            subnet = self.config['subnet']
        if "interface" in self.config:
            interface = self.config['interface']
        
        # Check if kernel parameter net.ipv4.ip_forward=1 is enabled, if not, enable it
        target_line = "#net.ipv4.ip_forward=1"
        updated_lines = []

        try:
            with open(self.SYSCTL_FILE, "r") as file:
                for line in file:
                    if line.strip() == target_line:
                        # Remove the first '#' character
                        updated_line = line.lstrip("#")
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)

            # Save the updated file
            with open("/etc/sysctl.conf", "w") as file:
                file.writelines(updated_lines)

        except FileNotFoundError:
            print("/etc/sysctl.conf not found.")

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

        with open(self.install_location(), 'w') as f: # TODO Make sure the install_location is set up correctly
            f.write(iptables_rules)

    # end install

# end nat class