'''
Notes for self: 
This module will handle the downloading of all of the OS files necessary for the PXE booting of a client machine. 

- vmlinuz (Kernel) & initrd/initramfs (Initial Ram Disk)
- pxelinux.cfg 
- pxelinux.0 or GRUB (Depends on OS/Version)

Link to Debian files (amd64): https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/ 
'''
from genisys.modules import base
from pathlib import Path
from typing_extensions import Self
import requests
import tarfile
import os

class OSDownload(base.Module):
    DEBIAN_TAR_FILE_LINK = "https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz" 
    DEBIAN_TAR_FILENAME = "netboot.tar.gz"

    def __init__(self: Self, config) -> None:
       self.config = config
       self.config["network"] = config["Network"]

    # end __init__

    def install(self: Self, chroot: Path = ...):
        tftp_directory = self.config["network"]["tftp_directory"]

        try:
            response = requests.get(self.DEBIAN_TAR_FILE_LINK, allow_redirects=True)
            response.raise_for_status()  # Check for request errors

            tmp_directory = Path("/tmp")
            download_dir = tmp_directory / self.DEBIAN_TAR_FILENAME

            with open(download_dir, "wb") as file:
                file.write(response.content)

            target_directory = Path(chroot, tftp_directory) if chroot else Path(tftp_directory)

            with tarfile.open(download_dir, "r:gz") as tar:
                tar.extractall(target_directory)

            # Remove the downloaded .tar.gz file from /tmp
            os.remove(download_dir)

        except requests.RequestException as e:
            print(f"Request failed: {e}")  # Handle request exceptions
        except (OSError, tarfile.TarError) as e:
            print(f"Error: {e}")  # Handle file and extraction errors
    #end install

# end OSDownload