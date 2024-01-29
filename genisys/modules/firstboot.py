from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class FirstBoot(Module):
    """
    The FirstBoot class generates a shell script for the 
    client machines which sends a POST request to the 
    Genisys server containing the IP address of the client 
    machine for use in the Ansible inventory file. 
    """

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["scripts"] = config.get_section("Scripts")
        self.config["network"] = config.get_section("Network")
    #end __init__

    def generate(self: Self):
        content = []

        # Shell command to get IP address
        content.append("ipaddr=$(hostname -I)")

        # Command to send POST request to Genisys server (Subject to change)
        curl_command = "curl -X POST -d \"$(ipaddr)\" " + self.config["network"]["ip"]
        content.append(curl_command)

        return content
    #end generate

    def install_location(self: Self) -> Path:
        pass
    #end install_location

    def install(self: Self, chroot: Path = Path('/')):
        pass
    #end install
