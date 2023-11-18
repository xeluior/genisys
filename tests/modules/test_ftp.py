import unittest
from genisys.modules.ftp import VsftpdModule
from genisys import configParser
from pathlib import Path

class VsftpdModuleTest(unittest.TestCase):
    """Tests for the VsftpdModule"""

    def test_ftp_config_generation(self):
        """Test correct generation of FTP configuration"""
        with open("tests/configs/ftp_test_1.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = VsftpdModule(config)
            output = module.generate()
            self.assertIn("anonymous_enable=YES", output)
            self.assertIn("listen=YES", output)
            # Add checks for other configuration lines as necessary

    def test_missing_config_option(self):
        """Ensure that a missing config option raises the expected error"""
        with open("tests/configs/ftp_test_2.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = VsftpdModule(config)
            with self.assertRaises(KeyError):
                output = module.generate()

    def test_install_location(self):
        """Test if the install location is correct"""
        with open("tests/configs/ftp_test_1.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = VsftpdModule(config)
            self.assertEqual(module.install_location(), Path("/etc/vsftpd.conf"))

    def test_setup_commands(self):
        """Test if the setup commands are correct"""
        with open("tests/configs/ftp_test_1.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            module = VsftpdModule(config)
            self.assertIn("systemctl restart vsftpd.service", module.setup_commands())

if __name__ == "__main__":
    unittest.main()
