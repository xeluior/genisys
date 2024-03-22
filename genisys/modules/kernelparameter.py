from pathlib import Path
from typing_extensions import Self, Union, List
from genisys.modules import base
from genisys.config_parser import YAMLParser

class KernelParameter(base.Module):
    '''99 prefix guarantees that this rule will overwrite sysctl.conf parameter assignment,
    this file will need to be created beforehand
    '''
    SYSCTL_FILE = "/etc/sysctl.d/99-ip-forwarding-rule.conf"

    def __init__(self: Self, config: YAMLParser):
        self.config = config
    # end __init__

    def install_location(self: Self):
        return Path(self.SYSCTL_FILE)
    # end install_location

    def generate(self: Self) -> str:
        return "net.ipv4.ip_forward=1"
    # end generate

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        return [["sysctl", "-p", self.SYSCTL_FILE]]
    # end generate
# end class KernelParameter
