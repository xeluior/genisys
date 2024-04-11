import subprocess
from passlib.hash import pbkdf2_sha256
import yaml
from genisys.config_parser import YAMLParser

class MakePassword:
    """ Accepts command line argument to generate user password """
    def __init__(self, config: YAMLParser):
        self.config = {}
        self.config["users"] = config.get_section("Users")
    # end __init__
     
    def make_password(self, raw_password, filename):
        """ Encrypts user password in hashed format and ansible vault format """
        # use Passlib library to encrypt raw_ password, in /etc/shadow format in the "root-password" key under the "Users" section of the genisys config.
        secret_password = pbkdf2_sha256.hash(raw_password)

        # store updated configuration back into config file
        parser = YAMLParser(filename)
        config = parser.as_dict()
        config["Users"]["root-login"] = secret_password

        with open(filename, 'w', encoding='utf-8') as file:
            yaml.dump(config, file)

        # encrypt raw_password from stdin using ansible vault, stored as secret_password in file specified
        user_password = ""
        subprocess.run(["echo", "-n", raw_password, "ansible-vault", "encrypt_string", "--vault-password-file", filename, "--stdin-name", user_password], check=False)
    # end make_password
# end MakePassword
        
