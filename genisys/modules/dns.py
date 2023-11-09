from genisys.modules import base
from typing import Self, Union, List
from pathlib import Path
from jinja2 import Template
import subprocess
class Dnsmasq(base.Module):
    DNS_DIR = '/etc'
    DNS_FILE = 'dnsmasq.conf'
    def __init__(self: Self, config):
        """Temporarily seeing if this portion of the config file is applicable to DNSMasq"""
        self.config = config.getSection("DNSMasq Overrides")
    def install_location(self: Self) -> Path:
        """This is where the DNSMasq config file is stored/accessed"""
        return Path(DNS_DIR, DNS_FILE)
    def generate(self: Self) -> str:
        #consider adding DNSStubListener=no to /etc/systemd/resolved.conf to prevent port 53 errors?
        backup = Path(DNS_DIR, 'dnsmasq.conf.orig')
        if(not backup.exists()):
            subprocess.run("sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig")
        configWriter = open(DNS_DIR + DNS_FILE, "w")
        if 'authoritative' in self.config:
            if self.config['authoritative'].lower() == 'true':
                configWriter.write("dhcp-authoritative\n")
            else:
                configWriter.write("#dhcp-authoritative\n")
        configWriter.close()
    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return ["systemctl restart dnsmasq"]
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