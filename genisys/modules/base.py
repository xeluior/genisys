from pathlib import Path
from abc import ABCMeta, abstractmethod
from typing_extensions import Self, Union, List

class Module(metaclass=ABCMeta):
    """Base class all module should inherit from"""
    @abstractmethod
    def generate(self: Self) -> str:
        """Generates the content of the configuration file."""

        raise NotImplementedError
    #end generate

    @abstractmethod
    def install_location(self: Self) -> Path:
        """Returns the location that the config file should be installed to.
        This path should always be absolute. Relative paths will be assumed
        to be relative to the root directory.
        """

        raise NotImplementedError
    #end install_location

    def install(self: Self, chroot: Union[Path, str] = Path('/')):
        """Default implementation of the installation procedure. Without chroot
        this will likely require the application is ran as root.
        """

        install_file = Path(chroot, self.install_location())
        with open(install_file, 'w', encoding="utf-8") as fd:
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

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        """Returns commands which are should be ran before the module's configuration output is
        completed. Should return a List such that each item can be passed to the subprocess.run()
        function.
        """
        return []
    # end setup
#end class Module
