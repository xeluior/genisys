from pathlib import Path
from typing_extensions import Self
import requests
from genisys.modules import base

class OSDownload(base.Module):
    """
    This module downloads the Netboot.xyz PXE file and potentially interacts with the Netboot UI to select an OS.
    
    Link to Netboot.xyz PXE file: https://boot.netboot.xyz/ipxe/netboot.xyz.kpxe
    """

    def __init__(self: Self, config) -> None:
        self.config = config
        self.config["network"] = config["Network"]

        self.NETBOOT_FILENAME = "netboot.xyz.kpxe"
        self.NETBOOT_PXE_LINK = "https://boot.netboot.xyz/ipxe/netboot.xyz.kpxe"
    # end __init__

    def download_file(self: Self) -> bytes:
        try:
            response = requests.get(self.NETBOOT_PXE_LINK, allow_redirects=True, timeout=15)
            response.raise_for_status()  # Check for request errors
            return response.content
        except requests.RequestException as e:
            print(f"Request failed: {e}")  # Handle request exceptions
            return b''  # Return an empty bytes object to indicate download failure
    # end download_file

    def write_file(self: Self, content: bytes, download_dir: Path):
        try:
            download_dir.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            with open(download_dir, "wb") as file:
                file.write(content)
        except (FileNotFoundError, PermissionError, IOError) as e:
            print(f"File writing error: {e}")  # Handle file writing exceptions
    # end write_file

    def install(self: Self, chroot: Path = ...):
        tftp_directory = self.config["network"]["tftp_directory"]
        content = self.download_file()

        if content:
            if chroot:
                download_dir = chroot / tftp_directory / self.NETBOOT_FILENAME
            else:
                download_dir = tftp_directory / self.NETBOOT_FILENAME

            self.write_file(content, download_dir)
    # end install

# end OSDownload
