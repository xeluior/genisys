# test_ftp.py
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
            self.assertIn("use_localtime=YES", output)
            self.assertIn("pasv_enable=YES", output)
            self.assertIn("listen_port=", output)
            self.assertIn("local_root=", output)
            self.assertIn("listen_address=", output)

    def test_missing_config_option(self):
        """Ensure that a missing config option raises the expected error"""
        with open("tests/configs/ftp_test_2.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            with self.assertRaises(KeyError):
                module = VsftpdModule(config)

    def test_missing_directive(self):
        """Test if error is raised when listen_port, local_root, or listen_address is missing"""
        # Testing missing ftp_port
        with open("tests/configs/ftp_test_3.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            with self.assertRaises(ValueError):
                module = VsftpdModule(config)

        # Testing missing directory
        with open("tests/configs/ftp_test_4.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            with self.assertRaises(ValueError):
                module = VsftpdModule(config)

        # Testing missing ip
        with open("tests/configs/ftp_test_5.yml") as config_file:
            config = configParser.YAMLParser(config_file.name)
            with self.assertRaises(ValueError):
                module = VsftpdModule(config)

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
            self.assertEqual(
                module.setup_commands(), ["systemctl restart vsftpd.service"]
            )


if __name__ == "__main__":
    unittest.main()
