import json
from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Hello(Module):
    """
    The FirstBoot class generates a shell script for the 
    client machines which sends a POST request to the 
    Genisys server containing the IP address and hostname 
    of the client machine for use in the Ansible inventory file. 
    """
    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["scripts"] = config.get_section("Scripts")
        self.config["network"] = config.get_section("Network")
    #end __init__

    def generate(self: Self):
        content = []
        json_body = {
            'message' : 'hello', 
            'ip' : '$(hostname -I)',
            'hostname' : '$(hostname)'
        }
        # Not sure of json.dumps() is necessary, will need testing
        json_object = json.dumps(json_body)

        content.append("#!/bin/bash")

        # Command to send POST request to Genisys server (Subject to change)
        curl_command = "curl -X POST -H \"Content-Type: application/json\" -d" + "\"" + json_object + "\"" + self.config["network"]["ip"]
        content.append(curl_command)

        return content
    #end generate

    def install_location(self: Self) -> Path:
        return "/first-boot/"
    #end install_location

    def install(self: Self, chroot: Path = Path('/')):
        pass
    #end install
