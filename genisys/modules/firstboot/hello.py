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

        # set the shebang, bash for extra features over posix
        content.append("#!/bin/bash")

        # ensure some programs are installed
        # this should be taken care of by the preseed, but just in case
        content.append("apt update && apt install iproute2 gawk coreutils curl jq")

        # thanks chat gpt for this command
        content.append('ip_addr="$(ip -o -4 show scope global | awk \'{print $4}\' | cut -d/ -f1 | head -n1)')

        # use jq to avoid trying to wrangle quotes (theres still some wrangling)
        content.append('jq --null-input --arg ip "${ip_addr}" \'{message: "hello", ip: $ip}\' > ip.json')

        # Building target IP for curl request
        server_config = self.config["network"].get("server") or {}
        prefix = "https://" if "ssl" in server_config else "http://"
        server_ip = self.config["network"]["ip"]
        server_port = self.config["network"]["server"]["port"]
        target_ip = prefix + server_ip + ":" + str(server_port)

        # Command to send POST request to Genisys server (Subject to change)
        content.append(f"hostname=\"$(curl --json @ip.json {target_ip} | jq -r '.hostname')\"")

        # set the machine's hostname with the response iff the response included one
        content.append('[ "$hostname" != "null" ] && hostnamectl set-hostname "$hostname"')

        # Turning array of strings into single block
        formatted_string = "\n".join(content)
        return formatted_string
    #end generate

    def install_location(self: Self) -> Path:
        return Path(self.config["network"]["ftp"]["directory"]) / "first-boot" / "entrypoint"
    #end install_location
#end Hello
