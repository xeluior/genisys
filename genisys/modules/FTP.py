# ftp.py
from pathlib import Path
from typing import List
from genisys.modules.base import Module


class VsftpdModule(Module):
    """Represents a module for configuring and handling the vsftpd service."""
    
    def __init__(self, config):
        # Obtain the 'ftp' section from the 'Network' configuration
        self.config = config.getSection("Network")["ftp"]
        # Obtain the entire 'Network' section from the configuration
        self.network = config.getSection("Network")
        # Retrieve the IP address for the FTP service to bind to
        self.bind_addr = self.network.get("ip")

    def generate(self) -> str:
        # Retrieve the directory path where the FTP service should root its file system
        directory = self.config["directory"]
        # Retrieve the FTP service port from the configuration
        ftp_port = self.config["ftp-port"]
        # Use the bind address obtained from the configuration
        bind_addr = self.bind_addr
        # Assemble the configuration lines for vsftpd.conf
        config_lines = [
            "anonymous_enable=YES",  # Allows anonymous users to access the FTP server
            "listen=YES",            # Instructs vsftpd to run in standalone mode
            "use_localtime=YES",     # Configures vsftpd to display timestamps according to the server's local timezone
            "pasv_enable=Yes",       # Enables passive mode - necessary for clients behind firewalls or NAT
            f"listen_port={ftp_port}",     # Sets the port for vsftpd to listen on
            f"local_root={directory}",     # Defines the root directory for FTP users
            f"listen_address={bind_addr}"  # Sets the specific IP address for vsftpd to bind to
        ]
        # Joins all configuration lines into a single string separated by newline characters
        return "\n".join(config_lines) + '\n'

    def install_location(self) -> Path:
        """Returns the location where the vsftpd config file should be installed."""
        # Provides the path to the configuration file where vsftpd expects to find it
        return Path("/etc/vsftpd.conf")

    def setup_commands(self) -> List[str]:
        """Returns a list of shell commands to set up the vsftpd service."""
        return ["systemctl restart vsftpd.service"]
