#!/usr/bin/env python

import argparse
import subprocess
import genisys.modules.netplan as net
import genisys.modules.preseed as ps
import genisys.modules.nat as nt
import genisys.modules.kernelparameter as kp
import genisys.configParser as cp

def validate(modules):
    for module in modules:
        if not module.validate():
            print(f"Error in {module.__class__.__name__} configuration!")
        else:
            print(f"{module.__class__.__name__} configuration is valid!")

def install_config(file, root="/"):
    print(f"Installing config file: {file} with root at {root}")
    # netplan
    netplan = net.Netplan(file)
    netplan.install(root)

    # preseed
    preseed = ps.Preseed(file)
    preseed.install(root)

    # nat
    nat = nt.Nat(file)
    nat.install(root)

    # kernelparameter
    kernelParameter = kp.KernelParameter(file)
    kernelParameter.install(root)

def generate_config(file, root="."):
    print(f"Generating config file: {file} with root at {root}")
    # netplan
    netplan = net.Netplan(file)
    netplan.generate()

    # preseed
    preseed = ps.Preseed(file)
    preseed.generate()

    # nat
    nat = nt.Nat(file)
    nat.generate()

    # kernelparameter
    kernelParameter = kp.KernelParameter(file)
    kernelParameter.generate()

def daemon():
    print("Starting daemon...")

    raise NotImplementedError
    # TODO: Implement the daemon logic here

def run(subcommand, args, modules):
    # Config Parser
    yamlParser = cp.YAMLParser(args.file)

    # netplan
    netplan = net.Netplan(yamlParser)

    # preseed
    preseed = ps.Preseed(yamlParser)

    # nat
    nat = nt.Nat(yamlParser)

    # kernelparameter
    kernelParameter = kp.KernelParameter(yamlParser)

    modulesList = [netplan, preseed, nat, kernelParameter]

    if subcommand == "validate":
        validate(modules)
    elif subcommand == "install":
        install_config(args.file, args.root)
        # setup commands
        for mod in modulesList:
            # function setup_commands returns list
            for command in mod.setup_commands:
                subprocess.run(command, check=False)
    elif subcommand == "generate":
        generate_config(args.file, args.root)

def main():
    parser = argparse.ArgumentParser(description="Config File Management Tool")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate the configuration file.")
    install_parser = subparsers.add_parser("install", help="Install the configuration files.")
    generate_parser = subparsers.add_parser("generate", help="Generate the configuration files.")
    daemon_parser = subparsers.add_parser("daemon", help="Monitor the config file for changes.")

    # Flags for all subparsers
    for subparser in [validate_parser, install_parser, generate_parser]:
        subparser.add_argument("-f", "--file", type=str, default="default_config.cfg", help="Specify input configuration file.")

    # Adding root argument to install and generate parsers
    install_parser.add_argument("--root", type=str, default="/", help="Specify the root directory for installation.")
    generate_parser.add_argument("--root", type=str, default=".", help="Specify the root directory for generation.")

    args = parser.parse_args()

    # TODO: Instantiate modules here
    modules = [] # Example: modules = [NetworkModule(), FirewallModule()]
    
    run(args.command, args, modules)

if __name__ == "__main__":
    main()
