from pathlib import Path
from typing_extensions import Self
from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Service(Module):
    """Installs the firstboot systemd service file to the ftp dir to be downloaded by clients"""
    SERVICE_NAME = "genisys-firstboot.service"

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["path"] = config.get_section("Network").get("ftp", {}).get("directory")

    def install_location(self: Self) -> Path:
        return Path(self.config["path"]) / "first-boot" / self.SERVICE_NAME

    def generate(self: Self):
        template_path = Path(__file__).parent.parent.parent / "templates" / self.SERVICE_NAME
        with template_path.open("r") as fd:
            return fd.read()
