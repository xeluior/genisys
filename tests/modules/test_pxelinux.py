import unittest
import tempfile
import yaml
from typing_extensions import Self
from genisys.modules.syslinux import Syslinux
from genisys.configParser import YAMLParser

class SyslinuxTest(unittest.TestCase):
    """Test the syslinux module"""
    def test_kernel_paramenters(self: Self):
        """Ensure the kernel options passed match the config"""
        expected = "    append initrd=debian-installer/initrd.gz ip=dhcp auto url=ftp://10.0.0.1:20/preseed.cfg"
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(
                    bytes(yaml.dump({"Network": {"ip": "10.0.0.1", "ftp_port": 20}}), 'utf-8'))
            config_file.seek(0)
            config = YAMLParser(config_file.name)
            module = Syslinux(config)
            output = module.generate().split("\n")
            self.assertIn(expected, output)
