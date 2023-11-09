import ipaddress
from pathlib import Path
import yaml

from typing_extensions import Self, Union, List
from genisys.modules.base import Module

NETPLAN_DIR = '/etc/netplan'
NETPLAN_FILE = '99-genisys.yaml'
IPV4_BITS = 32

class Netplan(Module):
    """Generates a Ubuntu netplan for the internal interface"""

    def __init__(self: Self, config):
        """Stores only the nessecary portions of the config"""
        self.config = config.getSection("Network")
    # end __init__

    def install_location(self: Self) -> Path:
        """Returns a file in the netplan directory where the configuration will be stored"""
        return Path(NETPLAN_DIR, NETPLAN_FILE)
    # end install_location

    def generate(self: Self) -> str:
        """Output the netplan yaml and throw exceptions for inconsistent configuration"""
        # validate netmask and subnet config options agree
        # parse the netmask option to prefix length
        if 'netmask' in self.config:
            netmask = self.config['netmask']
            prefix_len = ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen
        else:
            prefix_len = None

        # parse the subnet option if it uses CIDR notation
        cidr_start = self.config['subnet'].find('/')
        if cidr_start != -1:
            cidr_pfx_len = int(self.config['subnet'][cidr_start+1:])
            if prefix_len is not None and prefix_len != cidr_pfx_len:
                raise ValueError("Subnet mask does not match CIDR prefix length")
            subnet_cidr = self.config['subnet']
        else: # subnet is not already in cidr
            # set a default prefix length
            if not prefix_len:
                prefix_len = IPV4_BITS
            subnet_cidr = f'{self.config["subnet"]}/{prefix_len}'

        # validate the ip is in the subnet
        subnet = ipaddress.ip_network(subnet_cidr)
        if ipaddress.IPv4Address(self.config['ip']) not in subnet:
            raise ValueError("IP is not in the given subnet")

        # construct the netplan
        ip = f'{self.config["ip"]}/{prefix_len}'
        netplan = {
            'network': {
                'ethernets': {
                    self.config['interface']: {
                        'addresses': [ ip ]
                    }
                }
            }
        }

        # return the yaml
        return yaml.dump(netplan)
    # end generate

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return [ "netplan apply" ]
    # end setup_commands
# end class Interface
