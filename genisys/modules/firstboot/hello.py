from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Hello(Module):
    """
    The Hello class generates a shell script for the 
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

        content.append("#!/bin/bash")

        #Shell Variables
        content.append("ip_addr=$(hostname -I)")
        content.append("hostname=$(hostname)")

        #Writing JSON content to file
        append_string = " >> ip.json"

        content.append("echo \"{\" > ip.json") #single > to overwrite
        content.append("echo \"    \"message\" : \"hello\",\"" + append_string)
        content.append("echo \"    \"ip\" : \"$(hostname -I)\",\"" + append_string)
        content.append("echo \"    \"hostname\" : \"$(hostname)\",\"" + append_string)
        # Additional JSON content can be added on this line
        content.append("echo \"}\"" + append_string)

        # Building target IP for curl request
        server_config = self.config["network"].get("server", {}) or {}
        prefix = "https://" if "ssl" in server_config else ""
        server_ip = self.config["network"]["ip"]
        server_port = self.config["network"]["server"]["port"]
        target_ip = prefix + server_ip + ":" + str(server_port)

        # Command to send POST request to Genisys server (Subject to change)
        curl_command = f"curl --json @ip.json {target_ip}"
        content.append(curl_command)

        # Turning array of strings into single block
        formatted_string = "\n".join(content)
        return formatted_string
    #end generate

    def install_location(self: Self) -> Path:
        return Path(self.config["network"]["ftp"]["directory"]) / "first-boot" / "entrypoint"
    #end install_location
#end Hello
