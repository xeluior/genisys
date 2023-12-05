from pathlib import Path
from typing_extensions import Self
import jinja2
from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

FILENAME = "preseed.cfg"

class Preseed(Module):
    """Generates a Preseed file to be served over the network to a booting Debian system"""
    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["network"] = config.get_section("Network")
        self.config["users"] = config.get_section("Users")
        self.config["apps"] = config.get_section("Applications")
    # end __init__

    def install_location(self: Self) -> Path:
        """Places the Preseed file in the TFTP root"""
        ftp_dir = Path(self.config["network"]["tftp_directory"])
        return Path(ftp_dir, FILENAME)
    # end install_location

    def generate(self: Self) -> str:
        """Renders the Jinja template with the prespecified configurations"""
        loader = jinja2.PackageLoader('genisys')
        jinja_env = jinja2.Environment(loader=loader)
        template = jinja_env.get_template("preseed.cfg.jinja2")

        # convert booleans to lowercase to match preseed format
        for key, value in self.config["users"].items():
            if isinstance(value, bool):
                self.config["users"][key] = str(value).lower()

        return template.render(settings=self.config["users"])
    # end generate
# end class Preseed
