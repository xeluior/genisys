'''
This module will handle the downloading of all of the files necessary for the PXE booting of a client machine. 

NOTES:
Downloading and storing all of the various files needed for boot:
syslinux.pxe / whatever
post-boot ISO/debian.whatever files
Need to download and install these files to the correct directories
Look into netboot.xyz

- vmlinuz (Kernel) & initrd/initramfs (Initial Ram Disk)
- pxelinux.cfg 
- pxelinux.0 or GRUB (Depends on OS/Version)

Link to Debian files (amd64): https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/ 
'''
from genisys.modules import base
from pathlib import Path
from typing_extensions import Self, Union, List

class OSDownload(base.Module):
    DEBIAN_TAR_FILE_LINK = "https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz" 

    def __init__(self: Self, config) -> None:
       self.config = config

    def setup_commands(self: Self) -> Union[List[str], List[List[str]]]:
        # Downloading and unpacking Debian netboot files
        download_command = f"curl \"{self.DEBIAN_TAR_FILE_LINK}\" -o netboot.tar.gz"
        unpack_command = "tar -xzvf netboot.tar.gz"
        remove_tar_file_command = "rm netboot.tar.gz" # Remove tar file once completed unpacking
        
        # TODO: Moving files to the correct locations

        return [download_command, unpack_command, remove_tar_file_command]