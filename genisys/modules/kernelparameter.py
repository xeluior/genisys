from typing_extensions import Self, Union, List
from pathlib import Path
from genisys.modules import base

class KernelParameter(base.module):
    ''' 99 prefix guarantees that this rule will overwrite sysctl.conf parameter assignment, this file will need to be created beforehand '''
    SYSCTL_FILE = "/etc/sysctl.d/99-ip-forwarding-rule.conf" 

    def __init__(self: Self, config: dict):
        self.config = config

    # end __init__

    def install_location(self: Self):
        return Path(self.SYSCTL_FILE)

    # end install_location

    def generate(self: Self) -> str:
        return "net.ipv4.ip_forward=1"


    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return ["sysctl -p"]
    # end generate

    
