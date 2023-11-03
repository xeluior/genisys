# FTP.py
from pathlib import Path
from typing_extensions import Self, Union, List
from .base import Module


class VsftpdModule(Module):
    def __init__(self, anonymous_enable: bool = True):
        self.anonymous_enable = anonymous_enable

    def generate(self: Self) -> str:
        """Generates the content of the vsftpd configuration file."""
        config_lines = [
            "listen=NO",
            f"anonymous_enable={'YES' if self.anonymous_enable else 'NO'}",
            "local_enable=YES",
            "write_enable=YES",
            "dirmessage_enable=YES",
            "use_localtime=YES",
            "xferlog_enable=YES",
            "connect_from_port_20=YES",
            "chroot_local_user=YES",
            "secure_chroot_dir=/var/run/vsftpd/empty",
            "pam_service_name=vsftpd",
            "rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem",
            "rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key",
            "ssl_enable=NO",
            "pasv_enable=Yes",
            "pasv_min_port=10000",
            "pasv_max_port=10100",
            "allow_writeable_chroot=YES",
            # ... more options as needed
        ]
        return "\n".join(config_lines)

    def install_location(self: Self) -> Path:
        """Returns the location that the vsftpd config file should be installed to."""
        return Path("/etc/vsftpd.conf")
