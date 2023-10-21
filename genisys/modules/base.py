from typing_extensions import Self
from pathlib import Path

class Module:
    def generate(self: Self) -> str:
        """Generates the content of the configuration file."""

        raise NotImplementedError
    #end generate
    
    def install_location(self: Self) -> Path:
        """Returns the location that the config file should be installed to.
        This path should always be absolute. Relative paths will be assumed
        to be relative to the root directory.
        """

        raise NotImplementedError
    #end install_location

    def install(self: Self, chroot: Path = Path('/')):
        """Default implementation of the installation procedure. Without chroot
        this will likely require the application is ran as root.
        """
        
        install_file = Path(chroot, self.install_location())
        with open(install_file, 'w') as fd:
            fd.write(self.generate())
        #end with
    #end install

    def validate(self: Self) -> bool:
        """Validates the configuration by attempting to generate the configuration file."""

        try:
            self.generate()
            return True
        except:
            return False
    #end validate
#end class Module
