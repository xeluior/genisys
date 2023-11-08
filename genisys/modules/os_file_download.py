from pathlib import Path
from typing_extensions import Self
import requests
from genisys.modules import base

class OSDownload(base.Module):
    """
    This module downloads the Netboot.xyz PXE file, and (maybe? might be automated buy a different module) 
    automates interacting with the Netboot UI to select an os. 
    
    Link to Netboot.xyz pxe file: https://boot.netboot.xyz/ipxe/netboot.xyz.kpxe
    """

    def __init__(self: Self, config) -> None:
        self.config = config
        self.config["network"] = config["Network"]

        self.NETBOOT_FILENAME = "netboot.xyz.kpxe"
        self.NETBOOT_PXE_LINK = "https://boot.netboot.xyz/ipxe/netboot.xyz.kpxe"
    # end __init__

    def install(self: Self, chroot: Path = ...):
        tftp_directory = self.config["network"]["tftp_directory"]

        try:
            response = requests.get(self.NETBOOT_PXE_LINK, allow_redirects=True, timeout=15)
            response.raise_for_status()  # Check for request errors

            if chroot:
                download_dir = chroot / tftp_directory / self.NETBOOT_FILENAME
            else:
                download_dir = tftp_directory / self.NETBOOT_FILENAME


            try:
                with open(download_dir, "wb") as file:
                    file.write(response.content)
                    
            except (FileNotFoundError, PermissionError, IOError) as e:
                print(f"File writing error: {e}")  # Handle file writing exceptions

        except requests.RequestException as e:
            print(f"Request failed: {e}")  # Handle request exceptions
    # end install 

# end OSDownload
