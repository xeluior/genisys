#!/usr/bin/env python3

import argparse
import subprocess
from genisys.modules.netplan import Netplan
from genisys.modules.preseed import Preseed
from genisys.modules.nat import Nat
from genisys.modules.kernelparameter import KernelParameter
from genisys.modules.dns import Dnsmasq
from genisys.modules.ftp import VsftpdModule
from genisys.modules.os_file_download import OSDownload
from genisys.modules.syslinux import Syslinux
from genisys.modules.script import Script
from genisys.modules.firstboot.hello import Hello
from genisys.modules.firstboot.service import Service
import genisys.config_parser as cp
import genisys.server
from genisys.make_password import MakePassword

MODULES = [
    OSDownload,
    Netplan,
    Preseed,
    Nat,
    KernelParameter,
    Dnsmasq,
    VsftpdModule,
    Syslinux,
    Hello, 
    Service,
    Script
]

def validate(file):
    """Display validation errors to the user."""
    for module in MODULES:
        mod = module(file)
        if not mod.validate():
            print(f"Error in {module.__class__.__name__} configuration!")
        else:
            print(f"{module.__class__.__name__} configuration is valid!")


def install_config(file, root="/"):
    """Install all genisys files to their specified directories
    and run any setup commands they have
    """
    print(f"Installing config file: {file} with root at {root}")
    for module in MODULES:
        mod = module(file)
        mod.install(root)
        for command in mod.setup_commands():
            subprocess.run(command, check=False)

def generate_config(file, root="."):
    """Generate all genisys files and save them to the specified directory"""
    print(f"Generating config file: {file} with root at {root}")
    for module in MODULES:
        mod = module(file)
        mod.install(root)

def run(subcommand, args):
    """Parse command line options and run the relevant helper method"""
    # Config Parser
    yaml_parser = cp.YAMLParser(args.file)
    mkpass = MakePassword(yaml_parser)

    if subcommand == "validate":
        validate(yaml_parser)
    elif subcommand == "install":
        install_config(yaml_parser, args.root)
    elif subcommand == "generate":
        generate_config(yaml_parser, args.root)
    elif subcommand == "server":
        genisys.server.run(yaml_parser)
    elif subcommand == "password":
        mkpass.make_password(args.password, yaml_parser)


def main():
    """Parse the command line options"""
    parser = argparse.ArgumentParser(description="Config File Management Tool")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate", help="Validate the configuration file."
    )
    install_parser = subparsers.add_parser(
        "install", help="Install the configuration files."
    )
    generate_parser = subparsers.add_parser(
        "generate", help="Generate the configuration files."
    )
    server_parser = subparsers.add_parser(
        "server", help="Run the server to listen for new clients."
    )
    password_parser = subparsers.add_parser(
        "password", help="Update the Ansible Vault and your config with a password."
    )

    # Flags for all subparsers
    for subparser in [validate_parser, install_parser, generate_parser, server_parser, password_parser]:
        subparser.add_argument(
            "-f",
            "--file",
            type=str,
            default="/etc/genisys.yaml",
            help="Specify input configuration file.",
        )

    # Adding root argument to install and generate parsers
    install_parser.add_argument(
        "--root",
        type=str,
        default="/",
        help="Specify the root directory for installation.",
    )
    generate_parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Specify the root directory for generation.",
    )
    password_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="The password to hash."
    )

    args = parser.parse_args()

    run(args.command, args)


if __name__ == "__main__":
    main()
