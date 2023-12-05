from pathlib import Path
from typing_extensions import Self, Union, List
from genisys.modules import base

class Dnsmasq(base.Module):
    """Creates the nessecary DNS, DHCP, and TFTP configurations to PXE boot clients"""
    DNS_DIR = '/etc'
    DNS_FILE = 'dnsmasq.conf'

    def __init__(self: Self, config):
        """Pulling DNSMasq config information from the Network header in the config yaml file"""
        self.config = {}
        self.config["network"] = config.get_section("Network")
        #Adding override config to read the last field in our config file
        self.config["overrides"] = config.get_section("DNSMasq Overrides")

    def install_location(self: Self) -> Path:
        """This is where the DNSMasq config file is stored/accessed"""
        return Path(self.DNS_DIR, self.DNS_FILE)

    def generate(self: Self) -> str:
        config_writer = ''

        # The below line deals with the port 53 resolved issue when running dnsmasq
        config_writer+="bind-interfaces\n"
        if 'interface' in self.config["network"]:
            config_writer+=("interface=" + self.config['network']['interface'] + "\n")
        if 'no-dhcp' in self.config["network"]:
            if not self.config['network']['no-dhcp']:
                if 'dhcp-ranges' in self.config['network'] \
                    and 'dhcp-lease' in self.config['network']:
                    config_writer+=(f'dhcp-boot={self.config["network"]["tftp_directory"]}/pxelinux.0\n')
                    config_writer+=(f'dhcp-range={self.config['network']['dhcp-ranges']},{self.config['network']['dhcp-lease']}\n')
        config_writer+="enable-tftp\n"
        if 'tftp_directory' in self.config['network']:
            config_writer+=("tftp-root=" + self.config['network']['tftp_directory'] + "\n")
        if 'dns-servers' in self.config['network']:
            config_writer+=("server=" + self.config['network']['dns-servers'] + "\n")
        #adding potential future logic for disabling only dns below
        # if 'no-dns' in self.config:
        #     We add the following string: DNSMASQ_EXCEPT=lo to the file /etc/default/dnsmasq
        if 'authoritative' in self.config['overrides']:
            if self.config['overrides']['authoritative']:
                config_writer+="dhcp-authoritative\n"
            else:
                config_writer+="#dhcp-authoritative\n"
        return config_writer

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return [["systemctl", "restart", "dnsmasq"]]
