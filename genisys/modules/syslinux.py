from pathlib import Path

import jinja2
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.configParser import YAMLParser
from genisys.modules import preseed

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
        jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("genisys"))
        template = jinja_env.get_template("pxelinux.cfg.j2")

        initrd = "debian-installer/amd64/initrd.gz"
        kernel = "debian-installer/amd64/linux"
        return template.render(network=self.config["network"],
                               initrd=initrd,
                               kernel=kernel,
                               preseed_filename=preseed.FILENAME)
    # end generate
# end class Syslinux
