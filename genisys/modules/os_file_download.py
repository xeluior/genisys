from pathlib import Path
import tempfile
import tarfile
import os
from typing_extensions import Self
import requests
from genisys.modules import base

class OSDownload(base.Module):
    """
    This module handles the downloading of OS files necessary for PXE booting a client machine.
    - vmlinuz (Kernel) & initrd/initramfs (Initial Ram Disk)
    - pxelinux.cfg
    - pxelinux.0 or GRUB (Depends on OS/Version)
    Link to Debian files (amd64):
        https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/
    """

    def __init__(self: Self, config) -> None:
        self.config = {}
        self.config["network"] = config.get_section("Network")
        self.config["OS"] = config.get_section("OS")

        self.debian_tar_filename = "netboot.tar.gz"
        self.debian_tar_link = f"https://deb.debian.org/debian/dists/{self.config['OS']['version-name']}/main/installer-{self.config['OS']['target-architecture']}/current/images/netboot/netboot.tar.gz"
    # end __init__

    def install(self: Self, chroot: Path = Path('/')):
        tftp_directory = self.config["network"]["tftp_directory"]

        try:
            response = requests.get(self.debian_tar_link, allow_redirects=True, timeout=15)
            response.raise_for_status()  # Check for request errors

            tmp_directory = tempfile.gettempdir()
            download_dir = tmp_directory + os.sep + self.debian_tar_filename

            with open(download_dir, "wb") as file:
                file.write(response.content)

            target_directory = Path(chroot, tftp_directory) if chroot else Path(tftp_directory)

            tftp_directory = Path(tftp_directory)

            if tftp_directory.is_absolute():
                target_directory = Path(chroot, *tftp_directory.parts[1:])
            else:
                target_directory = Path(chroot, tftp_directory)

            with tarfile.open(download_dir, "r:gz") as tar:
                tar.extractall(target_directory)

            # Remove the downloaded .tar.gz file from /tmp
            os.remove(download_dir)

        except requests.RequestException as e:
            print(f"Request failed: {e}")  # Handle request exceptions
        except (OSError, tarfile.TarError) as e:
            print(f"Error: {e}")  # Handle file and extraction errors
    # end install

# end OSDownload
