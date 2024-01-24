import os
import shutil
from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Script(Module):
    """
    The Script class is responsible for moving user-defined scripts
    from the specified directory to the FTP directory for client machines.
    """

    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["scripts"] = config.get_section("Scripts")
        self.config["network"] = config.get_section("Network")
    #end __init__

    def generate(self: Self):
        pass
    #end generate

    def install_location(self: Self) -> Path:
        pass
    #end install_location

    def install(self: Self, chroot: Path = Path('/')):
        """ 
        Method that moves either all scripts in the scripts directory
        defined in the configuration file, or only moves the specified scripts 
        if the move-all option is set to false into the correct FTP directory. 
        """
        #Location of scripts in genisys directory
        script_source_dir = self.config["scripts"]["script-dir"]
        source = Path(chroot, script_source_dir)

        #Location of FTP directory on genisys host
        ftp_dir = self.config["network"]["ftp"]["directory"]

        #Creating file structure for scripts folder
        #Creating first_boot_path dir
        first_boot_path = Path(chroot, ftp_dir, "/first-boot")

        # exist_ok prevents errors if directory already exists
        # parents=true ensures that all parent directories exist as well 
        first_boot_path.parent.mkdir(exist_ok=True, parents=True)

        #Creating /first-boot/scripts dir
        scripts_path = Path(first_boot_path, "/scripts")

        scripts_path.parent.mkdir(exist_ok=True, parents=True)

        if self.config["scripts"]["move-all"]:
            # If the user wants to move all scripts into the scripts dir
            for file in os.listdir(source):
                shutil.copy((source / file), scripts_path)
        else:
            # If the user wants only specified scripts moved
            scripts_to_move = self.config["scripts"]["script-list"]
            for file in os.listdir(source):
                if file in scripts_to_move:
                    shutil.copy((source / file), scripts_path)
    # end install
