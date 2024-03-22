import unittest
from genisys.modules.firstboot.hello import Hello
from genisys import config_parser

class HelloModuleTest(unittest.TestCase):
    """Tests for the Hello module"""
    def test_ssl_config_values_present(self):
        """Test that the ssl option is correctly detected"""
        expected_output_list = [
            'hostname="$(curl --json @ip.json https://genisys.internal:15206 | jq -r \'.hostname\')"',
        ]

        with open("tests/configs/hello_test_1.yml", encoding='utf-8') as config_file:
            config = config_parser.YAMLParser(config_file.name)
            module = Hello(config)

            output = module.generate().split("\n")
            for line in expected_output_list:
                self.assertIn(line, output)

    def test_ssl_config_values_not_present(self):
        """Test that the ssl option is correctly detected, opposite of test 1"""
        expected_output_list = [
            'hostname="$(curl --json @ip.json http://genisys.internal:15206 | jq -r \'.hostname\')"',
        ]

        with open("tests/configs/hello_test_2.yml", encoding='utf-8') as config_file:
            config = config_parser.YAMLParser(config_file.name)
            module = Hello(config)

            output = module.generate().split("\n")
            for line in expected_output_list:
                self.assertIn(line, output)
