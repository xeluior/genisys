from pathlib import Path
from os import rename, mkdir
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

    def install_location(self: Self) -> Path:
        pass

    def install(self: Self, chroot: Path = Path('/')):
        """ Method that moves either all scripts in the scripts directory
          defined in the configuration file, or only moves the specified scrips 
          if the move-all option is set to false, into the correct FTP directory. 
        """
        #Location of scripts in genisys directory
        script_source_dir = self.config["scripts"]["script-dir"]
        source = Path(chroot, script_source_dir) if chroot else Path(script_source_dir)

        #Location of FTP directory on genisys host
        ftp_dir = self.config["network"]["ftp"]["directory"]
        destination = Path(chroot, ftp_dir) if chroot else Path(ftp_dir)

        #Creating file structure for scripts folder
        #Creating first_boot_path dir
        first_boot_path = Path(chroot, ftp_dir, "/first-boot") if chroot else Path(ftp_dir, "/first-boot")
        try:
            mkdir(first_boot_path)
        except FileExistsError:
            pass #Do nothing if already exists
 
        #Creating /first-boot/scripts dir
        scripts_path = Path(first_boot_path, "/scripts")
        try:
            mkdir(scripts_path)
        except FileExistsError:
            pass #Do nothing if already exists

        #TODO: actually move the files now that directories have been confirmed to exist
        rename(source, destination)

# def main():
#     script = Script(YAMLParser('C:/Users/greeht01/Desktop/genisys/documentation/example.yml'))
#     script.move_files()

# if __name__ == '__main__':
#     main()
