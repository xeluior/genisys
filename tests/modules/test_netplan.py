from genisys.modules.netplan import Netplan
import unittest
import genisys.configParser as configParser
import yaml
import tempfile

class NetplanTests(unittest.TestCase):
    def test_netmask_eq_cidr(self):
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n  subnet: 10.0.0.0/24\n  netmask: 255.255.254.0")
            config_file.seek(0)
            config = configParser.YAMLParser(config_file.name)
            module = Netplan(config)
            with self.assertRaises(ValueError) as err:
                module.generate()
            self.assertEqual(
                    err.exception.args[0],
                    "Subnet mask does not match CIDR prefix length"
            )

    def test_ip_in_subnet(self):
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n  subnet: 10.0.0.0/24\n  ip: 192.168.0.1")
            config_file.seek(0)
            config = configParser.YAMLParser(config_file.name)
            module = Netplan(config)
            with self.assertRaises(ValueError) as err:
                module.generate()
            self.assertEqual(err.exception.args[0], "IP is not in the given subnet")

    def test_expected_yaml(self):
        expected = yaml.dump({"network": {"ethernets": {"eth0": {"addresses": ["10.0.0.1/24"]}}}})
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(b"Network:\n"
                              b"  interface: eth0\n"
                              b"  ip: 10.0.0.1\n"
                              b"  subnet: 10.0.0.0\n"
                              b"  netmask: 255.255.255.0")
            config_file.seek(0)
            config = configParser.YAMLParser(config_file.name)
            module = Netplan(config)
            self.assertEqual(expected, module.generate())

if __name__ == "__main__":
    unittest.main()
    
