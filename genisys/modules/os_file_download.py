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
from requests import get
import tarfile

class OSDownload(base.Module):
    DEBIAN_TAR_FILE_LINK = "https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz" 
    DEBIAN_TAR_FILENAME = "netboot.tar.gz"

    def __init__(self: Self, config) -> None:
       self.config = config
       self.config["network"] = config["Network"]

    # end __init__

    def install(self: Self, chroot: Path = ...):
        if chroot:
            directory = Path(chroot, self.config["network"]["tftp_directory"])
        else:
            directory = Path(self.config["network"]["tftp_directory"])
        
        res = get(self.DEBIAN_TAR_FILE_LINK, allow_redirects=True) # Look into allow_redirects
        download_dir = Path(directory, self.DEBIAN_TAR_FILENAME)

        with open(download_dir, "wb") as file:
            file.write(res.content)

        with tarfile.open(download_dir, "r:gz") as tar:
            tar.extractall(directory)
    
    #end install

# end OSDownload