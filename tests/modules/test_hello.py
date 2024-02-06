import unittest
from pathlib import Path
from genisys.modules.firstboot.hello import Hello
from genisys import config_parser

class HelloModuleTest(unittest.TestCase):
    """Tests for the Hello module"""
    def test_ssl_config_values_present(self):
        """Test that the ssl option is correctly detected"""
        with open("tests/configs/hello_test_1.yml", encoding='utf-8') as config_file:
            config = config_parser.YAMLParser(config_file.name)
            module = Hello(config)

            output = module.generate()
            print(output)
            