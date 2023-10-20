import unittest
import tempfile
import yaml
import crypt
try:
    import genisys.configParser
except ModuleNotFoundError:
    import importlib
    configParser = importlib.import_module("genisys.yaml-parser")
from genisys.modules.preseed import Preseed

def get_hash(password):
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    return crypt.crypt(password, salt)
# end get_hash

class PreseedTests(unittest.TestCase):
    def test_root_password(self):
        crypted_password = get_hash("password")
        expected_line = f"d-i passwd/root-password-crypted password {crypted_password}"
        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(bytes(yaml.dump({
                "Network": {
                    "tftp_directory": "/tftpboot"
                    },
                "Applications": [],
                "Users": {
                    "root-login": True,
                    "root-password": crypted_password
                    }
                }), 'utf-8'))
            config_file.seek(0)
            config = configParser.YAMLParser(config_file.name)
            module = Preseed(config)
            output = module.generate().split("\n")
            self.assertIn("d-i passwd/root-login boolean true", output)
            self.assertIn(expected_line, output)
    # end test_root_password

    def test_make_user(self):
        password = get_hash("password")
        username = "user"
        expected_lines = [
                "d-i passwd/make-user boolean true",
                f"d-i passwd/username string {username}",
                f"d-i passwd/user-password-crypted password {password}"
                ]
        with tempfile.NamedTemporaryFile() as fd:
            fd.write(bytes(yaml.dump({
                "Network": { "tftp_directory": "/tftpboot" },
                "Applications": [],
                "Users": {
                    "username": username,
                    "password": password
                    }
                }), 'utf-8'))
            fd.seek(0)
            config = configParser.YAMLParser(fd.name)
            module = Preseed(config)
            output = module.generate().split("\n")
            for line in expected_lines:
                self.assertIn(line, output)
    # end test_make_user

    def test_sudoer(self):
        expected_line = "d-i passwd/user-default-groups string cdrom floppy audio dip video plugdev users netdev lpadmin scanner sudo"
        username = "user"
        password = get_hash("password")
        with tempfile.NamedTemporaryFile() as fd:
            fd.write(bytes(yaml.dump({
                "Network": { "tftp_directory": "/tftpboot" },
                "Applications": [],
                "Users": {
                    "username": username,
                    "password": password,
                    "sudoer": True
                    }
                }), "utf-8"))
            fd.seek(0)
            config = configParser.YAMLParser(fd.name)
            module = Preseed(config)
            output = module.generate().split("\n")
            self.assertIn(expected_line, output)
        # end test_sudoer
# end class PreseedTests

if __name__ == "__main__":
    unittest.main()
    
