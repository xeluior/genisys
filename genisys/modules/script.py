import os
import shutil
from pathlib import Path
from typing_extensions import Self

from genisys.modules.base import Module
from genisys.config_parser import YAMLParser

class Script(Module):
    """
    The Script class is responsible for moving any user defined scripts
    from the scripts directory specified by the configuration file into
    the FTP directory where they can be accessed by the client machines.
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
        source = Path(chroot, script_source_dir) if chroot else Path(script_source_dir)

        #Location of FTP directory on genisys host
        ftp_dir = self.config["network"]["ftp"]["directory"]

        #Creating file structure for scripts folder
        #Creating first_boot_path dir
        first_boot_path = Path(chroot, ftp_dir, "/first-boot") if chroot else Path(ftp_dir, "/first-boot")
        try:
            os.mkdir(first_boot_path)
        except FileExistsError:
            pass #Do nothing if already exists

        #Creating /first-boot/scripts dir
        scripts_path = Path(first_boot_path, "/scripts")
        try:
            os.mkdir(scripts_path)
        except FileExistsError:
            pass #Do nothing if already exists

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

# def main():
#     script = Script(YAMLParser('C:/Users/greeht01/Desktop/genisys/documentation/example.yml'))
#     script.move_files()

# if __name__ == '__main__':
#     main()