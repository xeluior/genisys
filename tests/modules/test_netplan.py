import unittest
import tempfile
import yaml
from genisys.modules.netplan import Netplan
from genisys import config_parser

class NetplanTests(unittest.TestCase):
    """Run tests for the netplan module"""
    def test_netmask_eq_cidr(self):
        """Ensure that an expection is thrown when both CIDR and Netmask are specified but they
        disagree on the prefix length
        """
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n  subnet: 10.0.0.0/24\n  netmask: 255.255.254.0")
            config_file.seek(0)
            config = config_parser.YAMLParser(config_file.name)
            module = Netplan(config)
            with self.assertRaises(ValueError) as err:
                module.generate()
            self.assertEqual(
                    err.exception.args[0],
                    "Subnet mask does not match CIDR prefix length"
            )

    def test_ip_in_subnet(self):
        """Ensure that an exception is thrown when the IP is not in the specified subnet"""
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n  subnet: 10.0.0.0/24\n  ip: 192.168.0.1")
            config_file.seek(0)
            config = config_parser.YAMLParser(config_file.name)
            module = Netplan(config)
            with self.assertRaises(ValueError) as err:
                module.generate()
            self.assertEqual(err.exception.args[0], "IP is not in the given subnet")

    def test_expected_yaml(self):
        """Ensure the happy path works properly"""
        expected = yaml.dump({"network": {"ethernets": {"eth0": {"addresses": ["10.0.0.1/24"]}}}})
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n"
                              b"  interface: eth0\n"
                              b"  ip: 10.0.0.1\n"
                              b"  subnet: 10.0.0.0\n"
                              b"  netmask: 255.255.255.0")
            config_file.seek(0)
            config = config_parser.YAMLParser(config_file.name)
            module = Netplan(config)
            self.assertEqual(expected, module.generate())

if __name__ == "__main__":
    unittest.main()
