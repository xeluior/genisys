#!/usr/bin/env python3
import ssl
import pwd
import grp
import os
from datetime import datetime, timedelta
from pathlib import Path
from warnings import warn
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import Self, Dict, TypedDict, cast, Union, NotRequired
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from genisys.config_parser import YAMLParser

DEFAULT_PORT = 15206
CERTIFICATE_STORE_PATH = Path(os.getenv('GENISYS_CERT_STORE', '/etc/genisys/ssl'))

class ServerOptions(TypedDict):
    port: int
    user: str
    group: str
    ssl: Dict[str, str]

class CertChainArgs(TypedDict):
    keyfile: str
    certfile: str
    password: NotRequired[Union[str, None]]

class GenisysHTTPRequestHandler(BaseHTTPRequestHandler):
    """Process client "hello"s by running ansible playbooks on a received POST"""
    def do_POST(self: Self):
        """On POST, store the client in the Ansible inventory and run playbooks"""
        print('posted')

def run(config: YAMLParser):
    """Drops priviledges, creates the server (with SSL, if applicable), then waits for requests"""
    # parse config
    network = config.get_section("Network")
    server_options = cast(ServerOptions, network.get("server", {}) or {})

    # drop priviledges
    if not drop_priviledges(server_options):
        warn("Unable to drop privledges to the specified user. Continuing as current user.")

    # create a server
    server_address = network.get('ip', '')
    server_port = server_options.get("port", DEFAULT_PORT)
    httpd = HTTPServer((server_address, server_port), GenisysHTTPRequestHandler)

    # apply TLS if applicable
    if 'ssl' in server_options:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_cert = get_keychain(server_options['ssl'] or {})
        ssl_context.load_cert_chain(**ssl_cert)
        httpd.socket = ssl_context.wrap_socket(httpd.socket)

    # listen
    httpd.serve_forever()

def drop_priviledges(config: ServerOptions) -> bool:
    """Attempts to drop the priviledges to that of the specified users, returns false on failure"""
    if 'user' not in config:
        warn("No user specified. Continuing as current user.")
        return True

    grpnam = config.get('group', config['user'])
    uid = pwd.getpwnam(config['user'])
    gid = grp.getgrnam(grpnam)

    try:
        os.setuid(uid.pw_uid)
        os.setgid(gid.gr_gid)
        return True
    except PermissionError:
        return False

def get_keychain(config: Dict[str, str]) -> CertChainArgs:
    """Converts from the configured filenames to the nessecary format to pass to
    SSLContext.load_cert_chain, creating the keypair if nessecary
    """
    if ('cert' not in config and 'key' in config) \
        or ('cert' in config and 'key' not in config):
        raise ValueError("Only one of SSL Certificate or Key have been specified")

    if 'cert' in config:
        passwd = None
        if 'password-file' in config:
            with open(config['password-file'], 'r', encoding='utf-8') as fd:
                passwd = fd.readline().strip('\n')
        return {
            'certfile': config['cert'],
            'keyfile': config['key'],
            'password': passwd
        }

    # generate or use the cert if applicable
    cert_path = CERTIFICATE_STORE_PATH / 'cert.pem'
    key_path = CERTIFICATE_STORE_PATH / 'key.pem'

    if not (cert_path.exists() and key_path.exists()):
        # generate new keys
        CERTIFICATE_STORE_PATH.mkdir(parents=True, exist_ok=True)
        generate_keypair(cert_path, key_path)

    return { 'certfile': str(cert_path), 'keyfile': str(key_path) }

def generate_keypair(cert_path: Path, key_path: Path):
    """Generates a new x509 keypair into the specified cert and key files"""
    # thanks ChatGPT
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create a self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, 'genisys.internal'),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).sign(
        private_key, hashes.SHA256()
    )

    # Serialize the private key and certificate to PEM format
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    pem_cert = cert.public_bytes(encoding=serialization.Encoding.PEM)

    # ensure files exist and have correct permissions
    cert_perms = 0o644
    if cert_path.exists():
        cert_path.chmod(cert_perms)
    else:
        cert_path.touch(cert_perms)

    key_perms = 0o600
    if key_path.exists():
        key_path.chmod(key_perms)
    else:
        key_path.touch(key_perms)

    # write the certs to their files
    with cert_path.open('w') as cert_file:
        cert_file.write(pem_cert.decode())
    with key_path.open('w') as key_file:
        key_file.write(pem_private_key.decode())
