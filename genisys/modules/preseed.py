from pathlib import Path
from typing_extensions import Self
import jinja2
from genisys.modules.base import Module
from genisys.config_parser import YAMLParser
import sys
FILENAME = "preseed.cfg"

class Preseed(Module):
    """Generates a Preseed file to be served over the network to a booting Debian system"""
    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["network"] = config.get_section("Network")
        self.config["users"] = config.get_section("Users")
        self.config["apps"] = config.get_section("Applications")

    def install_location(self: Self) -> Path:
        """Places the Preseed file in the TFTP root"""
        ftp_dir = Path(self.config["network"]["tftp_directory"])
        return Path(ftp_dir, FILENAME)

    def generate(self: Self) -> str:
        """Renders the Jinja template with the prespecified configurations"""
        loader = jinja2.PackageLoader('genisys')
        jinja_env = jinja2.Environment(loader=loader)
        template = jinja_env.get_template("preseed.cfg.jinja2")

        # convert booleans to lowercase to match preseed format
        for key, value in self.config["users"].items():
            if isinstance(value, bool):
                self.config["users"][key] = str(value).lower()

        # Read SSH key files and store their contents as strings
        ssh_keys_contents = []
        ssh_keys_dir = Path("../ssh_keys")  # Update this to your directory path
        for ssh_key_file in self.config["users"].get("ssh-keys", []):
            ssh_key_path = ssh_keys_dir / ssh_key_file
            with open(ssh_key_path, 'r') as f:
                ssh_keys_contents.append(f.read())

        # New code to read SSL certificate
        ssl_cert_path = Path("../ssl/cert.pem")  # Update this to your SSL certificate path
        ssl_cert_content = ""
        if ssl_cert_path.exists():
            with open(ssl_cert_path, 'r') as f:
                ssl_cert_content = f.read()

        # Pass SSL certificate content along with other settings to the template
        rendered_template = template.render(settings=self.config["users"], ssh_keys_contents=ssh_keys_contents, ssl_cert_content=ssl_cert_content)
        return rendered_template

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preseed.py <config_file>")
        sys.exit(1)

    config = YAMLParser(sys.argv[1])
    preseed = Preseed(config)
    print(preseed.generate())
