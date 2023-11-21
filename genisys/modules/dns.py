from genisys.modules import base
from typing import Self, Union, List
from pathlib import Path
from jinja2 import Template
import subprocess
class Dnsmasq(base.Module):
    DNS_DIR = '/etc'
    DNS_FILE = 'dnsmasq.conf'
    def __init__(self: Self, config):
        """Pulling DNSMasq config information from the Network header in the config yaml file"""
        self.config["network"] = config.getSection("Network")
        #Adding override config to read the last field in our config file
        self.config["overrides"] = config.getSection("DNSMasq Overrides")
    def install_location(self: Self) -> Path:
        """This is where the DNSMasq config file is stored/accessed"""
        return Path(DNS_DIR, DNS_FILE)
    def generate(self: Self) -> str:
        configWriter = ''
        #The below line deals with the port 53 resolved issue when running dnsmasq after installation
        configWriter+="bind-interfaces\n"
        if 'interface' in self.config["network"]:
            configWriter+=("interface=" + self.config['network']['interface'] + "\n")
        if 'no-dhcp' in self.config["network"]:
            if self.config['network']['no-dhcp'] == 'false':
                if 'dhcp-ranges' in self.config['network'] and 'dhcp-lease' in self.config['network']:
                    configWriter+=("dhcp-range=" + self.config['network']['dhcp-ranges'] + "," + self.config['network']['dhcp-lease'] + "\n")
        configWriter+="enable-tftp\n"
        if 'tftp_directory' in self.config['netowrk']:
            configWriter+=("tftp-root=" + self.config['network']['tftp_directory'] + "\n")
        if 'dns-servers' in self.config['network']:
            configWriter+=("server=" + self.config['network']['dns-servers'] + "\n")
        #adding potential future logic for disabling only dns below
        # if 'no-dns' in self.config:
        #     We add the following string: DNSMASQ_EXCEPT=lo to the file /etc/default/dnsmasq 
        if 'authoritative' in self.config['overrides']:
            if self.config['overrides']['authoritative'].lower() == 'true':
                configWriter+="dhcp-authoritative\n"
            else:
                configWriter+="#dhcp-authoritative\n"
        return configWriter
    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return [["systemctl", "restart", "dnsmasq"]]
    def validate(self: Self) -> bool:
        """Validates the configuration by attempting to generate the configuration file."""
        try:
            self.generate()
            #The following logic is supposed to use dnsmasq inbuitl validation dnsmasq --test which returns dnsmasq: syntax check OK. when valid
            #For some reason, this code cannot check the output of the command to verify that the config file passed the test
            #valid = subprocess.check_output(["sudo", "dnsmasq", "--test"], stdout=subprocess.PIPE)
            #validString = valid.stdout.decode('utf-8')
            #if validString
            return True
        except:
            return False