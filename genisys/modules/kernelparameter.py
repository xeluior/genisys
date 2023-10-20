from typing import Self
from pathlib import Path

from . import base
from typing import Self
from pathlib import Path

class KernelParameter(base.module):
    SYSCTL_FILE = "/etc/sysctl.conf"

    def __init__(self: Self, config: dict):
        self.config = config

    # end __init__

    def install_location(self: Self):
        return Path(self.SYSCTL_FILE)

    # end install_location

    def generate(self: Self) -> str:
        return "net.ipv4.ip_forward=1"

    # end generate

    # Checks if the line is uncommented or not in /etc/sysctl.conf and if not, uncomments it
    def add_parameter_to_existing_file(self: Self):
        # check for kernel parameter net.ipv4.ip_forward=1 in /etc/sysctl.conf
        target_line = "#net.ipv4.ip_forward=1"
        kernel_parameter_present = False

        try:
            with open("/etc/sysctl.conf", "r") as file:
                for line in file:
                    if line.strip() == target_line:
                        kernel_parameter_present = True
        except FileNotFoundError:
            print("/etc/sysctl.conf not found.")

        if not kernel_parameter_present:
            print(
                'Kernel parameter "net.ipv4.ip_forward=1" is not present in /etc/sysctl.conf'
            )

    # end addParameterToExistingFile
