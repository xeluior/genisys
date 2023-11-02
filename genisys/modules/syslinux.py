from typing_extensions import Self
from pathlib import Path
from genisys.modules.base import Module
from genisys.configParser import YAMLParser

CONFIG_DIR="pxelinux.cfg"
FILENAME="default"

class Syslinux(Module):
    """Generates the pxelinux.cfg files for the PXE version of SYSLINUX to boot from"""
    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["network"] = config.getSection("Network")
    # end __init__

    def install_location(self: Self) -> Path:
        return Path(self.config["network"]["tftp_directory"], CONFIG_DIR, FILENAME)
    # end install_location

    def generate(self: Self) -> str:
        return ""
    # end generate
# end class Syslinux
