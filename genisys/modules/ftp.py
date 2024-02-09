# ftp.py
from pathlib import Path
from typing import List
from genisys.modules.base import Module


class VsftpdModule(Module):
    """Represents a module for configuring and handling the vsftpd service."""

    def __init__(self, config):
        # Obtain the 'Network' section from the configuration
        network_config = config.get_section("Network")

        # Check and obtain the 'ftp' section from the 'Network' configuration
        if "ftp" not in network_config:
            raise KeyError("Missing 'ftp' section in 'Network' configuration")
        self.config = network_config["ftp"]

        # Check and retrieve the IP address for the FTP service to bind to
        if "ip" not in network_config:
            raise KeyError("Missing 'ip' key in 'Network' configuration")
        self.bind_addr = network_config["ip"]

        # Check for empty or missing listen_port, local_root, and listen_address
        if not self.config.get("ftp-port"):
            raise ValueError("Missing or empty 'ftp-port'")
        if not self.config.get("directory"):
            raise ValueError("Missing or empty 'directory'")
        if not self.bind_addr:
            raise ValueError("Missing or empty 'ip'")

    def generate(self) -> str:
        # Retrieve the directory path where the FTP service should root its file system
        directory = self.config.get("directory")
        # Retrieve the FTP service port from the configuration
        ftp_port = self.config.get("ftp-port")
        # Use the bind address obtained from the configuration
        bind_addr = self.bind_addr
        # Assemble the configuration lines for vsftpd.conf
        config_lines = [
            "anonymous_enable=YES",
            "listen=YES",
            "use_localtime=YES",
            "pasv_enable=YES",
            f"listen_port={ftp_port}",
            f"anon_root={directory}",
            f"listen_address={bind_addr}",
            "chmod 0644 /first-boot",
            "chown root /first-boot",
        ]
        # Joins all configuration lines into a single string separated by newline characters
        return "\n".join(config_lines) + "\n"

    def install_location(self) -> Path:
        """Returns the location where the vsftpd config file should be installed."""
        return Path("/etc/vsftpd.conf")

    def setup_commands(self) -> List[str]:
        """Returns a list of shell commands to set up the vsftpd service."""
        return [["systemctl", "restart", "vsftpd.service"]]
