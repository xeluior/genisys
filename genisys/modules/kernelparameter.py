from typing import Self
from pathlib import Path

from . import base
from typing import Self
from pathlib import Path

class KernelParameter(base.module):
    SYSCTL_FILE = "/etc/sysctl.d/99-ip-forwarding-rule.conf" # 99 prefix guarantees that this rule will overwrite sysctl.conf parameter assignment 

    def __init__(self: Self, config: dict):
        self.config = config

    # end __init__

    def install_location(self: Self):
        return Path(self.SYSCTL_FILE)

    # end install_location

    def generate(self: Self) -> str:
        return "net.ipv4.ip_forward=1"

    # end generate

    
