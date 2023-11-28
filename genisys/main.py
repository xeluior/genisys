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
import genisys.configParser as cp


def validate(modules):
    for module in modules:
        if not module.validate():
            print(f"Error in {module.__class__.__name__} configuration!")
        else:
            print(f"{module.__class__.__name__} configuration is valid!")


def install_config(file, root="/"):
    print(f"Installing config file: {file} with root at {root}")
    for module in [Netplan, Preseed, Nat, KernelParameter, Dnsmasq, VsftpdModule, OSDownload, Syslinux]:
        mod = module(file)
        mod.install(root)
        for command in mod.setup_commands():
            subprocess.run(command, check=False)

def generate_config(file, root="."):
    print(f"Generating config file: {file} with root at {root}")
    for module in [Netplan, Preseed, Nat, KernelParameter, Dnsmasq, VsftpdModule, OSDownload, Syslinux]:
        mod = module(file)
        mod.install(root)

def daemon():
    print("Starting daemon...")

    raise NotImplementedError
    # TODO: Implement the daemon logic here


def run(subcommand, args, module):
    # Config Parser
    yamlParser = cp.YAMLParser(args.file)

    if subcommand == "validate":
        validate(module)
    elif subcommand == "install":
        install_config(yamlParser, args.root)
    elif subcommand == "generate":
        generate_config(yamlParser, args.root)


def main():
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
    daemon_parser = subparsers.add_parser(
        "daemon", help="Monitor the config file for changes."
    )

    # Flags for all subparsers
    for subparser in [validate_parser, install_parser, generate_parser]:
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

    args = parser.parse_args()

    # TODO: Instantiate modules here
    modules = []  # Example: modules = [NetworkModule(), FirewallModule()]

    run(args.command, args, modules)


if __name__ == "__main__":
    main()
