from pathlib import Path
from typing_extensions import Self
import jinja2
from genisys.modules.base import Module
from genisys.config_parser import YAMLParser
from genisys.server import tls
import sys

FILENAME = "preseed.cfg"
class Preseed(Module):
    """Generates a Preseed file to be served over the network to a booting Debian system"""
    def __init__(self: Self, config: YAMLParser):
        self.config = {}
        self.config["network"] = config.get_section("Network")
        self.config["users"] = config.get_section("Users")
        self.config["apps"] = {
            k: str(v).lower() if isinstance(v, bool) else v 
            for k,v in config.get_section("Applications")
        }

    def install_location(self: Self) -> Path:
        """Places the Preseed file in the TFTP root"""
        ftp_dir = Path(self.config["network"]["tftp_directory"])
        return Path(ftp_dir, FILENAME)

    def generate(self: Self) -> str:
        """Renders the Jinja template with the prespecified configurations"""
        loader = jinja2.PackageLoader('genisys')
        jinja_env = jinja2.Environment(loader=loader)
        template = jinja_env.get_template("preseed.cfg.jinja2")


        # Read SSH key files and store their contents as strings
        ssh_keys_contents = []
        for ssh_key_path_str in self.config["users"].get("ssh-keys", []):
            ssh_key_path = Path(ssh_key_path_str)  # Directly use the provided absolute path
            try:
                with open(ssh_key_path, 'r') as f:
                    ssh_keys_contents.append(f.read())
            except FileNotFoundError:
                print(f"Warning: SSH key file {ssh_key_path} not found.")

        # Initialize SSL certificate content as None
        ssl_cert_content = None
        # Check if 'server' and 'ssl' keys are present in the configuration
        if 'server' in self.config["network"] and 'ssl' in self.config["network"]["server"]:
            # Determine SSL certificate path
            ssl_config = self.config["network"]["server"]["ssl"] or {}
            ssl_cert_path = Path(tls.get_keychain(ssl_config)["certfile"])
            # Read SSL certificate file and store its contents as a string
            with open(ssl_cert_path, 'r') as f:
                ssl_cert_content = f.read()

        # Pass settings, FTP configuration, SSH keys, and SSL certificate content to the template
        rendered_template = template.render(
            settings=self.config["users"],
            ftp=self.config["network"].get("ftp", {}),
            ssh_keys_contents=ssh_keys_contents,
            ssl_cert_content=ssl_cert_content
        )
        return rendered_template

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preseed.py <config_file>")
        sys.exit(1)

    config = YAMLParser(sys.argv[1])
    preseed = Preseed(config)
    print(preseed.generate())
