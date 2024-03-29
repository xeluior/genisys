import grp
import os
from pathlib import Path
import pwd
from typing_extensions import Optional, Self
from warnings import warn
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
        self.config["users"] = {
            k: str(v).lower() if isinstance(v, bool) else v 
            for k,v in config.get_section("Users").items()
        }
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

        # Pass settings, FTP configuration, SSH keys, and SSL certificate content to the template
        rendered_template = template.render(
            settings=self.config["users"],
            late_command=self.late_command()
        )
        return rendered_template


    # private:

    def ftp_uri(self: Self) -> str:
        """Construct the ftp uri for wget"""
        proto = 'ftp://'
        host = self.config['network']['ip']
        port = self.config['network'].get('ftp', {}).get('ftp-port', 21)
        path = 'first-boot'
        return f'{proto}{host}:{port}/{path}'

    def ssh_keys_contents(self: Self) -> str:
        """Read SSH key files and store their contents as strings"""
        ssh_keys_contents = []
        for ssh_key_path in self.config["users"].get("ssh-keys", []):
            try:
                with open(ssh_key_path, 'r') as f:
                    ssh_keys_contents.append(f.read())
            except FileNotFoundError:
                warn(f"SSH key file {ssh_key_path} not found.")
        return "\\n".join(ssh_keys_contents)

    def ssl_cert_content(self: Self) -> Optional[str]:
        """Get the SSL public cert key"""
        # Initialize SSL certificate content as None
        ssl_cert_content = None
        # Check if 'server' and 'ssl' keys are present in the configuration
        if 'server' in self.config["network"] and 'ssl' in self.config["network"]["server"]:
            # Determine SSL certificate path
            ssl_certs_path = tls.get_keychain(self.config["network"]["server"]["ssl"])
            # ensure ownership by the server user
            server = self.config['network']['server']
            user = server.get('user')
            group = server.get('group')
            uid = pwd.getpwnam(user) if user else pwd.getpwuid(os.geteuid())
            gid = grp.getgrnam(group) if group else grp.getgrgid(os.getgid())
            for _, path in ssl_certs_path.items():
                if path is None: continue
                os.chown(str(path), uid.pw_uid, gid.gr_gid)
            # Read SSL certificate file and store its contents as a string
            with open(ssl_certs_path['certfile'], 'r') as f:
                ssl_cert_content = f.read()
        return ssl_cert_content

    def late_command(self: Self) -> str:
        """Generates the late_command for the preseed file"""
        command = ""
        ssh_keys = self.ssh_keys_contents()
        ssl_cert = self.ssl_cert_content()
        ftp = self.ftp_uri()

        if ssh_keys != "":
            command += f'mkdir -p /root/.ssh && echo "{ssh_keys}" >> /root/.ssh/authorized_keys && chown -R root:root /root/.ssh/ && chmod 644 /root/.ssh/authorized_keys && chmod 700 /root/.ssh/;'
        if ssl_cert:
            command += f'echo "{ssl_cert}" > /usr/local/share/ca-certificates/genisys.crt && update-ca-certificates;'
        command += f'wget -nH -m {ftp} -P / && chown -R root:root /first-boot && chmod -R 0755 /first-boot && mv /first-boot/genisys-firstboot.service /etc/systemd/system/ && ln -s /etc/systemd/system/genisys-firstboot.service /etc/systemd/system/multi-user.target.wants/genisys-firstboot.service;'
        return command.replace('\n', '\\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preseed.py <config_file>")
        sys.exit(1)

    config = YAMLParser(sys.argv[1])
    preseed = Preseed(config)
    print(preseed.generate())
