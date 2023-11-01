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
from typing_extensions import Self

class OSDownload(base.Module):
    def __init__(self: Self, config) -> None:
        super().__init__()