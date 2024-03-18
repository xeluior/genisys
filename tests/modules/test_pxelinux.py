import unittest
import tempfile
import yaml
from typing_extensions import Self
from genisys.modules.syslinux import Syslinux
from genisys.config_parser import YAMLParser

class SyslinuxTest(unittest.TestCase):
    """Test the syslinux module"""
    def test_kernel_paramenters(self: Self):
        """Ensure the kernel options passed match the config"""
        expected = '    append initrd=debian-installer/amd64/initrd.gz ip=dhcp auto=enable language=en country=US locale=en_US.UTF-8 keymap=ansi hostname=debian domain="" url=tftp://10.0.0.1/preseed.cfg VGA=788'
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(
                    bytes(yaml.dump({"Network": {"ip": "10.0.0.1", "ftp_port": 20}}), 'utf-8'))
            config_file.seek(0)
            config = YAMLParser(config_file.name)
            module = Syslinux(config)
            output = module.generate().split("\n")
            self.assertIn(expected, output)
