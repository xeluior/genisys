import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from typing_extensions import TypedDict, Optional, NotRequired, Dict

CERTIFICATE_STORE_PATH = Path(os.getenv('GENISYS_CERT_STORE', '/etc/genisys/ssl'))

class CertChainArgs(TypedDict):
    """Typed Dict for arguments to be applied to the SSLContext#load_cert_chain method"""
    keyfile: str
    certfile: str
    password: NotRequired[Optional[str]]

def get_keychain(config: Dict[str, str]) -> CertChainArgs:
    """Converts from the configured filenames to the nessecary format to pass to
    SSLContext.load_cert_chain, creating the keypair if nessecary
    """
    config = config or {}

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
