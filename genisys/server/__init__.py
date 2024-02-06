#!/usr/bin/env python3
import ssl
import pwd
import grp
import os
import sys
from warnings import warn
from signal import signal, SIGTERM
from typing_extensions import Dict, TypedDict, cast
from genisys.config_parser import YAMLParser
from genisys.server.inventory import Inventory
from genisys.server.http import GenisysHTTPServer, GenisysHTTPRequestHandler
import genisys.server.tls

DEFAULT_PORT = 15206
DEFAULT_INVENTORY = "/etc/ansible/hosts"

ServerOptions = TypedDict("ServerOptions", {
    "port": int,
    "user": str,
    "group": str,
    "working-directory": str,
    "ssl": Dict[str, str]
})

def run(config: YAMLParser):
    """Drops priviledges, creates the server (with SSL, if applicable), then waits for requests"""
    # parse config
    network = config.get_section("Network")
    server_options = cast(ServerOptions, network.get("server", {}) or {})

    # drop priviledges
    try:
        server_user = drop_priviledges(server_options)
    except PermissionError:
        warn("Unable to drop privledges to the specified user. Continuing as current user.")
        server_user = pwd.getpwuid(os.getuid())

    # change working directory
    workdir = server_options.get("working-directory", server_user.pw_dir)
    os.chdir(workdir)

    # create a server
    server_address = network.get('ip', '')
    server_port = server_options.get("port", DEFAULT_PORT)
    httpd = GenisysHTTPServer((server_address, server_port), GenisysHTTPRequestHandler)

    # apply TLS if applicable
    if 'ssl' in server_options:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_cert = genisys.server.tls.get_keychain(server_options['ssl'] or {})
        ssl_context.load_cert_chain(**ssl_cert)
        httpd.socket = ssl_context.wrap_socket(httpd.socket)

    # install additional data for the server to use
    ansible_cfg = config.get_section("ansible")
    inventory_path = ansible_cfg.get("inventory", DEFAULT_INVENTORY)
    httpd.inventory = Inventory(inventory_path)

    # run until SIGTERM is caught
    def sigterm_handler(*_):
        print("killed")
        del httpd.inventory
        sys.exit(SIGTERM)
    signal(SIGTERM, sigterm_handler)
    httpd.serve_forever()

def drop_priviledges(config: ServerOptions) -> pwd.struct_passwd:
    """Attempts to drop the priviledges to that of the specified users, returns false on failure"""
    if 'user' not in config:
        warn("No user specified. Continuing as current user.")
        return pwd.getpwuid(os.geteuid())

    grpnam = config.get('group', config['user'])
    uid = pwd.getpwnam(config['user'])
    gid = grp.getgrnam(grpnam)

    os.setuid(uid.pw_uid)
    os.setgid(gid.gr_gid)
    return uid
