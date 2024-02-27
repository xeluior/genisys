import subprocess

def make_password(raw_password):
    secret_password = ""
    # encrypt raw_password from stdin stored as secret_password in file etc/shadow
    subprocess.run(["echo", "-n", raw_password, "ansible-vault", "encrypt_string", "--vault-password-file", "etc/shadow", "--stdin-name", secret_password], check=False)