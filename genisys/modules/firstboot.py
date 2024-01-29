from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class FirstBoot(Module):
    """
    The FirstBoot class generates a shell script that will be 
    sent to the client which will send a POST request to the 
    Genisys server containing the IP address of the client 
    machine for use in the Ansible inventory file. 
    """

    def __init__(self: Self, config: YAMLParser):
        pass
    #end __init__

    def generate(self: Self):
        pass
    #end generate

    def install_location(self: Self) -> Path:
        pass
    #end install_location
