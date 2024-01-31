# Description

Genisys is a program that unifies the configuration of the various services needed to use an Ubuntu 22.04 machine as a PXE boot device which will automatically provision connected devices to the specified OS. It does so by generating the nessecary configuration files for the services it has been designed to configure.

## Running

Since the application writes configuration files to priveledged locations, such as /etc/, it expects to be ran as root in most cases. This can be avoided by first generating the files to a different base directory, then manually moving them into place. Performing the installation manually this way does not execute any setup commands defined by the application, thus some services may need restarted before the PXE server can be considered fully operational.

# Prerequisites

The python dependecies are listed in requirements.txt, if you installed via `pip` these should have been taken care of automatically. You can run the application with just these dependecies. To actually be able to use the generated configurations, a number of external dependecies are required:

- dnsmasq, provides the DNS, DHCP, and TFTP servers needed to PXE boot
- vsftpd, provides the FTP server used to serve the preseed file
- iptables and iptables-persistent, used to configure the server as a NAT gateway for connected machines
- ansible, required only if using the dynamic inventory feature

# Configuration

The configuration is done via a yaml file, either specified on the command line or defaulting to `/etc/genisys.yaml`. An example configuration can be found under documentation/example.yml.

# Building and Development

This project uses the [Poetry](https://python-poetry.org/) packaging system for building and managing dependecies. To get the dependencies:

1. Install Poetry `pip install poetry`
2. If you are using VS Code, create a virtual environment in the current directory `python -m venv .venv`
3. Install the dependecies with `poetry install`

You can build the pip distribution by running `poetry build`. Refer to the poetry documentation for more commands.

## Modules

The application handles the heavy lifting of converting the Genisys config to the required service config with a modular approach. The modules exist in the genisys/modules directory and are subclasses of the Module class defined in genisys/modules/base.py. The main program loop only ever calls the `install`, `validate`, and `setup_commands` methods of the modules, which have default behavior defined in the base Module class.

The default behavior of the `install` method is to call the subclass's internal `generate` function and write the output to the file specified by the subclass's `install_location` function. It will make any parent directories needed in order to create the output file. If the output file already exists, it will move that file to the same location with the `.bak` extension.

The default behavior of the `validate` function is to run the subclass's internal `generate` function and check for any exceptions to be thrown. This indicates whether the generation of the subclass's configuration file's contents would be successful were an install attempted.

The default behavior of the `setup_commands` function is the return the empty list. It is expected that subclasses override this method to instead return a list of commands that need ran after their configuration is installed to complete the installation. This could include restarting services, or performing cleanup.

# See Also

Other programs have attempted bare-metal automation before:

- [Cobbler](https://cobbler.github.io/) provides significantly more features at the expense of complexity and additional setup.
- [Netboot.xzy](https://netboot.xyz/) allows booting of more operating systems with less automation capabilities
- [Puppet](https://www.puppet.com/)

